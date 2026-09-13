import fs from 'node:fs';

const hubPath = 'public/compare/index.html';
const hubUrl = 'https://coshuma.com/compare/';
if (!fs.existsSync(hubPath)) {
  throw new Error(`Comparison hub is missing: ${hubPath}`);
}

const sitemapPath = 'public/sitemap.xml';
let sitemap = fs.readFileSync(sitemapPath, 'utf8');
if (!sitemap.includes(`<loc>${hubUrl}</loc>`)) {
  sitemap = sitemap.replace(
    '</urlset>',
    `  <url>\n    <loc>${hubUrl}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n</urlset>`,
  );
  fs.writeFileSync(sitemapPath, sitemap);
}

console.log('Comparison hub sitemap entry ensured');
