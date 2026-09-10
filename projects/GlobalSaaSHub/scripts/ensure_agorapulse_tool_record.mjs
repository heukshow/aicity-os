import fs from 'node:fs';

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
  affiliate_status: 'unverified',
  affiliate_source_url: 'https://www.agorapulse.com/partners/agency/',
  affiliate_verified_at: null,
  affiliate_evidence_markers: [
    'Official agency partner program exists',
    'No COSHUMA-specific commission-bearing customer URL verified as of 2026-09-11',
    'Use official non-affiliate links only until an exact customer tracking route is proven',
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
