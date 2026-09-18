import './reconcile_livechat_approved_tracking.mjs';
import fs from 'node:fs';

const trackingUrl = 'https://try.sanebox.com/s1ooqjj73rpz';
const checkedAt = '2026-09-16T06:20:00+09:00';
const evidenceFile = 'data/sanebox-approved-tracking-2026-09-16.md';
const evidenceNote =
  'SaneBox Partner Program welcome email from Tony Bass to support@coshuma.com explicitly welcomed COSHUMA to the program and identified https://try.sanebox.com/s1ooqjj73rpz as the SaneBox referral link. No click, trial, paying customer, commission, payout, or revenue is inferred from approval/link issuance.';

function writeJson(path, value) {
  fs.writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

function mergeMarker(existing, marker) {
  const markers = Array.isArray(existing) ? existing : [];
  return markers.includes(marker) ? markers : [...markers, marker];
}

for (const toolsPath of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(toolsPath, 'utf8'));
  const tool = tools.find((item) => item.id === 'sanebox');
  if (tool) {
    Object.assign(tool, {
      affiliate_status: 'approved_tracking',
      affiliate_verified: true,
      affiliate_url: trackingUrl,
      affiliate_final_url: trackingUrl,
      affiliate_verified_at: checkedAt,
      affiliate_status_checked_at: checkedAt,
      affiliate_status_evidence_url: evidenceFile,
      affiliate_evidence_markers: mergeMarker(tool.affiliate_evidence_markers, evidenceNote),
      affiliate_next_action: 'Use the exact SaneBox-issued customer referral URL. Do not reapply or replace it with a dashboard, PartnerStack, or generic URL. Verify downstream metrics only from dashboard/vendor evidence.',
    });
    delete tool.affiliate_rejection_reason;
    writeJson(toolsPath, tools);
  }
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-16';
outreach.programs ||= {};
outreach.programs.sanebox = {
  status: 'approved_tracking',
  contact: 'SaneBox Partner Program / Tony Bass',
  gmail_message_id: '1a0a6da406db7ad2',
  application_receipt_message_id: '1a0a629f47d0f216',
  sender: 'support@coshuma.com',
  tracking_url: trackingUrl,
  verified_at: checkedAt,
  evidence_file: evidenceFile,
  commission_terms: '20% recurring on referred revenue; 30% tier after $500 completed sales, per SaneBox welcome email',
  optional_trial_credit_status: 'requested_pending_vendor_confirmation',
  note: evidenceNote,
};
writeJson(outreachPath, outreach);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const staleStatuses = new Set(['outreach_sent', 'enrollment_requested', 'browser_required_partnerstack_application']);
for (const item of queue) {
  if ((item.tool_id === 'sanebox' || item.id === 'sanebox' || item.id === 'sanebox-partnerstack-application') && staleStatuses.has(item.affiliate_status)) {
    item.status = 'resolved';
    item.affiliate_status = 'approved_tracking';
    item.exact_tracking_url = trackingUrl;
    item.tracking_url = trackingUrl;
    item.evidence_file = evidenceFile;
    item.reason = evidenceNote;
    item.blocker = null;
    item.next_action = 'Use the exact SaneBox-issued customer referral URL. Do not reapply or replace it with a dashboard, PartnerStack, or generic URL. Verify downstream metrics only from dashboard/vendor evidence.';
    item.updated_at = checkedAt;
  }
}
if (!queue.some((item) => item.affiliate_status === 'approved_tracking' && item.exact_tracking_url === trackingUrl)) {
  queue.push({
    id: 'sanebox-approved-tracking-2026-09-16',
    tool_id: 'sanebox',
    priority: 'high',
    status: 'resolved',
    cost: '0',
    affiliate_status: 'approved_tracking',
    exact_tracking_url: trackingUrl,
    tracking_url: trackingUrl,
    evidence_file: evidenceFile,
    evidence_message_id: 'gmail:1a0a6da406db7ad2',
    updated_at: checkedAt,
    blocker: null,
    reason: evidenceNote,
    next_action: 'Verify PartnerStack/SaneBox dashboard metrics separately; do not infer clicks, trials, customers, commission, payout, or revenue from link issuance.',
  });
}
writeJson(queuePath, queue);

console.log(`SaneBox approved tracking reconciled: ${trackingUrl}`);
