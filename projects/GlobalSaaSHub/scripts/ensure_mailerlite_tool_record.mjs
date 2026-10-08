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
  affiliate_status: 'browser_required_legal_program_consent',
  affiliate_source_url: 'https://www.mailerlite.com/affiliate',
  affiliate_workflow_url: 'https://mailerlite.trackdesk.com/sign-up',
  affiliate_status_checked_at: '2026-10-08T09:19:54+09:00',
  application_state: 'not_submitted_legal_consent_required',
  affiliate_verified_at: null,
  affiliate_evidence_markers: [
    "MailerLite's current official affiliate page advertises 30% recurring lifetime commission and a 45-day referral cookie.",
    "MailerLite's current official affiliate page says approved affiliates receive a unique referral link; the application route is https://mailerlite.trackdesk.com/sign-up.",
    "MailerLite's official Affiliate Program Terms state that submitting the application constitutes acceptance of a legally binding agreement and requires accurate identity, business, and promotion-method information.",
    "Current official payout terms require at least $100 in approved commissions from at least two different referred customers; eligible payouts are processed through Tipalti.",
    "No MailerLite legal terms were accepted, no application was submitted, and no account-specific customer tracking URL was observed.",
    "Generic MailerLite, application, onboarding, dashboard, and Trackdesk URLs must not be used as customer affiliate links.",
  ],
  affiliate_next_action: "The account holder must review and accept MailerLite's Affiliate Program Terms before submitting the official Trackdesk application. Submit once only if accepted, then recover and verify only the exact vendor-issued customer-facing referral URL. Stop for CAPTCHA, OTP, payment approval, forced identity verification, or any additional legal consent.",
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
