import assert from 'node:assert/strict';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import { browserFollowups, applyBrowserFollowup } from '../browser_followup_evidence.mjs';

const paths = ['data/tools.json', 'data/tools.next.json'];
const originals = paths.map(p => fs.readFileSync(p, 'utf8'));
const state = JSON.parse(fs.readFileSync('data/affiliate_outreach_state.json')).programs;
const queue = JSON.parse(fs.readFileSync('data/browser_required_queue.json'));
function check() {
  for (const p of paths) {
    const tools = JSON.parse(fs.readFileSync(p));
    for (const [id, evidence] of browserFollowups) {
      const t = tools.find(t => t.id === id);
      assert.equal(t.affiliate_status, evidence.status, id);
      assert.equal(t.affiliate_url, evidence.affiliate_url, id);
      assert.equal(t.affiliate_verified, evidence.status === 'approved_tracking', id);
      assert.equal(state[id].status, t.affiliate_status, id);
      assert.equal(state[id].tracking_url, t.affiliate_url, id);
      const q = queue.filter(q => q.tool_id === id);
      assert.equal(q.length, 1, id);
      assert.equal(q[0].affiliate_status, t.affiliate_status, id);
      assert.equal(q[0].exact_tracking_url, t.affiliate_url, id);
      if (t.affiliate_url && evidence.current_dashboard_status === 'otp_required') {
        assert.equal(q[0].status, 'browser_required_otp');
        assert.equal(t.affiliate_tracking_attribution_currently_verified, false);
      }
    }
  }
}
check();
try {
  // Exercise both deployment syncs twice: no stale override may reopen an application.
  for (let n = 0; n < 2; n++) {
    for (const s of ['sync_verified_affiliates', 'sync_latest_affiliate_states']) {
      execFileSync(process.execPath, [`scripts/${s}.mjs`]);
      check();
    }
    for (let i = 0; i < paths.length; i++) {
      const before = JSON.parse(originals[i]);
      const after = JSON.parse(fs.readFileSync(paths[i]));
      for (const id of browserFollowups.keys()) {
        assert.deepEqual(after.find(t => t.id === id), before.find(t => t.id === id));
      }
    }
  }
} finally {
  paths.forEach((p, i) => fs.writeFileSync(p, originals[i]));
}
assert.equal(state.typedesk.sender, 'qmfforfhem@gmail.com');
assert.equal(state.typedesk.portal_enrollment_confirmed, false);
assert.equal(state.n8n.application_state, 'submitted');
assert.equal(state.webflow.application_state, 'submitted');
for (const id of ['airia', 'joiin']) {
  assert.equal(state[id].status, 'application_submitted');
  assert.equal(state[id].review_state, 'pending_review');
  assert.equal(state[id].do_not_reapply, true);
  assert.equal(queue.find(q => q.tool_id === id).status, 'resolved');
}
assert.equal(state.aiassistworks.application_state, 'submitted');
assert.equal(state.aiassistworks.status, 'approved_tracking');
assert.equal(state.aiassistworks.tracking_url, 'https://www.aiassistworks.com/?via=coshuma');
assert.equal(state.aiassistworks.portal_enrollment_confirmed, true);
assert.equal(queue.find(q => q.tool_id === 'aiassistworks').status, 'resolved');
const issued = browserFollowups.get('aiassistworks');
for (const patch of [{customer_landing_verified:false}, {portal_enrollment_confirmed:false}, {affiliate_url:'https://www.aiassistworks.com/'}, {affiliate_url:'https://aiassistworks.affonso.io/'}]) {
  browserFollowups.set('aiassistworks', {...issued,...patch});
  assert.throws(() => applyBrowserFollowup({id:'aiassistworks'}));
}
browserFollowups.set('aiassistworks', issued);
assert.equal(state['novita-ai'].application_state, 'not_submitted');
for (const id of ['n8n', 'novita-ai', 'typedesk', 'airia', 'joiin']) {
  const stale = {id, affiliate_url: 'https://example.com/dashboard', affiliate_verified: true};
  applyBrowserFollowup(stale);
  assert.equal(stale.affiliate_url, null);
  assert.equal(stale.affiliate_verified, false);
  const page = fs.readFileSync(`dist/tool/${id}.html`, 'utf8');
  assert.ok(!page.includes(`data-cta="affiliate" data-tool-id="${id}"`));
}
console.log('PASS: browser states, confirmed submissions, duplicate prevention, exact links, and repeat sync preservation');
