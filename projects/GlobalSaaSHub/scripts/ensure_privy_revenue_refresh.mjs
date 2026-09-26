import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-09-14T13:32:00+09:00';
const privy = {
  id: 'privy',
  name: 'Privy',
  category: 'sales_crm',
  category_display: 'Ecommerce Email & Conversion',
  description: 'Ecommerce email, SMS, popups and onsite conversion platform with a 15-day no-card trial on the current Email plan.',
  affiliate_url: null,
  pricing: 'Email starts at $30/month with a 15-day free trial and no credit card required; Pop-ups & Displays only starts at $24/month',
  key_features: ['Ecommerce email marketing', 'SMS campaigns', 'Popups and displays', 'Automation and segmentation', 'Shopify/BigCommerce/Wix integrations'],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=privy.com&sz=128',
  primary_category: 'sales_crm',
  comparison_group: 'ecommerce_retention',
  official_url: 'https://www.privy.com/',
  pricing_source_url: 'https://www.privy.com/pricing',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly; pricing scales by mailable contacts/pageviews',
  evidence_source_type: 'official_privy_pricing_partner_signup_partner_agreement_and_gmail',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://www.privy.com/partnerships/sign-up',
  affiliate_verified: false,
  affiliate_status: 'browser_required_legal_program_consent',
  affiliate_source_url: 'https://www.privy.com/partnerships/sign-up',
  affiliate_workflow_url: 'https://www.privy.com/partnerships/sign-up',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted_legal_consent_required',
  affiliate_evidence_markers: [
    'Existing support@coshuma.com outreach to partners@privy.com is Gmail message 1a07d1178d900425 from 2026-09-07; the thread has no vendor reply as of 2026-09-14, so duplicate outreach is prohibited.',
    'Privy currently exposes a public partner signup page with Affiliate, Technology and Co-Marketing partnership types.',
    'Privy current pricing shows Email from $30/month with a 15-day free trial and no credit card required; Pop-ups & Displays only starts at $24/month.',
    'Privy Partner Program Agreement states participation/acceptance is a binding agreement. Unattended submission is therefore blocked on account-holder legal/program consent.',
    'Privy current agreement uses tier-based Partner Share; COSHUMA must not market a guaranteed 20% starting commission.',
    'No account-issued Privy customer referral URL is verified. Homepage, pricing, partner signup and partner dashboard URLs are not affiliate tracking URLs.',
    'Clicks, signups, paid customers, commission, payout and revenue remain unknown.'
  ],
  affiliate_next_action: 'Do not resend the existing outreach. The account holder must review and accept the Privy Partner Program Agreement before a one-time affiliate application is submitted. After acceptance/approval, recover only the exact account-issued customer referral URL and verify its destination and attribution. Stop for CAPTCHA, OTP, additional legal consent, forced identity verification or payment approval.'
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find(t => t.id === 'privy');
  if (existing) Object.assign(existing, privy);
  else tools.push(privy);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-14';
outreach.programs ||= {};
outreach.programs.privy = {
  status: 'browser_required_legal_program_consent',
  tracking_url: null,
  application_state: 'not_submitted_legal_consent_required',
  account: 'support@coshuma.com',
  official_program_url: 'https://www.privy.com/partnerships/sign-up',
  workflow_url: 'https://www.privy.com/partnerships/sign-up',
  prior_outreach_message_id: '1a07d1178d900425',
  github_issue: 507,
  checked_at: checkedAt,
  note: 'Existing 2026-09-07 outreach has no reply. A current official signup path is now public, but Privy Partner Program participation is governed by a binding agreement, so application submission requires account-holder legal/program consent. Exact customer tracking URL and downstream revenue metrics remain unknown.'
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const queueItem = {
  id: 'privy-affiliate-legal-consent-2026-09-14',
  tool_id: 'privy',
  priority: 'high',
  status: 'browser_required_legal_program_consent',
  affiliate_status: 'browser_required_legal_program_consent',
  application_state: 'not_submitted_legal_consent_required',
  cost: 0,
  exact_tracking_url: null,
  user_action_required: true,
  blocker: 'Privy Partner Program participation/acceptance is governed by a binding agreement; application submission requires the account holder to review and accept the program terms.',
  reason: 'Existing outreach is already on record and has no reply. Privy now exposes the official application path publicly, so no duplicate email is needed; the only blocker is account-holder legal/program consent.',
  next_action: 'Open the official Privy partner signup, select the applicable Affiliate path, review the Partner Program Agreement and submit only if the account holder agrees. After approval, recover only the exact customer-facing referral link issued by Privy/PartnerStack. Stop for CAPTCHA, OTP, additional legal consent, forced identity verification or payment approval.',
  do_not_reapply: true,
  verified_at: checkedAt,
  github_issue: 507
};
const idx = queue.findIndex(i => i.tool_id === 'privy' || String(i.id || '').startsWith('privy-'));
if (idx >= 0) queue[idx] = { ...queue[idx], ...queueItem };
else queue.push(queueItem);
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/privy.html',
  'https://coshuma.com/best/privy-free-trial-pricing.html',
  'https://coshuma.com/compare/privy-vs-omnisend.html'
];
const sitemapPath = 'public/sitemap.xml';
let sitemap = fs.readFileSync(sitemapPath, 'utf8');
for (const url of urls) {
  if (!sitemap.includes(`<loc>${url}</loc>`)) {
    sitemap = sitemap.replace('</urlset>', `  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n</urlset>`);
  }
}
fs.writeFileSync(sitemapPath, sitemap);

const llmsPath = 'public/llms.txt';
let llms = fs.readFileSync(llmsPath, 'utf8');
if (!llms.includes('https://coshuma.com/best/privy-free-trial-pricing.html')) {
  llms += '\n## Privy buyer guides\n\n- https://coshuma.com/tool/privy.html — Privy email, SMS and popup buyer guide with current trial and affiliate-status facts\n- https://coshuma.com/best/privy-free-trial-pricing.html — Privy 15-day no-card trial and pricing decision guide\n- https://coshuma.com/compare/privy-vs-omnisend.html — Privy vs Omnisend ecommerce retention comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-privy-refresh="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-purple-500/25 bg-purple-500/5 p-5"><div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Ecommerce retention</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-purple-300" href="/best/privy-free-trial-pricing.html">Privy free trial & pricing</a> · <a class="font-bold text-white hover:text-purple-300" href="/tool/privy.html">Privy buyer guide</a> · <a class="font-bold text-white hover:text-purple-300" href="/compare/privy-vs-omnisend.html">Privy vs Omnisend</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'public/compare/index.html', 'index.html']) {
  if (!fs.existsSync(file)) continue;
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-privy-refresh="2026-09-14"')) {
    html = html.includes('</main>') ? html.replace('</main>', `${hubBlock}</main>`) : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

const comparePath = 'public/compare/privy-vs-omnisend.html';
if (fs.existsSync(comparePath)) {
  let html = fs.readFileSync(comparePath, 'utf8');
  if (!html.includes('data-privy-trial-guide="2026-09-14"')) {
    const related = '<p data-privy-trial-guide="2026-09-14" class="muted">Need the Privy-only cost check first? <a href="/best/privy-free-trial-pricing.html">See the Privy 15-day trial and pricing guide</a>.</p>';
    html = html.replace('<section><h2>Sources and method</h2>', `${related}<section><h2>Sources and method</h2>`);
    fs.writeFileSync(comparePath, html);
  }
}

console.log('Privy revenue truth, browser queue and buyer-intent discovery refreshed');
