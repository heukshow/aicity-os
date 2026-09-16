import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const publicDir = path.join(project, 'public');
const comparePath = path.join(publicDir, 'compare', 'unbounce-vs-landingi.html');
const compareHubPath = path.join(publicDir, 'compare', 'index.html');
const sitemapPath = path.join(publicDir, 'sitemap.xml');
const unbouncePath = path.join(publicDir, 'tool', 'unbounce.html');
const landingiPath = path.join(publicDir, 'tool', 'landingi.html');
const llmsPath = path.join(publicDir, 'llms.txt');
const compareUrl = 'https://coshuma.com/compare/unbounce-vs-landingi.html';

if (!fs.existsSync(comparePath)) {
  throw new Error(`Buyer-intent comparison is missing: ${comparePath}`);
}

function writeIfChanged(file, next) {
  const current = fs.readFileSync(file, 'utf8');
  if (current !== next) fs.writeFileSync(file, next, 'utf8');
}

function ensureCompareHub() {
  if (!fs.existsSync(compareHubPath)) throw new Error('Comparison hub is missing');
  let html = fs.readFileSync(compareHubPath, 'utf8');

  if (!html.includes(compareUrl)) {
    const itemPattern = /(\{"@type":"ListItem","position":11,"url":"https:\/\/coshuma\.com\/compare\/convertflow-vs-unbounce\.html","name":"ConvertFlow vs Unbounce"\})/;
    if (!itemPattern.test(html)) throw new Error('Comparison hub ItemList anchor changed');
    html = html.replace(itemPattern, '$1,\n        {"@type":"ListItem","position":12,"url":"https://coshuma.com/compare/unbounce-vs-landingi.html","name":"Unbounce vs Landingi"}');
  }

  if (!html.includes('href="/compare/unbounce-vs-landingi.html"')) {
    const gridStart = html.indexOf('<section class="mt-10 grid gap-4 md:grid-cols-2">');
    if (gridStart < 0) throw new Error('Comparison hub card grid changed');
    const gridEnd = html.indexOf('</section>', gridStart);
    if (gridEnd < 0) throw new Error('Comparison hub card grid closing tag missing');
    const card = `      <a href="/compare/unbounce-vs-landingi.html" class="rounded-2xl border border-purple-500/25 bg-purple-500/5 p-6 hover:border-purple-400/60"><div class="text-xs font-black uppercase tracking-wider text-purple-300">Landing pages & CRO</div><h2 class="mt-2 text-2xl font-black text-white">Unbounce vs Landingi</h2><p class="mt-2 text-sm leading-6 text-slate-300">Entry pricing, 14-day trials, traffic limits, A/B testing and agency fit—plus COSHUMA's verified Unbounce partner offer.</p></a>\n`;
    html = html.slice(0, gridEnd) + card + html.slice(gridEnd);
  }
  writeIfChanged(compareHubPath, html);
}

function ensureSitemap() {
  if (!fs.existsSync(sitemapPath)) throw new Error('Sitemap is missing');
  let xml = fs.readFileSync(sitemapPath, 'utf8');
  if (xml.includes(`<loc>${compareUrl}</loc>`)) return;
  if (!xml.includes('</urlset>')) throw new Error('Sitemap closing tag missing');
  const entry = `  <url>\n    <loc>${compareUrl}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n`;
  xml = xml.replace('</urlset>', `${entry}</urlset>`);
  writeIfChanged(sitemapPath, xml);
}

function ensureToolCrosslink(file, tool) {
  if (!fs.existsSync(file)) throw new Error(`${tool} tool page is missing`);
  let html = fs.readFileSync(file, 'utf8');
  if (html.includes('/compare/unbounce-vs-landingi.html')) return;
  if (!html.includes('</main>')) throw new Error(`${tool} page main closing tag missing`);
  const title = tool === 'Unbounce' ? 'Compare Unbounce with a direct landing-page alternative' : 'Compare Landingi with a direct CRO alternative';
  const copy = tool === 'Unbounce'
    ? 'Landingi competes more directly on landing-page creation, testing and agency-scale workflows. Compare page limits, traffic allowances and experiment tiers before committing.'
    : 'Unbounce competes directly on landing-page creation and conversion optimization. Compare entry limits, testing tiers and COSHUMA’s verified Unbounce partner offer before choosing.';
  const block = `\n<section data-buyer-intent-crosslink="unbounce-landingi" class="rounded-3xl border border-purple-500/20 bg-purple-500/5 p-6 md:p-7">\n  <div class="text-xs font-bold uppercase tracking-wider text-purple-300">Direct competitor comparison</div>\n  <h2 class="mt-2 text-2xl font-black text-white">${title}</h2>\n  <p class="mt-3 text-sm leading-6 text-slate-300">${copy}</p>\n  <a href="/compare/unbounce-vs-landingi.html" class="mt-5 inline-flex rounded-xl border border-purple-400/30 bg-purple-500/10 px-5 py-3 text-sm font-extrabold text-purple-100 hover:bg-purple-500/20">Unbounce vs Landingi buyer guide →</a>\n</section>\n`;
  html = html.replace('</main>', `${block}</main>`);
  writeIfChanged(file, html);
}

function ensureLlmsDiscovery() {
  if (!fs.existsSync(llmsPath)) return;
  let text = fs.readFileSync(llmsPath, 'utf8');
  if (text.includes(compareUrl)) return;
  text = `${text.trimEnd()}\n\n## Landing-page buyer comparisons\n\n- ${compareUrl} — Unbounce vs Landingi pricing, trials, A/B testing, traffic limits and agency-fit comparison\n`;
  writeIfChanged(llmsPath, text);
}

ensureCompareHub();
ensureSitemap();
ensureToolCrosslink(unbouncePath, 'Unbounce');
ensureToolCrosslink(landingiPath, 'Landingi');
ensureLlmsDiscovery();

console.log('Unbounce vs Landingi buyer-intent discovery: ensured');
