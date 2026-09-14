import fs from 'node:fs';

const checkedAt = '2026-09-14T16:40:00+09:00';
const benchmark = {
  id: 'benchmark-email',
  name: 'Benchmark Email',
  category: 'marketing_auto',
  category_display: 'Marketing Automation',
  description: 'Email marketing platform for campaigns, automation, signup forms and reporting, with a permanent free plan for small lists.',
  affiliate_url: null,
  pricing: 'Free $0 for up to 500 contacts; current US pricing lists Pro from $19/month',
  key_features: [
    'Drag-and-drop email builder',
    'Email campaigns and reporting',
    'Signup forms and contact management',
    'Automation Lite on the free plan',
    'Free plan with no credit card required',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=benchmarkemail.com&sz=128',
  primary_category: 'marketing_auto',
  comparison_group: 'email_marketing',
  official_url: 'https://www.benchmarkemail.com/',
  pricing_source_url: 'https://www.benchmarkemail.com/pricing/',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'free tier; monthly or annual paid plan',
  evidence_source_type: 'official_pricing_kb_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://www.benchmarkemail.com/partners/affiliates/',
  affiliate_verified: false,
  affiliate_status: 'browser_required_legal_program_consent',
  affiliate_source_url: 'https://www.benchmarkemail.com/partners/affiliates/',
  affiliate_workflow_url: 'https://www.benchmarkemail.com/partners/affiliates/',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official Benchmark Email affiliate page states the program is free and provides a unique tracking link and TrackDesk dashboard only after approval.',
    'Official affiliate page states 30% recurring commission on monthly plans for up to 30 months and 30% one-time commission on annual plans after a 60-day hold.',
    'Official affiliate FAQ states a 30-day cookie, first-touch attribution, monthly payouts, a $30 payout minimum, PayPal payouts, and worldwide eligibility.',
    'The public application form requires an explicit checkbox accepting the Affiliate Terms & Conditions and Privacy Policy; unattended automation must not provide that legal consent.',
    'Repository search found no pre-existing COSHUMA Benchmark Email tool or affiliate record before issue #516.',
    'support@coshuma.com Gmail search found no prior Benchmark Email application, approval, rejection, tracking-link, commission, or payout record before issue #516.',
    'Exact account-specific customer tracking URL is unknown; affiliate application, TrackDesk dashboard, onboarding, and generic vendor URLs must not be used as affiliate revenue links.',
    'Official English public pages disagree on the free-plan monthly send cap (current homepage shows 2,500; Jan 2026 knowledge-base article states 3,500), so COSHUMA avoids presenting one disputed send cap as universal and tells buyers to verify their account/region.',
  ],
  affiliate_next_action: 'When the account owner is available, review Benchmark Email Affiliate Terms & Conditions and Privacy Policy and decide whether to consent. Only after valid approval should COSHUMA recover and verify the exact vendor-issued customer tracking URL. Do not reapply or infer revenue.',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === benchmark.id);
  if (existing?.affiliate_url && benchmark.affiliate_url && existing.affiliate_url !== benchmark.affiliate_url) {
    throw new Error(`Refusing to overwrite existing Benchmark Email affiliate URL in ${file}`);
  }
  if (existing) Object.assign(existing, benchmark);
  else tools.push(benchmark);
  tools.sort((a, b) => String(a.id || '').localeCompare(String(b.id || '')));
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-14';
outreach.programs ||= {};
outreach.programs['benchmark-email'] = {
  status: 'browser_required_legal_program_consent',
  tracking_url: null,
  application_state: 'not_submitted',
  account: 'support@coshuma.com',
  official_program_url: 'https://www.benchmarkemail.com/partners/affiliates/',
  workflow_url: 'https://www.benchmarkemail.com/partners/affiliates/',
  github_issue: 516,
  checked_at: checkedAt,
  note: 'The public application requires explicit acceptance of Affiliate Terms & Conditions and Privacy Policy. No COSHUMA-specific tracking URL exists yet. Keep customer CTAs on official non-affiliate Benchmark Email pages until a vendor-issued URL is verified.',
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
if (!queue.some((item) => item.tool_id === 'benchmark-email' || String(item.id || '').startsWith('benchmark-email-'))) {
  queue.push({
    id: 'benchmark-email-legal-consent-2026-09-14',
    tool_id: 'benchmark-email',
    priority: 'medium',
    status: 'browser_required_legal_program_consent',
    affiliate_status: 'browser_required_legal_program_consent',
    application_state: 'not_submitted',
    cost: 0,
    exact_tracking_url: null,
    user_action_required: true,
    blocker: 'Benchmark Email affiliate application requires explicit acceptance of Affiliate Terms & Conditions and Privacy Policy.',
    reason: 'Duplicate checks are clear and the free public application is available, but legal-program consent must be made by the account owner. No tracking URL has been issued or verified.',
    next_action: 'Account owner reviews the affiliate terms/privacy policy and decides whether to consent. If submitted and approved, recover only the exact TrackDesk/vendor-issued customer-facing tracking URL. Stop for CAPTCHA, OTP, forced identity verification, payment approval, or any additional legal consent.',
    do_not_reapply: true,
    verified_at: checkedAt,
    github_issue: 516,
  });
}
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/benchmark-email.html',
  'https://coshuma.com/best/benchmark-email-free-plan-pricing.html',
  'https://coshuma.com/compare/benchmark-email-vs-emailoctopus.html',
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
if (!llms.includes('https://coshuma.com/tool/benchmark-email.html')) {
  llms += '\n- https://coshuma.com/tool/benchmark-email.html — Benchmark Email free-plan, pricing and email-marketing buyer guide\n- https://coshuma.com/best/benchmark-email-free-plan-pricing.html — Benchmark Email free-plan limits and upgrade guide\n- https://coshuma.com/compare/benchmark-email-vs-emailoctopus.html — Benchmark Email vs EmailOctopus free email-marketing comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-benchmarkemail-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-cyan-500/25 bg-cyan-500/5 p-5"><div class="text-xs uppercase tracking-widest text-cyan-300 font-bold">Email marketing</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-cyan-300" href="/best/benchmark-email-free-plan-pricing.html">Benchmark Email free plan & pricing</a> · <a class="font-bold text-white hover:text-cyan-300" href="/tool/benchmark-email.html">Benchmark Email review</a> · <a class="font-bold text-white hover:text-cyan-300" href="/compare/benchmark-email-vs-emailoctopus.html">Benchmark Email vs EmailOctopus</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'index.html']) {
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-benchmarkemail-fastlane="2026-09-14"')) {
    html = html.includes('</main>') ? html.replace('</main>', `${hubBlock}</main>`) : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

const emailOctopusPath = 'public/tool/emailoctopus.html';
if (fs.existsSync(emailOctopusPath)) {
  let html = fs.readFileSync(emailOctopusPath, 'utf8');
  if (!html.includes('/compare/benchmark-email-vs-emailoctopus.html')) {
    const related = `\n<section data-benchmarkemail-related="2026-09-14" class="max-w-6xl mx-auto px-5 pb-8"><a href="/compare/benchmark-email-vs-emailoctopus.html" class="block rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5"><div class="text-xs uppercase tracking-wider font-bold text-cyan-300">Related free-email comparison</div><div class="mt-2 font-extrabold text-white">Benchmark Email vs EmailOctopus: smaller all-in-one starter vs larger free sending limits →</div></a></section>\n`;
    html = html.includes('</main>') ? html.replace('</main>', `${related}</main>`) : html.replace('</body>', `${related}</body>`);
    fs.writeFileSync(emailOctopusPath, html);
  }
}

console.log('Benchmark Email fast-lane state, legal-consent queue and discoverability ensured');
