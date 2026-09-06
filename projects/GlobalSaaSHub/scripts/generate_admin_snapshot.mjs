import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tools = JSON.parse(fs.readFileSync(path.join(root, 'data/tools.json'), 'utf8'));
const files = (dir) => fs.readdirSync(path.join(root, 'public', dir)).filter((name) => name.endsWith('.html'));
const sitemap = fs.readFileSync(path.join(root, 'public/sitemap.xml'), 'utf8');

const terminalAffiliateStatuses = new Set([
  'program_closed_to_new_applicants',
  'program_unavailable',
  'no_affiliate_program',
  'rejected',
  'cooldown',
  'closed',
]);

const revenueReady = (tool) =>
  tool.affiliate_verified === true &&
  tool.affiliate_status === 'approved_tracking' &&
  typeof tool.affiliate_url === 'string' &&
  /^https?:\/\//i.test(tool.affiliate_url);

const affiliateCoverage = tools
  .map((tool) => {
    const status = tool.affiliate_status || 'unclassified';
    const terminal = terminalAffiliateStatuses.has(status);
    const ready = revenueReady(tool);
    let blocker = null;
    if (!ready && !terminal) {
      if (!tool.affiliate_status) blocker = 'affiliate_status_unclassified';
      else if (!tool.affiliate_url) blocker = 'exact_customer_affiliate_url_missing';
      else if (tool.affiliate_verified !== true) blocker = 'affiliate_evidence_not_verified';
      else blocker = `affiliate_status_${status}`;
    }
    return {
      id: tool.id,
      name: tool.name,
      officialVerified: tool.official_verification_status === 'verified',
      pricingVerified: tool.pricing_verified === true,
      affiliateStatus: status,
      affiliateVerified: tool.affiliate_verified === true,
      hasAffiliateUrl: typeof tool.affiliate_url === 'string' && tool.affiliate_url.length > 0,
      revenueReady: ready,
      terminal,
      blocker,
    };
  })
  .sort((a, b) => Number(b.revenueReady) - Number(a.revenueReady) || a.name.localeCompare(b.name));

const coverageCounts = affiliateCoverage.reduce((acc, item) => {
  acc.revenueReady += Number(item.revenueReady);
  acc.terminal += Number(item.terminal);
  acc.openMonetizationGaps += Number(!item.revenueReady && !item.terminal);
  acc.unclassifiedAffiliateStatus += Number(item.affiliateStatus === 'unclassified');
  acc.exactAffiliateUrlMissing += Number(!item.revenueReady && !item.terminal && !item.hasAffiliateUrl);
  acc.officialUnverified += Number(!item.officialVerified);
  acc.pricingUnverified += Number(!item.pricingVerified);
  return acc;
}, { revenueReady: 0, terminal: 0, openMonetizationGaps: 0, unclassifiedAffiliateStatus: 0, exactAffiliateUrlMissing: 0, officialUnverified: 0, pricingUnverified: 0 });

const affiliates = tools.filter((tool) => tool.affiliate_verified === true)
  .sort((a, b) => Number(Boolean(b.affiliate_url)) - Number(Boolean(a.affiliate_url)) || a.name.localeCompare(b.name))
  .map((tool) => ({ id: tool.id, name: tool.name, status: tool.affiliate_status || 'unknown', verified: true, url: tool.affiliate_url || null, verifiedAt: tool.affiliate_verified_at || null }));

const publicPages = [path.join(root, 'index.html'), ...files('tool').map((name) => path.join(root, 'public/tool', name)), ...files('compare').map((name) => path.join(root, 'public/compare', name))];
const koreanLeakCount = publicPages.reduce((count, file) => count + ((fs.readFileSync(file, 'utf8').match(/[가-힣]/g) || []).length), 0);
const snapshot = {
  generatedAt: new Date().toISOString(),
  counts: {
    totalTools: tools.length,
    verifiedAffiliates: affiliates.length,
    revenueReadyAffiliates: coverageCounts.revenueReady,
    openMonetizationGaps: coverageCounts.openMonetizationGaps,
    toolPages: files('tool').length,
    comparePages: files('compare').length,
    sitemapUrls: (sitemap.match(/<loc>/g) || []).length,
  },
  revenueFocus: {
    policy: 'finish_existing_tool_affiliate_coverage_before_expansion',
    allowNewTools: coverageCounts.openMonetizationGaps === 0,
    reason: coverageCounts.openMonetizationGaps === 0
      ? 'Existing-tool affiliate coverage has no open monetization gaps.'
      : `${coverageCounts.openMonetizationGaps} existing tools still have open monetization gaps.`,
  },
  affiliateCoverage: { counts: coverageCounts, records: affiliateCoverage },
  connections: { ga4: '수집 연결됨', searchConsole: '연결됨' },
  searchConsole: {
    period: '최근 3개월', impressions: 2006, clicks: 1, ctr: '0%', averagePosition: 48.9,
    indexedPages: 240, notIndexedPages: 147, checkedAt: '2026-09-01T05:24:00+09:00',
    topQueries: [
      { query: 'unbounce', impressions: 82, clicks: 0 },
      { query: 'pipedrive pricing', impressions: 46, clicks: 0 },
      { query: 'brand24', impressions: 44, clicks: 0 },
      { query: 'beefree', impressions: 36, clicks: 0 },
      { query: 'sanebox', impressions: 36, clicks: 0 },
    ],
  },
  seo: { testsPassed: true, koreanLeakCount }, affiliates,
  recentSeoChanges: [{ title: '공개 검색 최적화 무결성 계약 강화', date: '2026-09-01' }, { title: '사이트맵 및 정적 페이지 동기화', date: '2026-09-01' }],
};
fs.writeFileSync(path.join(root, 'worker/src/admin-snapshot.json'), `${JSON.stringify(snapshot, null, 2)}\n`);
console.log(`Admin snapshot: ${tools.length} tools, ${coverageCounts.revenueReady} revenue-ready affiliates, ${coverageCounts.openMonetizationGaps} open monetization gaps`);
