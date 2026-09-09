import fs from 'node:fs';

export const approvedTracking = new Map(JSON.parse(fs.readFileSync(new URL('../data/approved-tracking-2026-09-08.json', import.meta.url), 'utf8')).items.map(item => [item.id, item]));

// AWeber's official Advocate Program documentation says the assigned referral ID
// may be appended to any AWeber page while preserving the referral cookie. Keep
// the originally issued easy-email URL as the authoritative account tracking URL,
// but explicitly permit the pricing-page variant for buyer-intent CTAs.
const aweber = approvedTracking.get('aweber');
if (aweber) {
  aweber.allowed_cta_urls = [
    aweber.exact_tracking_url,
    'https://www.aweber.com/pricing.htm?id=561868',
  ];
  aweber.deep_link_evidence =
    'AWeber official Advocate Program documentation verified 2026-09-09: the referral id may be appended to any AWeber page and the referral cookie remains attributable. The issued easy-email URL remains the authoritative account tracking URL.';
}

// Newer authenticated Dub follow-up for a tool that already exists in the public catalog.
// Fillout approval remains valid operational evidence, but Fillout is not yet a catalog tool,
// so it must not enter this map because deployment verification requires a real tool page.
approvedTracking.set('krater', {
  id: 'krater',
  status: 'approved_tracking',
  exact_tracking_url: 'https://go.krater.ai/sang-kwon-an',
  destination: 'https://go.krater.ai/sang-kwon-an',
  evidence: 'Authenticated Dub partner dashboard shows Krater Approved/Enrolled and issues the exact customer-facing tracking link go.krater.ai/sang-kwon-an. The Dub partner-application URL is not treated as a customer tracking link. No referral, sale, commission, or revenue is inferred.',
  checked_at: '2026-09-08T14:00:00+09:00',
  evidence_file: 'data/krater-affiliate-enrollment-evidence-2026-09-08.md',
});

// Vendor-confirmed Rewardful tracking URL received in the COSHUMA company mailbox.
// Keep Rewardful login/dashboard/onboarding URLs out of buyer-facing CTAs.
approvedTracking.set('typedesk', {
  id: 'typedesk',
  status: 'approved_tracking',
  exact_tracking_url: 'https://www.typedesk.com?via=sangkwon',
  destination: 'https://www.typedesk.com?via=sangkwon',
  allowed_cta_urls: [
    'https://www.typedesk.com?via=sangkwon',
    'https://www.typedesk.com/pricing?via=sangkwon',
  ],
  company_mailbox: 'support@coshuma.com',
  vendor_reply_message_id: '1a083d37fcdad998',
  vendor_deeplink_reply_message_id: '1a0841c6e959ea36',
  evidence: 'Typedesk human reply from hennadiy@typedesk.com to support@coshuma.com explicitly identifies https://www.typedesk.com?via=sangkwon as COSHUMA\'s unique tracking link and says reports remain available in the Rewardful dashboard. A follow-up human reply confirms there are no coupon codes currently and that the affiliate attribution may be used on any Typedesk page. No click, signup, commission, or revenue is inferred from link issuance or deep-link permission alone.',
  checked_at: '2026-09-09T12:20:00+09:00',
  evidence_file: 'data/typedesk-approved-tracking-2026-09-09.md',
});

// Claap affiliate manager Lamia Karmaly copied both URLs directly from COSHUMA's
// existing PartnerStack dashboard into the company mailbox. The first issued URL
// is the default customer-facing route; the second remains a verified alternate
// until Lamia confirms the intended destination/custom label of each link.
approvedTracking.set('claap', {
  id: 'claap',
  status: 'approved_tracking',
  exact_tracking_url: 'https://get.claap.io/rc9nqme16a9q-gfvrqk',
  destination: 'https://get.claap.io/rc9nqme16a9q-gfvrqk',
  allowed_cta_urls: [
    'https://get.claap.io/rc9nqme16a9q-gfvrqk',
  ],
  company_mailbox: 'support@coshuma.com',
  vendor_reply_message_id: '1a08633651c79db9',
  alternate_verified_url: 'https://get.claap.io/ssb7dex1109s',
  evidence: 'Claap affiliate manager Lamia Karmaly replied to support@coshuma.com in Gmail message 1a08633651c79db9 and explicitly said she copied the two URLs from COSHUMA\'s PartnerStack dashboard: https://get.claap.io/rc9nqme16a9q-gfvrqk and https://get.claap.io/ssb7dex1109s. The first vendor-issued URL is the authoritative default CTA while COSHUMA awaits destination/custom-label mapping for the second. No click, signup, commission, or revenue is inferred from link issuance.',
  checked_at: '2026-09-09T21:45:09+09:00',
  evidence_file: 'data/claap-teachable-tracking-update-2026-09-09.json',
});

export function applyApprovedTracking(tool) {
  const item = approvedTracking.get(tool.id);
  if (!item) return false;
  if (tool.affiliate_url === item.exact_tracking_url && tool.affiliate_status === 'approved_tracking' && tool.affiliate_verified === true) return true;
  Object.assign(tool, {
    affiliate_url: item.exact_tracking_url,
    affiliate_status: 'approved_tracking',
    affiliate_verified: true,
    affiliate_verified_at: item.checked_at,
    affiliate_final_url: item.destination,
    affiliate_evidence_markers: [item.evidence, item.evidence_file || 'data/approved-tracking-2026-09-08.json'],
  });
  if ('affiliate_rejection_reason' in tool) tool.affiliate_rejection_reason = null;
  return true;
}
