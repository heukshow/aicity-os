import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tools = JSON.parse(fs.readFileSync(path.join(root, 'data/tools.json'), 'utf8'));
const toolMap = new Map(tools.map((t) => [t.id, t]));
const esc = (s) => String(s ?? '').replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const cleanHttps = (value) => {
  try {
    const u = new URL(value);
    return u.protocol === 'https:' ? u.toString() : null;
  } catch {
    return null;
  }
};
const approved = (t) => t?.affiliate_verified === true && t?.affiliate_status === 'approved_tracking' && cleanHttps(t.affiliate_url);
const publicSource = (t) => cleanHttps(t.pricing_source_url) || cleanHttps(t.official_evidence_url) || cleanHttps(t.official_url);
const features = (t) => Array.isArray(t.key_features) ? t.key_features.filter(Boolean) : [];
const category = (t) => t.category_display || 'AI & SaaS software';

const preferred = [
  'gohighlevel','make-com','elevenlabs','tubebuddy','outlierkit','pictory','fliki','sudowrite',
  'bolddesk','brand24','boldsign','omi-ai','chatbase','gamma','kittl','synthesia','castmagic',
  'murf-ai','unbounce','moosend','bookyourdata','taskip','novita-ai','aiassistworks'
];
const selected = [];
for (const id of preferred) {
  const t = toolMap.get(id);
  if (approved(t) && cleanHttps(t.official_url) && publicSource(t)) selected.push(t);
  if (selected.length === 15) break;
}
if (selected.length < 15) {
  for (const t of tools.filter(approved).sort((a,b) => (a.name || '').localeCompare(b.name || ''))) {
    if (selected.some((x) => x.id === t.id) || !cleanHttps(t.official_url) || !publicSource(t)) continue;
    selected.push(t);
    if (selected.length === 15) break;
  }
}
if (selected.length < 15) throw new Error(`Need 15 safe approved tools, found ${selected.length}`);

const bespoke = new Map([
  ['omi-ai', {
    best:['People who want searchable conversation notes','Teams reviewing spoken tasks and follow-ups'],
    not:['Workplaces that prohibit recording','Buyers who need verified hands-on accuracy benchmarks'],
    why:['Search memories instead of replaying entire conversations','Review generated tasks before acting','Share summaries for a clearer handoff'],
    pricing:'Check current pricing.', freePlan:'A free Basic plan is available; check current limits.',
    trial:'Not confirmed; check current pricing and trial terms.',
    risk:'Review recording permissions and your workplace policy first.', source:'https://www.omi.me/pages/product'
  }],
  ['chatbase', {
    best:['Teams testing AI customer support','Buyers who can estimate message-credit usage'],
    not:['A simple static FAQ is enough','Untested answers would create unacceptable risk'],
    why:['Test customer questions before scaling','Match channels to the right plan','Review credit usage before upgrading'],
    pricing:'Paid plans start at $40/month on monthly billing; see the detailed table below.', freePlan:'$0 plan with 50 message credits per month.',
    trial:'7-day trials listed for Hobby, Standard and Pro; confirm checkout terms.',
    risk:'Free-plan agents are deleted after 14 inactive days. Add-ons can increase total cost.', source:'https://www.chatbase.co/pricing'
  }]
]);

const sameGroupAlternatives = (t) => {
  const group = t.comparison_group || t.category;
  const matches = tools.filter((x) => x.id !== t.id && (x.comparison_group || x.category) === group);
  return matches.slice(0, 2).map((x) => [x.id, x.name]);
};
const list = (items) => '<ul class="list-disc pl-5 space-y-1">' + items.map((x) => `<li>${esc(x)}</li>`).join('') + '</ul>';

for (const t of selected) {
  const source = publicSource(t);
  const f = features(t);
  const alt = sameGroupAlternatives(t);
  const custom = bespoke.get(t.id);
  const cfg = custom || {
    best: [
      `Buyers comparing ${category(t)}`,
      f[0] ? `Teams that need ${f[0]}` : `Teams that need the core ${category(t)} workflow`
    ],
    not: [
      `Teams whose main need falls outside ${category(t)}`,
      'Buyers who need a guaranteed price or feature limit without checking the current vendor terms'
    ],
    why: [
      ...(f.slice(0, 2).length ? f.slice(0, 2) : [`Evaluate its ${category(t)} workflow against your current process`]),
      'Compare the official source and relevant alternatives before checkout'
    ],
    pricing: t.pricing || 'Check current vendor pricing.',
    freePlan: String(t.pricing || '').toLowerCase().includes('free') ? 'A free option is indicated in the current catalog snapshot; verify current limits.' : 'No free-plan claim is made here; check the current vendor pricing page.',
    trial: String(t.pricing || '').toLowerCase().includes('trial') ? 'A trial is indicated in the current catalog snapshot; verify current terms.' : 'Trial availability is not assumed; check the current vendor page.',
    risk: 'Features, limits and prices can change. Verify the final plan and checkout terms on the vendor site.',
    source
  };
  const p = path.join(root, 'public/tool', `${t.id}.html`);
  if (!fs.existsSync(p)) throw new Error(`Missing tool page: ${t.id}`);
  let html = fs.readFileSync(p, 'utf8');
  const pricingLabel = custom ? cfg.pricing : `Current catalog snapshot: ${cfg.pricing}`;
  const strongestAlt = alt[0] ? `<a class="underline" href="/tool/${alt[0][0]}.html">${esc(alt[0][1])}</a>` : 'See related tools in this category';
  const alternatives = alt.length ? alt.map(([id,name]) => `<a data-cta-source="buyer-box-alternative" class="underline" href="/tool/${id}.html">${esc(name)}</a>`).join(' · ') : 'Browse the directory for alternatives';
  const box = `<!-- buyer-box:start -->
<section data-buyer-decision-box="${t.id}" class="rounded-2xl border border-purple-400/40 bg-slate-900 p-6 my-6 space-y-4" aria-label="Buyer decision box">
<h2 class="text-2xl font-bold">Is ${esc(t.name)} right for you?</h2>
<div class="grid md:grid-cols-2 gap-5"><div><h3 class="font-bold">Best for</h3>${list(cfg.best)}</div><div><h3 class="font-bold">Skip if</h3>${list(cfg.not)}</div></div>
<h3 class="font-bold">Why consider it?</h3>${list(cfg.why)}
<div class="grid md:grid-cols-2 gap-4"><div><h3 class="font-bold">Starting price / free option</h3><p>${esc(pricingLabel)}</p></div><div><h3 class="font-bold">Strongest nearby alternative</h3><p>${strongestAlt}</p></div></div>
<dl><dt class="font-bold">Free plan</dt><dd>${esc(cfg.freePlan)}</dd><dt class="font-bold">Free trial</dt><dd>${esc(cfg.trial)}</dd></dl>
<p>${esc(cfg.risk)}</p>
<p class="text-sm text-slate-400">Official/public source: <a data-cta-source="buyer-box-source" href="${esc(cfg.source)}" target="_blank" rel="noopener noreferrer" class="underline">check current product or pricing details</a>. Editorial fit guidance, not a hands-on performance test.</p>
<p data-affiliate-disclosure="buyer-box" class="text-sm text-slate-300">COSHUMA may earn a commission on qualifying purchases through this partner link, at no extra cost to you.</p>
<div class="flex flex-wrap gap-3"><a data-cta="affiliate" data-cta-source="buyer-box-primary" data-tool-id="${t.id}" href="${esc(t.affiliate_url)}" target="_blank" rel="sponsored noopener noreferrer" class="rounded-xl bg-purple-600 px-5 py-3 font-bold">Explore ${esc(t.name)} →</a><a data-cta="official" data-cta-source="buyer-box-official" href="${esc(t.official_url)}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-slate-500 px-5 py-3">Official website</a></div>
<p>Compare alternatives: ${alternatives}</p>
</section>
<!-- buyer-box:end -->`;
  html = html.includes('<!-- buyer-box:start -->') ? html.replace(/<!-- buyer-box:start -->[\s\S]*?<!-- buyer-box:end -->/, box) : html.replace('<!-- Description -->', box + '\n<!-- Description -->');
  if (!html.includes(`data-buyer-decision-box="${t.id}"`)) throw new Error(`Buyer box insertion failed: ${t.id}`);
  if (!html.includes('/affiliate-attribution.js')) html = html.replace('</head>', '<script defer src="/affiliate-attribution.js"></script>\n</head>');
  html = html.replace(/<a\b(?=[^>]*data-cta=)(?![^>]*data-cta-source=)/g, '<a data-cta-source="tool-existing"');
  fs.writeFileSync(p, html);
}

// Add a decision-oriented "winner by use case" block to 10 strong comparison pages.
const compareDir = path.join(root, 'public/compare');
const compareCandidates = fs.existsSync(compareDir) ? fs.readdirSync(compareDir).filter((f) => f.endsWith('.html')).map((file) => {
  const stem = file.slice(0, -5);
  const parts = stem.split('-vs-');
  if (parts.length !== 2) return null;
  const a = toolMap.get(parts[0]);
  const b = toolMap.get(parts[1]);
  if (!a || !b) return null;
  const approvedCount = Number(approved(a)) + Number(approved(b));
  const preferredCount = Number(preferred.includes(a.id)) + Number(preferred.includes(b.id));
  return {file, a, b, score: approvedCount * 10 + preferredCount * 3};
}).filter(Boolean).filter((x) => x.score > 0).sort((x,y) => y.score - x.score || x.file.localeCompare(y.file)).slice(0, 10) : [];

if (compareCandidates.length < 10) throw new Error(`Need 10 comparison pages for use-case tables, found ${compareCandidates.length}`);
for (const {file, a, b} of compareCandidates) {
  const p = path.join(compareDir, file);
  let html = fs.readFileSync(p, 'utf8');
  const af = features(a)[0] || category(a);
  const bf = features(b)[0] || category(b);
  const rows = [
    [`If you prioritize ${af}`, a.name, `Choose ${a.name} when this capability is the deciding requirement.`],
    [`If you prioritize ${bf}`, b.name, `Choose ${b.name} when this capability is the deciding requirement.`]
  ];
  const aFree = String(a.pricing || '').toLowerCase().includes('free');
  const bFree = String(b.pricing || '').toLowerCase().includes('free');
  if (aFree !== bFree) {
    const winner = aFree ? a : b;
    rows.push(['If a cataloged free option matters', winner.name, `${winner.name} currently has a free option indicated in COSHUMA's catalog snapshot; verify vendor limits.`]);
  }
  const rowHtml = rows.map(([use,winner,why]) => `<tr class="border-t border-slate-700"><td class="p-3">${esc(use)}</td><td class="p-3 font-bold">${esc(winner)}</td><td class="p-3">${esc(why)}</td></tr>`).join('');
  const table = `<!-- winner-table:start --><section data-winner-by-use-case class="my-8 rounded-2xl border border-purple-400/30 bg-slate-900 p-6"><h2 class="text-2xl font-bold">Winner by use case</h2><p class="mt-2 text-sm text-slate-400">Use the requirement that matters most to you. Pricing and feature limits can change, so verify vendor terms before purchase.</p><div class="overflow-x-auto mt-4"><table class="w-full text-left text-sm"><thead><tr><th class="p-3">Use case</th><th class="p-3">Better fit</th><th class="p-3">Why</th></tr></thead><tbody>${rowHtml}</tbody></table></div><p class="mt-4 text-sm">Read the full guides: <a class="underline" href="/tool/${a.id}.html">${esc(a.name)}</a> · <a class="underline" href="/tool/${b.id}.html">${esc(b.name)}</a></p></section><!-- winner-table:end -->`;
  html = html.includes('<!-- winner-table:start -->') ? html.replace(/<!-- winner-table:start -->[\s\S]*?<!-- winner-table:end -->/, table) : html.replace('</main>', table + '\n</main>');
  if (!html.includes('data-winner-by-use-case')) throw new Error(`Winner table insertion failed: ${file}`);
  fs.writeFileSync(p, html);
}

console.log(`inject_buyer_decision_boxes: tool_boxes=${selected.length} comparison_winner_tables=${compareCandidates.length}`);
