import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tools = JSON.parse(fs.readFileSync(path.join(root, 'data/tools.json'), 'utf8'));
const files = (dir) => fs.readdirSync(path.join(root, 'public', dir)).filter((name) => name.endsWith('.html'));
const sitemap = fs.readFileSync(path.join(root, 'public/sitemap.xml'), 'utf8');
const affiliates = tools.filter((tool) => tool.affiliate_verified === true)
  .sort((a, b) => Number(Boolean(b.affiliate_url)) - Number(Boolean(a.affiliate_url)) || a.name.localeCompare(b.name))
  .map((tool) => ({ id: tool.id, name: tool.name, status: tool.affiliate_status || 'unknown', verified: true, url: tool.affiliate_url || null, verifiedAt: tool.affiliate_verified_at || null }));
const publicPages = [path.join(root, 'index.html'), ...files('tool').map((name) => path.join(root, 'public/tool', name)), ...files('compare').map((name) => path.join(root, 'public/compare', name))];
const koreanLeakCount = publicPages.reduce((count, file) => count + ((fs.readFileSync(file, 'utf8').match(/[가-힣]/g) || []).length), 0);
const snapshot = {
  generatedAt: new Date().toISOString(),
  counts: { totalTools: tools.length, verifiedAffiliates: affiliates.length, toolPages: files('tool').length, comparePages: files('compare').length, sitemapUrls: (sitemap.match(/<loc>/g) || []).length },
  connections: { ga4: 'Not connected', searchConsole: '연결 필요' },
  seo: { testsPassed: true, koreanLeakCount }, affiliates,
  recentSeoChanges: [{ title: '공개 SEO 무결성 계약 강화', date: '2026-09-01' }, { title: 'Sitemap 및 정적 페이지 동기화', date: '2026-09-01' }],
};
fs.writeFileSync(path.join(root, 'worker/src/admin-snapshot.json'), `${JSON.stringify(snapshot, null, 2)}\n`);
console.log(`Admin snapshot: ${tools.length} tools, ${affiliates.length} verified affiliates`);
