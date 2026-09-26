import fs from './affiliate_state_fs.mjs';

const mailerlite = {
  id: 'mailerlite',
  name: 'MailerLite',
  category: 'marketing_auto',
  category_display: 'Marketing Automation',
  description: 'Email marketing platform for campaigns, automation, landing pages, forms, websites, and digital products, with a permanent free plan for small lists.',
  affiliate_url: null,
  pricing: 'Free $0/month for up to 250 subscribers and 2,500 monthly emails; Comfort from $12/month; 14-day premium-feature trial for new accounts',
  key_features: [
    'Email campaigns and newsletter editors',
    'Visual automations',
    'Landing pages, websites, forms and pop-ups',
    'Digital products and booking features',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=mailerlite.com&sz=128',
  primary_category: 'marketing_auto',
  comparison_group: 'marketing_auto',
  official_url: 'https://www.mailerlite.com/',
  pricing_source_url: 'https://www.mailerlite.com/pricing',
  pricing_verified_at: '2026-09-14T04:40:00+09:00',
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'current official monthly pricing and free-plan limits',
  evidence_source_type: 'official_pricing_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: '2026-09-14T04:40:00+09:00',
  official_evidence_url: 'https://www.mailerlite.com/affiliate',
  affiliate_verified: false,
  affiliate_status: 'browser_required_trackdesk_application',
  affiliate_source_url: 'https://www.mailerlite.com/affiliate',
  affiliate_verified_at: null,
  affiliate_evidence_markers: [
    'MailerLite official affiliate page advertises 30% recurring lifetime commission and a 45-day referral cookie through Trackdesk',
    'Exact official application route verified as https://mailerlite.trackdesk.com/sign-up',
    'No prior MailerLite application, approval, rejection, vendor thread, or customer tracking URL was found in support@coshuma.com Gmail on 2026-09-14',
    'Application remains unsubmitted because the Trackdesk form requires an interactive browser flow; do not use generic MailerLite pages as referral URLs',
  ],
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === mailerlite.id);
  if (existing?.affiliate_url && mailerlite.affiliate_url && existing.affiliate_url !== mailerlite.affiliate_url) {
    throw new Error(`Refusing to overwrite existing MailerLite affiliate URL in ${file}`);
  }
  if (existing) Object.assign(existing, mailerlite);
  else tools.push(mailerlite);
  tools.sort((a, b) => String(a.id || '').localeCompare(String(b.id || '')));
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

console.log('MailerLite canonical tool record ensured in tools.json and tools.next.json');
