import fs from 'node:fs';

const PROJECT = new URL('../', import.meta.url);
const approvedPath = new URL('data/approved-tracking-2026-09-08.json', PROJECT);
const outreachPath = new URL('data/affiliate_outreach_state.json', PROJECT);
const queuePath = new URL('data/browser_required_queue.json', PROJECT);

const approved = JSON.parse(fs.readFileSync(approvedPath, 'utf8')).items.find(item => item.id === 'tagshop-ai');
if (!approved || approved.status !== 'approved_tracking' || !approved.exact_tracking_url) {
  throw new Error('Tagshop approved tracking evidence is missing');
}

const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
const prior = outreach.programs['tagshop-ai'] || {};
outreach.updated_at = '2026-09-09';
outreach.programs['tagshop-ai'] = {
  ...prior,
  status: 'approved_tracking',
  tracking_url: approved.exact_tracking_url,
  sender: 'support@coshuma.com',
  contact: prior.contact || 'priyanka@tagshop.ai',
  gmail_message_id: '1a0829e45df98eb7',
  verified_at: approved.checked_at,
  evidence_file: 'data/tagshop-approved-tracking-2026-09-09.md',
  note: 'Tagshop welcome email 1a0829e45df98eb7 explicitly issued the customer-facing referral URL and says paid referred subscriptions are rewarded. Preserve this exact via-bearing link; the FirstPromoter login URL is administrative only. Do not reapply. No signup, sale, commission, payout or revenue is inferred.',
  next_action: 'Preserve the issued customer tracking URL and optimize eligible Tagshop CTAs. Do not reapply.',
  do_not_reapply: true,
};
fs.writeFileSync(outreachPath, JSON.stringify(outreach, null, 2) + '\n');

const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
let item = queue.find(q => q.tool_id === 'tagshop-ai' || q.id === 'tagshop-ai-affiliate-followup');
if (!item) {
  item = { id: 'tagshop-ai-affiliate-followup', tool_id: 'tagshop-ai', priority: 'high', cost: '0' };
  queue.push(item);
}
Object.assign(item, {
  status: 'approved_tracking',
  affiliate_status: 'approved_tracking',
  exact_tracking_url: approved.exact_tracking_url,
  verified_at: approved.checked_at,
  resolved_at: approved.checked_at,
  blocker: null,
  reason: 'Resolved by Tagshop welcome email 1a0829e45df98eb7, which issued the exact customer-facing referral URL https://tagshop.ai?via=coshuma-22501e and states paid referred subscriptions are rewarded.',
  next_action: 'No browser follow-up or reapplication. Preserve the exact issued customer URL and use it only on eligible customer CTAs.',
  resolution_evidence: 'data/tagshop-approved-tracking-2026-09-09.md',
  application_submitted: true,
  portal_enrollment_confirmed: true,
  do_not_reapply: true,
});
item.do_not = [
  'Do not reapply to Tagshop or create another affiliate account.',
  'Do not use tagshop.firstpromoter.com/login, an onboarding page, application page, or generic homepage as the affiliate/revenue URL.',
  'Do not infer customer signup, paid conversion, commission, payout or revenue from link issuance or link verification.',
];
fs.writeFileSync(queuePath, JSON.stringify(queue, null, 2) + '\n');

console.log(`Tagshop operational state reconciled to approved_tracking: ${approved.exact_tracking_url}`);