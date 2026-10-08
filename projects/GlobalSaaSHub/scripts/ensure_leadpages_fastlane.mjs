import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-10-08T14:17:20+09:00';
const leadpages = {
  id: 'leadpages',
  name: 'Leadpages',
  category: 'dev_coding',
  category_display: 'Coding & Dev Tools',
  description: 'Landing-page and conversion-optimization platform with AI page creation, A/B testing, analytics, lead enrichment, Smart Traffic, heatmaps and campaign publishing workflows.',
  affiliate_url: null,
  pricing: '7-day trial; Grow $99/month, Optimize $199/month, Scale $399/month',
  key_features: [
    'AI landing-page creation and visual editing',
    'Unlimited-page CRO plans',
    'A/B testing and dynamic text replacement',
    'Smart Traffic and heatmaps on higher plans',
    'Lead enrichment, analytics and integrations',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=leadpages.com&sz=128',
  primary_category: 'dev_coding',
  comparison_group: 'landing_page_builder',
  official_url: 'https://leadpages.com/',
  pricing_source_url: 'https://leadpages.com/pricing',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly or annual depending on plan',
  evidence_source_type: 'official_pricing_offer_help_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://leadpages.com/affiliates',
  affiliate_verified: false,
  affiliate_status: 'browser_required_legal_program_consent',
  affiliate_source_url: 'https://leadpages.com/affiliates',
  affiliate_workflow_url: 'https://dash.partnerstack.com/application?company=leadpages&group=affiliatewebsite',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official Leadpages affiliate page says the application is free and does not require a paid Leadpages subscription.',
    'Official program routes affiliate applications through PartnerStack and approved affiliates receive unique tracking links.',
    'Official public program currently advertises upfront referral commissions, with the current application form showing plan-specific amounts and commission timing.',
    'The current official PartnerStack application form links Leadpages program Terms of Service and requires an explicit agreement to the branded-search restriction before submission; enrollment therefore requires owner legal-program consent.',
    'GitHub search found no pre-existing COSHUMA Leadpages record before this fast-lane cycle.',
    'support@coshuma.com Gmail search for leadpages found no prior application, approval, rejection, tracking-link, commission, or payout message.',
    'Exact account-specific customer tracking URL is unknown; PartnerStack portal/application URLs must not be used as customer revenue links.',
    'GitHub issue #477 tracks the authenticated PartnerStack duplicate check and one-time application/recovery step.',
  ],
  affiliate_next_action: 'Hold at the legal-program-consent gate. After the owner reviews and accepts the Leadpages program Terms of Service and branded-search restriction, reuse the existing COSHUMA PartnerStack identity, submit once only if no relationship exists, and recover only the exact vendor-issued customer tracking URL after approval.',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === leadpages.id);
  if (existing) Object.assign(existing, leadpages);
  else tools.push(leadpages);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = checkedAt;
outreach.programs ||= {};
outreach.programs.leadpages = {
  status: 'browser_required_legal_program_consent',
  tracking_url: null,
  application_state: 'not_submitted',
  account: 'support@coshuma.com',
  official_program_url: 'https://leadpages.com/affiliates',
  workflow_url: 'https://dash.partnerstack.com/application?company=leadpages&group=affiliatewebsite',
  github_issue: 477,
  checked_at: checkedAt,
  note: 'Official affiliate program and exact PartnerStack application route are confirmed. The current application requires review of program Terms of Service and an explicit agreement to the branded-search restriction. No COSHUMA Leadpages application or issued customer tracking URL is evidenced. Keep the application on hold until owner legal-program consent; never use the PartnerStack application URL as a customer CTA.',
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const leadpagesQueueItem = {
  id: 'leadpages-partnerstack-2026-09-14',
  tool_id: 'leadpages',
  priority: 'medium',
  status: 'browser_required_legal_program_consent',
  affiliate_status: 'browser_required_legal_program_consent',
  application_state: 'not_submitted',
  cost: 0,
  exact_tracking_url: null,
  user_action_required: true,
  blocker: 'The current official Leadpages PartnerStack application links program Terms of Service and requires explicit agreement to its branded-search restriction before submission. Enrollment requires owner legal-program consent.',
  reason: 'Official program and PartnerStack application routes are verified, but no application, approval, or exact customer tracking URL is evidenced.',
  next_action: 'After the owner reviews and accepts the Leadpages program Terms of Service and branded-search restriction, reuse the existing COSHUMA PartnerStack identity, check for an existing relationship, submit once only if absent, and recover only the exact vendor-issued customer tracking URL after approval. Stop for CAPTCHA, OTP, forced identity verification, or payment approval.',
  do_not_reapply: true,
  verified_at: checkedAt,
  github_issue: 477,
};
const existingQueueItem = queue.find((item) => item.tool_id === 'leadpages' || String(item.id || '').startsWith('leadpages-'));
if (existingQueueItem) Object.assign(existingQueueItem, leadpagesQueueItem);
else queue.push(leadpagesQueueItem);
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/leadpages.html',
  'https://coshuma.com/best/leadpages-free-trial-pricing.html',
  'https://coshuma.com/compare/leadpages-vs-unbounce.html',
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
if (!llms.includes('https://coshuma.com/tool/leadpages.html')) {
  llms += '\n## Leadpages buyer guides\n\n- https://coshuma.com/tool/leadpages.html — Leadpages pricing, 7-day trial and CRO buyer guide\n- https://coshuma.com/best/leadpages-free-trial-pricing.html — Leadpages trial billing and pricing decision guide\n- https://coshuma.com/compare/leadpages-vs-unbounce.html — Leadpages vs Unbounce landing-page and CRO comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-leadpages-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-cyan-500/25 bg-cyan-500/5 p-5"><div class="text-xs uppercase tracking-widest text-cyan-300 font-bold">Landing pages & CRO</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-cyan-300" href="/best/leadpages-free-trial-pricing.html">Leadpages free trial & pricing</a> · <a class="font-bold text-white hover:text-cyan-300" href="/tool/leadpages.html">Leadpages review</a> · <a class="font-bold text-white hover:text-cyan-300" href="/compare/leadpages-vs-unbounce.html">Leadpages vs Unbounce</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'index.html']) {
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-leadpages-fastlane="2026-09-14"')) {
    html = html.includes('</main>') ? html.replace('</main>', `${hubBlock}</main>`) : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

console.log('Leadpages fast-lane state, browser queue and discoverability ensured');
