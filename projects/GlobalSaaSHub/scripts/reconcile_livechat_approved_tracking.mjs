import fs from 'node:fs';

const trackingUrl = 'https://www.livechat.com/?a=8IetMhQv&utm_campaign=pp_livechat-default&utm_source=PP';
const vendorShortUrl = 'https://share.text.com/q8mL2psx';
const checkedAt = '2026-09-18T19:38:07+09:00';
const evidenceIssue = 'https://github.com/heukshow/aicity-os/issues/310';
const evidenceNote =
  'Text Support replied to support@coshuma.com in existing Gmail thread 1a08c0544c56b5ac (message 1a0b418541063824) and explicitly said the LiveChat affiliate URL is available under the existing Partner App Affiliate area, supplying https://share.text.com/q8mL2psx. Prior authenticated Partner App evidence had already issued https://www.livechat.com/?a=8IetMhQv&utm_campaign=pp_livechat-default&utm_source=PP and verified that it resolves to the official LiveChat destination with attribution retained. Preserve that canonical verified URL; record the vendor-supplied short URL as corroborating alternate evidence. No new campaign, duplicate enrollment, signup, trial, paid account, commission, payout, or revenue is inferred.';

function writeJson(path, value) {
  fs.writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`);
}

function mergeMarker(existing, marker) {
  const markers = Array.isArray(existing) ? existing : [];
  return markers.includes(marker) ? markers : [...markers, marker];
}

for (const toolsPath of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(toolsPath, 'utf8'));
  const tool = tools.find((item) => item.id === 'livechat');
  if (tool) {
    Object.assign(tool, {
      affiliate_status: 'approved_tracking',
      affiliate_verified: true,
      affiliate_url: trackingUrl,
      affiliate_final_url: 'https://www.livechat.com/',
      affiliate_verified_at: checkedAt,
      affiliate_status_checked_at: checkedAt,
      affiliate_status_evidence_url: evidenceIssue,
      affiliate_evidence_markers: mergeMarker(tool.affiliate_evidence_markers, evidenceNote),
      affiliate_next_action: 'Preserve the already verified LiveChat customer tracking URL. Do not create another campaign or send another exact-link request. Keep the vendor-supplied share.text.com URL as corroborating alternate evidence unless it is separately chosen and validated for publication.',
    });
    delete tool.affiliate_rejection_reason;
    writeJson(toolsPath, tools);
  }
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-18';
outreach.programs ||= {};
outreach.programs.livechat = {
  status: 'approved_tracking',
  contact: 'Text Support / LiveChat Partner Program',
  gmail_message_id: '1a0b418541063824',
  gmail_thread_id: '1a08c0544c56b5ac',
  sender: 'support@coshuma.com',
  tracking_url: trackingUrl,
  vendor_supplied_alternate_url: vendorShortUrl,
  verified_at: checkedAt,
  note: evidenceNote,
  do_not_reapply: true,
  do_not_repeat_exact_link_outreach: true,
};
writeJson(outreachPath, outreach);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
for (const item of queue) {
  if (item.tool_id === 'livechat' || item.id === 'livechat' || item.id === 'livechat-existing-partner-referral-link') {
    item.status = 'resolved';
    item.affiliate_status = 'approved_tracking';
    item.exact_tracking_url = trackingUrl;
    item.tracking_url = trackingUrl;
    item.vendor_supplied_alternate_url = vendorShortUrl;
    item.evidence_message_id = 'gmail:1a0b418541063824';
    item.reason = evidenceNote;
    item.blocker = null;
    item.next_action = 'No browser recovery or duplicate campaign creation is required. Preserve the verified LiveChat tracking URL and only update downstream KPI values from new dashboard or vendor evidence.';
    item.updated_at = checkedAt;
  }
}
if (!queue.some((item) => item.affiliate_status === 'approved_tracking' && item.exact_tracking_url === trackingUrl)) {
  queue.push({
    id: 'livechat-existing-partner-referral-link',
    tool_id: 'livechat',
    priority: 'high',
    status: 'resolved',
    cost: '0',
    affiliate_status: 'approved_tracking',
    exact_tracking_url: trackingUrl,
    tracking_url: trackingUrl,
    vendor_supplied_alternate_url: vendorShortUrl,
    evidence_message_id: 'gmail:1a0b418541063824',
    gmail_thread_id: '1a08c0544c56b5ac',
    updated_at: checkedAt,
    blocker: null,
    reason: evidenceNote,
    next_action: 'No further exact-link outreach or campaign creation. Preserve the verified route; downstream KPI fields stay evidence-only and unknown where not reported.',
    do_not: [
      'Do not create a duplicate LiveChat affiliate campaign or Partner Program account.',
      'Do not replace the verified customer tracking URL with a Partner App dashboard, onboarding URL, or generic untracked homepage.',
      'Do not infer signups, trials, paid accounts, commission, payout, or revenue from link issuance or link validation.',
    ],
  });
}
writeJson(queuePath, queue);

console.log(`LiveChat approved tracking reconciled: ${trackingUrl}`);
