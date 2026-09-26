import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-09-14T06:05:00+09:00';
const landingi = {
  id: 'landingi',
  name: 'Landingi',
  category: 'dev_coding',
  category_display: 'Coding & Dev Tools',
  description: 'Landing-page platform with a visual builder, AI-assisted page generation, forms, analytics, experimentation, programmatic pages and agency workflows.',
  affiliate_url: null,
  pricing: '14-day free trial; Build from $24/month billed annually',
  key_features: [
    'Visual drag-and-drop landing-page builder',
    'Lunar AI page generation',
    'Forms and integrations',
    'A/B testing and EventTracker on higher plans',
    'Programmatic landing pages and agency workflows on higher plans',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=landingi.com&sz=128',
  primary_category: 'dev_coding',
  comparison_group: 'landing_page_builder',
  official_url: 'https://landingi.com/',
  pricing_source_url: 'https://landingi.com/pricing/',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly or annual depending on plan',
  evidence_source_type: 'official_pricing_help_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://landingi.com/help/affiliate-program-faq/',
  affiliate_verified: false,
  affiliate_status: 'browser_required_portal_access',
  affiliate_source_url: 'https://landingi.com/help/affiliate-program-faq/',
  affiliate_workflow_url: 'https://landingi.partnerstack.com/',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official Landingi Affiliate Program FAQ says enrollment uses Landingi PartnerStack.',
    'Official current commission is 20% during the first 12 months of the customer lifecycle with a 90-day cookie window.',
    'GitHub search found no pre-existing COSHUMA Landingi record before this fast-lane cycle.',
    'support@coshuma.com Gmail search for landingi found no prior application, approval, rejection, tracking-link, commission, or payout message.',
    'Exact account-specific customer tracking URL is unknown; PartnerStack portal/application URLs must not be used as customer revenue links.',
    'GitHub issue #474 tracks the authenticated PartnerStack duplicate check and one-time application/recovery step.',
  ],
  affiliate_next_action: 'Reuse the existing COSHUMA PartnerStack identity in an authenticated browser/Work session, check for an existing Landingi relationship, then submit once only if absent or recover the exact issued customer tracking URL if already enrolled.',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === landingi.id);
  if (existing) Object.assign(existing, landingi);
  else tools.push(landingi);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-14';
outreach.programs ||= {};
outreach.programs.landingi = {
  status: 'browser_required_portal_access',
  tracking_url: null,
  application_state: 'not_submitted',
  account: 'support@coshuma.com',
  official_program_url: 'https://landingi.com/help/affiliate-program-faq/',
  workflow_url: 'https://landingi.partnerstack.com/',
  github_issue: 474,
  checked_at: checkedAt,
  note: 'Official program is confirmed, but no existing COSHUMA Landingi application or issued customer tracking URL was found in GitHub/Gmail. Authenticated PartnerStack access is required before a one-time application or exact-link recovery. Do not use the portal URL as a customer CTA.',
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
if (!queue.some((item) => item.tool_id === 'landingi' || String(item.id || '').startsWith('landingi-'))) {
  queue.push({
    id: 'landingi-partnerstack-2026-09-14',
    tool_id: 'landingi',
    priority: 'medium',
    status: 'browser_required_portal_access',
    affiliate_status: 'browser_required_portal_access',
    application_state: 'not_submitted',
    cost: 0,
    exact_tracking_url: null,
    user_action_required: false,
    blocker: 'The official Landingi application route is an authenticated PartnerStack portal. This automation run has no authenticated interactive PartnerStack session.',
    reason: 'GitHub and Gmail duplicate checks were clear, but application submission has not occurred and no customer tracking URL is verified.',
    next_action: 'Reuse the existing COSHUMA PartnerStack identity in browser/Work. If an existing Landingi relationship is present, recover the issued exact customer link; otherwise submit the free application once. Stop for CAPTCHA, OTP, legal agreement, forced identity verification, or payment approval.',
    do_not_reapply: true,
    verified_at: checkedAt,
    github_issue: 474,
  });
}
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/landingi.html',
  'https://coshuma.com/best/landingi-free-trial-pricing.html',
  'https://coshuma.com/compare/landingi-vs-unbounce.html',
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
if (!llms.includes('https://coshuma.com/tool/landingi.html')) {
  llms += '\n## Landing page builders\n\n- https://coshuma.com/tool/landingi.html — Landingi pricing, trial and landing-page buyer guide\n- https://coshuma.com/best/landingi-free-trial-pricing.html — Landingi 14-day trial and pricing decision guide\n- https://coshuma.com/compare/landingi-vs-unbounce.html — Landingi vs Unbounce landing-page and CRO comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-landingi-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-5"><div class="text-xs uppercase tracking-widest text-emerald-300 font-bold">Landing pages & CRO</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-emerald-300" href="/best/landingi-free-trial-pricing.html">Landingi free trial & pricing</a> · <a class="font-bold text-white hover:text-emerald-300" href="/tool/landingi.html">Landingi review</a> · <a class="font-bold text-white hover:text-emerald-300" href="/compare/landingi-vs-unbounce.html">Landingi vs Unbounce</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'index.html']) {
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-landingi-fastlane="2026-09-14"')) {
    html = html.includes('</main>') ? html.replace('</main>', `${hubBlock}</main>`) : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

const unbouncePath = 'public/tool/unbounce.html';
if (fs.existsSync(unbouncePath)) {
  let html = fs.readFileSync(unbouncePath, 'utf8');
  if (!html.includes('/compare/landingi-vs-unbounce.html')) {
    const related = `\n<section data-landingi-related="2026-09-14" class="max-w-6xl mx-auto px-5 pb-8"><a href="/compare/landingi-vs-unbounce.html" class="block rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5"><div class="text-xs uppercase tracking-wider font-bold text-emerald-300">Related landing-page comparison</div><div class="mt-2 font-extrabold text-white">Landingi vs Unbounce: builder, CRO workflow and pricing →</div></a></section>\n`;
    html = html.includes('</main>') ? html.replace('</main>', `${related}</main>`) : html.replace('</body>', `${related}</body>`);
    fs.writeFileSync(unbouncePath, html);
  }
}

console.log('Landingi fast-lane state, browser queue and discoverability ensured');
