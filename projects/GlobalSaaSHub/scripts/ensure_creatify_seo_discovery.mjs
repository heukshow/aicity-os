import fs from 'node:fs';

const urls = [
  'https://coshuma.com/tool/creatify.html',
  'https://coshuma.com/best/creatify-free-plan-pricing.html',
];

const sitemapPath = 'public/sitemap.xml';
let sitemap = fs.readFileSync(sitemapPath, 'utf8');
for (const url of urls) {
  if (!sitemap.includes(`<loc>${url}</loc>`)) {
    sitemap = sitemap.replace(
      '</urlset>',
      `  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n</urlset>`,
    );
  }
}
fs.writeFileSync(sitemapPath, sitemap);

const llmsPath = 'public/llms.txt';
let llms = fs.readFileSync(llmsPath, 'utf8');
if (!llms.includes('https://coshuma.com/tool/creatify.html')) {
  llms += '\n## Creatify buyer guides\n\n- https://coshuma.com/tool/creatify.html — Creatify AI ad-creative product guide\n- https://coshuma.com/best/creatify-free-plan-pricing.html — Creatify free-plan and upgrade decision guide\n- https://coshuma.com/compare/tagshop-ai-vs-creatify.html — Tagshop AI vs Creatify AI UGC-ad comparison\n';
}
fs.writeFileSync(llmsPath, llms);

const hubBlock = `\n<section data-creatify-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-purple-500/25 bg-purple-500/5 p-5"><div class="text-xs uppercase tracking-widest text-purple-300 font-bold">AI ad creative</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-purple-300" href="/best/creatify-free-plan-pricing.html">Creatify free plan & pricing</a> · <a class="font-bold text-white hover:text-purple-300" href="/tool/creatify.html">Creatify buyer guide</a> · <a class="font-bold text-white hover:text-purple-300" href="/compare/tagshop-ai-vs-creatify.html">Tagshop AI vs Creatify</a></p></div></section>\n`;
for (const file of ['public/best/index.html', 'index.html']) {
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('data-creatify-fastlane="2026-09-14"')) {
    html = html.includes('</main>')
      ? html.replace('</main>', `${hubBlock}</main>`)
      : html.replace('</body>', `${hubBlock}</body>`);
    fs.writeFileSync(file, html);
  }
}

const comparePath = 'public/compare/tagshop-ai-vs-creatify.html';
if (fs.existsSync(comparePath)) {
  let html = fs.readFileSync(comparePath, 'utf8');
  if (!html.includes('data-creatify-buyer-links="2026-09-14"')) {
    const links = `<section data-creatify-buyer-links="2026-09-14" class="mx-auto mt-8 max-w-5xl rounded-2xl border border-violet-500/25 bg-violet-500/5 p-6"><h2 class="text-xl font-black text-white">Need the Creatify details first?</h2><p class="mt-2 text-sm text-slate-300">Check Creatify's current free-plan limits and independent product guide before choosing between ad-creative workflows.</p><div class="mt-4 flex flex-col gap-2 sm:flex-row"><a href="/tool/creatify.html" class="rounded-xl bg-violet-600 px-5 py-3 text-center text-sm font-black text-white">Creatify buyer guide →</a><a href="/best/creatify-free-plan-pricing.html" class="rounded-xl border border-white/10 px-5 py-3 text-center text-sm font-black text-white">Creatify free-plan guide →</a></div></section>`;
    html = html.includes('</main>')
      ? html.replace('</main>', `${links}</main>`)
      : html.replace('</body>', `${links}</body>`);
    fs.writeFileSync(comparePath, html);
  }
}

console.log('Creatify SEO sitemap and internal-discovery paths ensured');
