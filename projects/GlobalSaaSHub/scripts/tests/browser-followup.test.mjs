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
      // Browser evidence may include operational programs that are intentionally
      // not part of the public 151-tool catalog. Validate catalog records only.
      if (!t) continue;
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

assert.equal(state.framer.status, 'outreach_sent');
assert.equal(state.framer.tracking_url, null);
const staleFramer = {id: 'framer', affiliate_url: 'https://example.com/dashboard', affiliate_verified: true};
applyBrowserFollowup(staleFramer);
assert.equal(staleFramer.affiliate_status, 'outreach_sent');
assert.equal(staleFramer.affiliate_url, null);
assert.equal(staleFramer.affiliate_verified, false);

const kraterUrl = 'https://go.krater.ai/sang-kwon-an';
assert.equal(state.krater.status, 'approved_tracking');
assert.equal(state.krater.tracking_url, kraterUrl);
assert.equal(state.krater.application_state, 'submitted');
assert.equal(state.krater.do_not_reapply, true);
const staleKrater = {id: 'krater', affiliate_url: 'https://example.com/dashboard', affiliate_verified: false};
applyBrowserFollowup(staleKrater);
assert.equal(staleKrater.affiliate_status, 'approved_tracking');
assert.equal(staleKrater.affiliate_url, kraterUrl);
assert.equal(staleKrater.affiliate_verified, true);

// Fillout approval is valid operational evidence, but Fillout is not yet a public catalog tool.
// Keep duplicate-prevention state and the issued exact link without forcing a nonexistent tool page.
const filloutUrl = 'https://try.fillout.com/sang-kwon-an-hxwn';
assert.equal(state.fillout.status, 'approved_tracking');
assert.equal(state.fillout.tracking_url, filloutUrl);
assert.equal(state.fillout.application_state, 'submitted');
assert.equal(state.fillout.do_not_reapply, true);
assert.ok(queue.some(q =>
  (q.tool_id === 'fillout' || q.id === 'fillout' || (typeof q.id === 'string' && q.id.startsWith('fillout-'))) &&
  q.affiliate_status === 'approved_tracking' && q.exact_tracking_url === filloutUrl
));

// Newer human vendor evidence supersedes the older Typedesk browser-required snapshot.
// Keep the issued Rewardful customer URL live and ensure the stale browser task cannot
// remove the revenue CTA or reopen duplicate enrollment work.
const typedeskUrl = 'https://www.typedesk.com?via=sangkwon';
assert.equal(state.typedesk.status, 'approved_tracking');
assert.equal(state.typedesk.tracking_url, typedeskUrl);
assert.equal(state.typedesk.application_state, 'submitted');
assert.equal(state.typedesk.do_not_reapply, true);
assert.ok(queue.some(q =>
  q.tool_id === 'typedesk' && q.status === 'resolved' &&
  q.affiliate_status === 'approved_tracking' && q.exact_tracking_url === typedeskUrl
));
const typedeskPage = fs.readFileSync('dist/tool/typedesk.html', 'utf8');
assert.ok(typedeskPage.includes(typedeskUrl));
assert.ok(typedeskPage.includes('data-cta="affiliate"'));
assert.ok(typedeskPage.includes('data-tool-id="typedesk"'));
assert.ok(typedeskPage.includes('/affiliate-attribution.js'));
assert.match(typedeskPage, /affiliate disclosure/i);

// Omnisend now has a newer exact vendor-issued tracking URL from its Senior Affiliate Marketing Manager.
// The older approved-without-link snapshot must never downgrade the account or reopen link recovery.
const omnisendUrl = 'https://your.omnisend.com/4aA5k9';
assert.equal(state.omnisend.status, 'approved_tracking');
assert.equal(state.omnisend.tracking_url, omnisendUrl);
assert.equal(state.omnisend.application_state, 'submitted');
assert.equal(state.omnisend.do_not_reapply, true);
assert.ok(queue.some(q =>
  q.tool_id === 'omnisend' && q.status === 'resolved' &&
  q.affiliate_status === 'approved_tracking' && q.exact_tracking_url === omnisendUrl
));
const omnisendPage = fs.readFileSync('dist/tool/omnisend.html', 'utf8');
assert.ok(omnisendPage.includes(omnisendUrl));
assert.ok(omnisendPage.includes('data-cta="affiliate"'));
assert.ok(omnisendPage.includes('data-tool-id="omnisend"'));
assert.ok(omnisendPage.includes('/affiliate-attribution.js'));
assert.match(omnisendPage, /affiliate disclosure/i);

assert.equal(state.framer.application_state, 'not_submitted');
assert.equal(state.eprofessor.application_state, 'submitted');
assert.equal(state.eprofessor.payout_setup_complete, false);
assert.equal(state.eprofessor.earning_setup_complete, false);
const eprofessor = browserFollowups.get('eprofessor');
for (const patch of [{customer_landing_verified:false}, {portal_enrollment_confirmed:false}, {customer_tracking_kind:null}, {affiliate_url:'https://eprofessor.com/invite'}, {affiliate_url:'https://admin.eprofessor.com/referrals/'}, {affiliate_url:'https://eprofessor.com/invite/another-account'}]) {
  browserFollowups.set('eprofessor', {...eprofessor,...patch});
  assert.throws(() => applyBrowserFollowup({id:'eprofessor'}));
}
browserFollowups.set('eprofessor', eprofessor);
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
assert.equal(state['novita-ai'].application_state, 'submitted');
assert.equal(state['novita-ai'].tracking_url, 'https://novita.ai/?ref=mwjmyjy&utm_source=affiliate');
const novita = browserFollowups.get('novita-ai');
for (const patch of [{approval_email_confirmed:false}, {approval_email_recipient:'wrong@example.com'}, {affiliate_url:'https://novita.ai/'}, {customer_landing_verified:false}]) {
  browserFollowups.set('novita-ai', {...novita,...patch});
  assert.throws(() => applyBrowserFollowup({id:'novita-ai'}));
}
browserFollowups.set('novita-ai', novita);
for (const id of ['n8n', 'airia', 'joiin']) {
  const stale = {id, affiliate_url: 'https://example.com/dashboard', affiliate_verified: true};
  applyBrowserFollowup(stale);
  assert.equal(stale.affiliate_url, null);
  assert.equal(stale.affiliate_verified, false);
  const page = fs.readFileSync(`dist/tool/${id}.html`, 'utf8');
  assert.ok(!page.includes(`data-cta="affiliate" data-tool-id="${id}"`));
}
console.log('PASS: browser states, confirmed submissions, approved follow-ups, duplicate prevention, exact links, and repeat sync preservation');
