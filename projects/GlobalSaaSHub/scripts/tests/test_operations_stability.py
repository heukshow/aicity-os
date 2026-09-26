import copy
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import affiliate_lifecycle_guard as lifecycle
import verify_release_queue as release
import reconcile_operations_registry as registry


class LifecycleTests(unittest.TestCase):
    def test_unchanged_status_cannot_erase_newer_evidence(self):
        old = {'affiliate_status': 'approved_tracking', 'affiliate_status_checked_at': '2026-09-26',
               'affiliate_verified_at': '2026-09-25', 'affiliate_evidence_markers': ['vendor-issued link']}
        new = dict(old, affiliate_verified_at='2026-09-01', affiliate_evidence_markers=[])
        self.assertEqual(lifecycle.preserve(old, new)[0], old)

    def test_all_regressions_preserve_evidence_and_product_edits(self):
        for old_status, new_status in [
            ('application_submitted', 'not_submitted'), ('approved', 'application_pending'),
            ('approved', 'browser_required'), ('approved_tracking', 'approved'),
            ('rejected', 'application_submitted'), ('rejected', 'approved_tracking'),
        ]:
            old = {'id': 'vendor', 'affiliate_status': old_status, 'affiliate_status_checked_at': '2026-09-26T00:00:00Z',
                   'affiliate_url': 'https://vendor.test/ref/exact' if old_status == 'approved_tracking' else None}
            new = {'id': 'vendor', 'affiliate_status': new_status, 'affiliate_url': None, 'pricing': 'preserve product edit'}
            actual, changed = lifecycle.preserve(old, new)
            self.assertTrue(changed)
            self.assertEqual(actual['affiliate_status'], old_status)
            self.assertEqual(actual['affiliate_url'], old['affiliate_url'])
            self.assertEqual(actual['pricing'], new['pricing'])

    def test_newer_direct_rejection_can_revoke_tracking(self):
        old = {'affiliate_status': 'approved_tracking', 'affiliate_url': 'https://vendor.test/ref/exact',
               'checked_at': '2026-09-25T00:00:00Z'}
        new = {'affiliate_status': 'rejected', 'affiliate_url': None, 'affiliate_lifecycle_override': {
            'source_type': 'vendor_email', 'source_ref': 'fixture-message', 'reason': 'revoked',
            'observed_at': '2026-09-26T00:00:00Z'}}
        self.assertEqual(lifecycle.preserve(old, new), (new, False))
        replayed = dict(new, affiliate_status='application_submitted')
        self.assertEqual(lifecycle.preserve(new, replayed)[0]['affiliate_status'], 'rejected')

    def test_changed_url_without_direct_evidence_is_preserved(self):
        old = {'affiliate_status': 'approved_tracking', 'affiliate_url': 'https://vendor.test/ref/exact'}
        new = {'affiliate_status': 'approved_tracking', 'affiliate_url': 'https://vendor.test/dashboard'}
        self.assertEqual(lifecycle.preserve(old, new)[0]['affiliate_url'], old['affiliate_url'])

    def test_deletion_is_not_silently_accepted(self):
        with self.assertRaises(ValueError):
            lifecycle.reconcile([{'id': 'vendor', 'affiliate_status': 'approved'}], [], 'tools.json')


def candidate(name='one'):
    return {'record_id': name, 'task_key': name, 'lifecycle': 'production_verification_requested',
            'next_owner': 'Release & Reliability Team', 'completion_gate': 'production_verified',
            'evidence': {'implementation_pr': 1, 'merge_commit': 'a' * 40}}


class PublicProducerTests(unittest.TestCase):
    def test_final_dist_polish_preserves_source_disclosure_outside_cta_row(self):
        import self_heal_source_affiliate_disclosures as source
        import guard_built_customer_copy as built
        from guard_customer_only_copy import clean_html
        link='<a data-cta="affiliate" href="https://vendor.test/ref" rel="sponsored">Try free</a>'
        row='<div class="flex">'
        before=source.PAGE_NOTICE_SLOT+'\n'+source.PAGE_NOTICE+'\n'+row+link+'</div>'
        polish=lambda html: built.enforce_disclosure_policy('compare/fixture.html', built.final_polish(clean_html(html)))
        first=polish(before)
        self.assertNotIn(source.PAGE_NOTICE_SLOT, first)
        self.assertLess(first.index('data-affiliate-disclosure="page"'), first.index(row))
        self.assertEqual(first, polish(first))
        self.assertIn(link, first)
        self.assertEqual(first.count('Affiliate disclosure:'), 1)

    def test_disclosure_repairs_escaped_newlines_without_shrinking_cta_row(self):
        import self_heal_source_affiliate_disclosures as notice
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'public').mkdir()
            page=root/'public/gamma.html'
            link='<a data-cta="affiliate" href="https://vendor.test/ref" rel="sponsored">Try free</a>'
            page.write_text(notice.PAGE_NOTICE_SLOT+'<div class="flex">'+r'\n\n'+notice.PAGE_NOTICE+r'\n'+link+'</div><pre>'+r'code: \n'+'</pre>')
            with patch.object(notice,'ROOT',root):
                self.assertTrue(notice.normalize_page(page)); first=page.read_text()
                self.assertFalse(notice.normalize_page(page))
            self.assertLess(first.index('data-affiliate-disclosure'),first.index('<div class="flex">'))
            self.assertNotIn(r'\n\n',first)
            self.assertIn('<pre>'+r'code: \n'+'</pre>',first)
            self.assertIn(link,first)
            self.assertEqual(first.count('data-affiliate-disclosure="page"'),1)

    def test_default_page_and_home_disclosures_are_repeatable(self):
        import self_heal_source_affiliate_disclosures as notice
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'public').mkdir()
            page=root/'public/tool.html'; home=root/'index.html'
            html='<body><div> <a data-cta="affiliate" href="https://vendor.test/ref">Try</a></div></body>'
            page.write_text(html); home.write_text(html)
            with patch.object(notice,'ROOT',root):
                notice.normalize_page(page); notice.normalize_home()
                first=(page.read_text(),home.read_text())
                self.assertFalse(notice.normalize_page(page)); self.assertFalse(notice.normalize_home())
            self.assertEqual(first,(page.read_text(),home.read_text()))
            self.assertNotIn(r'\n', ''.join(first))

    def test_raw_source_rejects_internal_program_metadata_but_keeps_disclosure(self):
        import guard_raw_public_source as raw
        for text in ['<title>CRO Features & Affiliate Facts</title>',
                     '<meta content="current public affiliate-program facts"/>']:
            self.assertTrue(any(pattern.search(raw.masked(text)) for _, pattern in raw.FORBIDDEN))
        disclosure = 'Affiliate disclosure: We may earn a commission at no extra cost to you.'
        self.assertFalse(any(pattern.search(raw.masked(disclosure)) for _, pattern in raw.FORBIDDEN))

    def test_databox_cleanup_preserves_one_canonical_consumer_notice(self):
        from self_heal_source_affiliate_disclosures import PAGE_NOTICE
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir(); (root / 'public/tool').mkdir(parents=True)
            (root / 'config').mkdir()
            shutil.copy(SCRIPTS.parent / 'config/public_content_policy.json', root / 'config')
            for name in ['clean_databox_customer_copy.py', 'self_heal_source_affiliate_disclosures.py']:
                shutil.copy(SCRIPTS / name, root / 'scripts' / name)
            page = root / 'public/tool/databox.html'
            html = PAGE_NOTICE + '<a href="https://databox.com?aff_id=15298659&fp_ref=sangkwon-72c9ec">Try</a>'
            page.write_text(html)
            command = [sys.executable, str(root / 'scripts/clean_databox_customer_copy.py')]
            for _ in range(2):
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(page.read_text(), html)
            page.write_text(PAGE_NOTICE + html)
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_search_fillout_and_revenue_producers_can_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir(); (root / 'src').mkdir()
            shutil.copy(SCRIPTS.parent / 'src/App.jsx', root / 'src/App.jsx')
            scripts = ['fix_search_focus_scroll.py', 'simplify_home_tool_cards.py',
                       'improve_mobile_home_ux.py', 'apply_revenue_first_home_hook.py', 'add_fillout_search_shortcut.py']
            for name in scripts:
                shutil.copy(SCRIPTS / name, root / 'scripts' / name)
            snapshots = []
            for _ in range(2):
                for name in scripts:
                    result = subprocess.run([sys.executable, str(root / 'scripts' / name)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                snapshots.append((root / 'src/App.jsx').read_text())
            self.assertEqual(*snapshots)
            self.assertIn('tool.detail_url ||', snapshots[1])
            self.assertIn('Verified free trials & deals', snapshots[1])


class ReleaseTests(unittest.TestCase):
    def test_handoff_audit_recognizes_explicit_previous_revision_only(self):
        from audit_release_handoff_registry import known_release_pairs
        row=candidate()
        row['evidence']['previous_visual_revision']={'merge_commit': 'b' * 40}
        pairs=known_release_pairs([row])
        self.assertIn(('one', 'a' * 40), pairs)
        self.assertIn(('one', 'b' * 40), pairs)
        self.assertNotIn(('one', 'c' * 40), pairs)
        self.assertNotIn(('other', 'b' * 40), pairs)

    def test_artifact_ancestry_requires_exact_successful_pages_deployment(self):
        pages_sha = 'b' * 40
        deployment = {'name': 'pages build and deployment', 'head_sha': pages_sha,
                      'status': 'in_progress', 'conclusion': None, 'id': 123}
        with patch.object(release, 'deployed_source_sha', return_value='a' * 40), \
             patch.object(release, 'run', return_value=subprocess.CompletedProcess([], 0, stdout=pages_sha)), \
             patch.object(release, 'github_api', return_value={'workflow_runs': [deployment]}):
            failures = []
            release.verify_deployed_ancestry(candidate(), {'verify_deployed_ancestry': True}, failures, [])
            self.assertTrue(failures)
            deployment.update(status='completed', conclusion='success')
            failures = []
            release.verify_deployed_ancestry(candidate(), {'verify_deployed_ancestry': True}, failures, [])
            self.assertFalse(failures)
            deployment['head_sha'] = 'c' * 40
            failures = []
            release.verify_deployed_ancestry(candidate(), {'verify_deployed_ancestry': True}, failures, [])
            self.assertTrue(failures)

    def test_coverage_gap_is_a_failure(self):
        with self.assertRaises(SystemExit):
            release.validate_contract({'active_queue': [candidate()]}, {'schema_version': 1, 'records': {}})

    def test_failed_comment_does_not_block_retry(self):
        body = 'RELEASE_VERIFICATION\n- record_id: `one`\n- result: `verification_failed`\n' + 'a' * 40
        with patch.object(release, 'github_api', side_effect=[[{'body': body}], []]):
            self.assertFalse(release.has_existing_result(candidate(), 'test'))

    def test_missing_head_spec_does_not_block_next_candidate(self):
        records = {'active_queue': [candidate('one'), candidate('two')]}
        specs = {'schema_version': 1, 'records': {'two': {'mode': 'generated_json_state', 'producer': ['node', 'fixture'], 'checks': []}}}
        with patch.object(release, 'load_json', side_effect=[records, specs]), patch.object(sys, 'argv', ['verify']), \
             patch.dict(os.environ, {'GITHUB_TOKEN': 'test'}), patch.object(release, 'has_existing_result', return_value=False), \
             patch.object(release, 'verify_record', return_value=([], ['actual live checks'])) as verify, \
             patch.object(release, 'post_result') as post:
            self.assertEqual(release.main(), 1)
            self.assertEqual(verify.call_count, 1)
            self.assertEqual([c.args[1] for c in post.call_args_list], ['verification_failed', 'production_verified'])


class RegistryTests(unittest.TestCase):
    def test_form_completion_cannot_bypass_production_gate(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir(); (root / 'data').mkdir()
            shutil.copy(SCRIPTS / 'validate_operations_registry.py', root / 'scripts')
            row = dict(record_id='form', task_key='form', target='vendor', owner_team='Affiliate',
                lifecycle='completed_with_evidence', next_owner='Affiliate', priority='normal',
                evidence={'application_state':'submitted', 'submission_confirmation':'received',
                          'submission_evidence_comment_id':123, 'form_url':'https://vendor.test/form'},
                completion_gate='formal_application_submission_evidence_or_rejected_with_evidence',
                completion_gate_satisfied=True, user_action_required=False)
            def validate():
                (root / 'data/operations_registry.json').write_text(json.dumps({'schema_version':1,'active_queue':[row]}))
                return subprocess.run([sys.executable,str(root / 'scripts/validate_operations_registry.py')],capture_output=True).returncode
            self.assertEqual(validate(),0)
            row['completion_gate']='production_verified'
            self.assertNotEqual(validate(),0)
            row['completion_gate']='formal_application_submission_evidence_or_rejected_with_evidence'
            row['evidence'].pop('submission_evidence_comment_id')
            self.assertNotEqual(validate(),0)

    def test_merge_only_requests_verification(self):
        row = candidate(); row['lifecycle'] = 'assigned_to_team'
        result, _ = registry.reconcile({'active_queue': [row]}, [],
            lambda _: {'merged': True, 'merge_commit_sha': 'a' * 40}, lambda _: {}, lambda _: True)
        self.assertEqual(result['active_queue'][0]['lifecycle'], 'production_verification_requested')
        self.assertFalse(result['active_queue'][0]['completion_gate_satisfied'])

    def test_only_exact_trusted_success_advances(self):
        comment = {'id': 99, 'user': {'login': 'github-actions[bot]'}, 'created_at': '2026-09-27T00:00:00Z',
            'body': 'RELEASE_VERIFICATION\n- record_id: `one`\n- merge: `' + 'a' * 40 + '`\n- result: `production_verified`\n- verification_run: `123`'}
        pr = lambda _: {'merged': True, 'merge_commit_sha': 'a' * 40}
        run = lambda _: {'name': 'COSHUMA Release Verification', 'head_branch': 'main', 'status': 'completed'}
        result, _ = registry.reconcile({'active_queue': [candidate()]}, [comment], pr, run, lambda _: True)
        self.assertEqual(result['active_queue'][0]['lifecycle'], 'production_verified')
        self.assertEqual(result['active_queue'][0]['verification'],
                         'Deterministic production verification succeeded in run 123; trusted evidence comment 99.')
        comment['body'] = comment['body'].replace('production_verified', 'verification_failed')
        result, _ = registry.reconcile({'active_queue': [candidate()]}, [comment], pr, run, lambda _: True)
        self.assertEqual(result['active_queue'][0]['lifecycle'], 'production_verification_requested')


if __name__ == '__main__':
    unittest.main()
