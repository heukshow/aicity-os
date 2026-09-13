import fs from 'node:fs';

const checkedAt = '2026-09-14T06:15:00+09:00';
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
  affiliate_status: 'browser_required_portal_access',
  affiliate_source_url: 'https://leadpages.com/affiliates',
  affiliate_workflow_url: 'https://dash.partnerstack.com/application?company=leadpages&group=affiliatewebsite',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official Leadpages affiliate page says the application is free and does not require a paid Leadpages subscription.',
    'Official program routes affiliate applications through PartnerStack and approved affiliates receive unique tracking links.',
    'Official public program currently advertises up to $400 per referred converted customer.',
    'GitHub search found no pre-existing COSHUMA Leadpages record before this fast-lane cycle.',
    'support@coshuma.com Gmail search for leadpages found no prior application, approval, rejection, tracking-link, commission, or payout message.',
    'Exact account-specific customer tracking URL is unknown; PartnerStack portal/application URLs must not be used as customer revenue links.',
    'GitHub issue #477 tracks the authenticated PartnerStack duplicate check and one-time application/recovery step.',
  ],
  affiliate_next_action: 'Reuse the existing COSHUMA PartnerStack identity in an authenticated browser/Work session, check for an existing Leadpages relationship, then submit once only if absent or recover the exact issued customer tracking URL if already enrolled.',
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
outreach.updated_at = '2026-09-14';
outreach.programs ||= {};
outreach.programs.leadpages = {
  status: 'browser_required_portal_access',
  tracking_url: null,
  application_state: 'not_submitted',
  account: 'support@coshuma.com',
  official_program_url: 'https://leadpages.com/affiliates',
  workflow_url: 'https://dash.partnerstack.com/application?company=leadpages&group=affiliatewebsite',
  github_issue: 477,
  checked_at: checkedAt,
  note: 'Official affiliate program and exact PartnerStack application route are confirmed, but no existing COSHUMA Leadpages application or issued customer tracking URL was found in GitHub/Gmail. Authenticated PartnerStack access is required before one-time submission or exact-link recovery. Do not use the application URL as a customer CTA.',
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
if (!queue.some((item) => item.tool_id === 'leadpages' || String(item.id || '').startsWith('leadpages-'))) {
  queue.push({
    id: 'leadpages-partnerstack-2026-09-14',
    tool_id: 'leadpages',
    priority: 'medium',
    status: 'browser_required_portal_access',
    affiliate_status: 'browser_required_portal_access',
    application_state: 'not_submitted',
    cost: 0,
    exact_tracking_url: null,
    user_action_required: false,
    blocker: 'The official Leadpages affiliate application is an authenticated JavaScript PartnerStack flow. This automation run has no authenticated interactive PartnerStack session.',
    reason: 'GitHub and Gmail duplicate checks were clear, but application submission has not occurred and no customer tracking URL is verified.',
    next_action: 'Reuse the existing COSHUMA PartnerStack identity in browser/Work. If an existing Leadpages relationship is present, recover the issued exact customer link; otherwise submit the free application once. Stop for CAPTCHA, OTP, legal agreement, forced identity verification, or payment approval.',
    do_not_reapply: true,
    verified_at: checkedAt,
    github_issue: 477,
  });
}
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