import fs from 'node:fs';

const tally = {
  id: 'tally',
  name: 'Tally',
  category: 'workflow_auto',
  category_display: 'Workflow Automation',
  description: 'A no-code form builder with unlimited forms and submissions on its free plan within fair-use guidelines, plus logic, payments, integrations and paid business controls.',
  affiliate_url: null,
  pricing: 'Free plan; see official pricing for Pro and Business',
  key_features: [
    'Unlimited forms & submissions under fair-use guidelines',
    'Conditional logic & calculations',
    'File uploads & Stripe payments',
    'Integrations & custom workflows',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=tally.so&sz=128',
  primary_category: 'workflow_auto',
  comparison_group: 'workflow_auto',
  official_url: 'https://tally.so/',
  pricing_source_url: 'https://tally.so/pricing',
  pricing_verified_at: null,
  pricing_verified: false,
  currency: null,
  billing_period: null,
  evidence_source_type: 'official_pricing_page',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: '2026-09-10T15:21:00Z',
  official_evidence_url: 'https://tally.so/',
  affiliate_verified: false,
  affiliate_status: 'pending',
  affiliate_source_url: 'https://tally.so/help/referral-program',
  affiliate_verified_at: null,
  affiliate_evidence_markers: [
    'Existing COSHUMA Tally account confirmed under support@coshuma.com; do not create or submit another account.',
    'Tally Support confirmed on 2026-09-11 that the account-specific referral URL is visible only in Dashboard → Rewards and cannot be supplied from the support side.',
    'No current COSHUMA-specific customer-facing tracking URL has been copied from Rewards yet, so affiliate_url must remain null.',
    'Use official non-affiliate links only until the exact Rewards referral URL is recovered and verified.',
  ],
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === tally.id);
  if (existing) {
    Object.assign(existing, tally);
  } else {
    tools.push(tally);
  }
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

console.log('Tally canonical tool record ensured in tools.json and tools.next.json');
