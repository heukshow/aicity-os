import fs from './affiliate_state_fs.mjs';

const agorapulse = {
  id: 'agorapulse',
  name: 'Agorapulse',
  category: 'social_media',
  category_display: 'Social Media & Listening',
  description: 'A social media management platform with publishing, inbox, reporting and an Advanced Listening add-on for monitoring brands, competitors and market conversations.',
  affiliate_url: null,
  pricing: '30-day free trial; Standard $99/user/month or $79/user/month billed annually',
  key_features: [
    'Social publishing & unified inbox',
    'Social reporting & team workflows',
    'Advanced Listening add-on',
    'Competitive listening & share of voice',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=agorapulse.com&sz=128',
  primary_category: 'social_media',
  comparison_group: 'social_listening',
  official_url: 'https://www.agorapulse.com/',
  pricing_source_url: 'https://www.agorapulse.com/pricing/',
  pricing_verified_at: '2026-09-11T02:41:00+09:00',
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly; annual billing option',
  evidence_source_type: 'official_pricing_page',
  is_manual_override: true,
  pricing_evidence_markers: [
    '30-day free trial',
    'no credit card required',
    'Standard $99 monthly / $79 annual-billing equivalent',
  ],
  official_verification_status: 'verified',
  official_verified_at: '2026-09-11T02:41:00+09:00',
  official_evidence_url: 'https://www.agorapulse.com/pricing/',
  affiliate_verified: false,
  affiliate_status: 'waiting_vendor_response',
  affiliate_source_url: 'https://www.agorapulse.com/partners/referral/',
  affiliate_verified_at: null,
  affiliate_status_checked_at: '2026-10-03T03:05:00+09:00',
  affiliate_next_action: 'Wait for Mike Allton / Agorapulse to reply to the existing referral-partner inquiry and 2026-10-03 follow-up. Do not submit duplicate outreach or publish a guessed URL.',
  affiliate_evidence_markers: [
    'Agorapulse current Referral Partner Program advertises a unique referral link and 90-day tracking after enrollment.',
    'COSHUMA sent the original referral enrollment inquiry in Gmail 1a0907c7757252b0 and one follow-up on 2026-10-03 in Gmail 1a0fdcf483d35e25.',
    'Exact COSHUMA customer tracking URL remains unknown.',
  ],
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === agorapulse.id);
  if (existing) {
    Object.assign(existing, agorapulse);
  } else {
    tools.push(agorapulse);
  }
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

console.log('Agorapulse canonical tool record ensured in tools.json and tools.next.json');
