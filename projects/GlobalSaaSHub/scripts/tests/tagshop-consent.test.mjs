import assert from 'node:assert/strict';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';

const TRACKING_URL = 'https://tagshop.ai?via=coshuma-22501e';
const paths = ['data/tools.json', 'data/tools.next.json'];
const original = paths.map(p => fs.readFileSync(p, 'utf8'));
try {
  // Stale enrollment/browser snapshots must never overwrite the newer issued customer link.
  for (const p of paths) {
    const rows = JSON.parse(fs.readFileSync(p));
    Object.assign(rows.find(t => t.id === 'tagshop-ai'), {
      affiliate_status: 'application_submitted',
      affiliate_verified: false,
      affiliate_url: null,
    });
    fs.writeFileSync(p, JSON.stringify(rows));
  }
  for (const script of ['sync_verified_affiliates', 'sync_latest_affiliate_states']) {
    execFileSync(process.execPath, [`scripts/${script}.mjs`]);
    for (const p of paths) {
      const t = JSON.parse(fs.readFileSync(p)).find(t => t.id === 'tagshop-ai');
      assert.equal(t.affiliate_status, 'approved_tracking');
      assert.equal(t.affiliate_url, TRACKING_URL);
      assert.equal(t.affiliate_verified, true);
    }
  }
} finally {
  paths.forEach((p, i) => fs.writeFileSync(p, original[i]));
}

const approved = JSON.parse(fs.readFileSync('data/approved-tracking-2026-09-08.json'))
  .items.find(item => item.id === 'tagshop-ai');
assert.ok(approved);
assert.equal(approved.status, 'approved_tracking');
assert.equal(approved.exact_tracking_url, TRACKING_URL);
assert.match(approved.evidence, /1a0829e45df98eb7/);
assert.ok(!approved.exact_tracking_url.includes('firstpromoter.com'));

const historical = JSON.parse(fs.readFileSync('data/tagshop-submission-2026-09-08.json'));
assert.equal(historical.email_confirmed, true);
assert.equal(historical.approval_status, 'unconfirmed');
assert.equal(historical.exact_tracking_url, null);

const page = fs.readFileSync('dist/tool/tagshop-ai.html', 'utf8');
assert.ok(page.includes(TRACKING_URL));
assert.ok(page.includes('data-cta="affiliate"'));
assert.ok(!page.includes('href="https://tagshop.firstpromoter.com/login"'));
console.log('PASS: newer Tagshop welcome-link evidence overrides stale enrollment state and monetizes the customer CTA.');