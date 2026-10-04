"""Small regression tests for the English-copy quality gate."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from english_copy_quality import audit, reader_text, violations, REVIEWED_MARKERS

class EnglishCopyTests(unittest.TestCase):
    def test_rejects_known_awkward_labels(self):
        for text in ('Free-plan signals', 'Paid-plan direction', 'next rep or manager touch', 'live checkout is final'):
            with self.subTest(text=text):
                self.assertTrue(violations('<p>'+text+'</p>'))
    def test_detects_case_whitespace_and_inline_markup(self):
        self.assertTrue(violations('<p>FREE-PLAN <strong>signals</strong></p>'))
        self.assertTrue(violations('<p>next rep\n or manager touch</p>'))
    def test_rejects_customer_visible_internal_status(self):
        self.assertTrue(violations('<p>COSHUMA is currently verifying its partner referral route for this product.</p>'))
    def test_checks_description_metadata(self):
        self.assertTrue(violations('<meta name="description" content="Free-plan signals">'))
    def test_does_not_treat_urls_scripts_or_style_as_customer_copy(self):
        self.assertFalse(violations('<script>const old="Free-plan signals";</script><style>/* Paid-plan direction */</style><a href="https://example.com/Free-plan signals">Compare plans</a>'))
    def test_scope_does_not_rewrite_other_vendor_evidence(self):
        self.assertTrue(violations('<p>annual-billing view</p>', 'tool/agorapulse.html'))
        self.assertFalse(violations('<p>annual-billing view</p>', 'tool/another-product.html'))
    def test_accepts_clear_copy_and_disclosure(self):
        self.assertFalse(violations('<p>What the free plan includes. Confirm the current price and plan details at checkout.</p><p>Affiliate disclosure: COSHUMA may earn a commission at no extra cost to you.</p>'))
    def test_keeps_valid_domain_terms(self):
        self.assertFalse(violations('<p>Compare the CRM workflow, export formats and API access.</p>'))
    def test_preserves_main_fallback_reader_text(self):
        self.assertIn('Compare software', reader_text('<noscript><p>Compare software</p></noscript>'))
    def test_missing_reviewed_pages_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            _, errors=audit(Path(folder))
            self.assertTrue(errors)
            self.assertTrue(any('Missing reviewed page' in error for error in errors))
    def test_complete_fixture_and_regression(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for rel,text in REVIEWED_MARKERS.items():
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('<p>'+text+'</p>',encoding='utf-8')
            count, errors=audit(root)
            self.assertEqual(count,len(REVIEWED_MARKERS));self.assertEqual(errors,[])
            (root/'compare/gamma-vs-canva.html').write_text('<p>Free-plan signals</p>',encoding='utf-8')
            self.assertTrue(audit(root)[1])
    def test_curated_descript_source_and_template_keep_reviewed_text(self):
        root=Path(__file__).resolve().parents[2]
        expected=REVIEWED_MARKERS['tool/descript.html']
        for path in (root/'public/tool/descript.html',root/'scripts/public-copy-templates/descript.html'):
            self.assertIn(expected,reader_text(path.read_text(encoding='utf-8')))

if __name__ == '__main__':
    unittest.main()
