// Keep the two Search Console opportunity pages reproducible after SEO generation.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tools = JSON.parse(fs.readFileSync(path.join(root, 'data/tools.json'), 'utf8'));
const escape = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const pages = [
  {
    slug: 'semrush-vs-frase', ids: ['semrush', 'frase'],
    title: 'Semrush vs Frase: SEO Research or Content Workflow?',
    description: 'Compare Semrush and Frase for keyword research, content production, AI visibility and pricing. Choose by the work you need to complete, with official sources.',
    intro: 'Start with the work you need to finish. Semrush brings keyword, competitor and backlink research into a broader marketing toolkit. Frase connects content research, drafting, optimization and publishing. Their capabilities overlap; the better fit depends on your workflow.',
    fit: [
      'Shortlist Semrush when your first task is investigating keywords, competitors, backlinks or technical site issues across a broader SEO program.',
      'Shortlist Frase when your first task is turning research into drafts, optimizing pages and publishing through a connected content workflow.'
    ],
    rows: [
      ['Research', 'Keyword research, competitor analysis, backlink analysis and position tracking.', 'SEO research and topic clusters feed the content creation workflow.'],
      ['Creating and maintaining pages', 'Content tools are part of its wider toolkit offering; check which subscription includes your required features.', 'Drafting, content optimization, CMS publishing and Content Guard are presented together.'],
      ['AI visibility', 'An AI Visibility toolkit is offered; check the selected bundle.', 'SEO/GEO scoring and AI visibility are listed on the current plans.'],
      ['Budget check', 'Compare the exact SEO, content and AI toolkit combination, website limits and extra users on the official pricing page.', 'Starter lists $49 monthly or $39/month billed yearly, for one seat and one site. Article and audit allowances apply.']
    ],
    test: 'Use the same existing page as a trial task: identify the problem, prepare an improved brief, revise the draft and review how it reaches your CMS. Separately check whether you need backlink research or multi-site reporting. Do not buy two overlapping subscriptions before identifying the missing step.',
    questions: [
      ['Can Frase replace Semrush?', 'It may cover the content work you need, but do not assume every research dataset, reporting limit or integration is interchangeable. List your essential tasks and test those before switching.'],
      ['Which is cheaper?', 'A starting price is not a like-for-like quote. Compare seats, websites, content volume, audit limits and any extra toolkit subscriptions. Verify current billing terms at checkout.']
    ],
    sources: [['Semrush toolkits', 'https://www.semrush.com/toolkits/'], ['Semrush pricing', 'https://www.semrush.com/pricing/'], ['Frase platform', 'https://www.frase.io/'], ['Frase pricing', 'https://www.frase.io/pricing']]
  },
  {
    slug: 'privy-vs-omnisend', ids: ['privy', 'omnisend'],
    title: 'Privy vs Omnisend: Pop-ups, Email, SMS & Pricing',
    description: 'Privy or Omnisend for your store? Compare pop-up capture, email and SMS workflows, billing drivers and what to test before moving your subscriber list.',
    intro: 'Both products serve ecommerce email and SMS workflows. Start by deciding whether you need better on-site capture alongside your current email platform, or a platform for customer messaging across channels.',
    fit: [
      'Shortlist Privy when pop-up design and targeting are the immediate problem, especially if you want to evaluate its separate Pop-ups & Displays offering before replacing your email platform.',
      'Shortlist Omnisend when you want to evaluate email, SMS and web push together, with ecommerce automations and segmentation in the same platform.'
    ],
    rows: [
      ['Subscriber capture', 'Pop-up targeting, embedded forms and A/B testing; a separate displays product is available.', 'Signup forms and list-building features alongside its messaging platform.'],
      ['Messaging', 'Email and SMS campaigns, automation and segmentation.', 'Email, SMS and web push, with automation and reporting.'],
      ['Budget check', 'Email starts at $30/month. Displays-only starts at $24/month and is priced by page views. Email pricing uses mailable contacts.', 'Use the list-size pricing selector. Billed contacts include subscribers and non-subscribers receiving automated messages; SMS costs vary by destination and volume.'],
      ['Before migrating', 'Confirm your store integration and whether you are buying displays only or the email/SMS offering.', 'Confirm your store integration, message volumes and the workflows you will migrate.']
    ],
    test: 'Compare quotes using the same contact count, monthly email volume, SMS destination countries and store traffic. Then test a signup form, a welcome sequence and a cart-recovery flow. Review mobile display behavior and suppression rules before importing your full list.',
    questions: [
      ['Do I need to replace my email platform to use Privy?', 'Privy lists a separate Pop-ups & Displays product that can sync collected contacts to supported platforms. Confirm that your existing platform is supported before selecting it.'],
      ['Which will generate more sales?', 'This comparison does not establish a conversion or deliverability winner. Measure completed purchases and unsubscribes with your own audience; vendor features alone cannot predict the result.']
    ],
    sources: [['Privy pricing and features', 'https://www.privy.com/pricing'], ['Omnisend platform', 'https://www.omnisend.com/'], ['Omnisend pricing', 'https://www.omnisend.com/pricing/']]
  }
];
for (const p of pages) {
  const pair = p.ids.map(id => {
    const tool = tools.find(t => t.id === id);
    if (!tool) throw Error(`Missing tool ${id}`);
    return tool;
  });
  const canonical = `https://coshuma.com/compare/${p.slug}.html`;
  const ctas = pair.map(t => {
    const affiliate = t.affiliate_verified === true && t.affiliate_status === 'approved_tracking';
    const url = affiliate ? t.affiliate_url : t.official_url;
    if (new URL(url).protocol !== 'https:') throw Error(`Unsafe route for ${t.id}`);
    return `<a class="cta" data-cta="${affiliate ? 'affiliate' : 'official'}" data-tool-id="${escape(t.id)}" data-cta-source="comparison-decision" href="${escape(url)}" target="_blank" rel="${affiliate ? 'sponsored ' : ''}noopener noreferrer">Explore ${escape(t.name)} →</a>`;
  }).join('');
  const html = `<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escape(p.title)} | COSHUMA</title><meta name="description" content="${escape(p.description)}">
<link rel="canonical" href="${canonical}"><meta property="og:type" content="article"><meta property="og:url" content="${canonical}"><meta property="og:title" content="${escape(p.title)} | COSHUMA"><meta property="og:description" content="${escape(p.description)}">
<script type="application/ld+json">${JSON.stringify({'@context':'https://schema.org','@type':'WebPage',name:p.title,description:p.description,url:canonical,isPartOf:{'@type':'WebSite',name:'COSHUMA',url:'https://coshuma.com/'}})}</script>
<script defer src="/affiliate-attribution.js"></script>
<style>body{margin:0;background:#0b0c10;color:#e8eaf2;font:17px/1.7 system-ui,sans-serif}header,main,footer{max-width:960px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;border-bottom:1px solid #303445}a{color:#c4b5fd;text-underline-offset:4px}h1{font-size:clamp(30px,5vw,46px);line-height:1.16;color:white}h2{font-size:24px}h3{font-size:19px}section{margin:30px 0;padding:24px;background:#141724;border:1px solid #303445;border-radius:20px}.muted{color:#b0b6cc;font-size:14px}.fit{display:grid;grid-template-columns:1fr 1fr;gap:20px}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:570px;font-size:15px}th,td{text-align:left;vertical-align:top;padding:16px;border-bottom:1px solid #373c50}th{color:white}nav.ctas{display:flex;flex-wrap:wrap;gap:14px}.cta{display:inline-block;padding:13px 22px;background:#6d28d9;color:white;border-radius:12px;text-decoration:none;font-weight:700}a:focus-visible{outline:3px solid #fcd34d;outline-offset:4px}@media(max-width:600px){header,main,footer{padding:18px}section{padding:18px}.fit{grid-template-columns:1fr}}</style></head>
<body><header><a href="/">COSHUMA</a><a href="/">Browse tools</a></header><main data-source-comparison="${p.slug}">
<p class="muted">Buyer comparison · Official sources checked September 8, 2026</p><h1>${escape(p.title)}</h1><p>${escape(p.intro)}</p>
<section><h2>Which should you shortlist?</h2><div class="fit">${pair.map((t,i)=>`<div><h3>${escape(t.name)}</h3><p>${escape(p.fit[i])}</p><a href="/tool/${t.id}.html">Read the ${escape(t.name)} profile</a></div>`).join('')}</div></section>
<section><h2>Compare the work and the cost</h2><div class="scroll" role="region" aria-label="Feature and pricing comparison" tabindex="0"><table><thead><tr><th scope="col">Decision</th>${pair.map(t=>`<th scope="col">${escape(t.name)}</th>`).join('')}</tr></thead><tbody>${p.rows.map(r=>`<tr><th scope="row">${escape(r[0])}</th><td>${escape(r[1])}</td><td>${escape(r[2])}</td></tr>`).join('')}</tbody></table></div><p class="muted">USD pricing where shown. Plans, allowances and offers can change; check the linked official pages and checkout terms.</p></section>
<section><h2>What to test before paying</h2><p>${escape(p.test)}</p>${p.questions.map(([q,a])=>`<h3>${escape(q)}</h3><p>${escape(a)}</p>`).join('')}</section>
<section><h2>Check your preferred option</h2><nav class="ctas" aria-label="Product destinations">${ctas}</nav><p data-affiliate-disclosure="compare" class="muted">COSHUMA may earn a commission on qualifying purchases through partner links, at no extra cost to you. Official-source links below are provided separately.</p></section>
<section><h2>Sources and method</h2><p class="muted">This is an editorial comparison based on the official pages below, not a hands-on benchmark. Fit recommendations are our interpretation; no ranking, conversion or performance result is guaranteed.</p><ul>${p.sources.map(([label,url])=>`<li><a data-cta="source" href="${url}" target="_blank" rel="noopener noreferrer">${escape(label)}</a></li>`).join('')}</ul></section>
</main><footer class="muted">© 2026 COSHUMA · Independent AI & SaaS buyer guides</footer></body></html>`;
  fs.writeFileSync(path.join(root,'public/compare',`${p.slug}.html`),html+'\n');
}
console.log(`Built ${pages.length} source-backed search comparisons.`);

// Older hand-written comparisons can omit their own product profile links.
// Repair only those omissions; do not replace their researched content.
let linked = 0;
let schemaAdded = 0;
for (const filename of fs.readdirSync(path.join(root, 'public/compare'))) {
  if (!filename.endsWith('.html')) continue;
  const file = path.join(root, 'public/compare', filename);
  let html = fs.readFileSync(file, 'utf8');
  const ids = filename.slice(0, -5).split('-vs-');
  const pair = ids.map(id => tools.find(t => t.id === id));
  if (pair.length !== 2 || pair.some(t => !t)) continue;
  const missing = pair.filter(t => !html.includes(`href="/tool/${t.id}.html"`));
  if (missing.length) {
    html = html.replace('</main>', `<nav aria-label="Compared product profiles" class="my-6 p-5 text-sm">Product profiles: ${missing.map(t=>`<a class="underline" href="/tool/${t.id}.html">${escape(t.name)}</a>`).join(' · ')}</nav>\n</main>`);
    linked++;
  }
  if (!html.includes('application/ld+json')) {
    const schema = {'@context':'https://schema.org','@type':'WebPage',name:pair.map(t=>t.name).join(' vs '),url:`https://coshuma.com/compare/${filename}`};
    html = html.replace('</head>', `<script type="application/ld+json">${JSON.stringify(schema)}</script>\n</head>`);
    schemaAdded++;
  }
  fs.writeFileSync(file, html);
}
console.log(`Restored product links on ${linked} comparisons and WebPage metadata on ${schemaAdded}.`);
