import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-09-14T06:29:00+09:00';
const instapage = {
  id: 'instapage',
  name: 'Instapage',
  category: 'dev_coding',
  category_display: 'Coding & Dev Tools',
  description: 'Landing-page and conversion-optimization platform with AI content, reusable page blocks, A/B testing, dynamic text replacement, collaboration, forms and campaign publishing workflows.',
  affiliate_url: null,
  pricing: '14-day trial; Create $99/month, Optimize $199/month, Convert custom',
  key_features: [
    'Drag-and-drop landing-page builder',
    'AI content and reusable page blocks',
    'Server-side A/B testing on Optimize',
    'Dynamic text replacement and multi-step forms',
    'Collaboration, integrations and campaign publishing',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=instapage.com&sz=128',
  primary_category: 'dev_coding',
  comparison_group: 'landing_page_builder',
  official_url: 'https://instapage.com/',
  pricing_source_url: 'https://instapage.com/plans',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly or annual depending on plan',
  evidence_source_type: 'official_pricing_help_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://instapage.com/affiliate',
  affiliate_verified: false,
  affiliate_status: 'browser_required_portal_access',
  affiliate_source_url: 'https://instapage.com/affiliate',
  affiliate_workflow_url: 'https://instapage.partnerstack.com/?group=newaffiliateswebsite',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official Instapage affiliate page confirms a current affiliate program and routes Sign up now to Instapage PartnerStack.',
    'Official program says enrolled affiliates receive a unique promotion link and referral fees for customer signups.',
    'Official pricing page lists a 14-day trial for Create and Optimize, with current monthly prices of $99 and $199 respectively.',
    'Official pricing FAQ says a credit card is required for the trial and the selected plan is charged when the trial ends unless canceled.',
    'GitHub search found no pre-existing COSHUMA Instapage record before this fast-lane cycle.',
    'support@coshuma.com Gmail in:anywhere search found no prior Instapage application, approval, rejection, tracking-link, commission, or payout message.',
    'Exact account-specific customer tracking URL is unknown; PartnerStack portal/application URLs must not be used as customer revenue links.',
    'GitHub issue #480 tracks the authenticated PartnerStack duplicate check and one-time application/recovery step.',
  ],
  affiliate_next_action: 'Reuse the existing COSHUMA PartnerStack identity in an authenticated browser/Work session, check for an existing Instapage relationship, then submit once only if absent or recover the exact issued customer tracking URL if already enrolled.',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === instapage.id);
  if (existing) Object.assign(existing, instapage);
  else tools.push(instapage);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-14';
outreach.programs ||= {};
outreach.programs.instapage = {
  status: 'browser_required_portal_access',
  tracking_url: null,
  application_state: 'not_submitted',
  account: 'support@coshuma.com',
  official_program_url: 'https://instapage.com/affiliate',
  workflow_url: 'https://instapage.partnerstack.com/?group=newaffiliateswebsite',
  github_issue: 480,
  checked_at: checkedAt,
  note: 'Official Instapage affiliate program and exact PartnerStack route are confirmed, but no existing COSHUMA Instapage application or issued customer tracking URL was found in GitHub/Gmail. Authenticated PartnerStack access is required before one-time submission or exact-link recovery. Do not use the PartnerStack URL as a customer CTA.',
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
if (!queue.some((item) => item.tool_id === 'instapage' || String(item.id || '').startsWith('instapage-'))) {
  queue.push({
    id: 'instapage-partnerstack-2026-09-14',
    tool_id: 'instapage',
    priority: 'medium',
    status: 'browser_required_portal_access',
    affiliate_status: 'browser_required_portal_access',
    application_state: 'not_submitted',
    cost: 0,
    exact_tracking_url: null,
    user_action_required: false,
    blocker: 'The official Instapage affiliate enrollment is an authenticated PartnerStack flow. This automation run has no authenticated interactive PartnerStack session.',
    reason: 'GitHub and Gmail duplicate checks were clear, but application submission has not occurred and no customer tracking URL is verified.',
    next_action: 'Reuse the existing COSHUMA PartnerStack identity in browser/Work. If an existing Instapage relationship is present, recover the issued exact customer link; otherwise submit the free application once. Stop for CAPTCHA, OTP, legal agreement, forced identity verification, or payment approval.',
    do_not_reapply: true,
    verified_at: checkedAt,
    github_issue: 480,
  });
}
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/instapage.html',
  'https://coshuma.com/best/instapage-free-trial-pricing.html',
  'https://coshuma.com/compare/instapage-vs-unbounce.html',
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
if (!llms.includes('https://coshuma.com/tool/instapage.html')) {
  llms += '\n## Instapage buyer guides\n\n- https://coshuma.com/tool/instapage.html — Instapage pricing, trial and CRO buyer guide\n- https://coshuma.com/best/instapage-free-trial-pricing.html — Instapage 14-day trial billing and pricing decision guide\n- https://coshuma.com/compare/instapage-vs-unbounce.html — Instapage vs Unbounce landing-page and CRO comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-instapage-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-fuchsia-500/25 bg-fuchsia-500/5 p-5"><div class="text-xs uppercase tracking-widest text-fuchsia-300 font-bold">Landing pages & CRO</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-fuchsia-300" href="/best/instapage-free-trial-pricing.html">Instapage free trial & pricing</a> · <a class="font-bold text-white hover:text-fuchsia-300" href="/tool/instapage.html">Instapage review</a> · <a class="font-bold text-white hover:text-fuchsia-300" href="/compare/instapage-vs-unbounce.html">Instapage vs Unbounce</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'index.html']) {
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-instapage-fastlane="2026-09-14"')) {
    html = html.includes('</main>') ? html.replace('</main>', `${hubBlock}</main>`) : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

console.log('Instapage fast-lane state, browser queue and discoverability ensured');
