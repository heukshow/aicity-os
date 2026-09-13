import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const publicDir = path.join(root, 'public');

const beehiiv = {
  id: 'beehiiv',
  name: 'beehiiv',
  category: 'email_outreach',
  category_display: 'Email & Outreach',
  description: 'A newsletter platform for creators and publishers with website hosting, unlimited email sends, audience growth tools, monetization features and paid subscriptions.',
  affiliate_url: null,
  pricing: 'Launch $0/month for up to 2,500 subscribers; paid plans vary by subscriber tier and billing cadence',
  key_features: [
    'Newsletter publishing and website hosting',
    'Unlimited email sends on the free Launch plan',
    'Recommendation network and audience growth tools',
    'Paid subscriptions, ads and digital products on eligible paid plans'
  ],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=beehiiv.com&sz=128',
  primary_category: 'email_outreach',
  comparison_group: 'email_marketing',
  official_url: 'https://www.beehiiv.com/',
  pricing_source_url: 'https://www.beehiiv.com/pricing',
  pricing_verified_at: '2026-09-14T00:00:00+09:00',
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly or annual depending on plan',
  evidence_source_type: 'official_pricing_page',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: '2026-09-14T00:00:00+09:00',
  official_evidence_url: 'https://www.beehiiv.com/pricing',
  affiliate_verified: true,
  affiliate_status: 'application_available_account_required',
  affiliate_source_url: 'https://www.beehiiv.com/partners',
  affiliate_verified_at: '2026-09-14T00:00:00+09:00',
  affiliate_evidence_markers: [
    'Official beehiiv partner page states partners can earn up to 60% commission every month for each paying customer for one year',
    'Official partner page says applicants create a beehiiv account to unlock the partner dashboard and custom tracking link',
    'COSHUMA support@coshuma.com Gmail in:anywhere search returned no beehiiv messages before this registration cycle',
    'No COSHUMA-specific beehiiv customer tracking URL is verified yet; official non-affiliate customer URLs must remain in use until an issued tracking URL is observed'
  ],
  affiliate_next_action: 'Use the official beehiiv partner application/account flow once account-holder consent steps can be completed. Do not invent a tracking parameter or publish the partner application URL as a customer CTA.'
};

for (const rel of ['data/tools.json', 'data/tools.next.json']) {
  const file = path.join(root, rel);
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  const existing = tools.find((t) => t.id === beehiiv.id);
  if (existing) Object.assign(existing, beehiiv);
  else tools.push(beehiiv);
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const toolPage = `<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>beehiiv Pricing 2026: Free Plan, Newsletter Tools & Alternatives | COSHUMA</title>
  <meta name="description" content="beehiiv buyer guide for 2026: free Launch plan, 2,500-subscriber limit, unlimited email sends, monetization features and alternatives." />
  <link rel="canonical" href="https://coshuma.com/tool/beehiiv.html" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="https://coshuma.com/tool/beehiiv.html" />
  <meta property="og:title" content="beehiiv Pricing 2026 & Free Plan | COSHUMA" />
  <meta property="og:description" content="A buyer-focused beehiiv guide covering the free Launch plan, growth tools, monetization and alternatives." />
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"SoftwareApplication","name":"beehiiv","operatingSystem":"Web","applicationCategory":"BusinessApplication","url":"https://www.beehiiv.com/","description":"Newsletter publishing platform with website hosting, audience growth and monetization tools."}</script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body{background:#0b0c10;color:#f1f5f9;font-family:Inter,Arial,sans-serif}</style>
</head>
<body>
<header class="border-b border-slate-800 bg-[#07080c] py-4 px-6"><div class="max-w-5xl mx-auto flex justify-between"><a href="/" class="font-black text-white">COSHUMA</a><a href="/best/beehiiv-free-plan-pricing.html" class="text-sm text-purple-300">beehiiv buyer guide</a></div></header>
<main class="max-w-5xl mx-auto px-4 py-12 space-y-8">
  <section class="rounded-3xl border border-slate-800 bg-[#131520] p-8 space-y-5">
    <div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Newsletter platform</div>
    <h1 class="text-4xl md:text-5xl font-black">beehiiv pricing & buyer guide</h1>
    <p class="text-sm text-slate-500">Official pricing and partner pages checked September 14, 2026.</p>
    <p class="text-lg text-slate-300 leading-relaxed">beehiiv combines newsletter publishing, a hosted website, audience growth and monetization in one product. The free Launch plan is useful for testing the workflow before paying for advanced growth, automation or monetization features.</p>
    <div class="grid md:grid-cols-3 gap-4">
      <div class="rounded-2xl border border-slate-800 p-5"><div class="text-xs uppercase text-slate-500 font-bold">Launch</div><div class="text-2xl font-black mt-2">$0/month</div><p class="text-sm text-slate-400 mt-2">Up to 2,500 subscribers and unlimited email sends.</p></div>
      <div class="rounded-2xl border border-slate-800 p-5"><div class="text-xs uppercase text-slate-500 font-bold">Best for</div><div class="font-extrabold mt-2">Creator newsletters</div><p class="text-sm text-slate-400 mt-2">Useful when newsletter growth, a hosted site and monetization belong in one stack.</p></div>
      <div class="rounded-2xl border border-slate-800 p-5"><div class="text-xs uppercase text-slate-500 font-bold">Paid plans</div><div class="font-extrabold mt-2">Tier-based</div><p class="text-sm text-slate-400 mt-2">Scale and Max pricing varies by subscriber tier and billing cadence.</p></div>
    </div>
    <div class="flex flex-col sm:flex-row gap-3"><a data-cta="official" data-tool-id="beehiiv" data-cta-source="beehiiv-tool-free" href="https://www.beehiiv.com/pricing" target="_blank" rel="noopener noreferrer" class="rounded-xl bg-purple-600 px-6 py-3 font-extrabold text-center">See beehiiv pricing →</a><a href="/compare/beehiiv-vs-kit.html" class="rounded-xl bg-slate-800 px-6 py-3 font-extrabold text-center">beehiiv vs Kit →</a></div>
    <p class="text-xs text-slate-500">COSHUMA has verified that beehiiv currently operates a partner program, but no COSHUMA-specific customer tracking URL has been issued or verified yet. These beehiiv buttons intentionally use official non-affiliate URLs.</p>
  </section>
  <section class="rounded-3xl border border-slate-800 bg-[#131520] p-8 space-y-4"><h2 class="text-3xl font-black">What you can test for free</h2><ul class="list-disc pl-6 space-y-2 text-slate-300"><li>Run a newsletter with up to 2,500 subscribers.</li><li>Send unlimited emails on the Launch plan.</li><li>Use the hosted website, custom domains, campaign analytics and recommendation network.</li><li>Test the core publishing workflow before deciding whether paid automation and monetization features are worth the upgrade.</li></ul></section>
  <section class="rounded-3xl border border-purple-500/30 bg-purple-500/5 p-8 space-y-4"><div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Alternative path</div><h2 class="text-3xl font-black">Compare Kit if creator email automation matters more</h2><p class="text-slate-300 leading-relaxed">Kit is another creator-focused email platform already covered by COSHUMA. Use the side-by-side guide to compare the newsletter-first beehiiv model with Kit's creator email and automation workflow.</p><a href="/compare/beehiiv-vs-kit.html" class="inline-block rounded-xl bg-slate-800 px-6 py-3 font-extrabold">Compare beehiiv vs Kit →</a></section>
</main>
<footer class="border-t border-slate-800 py-8 text-center text-xs text-slate-500">COSHUMA — evidence-first AI & SaaS buyer guides</footer>
</body>
</html>\n`;

const bestPage = `<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>beehiiv Free Plan 2026: 2,500 Subscribers & Unlimited Sends | COSHUMA</title>
  <meta name="description" content="beehiiv free plan guide for 2026: $0 Launch plan, up to 2,500 subscribers, unlimited sends, websites, analytics and upgrade considerations." />
  <link rel="canonical" href="https://coshuma.com/best/beehiiv-free-plan-pricing.html" />
  <meta property="og:type" content="article" /><meta property="og:url" content="https://coshuma.com/best/beehiiv-free-plan-pricing.html" /><meta property="og:title" content="beehiiv Free Plan 2026 | COSHUMA" />
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage","name":"beehiiv Free Plan 2026","url":"https://coshuma.com/best/beehiiv-free-plan-pricing.html","about":{"@type":"SoftwareApplication","name":"beehiiv","url":"https://www.beehiiv.com/"}}</script>
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Is beehiiv free in 2026?","acceptedAnswer":{"@type":"Answer","text":"Yes. beehiiv's Launch plan is $0 per month and supports up to 2,500 subscribers with unlimited email sends."}},{"@type":"Question","name":"Does beehiiv require a credit card for the free plan?","acceptedAnswer":{"@type":"Answer","text":"beehiiv states its Launch plan is free forever and no credit card is required to get started."}},{"@type":"Question","name":"When should I consider a paid beehiiv plan?","acceptedAnswer":{"@type":"Answer","text":"Consider Scale or Max when you need paid-plan growth, automation, monetization, team or branding features. Pricing varies by subscriber tier and billing cadence."}}]}</script>
  <script src="https://cdn.tailwindcss.com"></script><style>body{background:#0b0c10;color:#f1f5f9;font-family:Inter,Arial,sans-serif}</style>
</head>
<body><header class="border-b border-slate-800 py-4 px-6"><div class="max-w-5xl mx-auto"><a href="/" class="font-black">COSHUMA</a></div></header>
<main class="max-w-5xl mx-auto px-4 py-12 space-y-8"><section class="space-y-5"><div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Buyer guide</div><h1 class="text-4xl md:text-6xl font-black">beehiiv free plan: what $0 actually gets you</h1><p class="text-lg text-slate-300">The current Launch plan is $0/month, supports up to 2,500 subscribers and includes unlimited email sends. That makes it a practical low-risk starting point for a new newsletter.</p><div class="grid md:grid-cols-3 gap-4"><div class="rounded-2xl border border-slate-800 p-5"><strong>$0/month</strong><p class="text-sm text-slate-400 mt-2">Free Launch plan.</p></div><div class="rounded-2xl border border-slate-800 p-5"><strong>2,500 subscribers</strong><p class="text-sm text-slate-400 mt-2">Current Launch-plan subscriber limit.</p></div><div class="rounded-2xl border border-slate-800 p-5"><strong>Unlimited sends</strong><p class="text-sm text-slate-400 mt-2">No extra email-send cap on Launch.</p></div></div><a data-cta="official" data-tool-id="beehiiv" data-cta-source="beehiiv-best-pricing" href="https://www.beehiiv.com/pricing" target="_blank" rel="noopener noreferrer" class="inline-block rounded-xl bg-purple-600 px-6 py-3 font-extrabold">Check current beehiiv pricing →</a><p class="text-xs text-slate-500">Official non-affiliate link until COSHUMA receives and verifies an account-specific beehiiv partner link.</p></section>
<section class="rounded-3xl border border-slate-800 bg-[#131520] p-8 space-y-4"><h2 class="text-3xl font-black">Upgrade only when the paid features matter</h2><p class="text-slate-300">Paid beehiiv plans add capabilities such as advanced monetization, automations, surveys, team features and branding controls. Because paid pricing changes by subscriber tier and billing cadence, check the current pricing page before committing.</p></section>
<section class="rounded-3xl border border-slate-800 bg-[#131520] p-8"><h2 class="text-2xl font-black">Related decision guides</h2><div class="mt-4 flex flex-wrap gap-3"><a href="/tool/beehiiv.html" class="rounded-xl bg-slate-800 px-5 py-3 font-bold">beehiiv tool guide</a><a href="/compare/beehiiv-vs-kit.html" class="rounded-xl bg-slate-800 px-5 py-3 font-bold">beehiiv vs Kit</a></div></section></main>
<footer class="border-t border-slate-800 py-8 text-center text-xs text-slate-500">COSHUMA — evidence-first AI & SaaS buyer guides</footer></body></html>\n`;

const comparePage = `<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>beehiiv vs Kit 2026: Free Plans, Newsletter Growth & Automation | COSHUMA</title><meta name="description" content="Compare beehiiv vs Kit in 2026 by free-plan fit, newsletter publishing, creator email workflows and upgrade path." /><link rel="canonical" href="https://coshuma.com/compare/beehiiv-vs-kit.html" /><meta property="og:url" content="https://coshuma.com/compare/beehiiv-vs-kit.html" /><script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage","name":"beehiiv vs Kit 2026","url":"https://coshuma.com/compare/beehiiv-vs-kit.html","about":[{"@type":"SoftwareApplication","name":"beehiiv","url":"https://www.beehiiv.com/"},{"@type":"SoftwareApplication","name":"Kit","url":"https://kit.com/"}]}</script><script src="https://cdn.tailwindcss.com"></script><style>body{background:#0b0c10;color:#f1f5f9;font-family:Inter,Arial,sans-serif}</style></head>
<body><header class="border-b border-slate-800 py-4 px-6"><div class="max-w-5xl mx-auto"><a href="/" class="font-black">COSHUMA</a></div></header><main class="max-w-5xl mx-auto px-4 py-12 space-y-8"><section class="space-y-5"><div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Email platform comparison</div><h1 class="text-4xl md:text-6xl font-black">beehiiv vs Kit</h1><p class="text-lg text-slate-300">Choose beehiiv when you want a newsletter-first product with a hosted site and native growth/monetization stack. Compare Kit when creator email automation and established creator-marketing workflows are the priority.</p></section><section class="rounded-3xl border border-slate-800 bg-[#131520] p-8 overflow-x-auto"><table class="w-full text-sm"><thead><tr class="text-left border-b border-slate-700"><th class="p-3">Decision</th><th class="p-3">beehiiv</th><th class="p-3">Kit</th></tr></thead><tbody class="text-slate-300"><tr class="border-b border-slate-800"><td class="p-3 font-bold">Free starting point</td><td class="p-3">Launch: $0, up to 2,500 subscribers, unlimited sends</td><td class="p-3">Use Kit's current pricing page for its latest free-plan limits</td></tr><tr class="border-b border-slate-800"><td class="p-3 font-bold">Core orientation</td><td class="p-3">Newsletter publishing, website, growth and monetization</td><td class="p-3">Creator email marketing and automation</td></tr><tr><td class="p-3 font-bold">Best first test</td><td class="p-3">Launch a real newsletter and website on Launch</td><td class="p-3">Build one creator email sequence and subscriber flow</td></tr></tbody></table></section><section class="grid md:grid-cols-2 gap-4"><div class="rounded-3xl border border-purple-500/30 bg-purple-500/5 p-7 space-y-4"><h2 class="text-2xl font-black">Start with beehiiv when…</h2><p class="text-slate-300">You want the newsletter, web presence, audience growth and monetization layer in one product.</p><a data-cta="official" data-tool-id="beehiiv" data-cta-source="compare-beehiiv-kit-beehiiv" href="https://www.beehiiv.com/pricing" target="_blank" rel="noopener noreferrer" class="inline-block rounded-xl bg-purple-600 px-5 py-3 font-bold">See beehiiv pricing →</a></div><div class="rounded-3xl border border-slate-800 bg-[#131520] p-7 space-y-4"><h2 class="text-2xl font-black">Start with Kit when…</h2><p class="text-slate-300">Creator email automation and subscriber communication are more important than a newsletter-first publishing stack.</p><a href="/tool/kit.html" class="inline-block rounded-xl bg-slate-800 px-5 py-3 font-bold">Read the Kit guide →</a></div></section><p class="text-xs text-slate-500">No COSHUMA-specific beehiiv partner URL is published on this page because none has been verified yet.</p></main><footer class="border-t border-slate-800 py-8 text-center text-xs text-slate-500">COSHUMA — evidence-first AI & SaaS buyer guides</footer></body></html>\n`;

fs.mkdirSync(path.join(publicDir, 'tool'), { recursive: true });
fs.mkdirSync(path.join(publicDir, 'best'), { recursive: true });
fs.mkdirSync(path.join(publicDir, 'compare'), { recursive: true });
fs.writeFileSync(path.join(publicDir, 'tool/beehiiv.html'), toolPage);
fs.writeFileSync(path.join(publicDir, 'best/beehiiv-free-plan-pricing.html'), bestPage);
fs.writeFileSync(path.join(publicDir, 'compare/beehiiv-vs-kit.html'), comparePage);

const addBefore = (file, marker, block) => {
  if (!fs.existsSync(file)) return;
  let text = fs.readFileSync(file, 'utf8');
  if (text.includes(block.trim())) return;
  if (!text.includes(marker)) return;
  text = text.replace(marker, `${block}\n${marker}`);
  fs.writeFileSync(file, text);
};

const sitemap = path.join(publicDir, 'sitemap.xml');
if (fs.existsSync(sitemap)) {
  let text = fs.readFileSync(sitemap, 'utf8');
  const urls = [
    'https://coshuma.com/tool/beehiiv.html',
    'https://coshuma.com/best/beehiiv-free-plan-pricing.html',
    'https://coshuma.com/compare/beehiiv-vs-kit.html'
  ];
  for (const url of urls) {
    if (!text.includes(url)) text = text.replace('</urlset>', `  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n</urlset>`);
  }
  fs.writeFileSync(sitemap, text);
}

const llms = path.join(publicDir, 'llms.txt');
if (fs.existsSync(llms)) {
  let text = fs.readFileSync(llms, 'utf8');
  const lines = [
    '- https://coshuma.com/tool/beehiiv.html — beehiiv pricing, free-plan and newsletter-platform buyer guide',
    '- https://coshuma.com/best/beehiiv-free-plan-pricing.html — beehiiv $0 Launch plan and 2,500-subscriber buyer guide',
    '- https://coshuma.com/compare/beehiiv-vs-kit.html — beehiiv vs Kit creator newsletter and email-platform comparison'
  ];
  for (const line of lines) if (!text.includes(line)) text += `\n${line}`;
  fs.writeFileSync(llms, `${text.trimEnd()}\n`);
}

addBefore(path.join(publicDir, 'best/index.html'), '</main>', `
<section data-beehiiv-entry class="max-w-6xl mx-auto px-4 pb-10">
  <a href="/best/beehiiv-free-plan-pricing.html" class="block rounded-3xl border border-purple-500/25 bg-[#131520] p-6 hover:border-purple-400/50">
    <div class="text-xs uppercase tracking-wider text-purple-300 font-bold">Newsletter platform</div>
    <div class="mt-2 text-xl font-black text-white">beehiiv free plan: $0, up to 2,500 subscribers</div>
    <p class="mt-2 text-sm text-slate-400">Compare the Launch plan, upgrade triggers and the beehiiv vs Kit decision path.</p>
  </a>
</section>`);

for (const rel of ['tool/kit.html', 'tool/convertkit.html']) {
  addBefore(path.join(publicDir, rel), '</main>', `
<section data-beehiiv-related class="max-w-4xl mx-auto px-4 pb-10">
  <a href="/compare/beehiiv-vs-kit.html" class="block rounded-2xl border border-purple-500/25 bg-[#131520] p-5 font-bold text-purple-200">Compare Kit with beehiiv →</a>
</section>`);
}

console.log('beehiiv complete registration cycle ensured: data + tool + best + comparison + sitemap + llms + internal links');
