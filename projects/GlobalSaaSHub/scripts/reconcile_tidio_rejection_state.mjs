import fs from './affiliate_state_fs.mjs';

const evidence = 'data/tidio-approved-tracking-2026-09-30.md';
const trackingUrl = 'https://affiliate.tidio.com/7ow2khr31ti8';
const authoritative = {
  affiliate_url: trackingUrl,
  affiliate_verified: true,
  affiliate_status: 'approved_tracking',
  affiliate_status_checked_at: '2026-09-29T14:37:23Z',
  affiliate_verified_at: '2026-09-30T09:42:19Z',
  affiliate_source_url: trackingUrl,
  affiliate_final_url: 'https://www.tidio.com/',
  affiliate_evidence_markers: [
    "Tidio PartnerStack welcome email to support@coshuma.com (Gmail 1a0ed995bd9fde81) explicitly welcomes COSHUMA to the affiliate program and identifies https://affiliate.tidio.com/7ow2khr31ti8 as 'Your affiliate link'. The email states 20% revenue share to start, scaling to 25%, a 30-day cookie window and a 7-day referral trial. Independent GET verification on 2026-09-30 followed HTTP 302 to the official tidio.com destination, observed PartnerStack attribution parameters/cookies, and ended at HTTP 200. No click, signup, paid customer, commission, payout, or revenue is inferred from approval/link validation.",
    `Authoritative repository evidence: ${evidence}`,
  ],
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const tool = tools.find((item) => item.id === 'tidio');
  if (!tool) throw new Error(`Tidio record missing from ${file}`);
  Object.assign(tool, authoritative);
  if ('affiliate_rejection_reason' in tool) tool.affiliate_rejection_reason = null;
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

console.log('Tidio authoritative approved_tracking state enforced in tools.json and tools.next.json');
