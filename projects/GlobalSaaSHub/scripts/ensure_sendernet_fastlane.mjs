import fs from 'node:fs';

const checkedAt = '2026-09-14T15:39:00+09:00';
const sender = {
  id: 'sender-net',
  name: 'Sender.net',
  category: 'marketing_auto',
  category_display: 'Marketing Automation',
  description: 'Email and SMS marketing platform with campaigns, automation, transactional email, landing pages, forms and popups, including a generous Free Forever plan.',
  affiliate_url: null,
  pricing: 'Free Forever $0 for up to 2,500 subscribers and 15,000 emails/month; paid pricing varies by subscriber volume, billing term and promotions',
  key_features: [
    'Email campaigns and drag-and-drop editor',
    'Email automation and segmentation',
    'Landing pages, forms and popups',
    'Transactional email',
    'Free plan with no credit card required',
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=sender.net&sz=128',
  primary_category: 'marketing_auto',
  comparison_group: 'email_marketing',
  official_url: 'https://www.sender.net/',
  pricing_source_url: 'https://www.sender.net/pricing/',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'free tier; paid pricing varies with subscriber count and billing choice',
  evidence_source_type: 'official_pricing_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://www.sender.net/affiliate-program/',
  affiliate_verified: false,
  affiliate_status: 'browser_required_partnerstack_application',
  affiliate_source_url: 'https://www.sender.net/affiliate-program/',
  affiliate_workflow_url: 'https://dash.partnerstack.com/application?company=sendernet&gref=page',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official Sender.net partner page exposes an exact PartnerStack application route.',
    'Current base partner tier states 30% lifetime recurring commission for up to 20 sales/month; higher performance tiers advertise 35% and 40%.',
    'Official FAQ states a 90-day cookie and recurring monthly commissions while the customer remains active and subscribed.',
    'GitHub search found no pre-existing COSHUMA Sender.net tool/application/tracking record before this fast-lane cycle.',
    'support@coshuma.com Gmail search for sender.net found no prior application, approval, rejection, tracking-link, commission, or payout message.',
    'Exact account-specific customer tracking URL is unknown; PartnerStack portal/application URLs and generic vendor URLs must not be used as affiliate revenue links.',
    'GitHub issue #513 tracks the authenticated PartnerStack duplicate check and one-time application/recovery step.',
  ],
  affiliate_next_action: 'Reuse the existing COSHUMA PartnerStack identity in an authenticated browser/Work session, check for an existing Sender.net relationship, then submit once only if absent or recover the exact issued customer tracking URL if already enrolled.',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((tool) => tool.id === sender.id);
  if (existing?.affiliate_url && sender.affiliate_url && existing.affiliate_url !== sender.affiliate_url) {
    throw new Error(`Refusing to overwrite existing Sender.net affiliate URL in ${file}`);
  }
  if (existing) Object.assign(existing, sender);
  else tools.push(sender);
  tools.sort((a, b) => String(a.id || '').localeCompare(String(b.id || '')));
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = '2026-09-14';
outreach.programs ||= {};
outreach.programs['sender-net'] = {
  status: 'browser_required_partnerstack_application',
  tracking_url: null,
  application_state: 'not_submitted',
  account: 'support@coshuma.com',
  official_program_url: 'https://www.sender.net/affiliate-program/',
  workflow_url: 'https://dash.partnerstack.com/application?company=sendernet&gref=page',
  github_issue: 513,
  checked_at: checkedAt,
  note: 'Official PartnerStack application route is confirmed, but no existing COSHUMA Sender.net enrollment or issued customer tracking URL was found in GitHub/Gmail. Reuse the existing PartnerStack identity and do not treat the application/dashboard route as a customer affiliate CTA.',
};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
if (!queue.some((item) => item.tool_id === 'sender-net' || String(item.id || '').startsWith('sender-net-'))) {
  queue.push({
    id: 'sender-net-partnerstack-2026-09-14',
    tool_id: 'sender-net',
    priority: 'medium',
    status: 'browser_required_partnerstack_application',
    affiliate_status: 'browser_required_partnerstack_application',
    application_state: 'not_submitted',
    cost: 0,
    exact_tracking_url: null,
    user_action_required: false,
    blocker: 'Sender.net uses an interactive PartnerStack application flow and this run has no authenticated interactive PartnerStack session.',
    reason: 'GitHub and Gmail duplicate checks were clear, but application submission has not occurred and no customer tracking URL is verified.',
    next_action: 'Reuse the existing COSHUMA PartnerStack identity, check for an existing Sender.net relationship, and submit the free application once only if absent. If already enrolled, recover only the exact issued customer-facing link. Stop for CAPTCHA, OTP, legal agreement, forced identity verification, or payment approval.',
    do_not_reapply: true,
    verified_at: checkedAt,
    github_issue: 513,
  });
}
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

const urls = [
  'https://coshuma.com/tool/sender-net.html',
  'https://coshuma.com/best/sender-net-free-plan-pricing.html',
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
if (!llms.includes('https://coshuma.com/tool/sender-net.html')) {
  llms += '\n- https://coshuma.com/tool/sender-net.html — Sender.net free-plan, pricing and email-marketing buyer guide\n- https://coshuma.com/best/sender-net-free-plan-pricing.html — Sender.net Free Forever plan and upgrade decision guide\n- https://coshuma.com/compare/sender-net-vs-emailoctopus.html — Sender.net vs EmailOctopus free email-marketing comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-sendernet-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-5"><div class="text-xs uppercase tracking-widest text-emerald-300 font-bold">Email marketing</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-emerald-300" href="/best/sender-net-free-plan-pricing.html">Sender.net free plan & pricing</a> · <a class="font-bold text-white hover:text-emerald-300" href="/tool/sender-net.html">Sender.net review</a> · <a class="font-bold text-white hover:text-emerald-300" href="/compare/sender-net-vs-emailoctopus.html">Sender.net vs EmailOctopus</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'index.html']) {
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-sendernet-fastlane="2026-09-14"')) {
    html = html.includes('</main>') ? html.replace('</main>', `${hubBlock}</main>`) : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

const emailOctopusPath = 'public/tool/emailoctopus.html';
if (fs.existsSync(emailOctopusPath)) {
  let html = fs.readFileSync(emailOctopusPath, 'utf8');
  if (!html.includes('/compare/sender-net-vs-emailoctopus.html')) {
    const related = `\n<section data-sendernet-related="2026-09-14" class="max-w-6xl mx-auto px-5 pb-8"><a href="/compare/sender-net-vs-emailoctopus.html" class="block rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5"><div class="text-xs uppercase tracking-wider font-bold text-emerald-300">Related free-email comparison</div><div class="mt-2 font-extrabold text-white">Sender.net vs EmailOctopus: 15,000 vs 10,000 free emails/month →</div></a></section>\n`;
    html = html.includes('</main>') ? html.replace('</main>', `${related}</main>`) : html.replace('</body>', `${related}</body>`);
    fs.writeFileSync(emailOctopusPath, html);
  }
}

console.log('Sender.net fast-lane state, browser queue and discoverability ensured');
