import fs from './affiliate_state_fs.mjs';
import './ensure_mailerlite_tool_record.mjs';

const brevo = {
  id: 'brevo',
  name: 'Brevo',
  category: 'marketing_auto',
  category_display: 'Marketing Automation',
  description: 'Email, SMS, WhatsApp, automation, CRM, and transactional-messaging platform with a permanent free marketing plan and paid plans that scale by sending volume and features.',
  affiliate_url: null,
  pricing: 'Free $0/month; Starter from $9/month; Standard from $18/month; Professional from $499/month; Enterprise custom',
  key_features: [
    'Email marketing & automation',
    'SMS and WhatsApp campaigns',
    'CRM and contact management',
    'Transactional messaging',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=brevo.com&sz=128',
  primary_category: 'marketing_auto',
  comparison_group: 'marketing_auto',
  official_url: 'https://www.brevo.com/',
  pricing_source_url: 'https://help.brevo.com/hc/en-us/articles/208589409-About-Brevo-s-pricing-plans',
  pricing_verified_at: '2026-09-14T04:00:00+09:00',
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly starting prices on current official pricing guidance',
  evidence_source_type: 'official_help_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: '2026-09-14T04:00:00+09:00',
  official_evidence_url: 'https://help.brevo.com/hc/en-us/articles/16487784994322-The-Brevo-Affiliate-program',
  affiliate_verified: false,
  affiliate_status: 'browser_required_legal_program_consent',
  affiliate_source_url: 'https://help.brevo.com/hc/en-us/articles/16487784994322-The-Brevo-Affiliate-program',
  affiliate_verified_at: null,
  affiliate_evidence_markers: [
    "Brevo's current official affiliate help states the program is for bloggers, publishers and content creators, uses PartnerStack, requires a website business email, and issues the personalized affiliate link only after application approval",
    "Brevo's official terms page states online acceptance is a binding legal commitment and requires acceptance of the terms without reserve",
    'No Brevo application approval, rejection, or COSHUMA-specific customer tracking URL is present in current repository or Gmail evidence; the application remains unsubmitted pending legal consent',
  ],
  affiliate_status_checked_at: '2026-10-03T22:13:49Z',
  affiliate_next_action: "Review and explicitly accept Brevo's binding Affiliate Program Terms before submitting the PartnerStack application. Do not submit or claim approval until that legal-consent gate is completed. After approval, recover and verify only the exact personalized customer-facing affiliate URL issued in PartnerStack.",
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === brevo.id);
  if (existing?.affiliate_url && brevo.affiliate_url && existing.affiliate_url !== brevo.affiliate_url) {
    throw new Error(`Refusing to overwrite existing Brevo affiliate URL in ${file}`);
  }
  if (existing) Object.assign(existing, brevo);
  else tools.push(brevo);
  tools.sort((a, b) => String(a.id || '').localeCompare(String(b.id || '')));
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

console.log('Brevo canonical tool record ensured in tools.json and tools.next.json');
