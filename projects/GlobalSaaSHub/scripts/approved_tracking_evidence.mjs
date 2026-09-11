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

// GetGenie was promoted to approved_tracking after the 2026-09-08 baseline file
// was created, so add the later vendor-human evidence directly to this authoritative
// normalization map. GetGenie support explicitly confirmed that the Pricing-page
// URL preserves COSHUMA attribution and is the recommended affiliate link there.
approvedTracking.set('getgenie', {
  id: 'getgenie',
  status: 'approved_tracking',
  exact_tracking_url: 'https://getgenie.ai?rui=3921',
  destination: 'https://getgenie.ai/',
  allowed_cta_urls: [
    'https://getgenie.ai?rui=3921',
    'https://getgenie.ai/pricing/?rui=3921',
  ],
  company_mailbox: 'support@coshuma.com',
  vendor_reply_message_id: '1a089dd50b6495b5',
  vendor_pricing_deeplink_reply_message_id: '1a08f03ee3235e3c',
  evidence: 'GetGenie human support directly confirmed https://getgenie.ai?rui=3921 as the support@coshuma.com account affiliate URL, then confirmed in Gmail message 1a08f03ee3235e3c that https://getgenie.ai/pricing/?rui=3921 preserves COSHUMA affiliate attribution and is the recommended Pricing-page affiliate link. No click, signup, paid customer, commission, payout, or revenue is inferred from link issuance.',
  checked_at: '2026-09-11T05:49:53Z',
  evidence_file: 'data/getgenie-pricing-affiliate-deeplink-2026-09-11.json',
});

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
// Claap's first-party affiliate page was rechecked 2026-09-10 and states that
// referrals using an affiliate link receive 30% off their first two monthly-plan
// months or 10% off their first year on an annual plan.
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
  referral_benefit: '30% off the first 2 months on a monthly plan or 10% off the first year on a yearly plan',
  referral_benefit_source: 'https://www.claap.io/affiliate-programs',
  referral_benefit_checked_at: '2026-09-10',
  evidence: 'Claap affiliate manager Lamia Karmaly replied to support@coshuma.com in Gmail message 1a08633651c79db9 and explicitly said she copied the two URLs from COSHUMA\'s PartnerStack dashboard: https://get.claap.io/rc9nqme16a9q-gfvrqk and https://get.claap.io/ssb7dex1109s. The first vendor-issued URL is the authoritative default CTA while COSHUMA awaits destination/custom-label mapping for the second. Claap\'s official affiliate page rechecked 2026-09-10 states that referred buyers using an affiliate link receive 30% off the first 2 months on a monthly plan or 10% off the first year on a yearly plan. No click, signup, commission, or revenue is inferred from link issuance.',
  checked_at: '2026-09-10T17:28:00+09:00',
  evidence_file: 'data/claap-teachable-tracking-update-2026-09-09.json',
});

// Teachable manager Camila Gouveia pasted COSHUMA's exact unique PartnerStack
// customer-facing URL and then the separate COSHUMA 30-day free-trial route into
// the support@coshuma.com mailbox. Keep the first as the default pricing-capable
// tracked route and permit the exact vendor-supplied 30-day route as a lower-friction
// conversion CTA. Never construct or guess a PartnerStack wrapper.
approvedTracking.set('teachable', {
  id: 'teachable',
  status: 'approved_tracking',
  exact_tracking_url: 'https://partnerstack.teachable.com/ce4muoxdj46j',
  destination: 'https://partnerstack.teachable.com/ce4muoxdj46j',
  allowed_cta_urls: [
    'https://partnerstack.teachable.com/ce4muoxdj46j',
    'https://partnerstack.teachable.com/COSHUMA',
  ],
  company_mailbox: 'support@coshuma.com',
  vendor_reply_message_id: '1a086aa6ef5a4d98',
  vendor_extended_trial_reply_message_id: '1a087337fdf3bdd1',
  extended_trial_tracking_url: 'https://partnerstack.teachable.com/COSHUMA',
  evidence: 'Teachable manager Camila Gouveia replied through PartnerStack to support@coshuma.com in Gmail message 1a086aa6ef5a4d98 and pasted COSHUMA\'s unique link https://partnerstack.teachable.com/ce4muoxdj46j, explicitly saying it is the unique link found under Links in the PartnerStack dashboard. In Gmail message 1a087337fdf3bdd1 she then supplied the exact COSHUMA 30-day Free Trial route https://partnerstack.teachable.com/COSHUMA and said it is also available under Links in the PartnerStack dashboard. Both routes are vendor-issued customer-facing PartnerStack URLs. No click, signup, commission, or revenue is inferred from link issuance.',
  checked_at: '2026-09-10T02:24:53+09:00',
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