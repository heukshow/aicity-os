import fs from 'node:fs';

const docusign = {
  id: 'docusign',
  name: 'Docusign',
  category: 'workflow_auto',
  category_display: 'Workflow Automation',
  description: 'Electronic-signature software for sending, signing, storing, and managing agreements, with reusable templates, audit trails, integrations, and paid team plans.',
  affiliate_url: null,
  pricing: 'Personal $10/month; Standard $25/user/month; Business Pro $40/user/month on the annual-billing US view',
  key_features: [
    'Electronic signatures & agreement sending',
    'Reusable templates & audit trails',
    '900+ integrations on the US product page',
    'Team collaboration & advanced agreement workflows',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=docusign.com&sz=128',
  primary_category: 'workflow_auto',
  comparison_group: 'workflow_auto',
  official_url: 'https://www.docusign.com/products/electronic-signature',
  pricing_source_url: 'https://www.docusign.com/products/electronic-signature',
  pricing_verified_at: '2026-09-11T04:00:00+09:00',
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'annual billing displayed monthly',
  evidence_source_type: 'official_product_pricing_page',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: '2026-09-11T04:00:00+09:00',
  official_evidence_url: 'https://www.docusign.com/products/electronic-signature',
  affiliate_verified: false,
  affiliate_status: 'unverified',
  affiliate_source_url: null,
  affiliate_verified_at: null,
  affiliate_evidence_markers: [
    'No current COSHUMA-specific Docusign customer-facing affiliate URL verified as of 2026-09-11',
    'Use official Docusign links only; do not infer referral attribution from generic product or trial URLs',
  ],
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === docusign.id);
  if (existing) Object.assign(existing, docusign);
  else tools.push(docusign);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

console.log('Docusign canonical tool record ensured in tools.json and tools.next.json');
