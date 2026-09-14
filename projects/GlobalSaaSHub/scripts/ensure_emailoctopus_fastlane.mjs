import fs from 'node:fs';

const checkedAt = '2026-09-14T15:34:00+09:00';
const emailoctopus = {
  id: 'emailoctopus',
  name: 'EmailOctopus',
  category: 'marketing_auto',
  category_display: 'Marketing Automation',
  description: 'Email marketing platform for campaigns, automations, forms and landing pages, with a permanent free Starter plan for small and growing lists.',
  affiliate_url: null,
  pricing: 'Starter Free $0 for up to 2,500 subscribers and 10,000 emails/month; Pro from $9/month billed yearly for the displayed base configuration',
  key_features: [
    'Email campaigns and drag-and-drop editor',
    'Email automations',
    'Forms and landing pages',
    'Audience tags and fields',
    'Free plan with no credit card required',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=emailoctopus.com&sz=128',
  primary_category: 'marketing_auto',
  comparison_group: 'email_marketing',
  official_url: 'https://emailoctopus.com/',
  pricing_source_url: 'https://emailoctopus.com/pricing',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'free tier; paid pricing varies with subscriber and send volume',
  evidence_source_type: 'official_pricing_help_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://emailoctopus.com/affiliates',
  affiliate_verified: false,
  affiliate_status: 'browser_required_tolt_application',
  affiliate_source_url: 'https://emailoctopus.com/affiliates',
  affiliate_workflow_url: 'https://emailoctopus.tolt.io/',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official EmailOctopus affiliate page says the affiliate account is free and provides a unique link after enrollment.',
    'Official affiliate page states 30% of referral revenue for one year with a 31-day cookie.',
    'GitHub search found no pre-existing COSHUMA EmailOctopus tool/application/tracking record before this fast-lane cycle.',
    'support@coshuma.com Gmail search for emailoctopus found no prior application, approval, rejection, tracking-link, commission, or payout message.',
    'Exact account-specific customer tracking URL is unknown; Tolt portal/application URLs and generic vendor URLs must not be treated as affiliate revenue links.',
    'GitHub issue #511 tracks the authenticated Tolt duplicate check and one-time application/recovery step.',
  ],
  affiliate_next_action: 'Open the official EmailOctopus Tolt route in an authenticated browser/Work session, check for an existing COSHUMA identity, then submit once only if absent or recover the exact issued customer tracking URL if already enrolled.',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === emailoctopus.id);
  if (existing?.affiliate_url && emailoctopus.affiliate_url && existing.affiliate_url !== emailoctopus.affiliate_url) {
    throw new Error(`Refusing to overwrite existing EmailOctopus affiliate URL in ${file}`);
  }
  if (existing) Object.assign(existing, emailoctopus);
  else tools.push(emailoctopus);
  tools.sort((a, b) => String(a.id || '').localeCompare(String(b.id || '')));
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-14';
outreach.programs ||= {};
outreach.programs.emailoctopus = {
  status: 'browser_required_tolt_application',
  tracking_url: null,
  application_state: 'not_submitted',
  account: 'support@coshuma.com',
  official_program_url: 'https://emailoctopus.com/affiliates',
  workflow_url: 'https://emailoctopus.tolt.io/',
  github_issue: 511,
  checked_at: checkedAt,
  note: 'Official free affiliate program and Tolt application route are confirmed, but no existing COSHUMA enrollment or issued customer tracking URL was found in GitHub/Gmail. Do not use the Tolt route or generic vendor pages as customer affiliate CTAs.',
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
if (!queue.some((item) => item.tool_id === 'emailoctopus' || String(item.id || '').startsWith('emailoctopus-'))) {
  queue.push({
    id: 'emailoctopus-tolt-2026-09-14',
    tool_id: 'emailoctopus',
    priority: 'medium',
    status: 'browser_required_tolt_application',
    affiliate_status: 'browser_required_tolt_application',
    application_state: 'not_submitted',
    cost: 0,
    exact_tracking_url: null,
    user_action_required: false,
    blocker: 'The official EmailOctopus affiliate enrollment route is an interactive Tolt flow and this run has no authenticated interactive Tolt session.',
    reason: 'GitHub and Gmail duplicate checks were clear, but application submission has not occurred and no customer tracking URL is verified.',
    next_action: 'Open the official Tolt route in browser/Work, check for an existing COSHUMA/support@coshuma.com affiliate identity, and submit once only if absent. Stop for CAPTCHA, OTP, legal agreement, forced identity verification, or payment approval.',
    do_not_reapply: true,
    verified_at: checkedAt,
    github_issue: 511,
  });
}
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/emailoctopus.html',
  'https://coshuma.com/best/emailoctopus-free-plan-pricing.html',
  'https://coshuma.com/compare/emailoctopus-vs-omnisend.html',
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
if (!llms.includes('https://coshuma.com/tool/emailoctopus.html')) {
  llms += '\n## Email marketing\n\n- https://coshuma.com/tool/emailoctopus.html — EmailOctopus pricing, free-plan limits and buyer guide\n- https://coshuma.com/best/emailoctopus-free-plan-pricing.html — EmailOctopus permanent free-plan and pricing decision guide\n- https://coshuma.com/compare/emailoctopus-vs-omnisend.html — EmailOctopus vs Omnisend free email-marketing comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-emailoctopus-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-5"><div class="text-xs uppercase tracking-widest text-emerald-300 font-bold">Email marketing</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-emerald-300" href="/best/emailoctopus-free-plan-pricing.html">EmailOctopus free plan & pricing</a> · <a class="font-bold text-white hover:text-emerald-300" href="/tool/emailoctopus.html">EmailOctopus review</a> · <a class="font-bold text-white hover:text-emerald-300" href="/compare/emailoctopus-vs-omnisend.html">EmailOctopus vs Omnisend</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'index.html']) {
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-emailoctopus-fastlane="2026-09-14"')) {
    html = html.includes('</main>') ? html.replace('</main>', `${hubBlock}</main>`) : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

const omnisendPath = 'public/tool/omnisend.html';
if (fs.existsSync(omnisendPath)) {
  let html = fs.readFileSync(omnisendPath, 'utf8');
  if (!html.includes('/compare/emailoctopus-vs-omnisend.html')) {
    const related = `\n<section data-emailoctopus-related="2026-09-14" class="max-w-6xl mx-auto px-5 pb-8"><a href="/compare/emailoctopus-vs-omnisend.html" class="block rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5"><div class="text-xs uppercase tracking-wider font-bold text-emerald-300">Related email-marketing comparison</div><div class="mt-2 font-extrabold text-white">EmailOctopus vs Omnisend: free limits, ecommerce focus and buyer fit →</div></a></section>\n`;
    html = html.includes('</main>') ? html.replace('</main>', `${related}</main>`) : html.replace('</body>', `${related}</body>`);
    fs.writeFileSync(omnisendPath, html);
  }
}

console.log('EmailOctopus fast-lane state, browser queue and discoverability ensured');
