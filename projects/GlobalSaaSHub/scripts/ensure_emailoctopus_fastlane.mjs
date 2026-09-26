import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-09-16T06:18:00+09:00';
const trackingUrl = 'https://emailoctopus.com/?ref=sangkwon';
const emailoctopus = {
  id: 'emailoctopus',
  name: 'EmailOctopus',
  category: 'marketing_auto',
  category_display: 'Marketing Automation',
  description: 'Email marketing platform for campaigns, automations, forms and landing pages, with a permanent free Starter plan for small and growing lists.',
  affiliate_url: trackingUrl,
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
  evidence_source_type: 'official_pricing_help_affiliate_pages_and_authenticated_tolt',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://emailoctopus.com/affiliates',
  affiliate_verified: true,
  affiliate_status: 'approved_tracking',
  affiliate_source_url: 'https://emailoctopus.com/affiliates',
  affiliate_workflow_url: 'https://emailoctopus.tolt.io/',
  affiliate_status_checked_at: checkedAt,
  application_state: 'enrolled_tracking_link_verified',
  affiliate_evidence_markers: [
    'Official EmailOctopus affiliate page says the affiliate account is free and provides a unique link after enrollment.',
    'Official affiliate page states 30% of referral revenue for one year with a 31-day cookie.',
    'COSHUMA reused the existing support@coshuma.com Tolt identity rather than creating a duplicate network account.',
    'The authenticated EmailOctopus Tolt onboarding flow completed successfully and issued the exact customer-facing referral URL https://emailoctopus.com/?ref=sangkwon.',
    'GitHub issue #511 and merged PR #579 record the completed onboarding and exact issued customer URL.',
    'Generic EmailOctopus homepage, pricing, Tolt dashboard, application and onboarding URLs must not be treated as tracking URLs.',
    'No clicks, signups, paid customers, commissions, payouts or revenue are inferred from link issuance alone.',
  ],
  affiliate_next_action: 'Preserve the exact Tolt-issued customer referral URL, do not create another Tolt or EmailOctopus affiliate identity, and only update clicks/signups/customers/commission/payout when separately evidenced in the authenticated dashboard.',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === emailoctopus.id);
  if (existing?.affiliate_url && existing.affiliate_url !== trackingUrl) {
    throw new Error(`Refusing to overwrite a different EmailOctopus affiliate URL in ${file}`);
  }
  if (existing) Object.assign(existing, emailoctopus);
  else tools.push(emailoctopus);
  tools.sort((a, b) => String(a.id || '').localeCompare(String(b.id || '')));
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-16';
outreach.programs ||= {};
outreach.programs.emailoctopus = {
  status: 'approved_tracking',
  tracking_url: trackingUrl,
  application_state: 'enrolled_tracking_link_verified',
  account: 'support@coshuma.com',
  official_program_url: 'https://emailoctopus.com/affiliates',
  workflow_url: 'https://emailoctopus.tolt.io/',
  github_issue: 511,
  checked_at: checkedAt,
  note: 'Existing support@coshuma.com Tolt identity was reused. Authenticated EmailOctopus onboarding completed and issued the exact customer-facing referral URL. Do not re-enroll or create another Tolt account. Link issuance is not evidence of clicks, signups, customers, commission, payout or revenue.',
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
let queueItem = queue.find((item) => item.tool_id === 'emailoctopus' || String(item.id || '').startsWith('emailoctopus-'));
if (!queueItem) {
  queueItem = { id: 'emailoctopus-tolt-2026-09-14', tool_id: 'emailoctopus', priority: 'medium' };
  queue.push(queueItem);
}
Object.assign(queueItem, {
  status: 'approved_tracking_url_verified',
  affiliate_status: 'approved_tracking_url_verified',
  application_state: 'enrolled_tracking_link_verified',
  cost: 0,
  exact_tracking_url: trackingUrl,
  user_action_required: false,
  blocker: null,
  reason: 'Authenticated EmailOctopus Tolt onboarding completed and issued the exact customer-facing referral URL using the existing support@coshuma.com identity.',
  next_action: 'No enrollment action. Preserve the exact issued URL and only re-open browser work when KPI evidence or a vendor program change needs verification.',
  do_not_reapply: true,
  verified_at: checkedAt,
  github_issue: 511,
});
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/emailoctopus.html',
  'https://coshuma.com/best/emailoctopus-free-plan-pricing.html',
  'https://coshuma.com/compare/emailoctopus-vs-omnisend.html',
  'https://coshuma.com/compare/benchmark-email-vs-emailoctopus.html',
  'https://coshuma.com/compare/sender-net-vs-emailoctopus.html',
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

for (const file of [
  'public/tool/emailoctopus.html',
  'public/best/emailoctopus-free-plan-pricing.html',
  'public/compare/emailoctopus-vs-omnisend.html',
  'public/compare/benchmark-email-vs-emailoctopus.html',
]) {
  if (!fs.existsSync(file)) continue;
  let html = fs.readFileSync(file, 'utf8');
  html = html.replaceAll('data-cta="official" data-tool-id="emailoctopus"', 'data-cta="affiliate" data-tool-id="emailoctopus"');
  html = html.replace(/(<a data-cta="affiliate" data-tool-id="emailoctopus"[^>]*?)href="https:\/\/emailoctopus\.com\/(?:pricing)?"/g, `$1href="${trackingUrl}"`);
  html = html.replace(/<a data-cta="affiliate" data-tool-id="emailoctopus"[^>]*>/g, (tag) => tag.replace('rel="noopener noreferrer"', 'rel="sponsored noopener noreferrer"'));
  html = html.replaceAll('COSHUMA completed EmailOctopus Tolt onboarding and verified the vendor-issued customer referral URL. The pricing button above remains the official pricing page.', 'COSHUMA completed EmailOctopus Tolt onboarding and uses the exact vendor-issued customer referral URL above. Eligible purchases may earn COSHUMA a commission at no additional cost to the buyer.');
  html = html.replaceAll('EmailOctopus publicly offers a free affiliate account with 30% revenue share for one year and a 31-day cookie. COSHUMA has a verified account-specific tracking URL, but this pricing page keeps its pricing CTA on the official non-affiliate page. No clicks, signups, revenue, commissions or payout are inferred.', 'EmailOctopus publicly offers a free affiliate account with 30% revenue share for one year and a 31-day cookie. COSHUMA uses its exact vendor-issued tracking URL on buyer CTAs. No clicks, signups, paid customers, revenue, commissions or payout are inferred from link issuance alone.');
  html = html.replaceAll("COSHUMA's EmailOctopus affiliate application has not been submitted and no COSHUMA-specific customer tracking link is verified.", 'COSHUMA completed EmailOctopus affiliate onboarding and verified its exact vendor-issued customer referral URL. Eligible purchases may earn COSHUMA a commission at no additional cost to the buyer.');
  html = html.replaceAll('Application not submitted; exact tracking URL unknown', 'Approved tracking URL verified');
  html = html.replaceAll('EmailOctopus uses an official non-affiliate pricing link here because COSHUMA has not verified an EmailOctopus customer tracking URL. The Omnisend button stays inside COSHUMA so the dedicated Omnisend page can apply its current evidence-backed CTA state.', 'EmailOctopus uses the exact vendor-issued COSHUMA tracking URL here. Eligible purchases may earn COSHUMA a commission at no additional cost to the buyer. The Omnisend button stays inside COSHUMA so its dedicated buyer guide can apply the current evidence-backed CTA state.');
  html = html.replaceAll("Neither product has a verified COSHUMA customer tracking URL on this comparison at publication time. Benchmark Email's affiliate application requires explicit legal consent and EmailOctopus's application remains unsubmitted. Both buttons above therefore use official non-affiliate destinations. COSHUMA does not infer clicks, signups, paid customers, commissions or revenue from these links.", "Benchmark Email does not yet have a verified COSHUMA customer tracking URL on this comparison because its affiliate application still requires explicit legal consent. EmailOctopus does have a verified vendor-issued COSHUMA customer tracking URL, so its button uses that affiliate destination. COSHUMA does not infer clicks, signups, paid customers, commissions or revenue from link issuance or clicks alone.");
  fs.writeFileSync(file, html);
}

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const tool = tools.find((item) => item.id === 'emailoctopus');
  if (!tool || tool.affiliate_url !== trackingUrl || tool.affiliate_status !== 'approved_tracking' || tool.affiliate_verified !== true) {
    throw new Error(`EmailOctopus approved tracking regression in ${file}`);
  }
}
for (const file of [
  'public/tool/emailoctopus.html',
  'public/best/emailoctopus-free-plan-pricing.html',
  'public/compare/emailoctopus-vs-omnisend.html',
  'public/compare/benchmark-email-vs-emailoctopus.html',
]) {
  const html = fs.readFileSync(file, 'utf8');
  if (!html.includes(trackingUrl) || !html.includes('data-cta="affiliate" data-tool-id="emailoctopus"')) {
    throw new Error(`EmailOctopus affiliate CTA regression in ${file}`);
  }
}

console.log('EmailOctopus approved tracking, duplicate-account guard and affiliate CTA state ensured');
