import assert from 'node:assert/strict';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';

const paths = ['data/tools.json', 'data/tools.next.json'];
const original = paths.map(p => fs.readFileSync(p, 'utf8'));
try {
  // A stale outreach snapshot must not restore an unverified revenue CTA.
  for (const p of paths) {
    const rows = JSON.parse(fs.readFileSync(p));
    Object.assign(rows.find(t => t.id === 'tagshop-ai'), {
      affiliate_status: 'browser_required_user_consent', affiliate_verified: true,
      affiliate_url: 'https://tagshop.firstpromoter.com/',
    });
    fs.writeFileSync(p, JSON.stringify(rows));
  }
  for (const script of ['sync_verified_affiliates', 'sync_latest_affiliate_states']) {
    execFileSync(process.execPath, [`scripts/${script}.mjs`]);
    for (const p of paths) {
      const t = JSON.parse(fs.readFileSync(p)).find(t => t.id === 'tagshop-ai');
      assert.equal(t.affiliate_status, 'application_submitted');
      assert.equal(t.affiliate_url, null);
      assert.equal(t.affiliate_verified, false);
    }
  }
} finally {
  paths.forEach((p, i) => fs.writeFileSync(p, original[i]));
}
const state = JSON.parse(fs.readFileSync('data/affiliate_outreach_state.json')).programs['tagshop-ai'];
assert.equal(state.status, 'application_submitted');
assert.equal(state.tracking_url, null);
assert.equal(state.portal_enrollment_confirmed, true);
assert.equal(state.email_confirmed, true);
const queue = JSON.parse(fs.readFileSync('data/browser_required_queue.json')).filter(q => q.tool_id === 'tagshop-ai');
assert.equal(queue.length, 1);
assert.equal(queue[0].status, state.status);
assert.equal(queue[0].program_consent_checked, true);
assert.equal(queue[0].application_submitted, true);
const evidence = JSON.parse(fs.readFileSync('data/tagshop-submission-2026-09-08.json'));
assert.equal(evidence.email_confirmed, true);
assert.equal(evidence.approval_status, 'unconfirmed');
assert.equal(evidence.exact_tracking_url, null);
const page = fs.readFileSync('dist/tool/tagshop-ai.html', 'utf8');
assert.ok(!page.includes('data-cta="affiliate"'));
console.log('PASS: Tagshop enrollment survives both syncs; no duplicate queue or unverified revenue CTA.');
