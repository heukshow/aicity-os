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
  'program_inactive',
  'application_blocked_region',
  'application_blocked_vendor_site_paused',
  'blocked_partnerstack_marketplace_limited',
  'excluded_user_request',
  'vendor-paused',
  'vendor_paused',
]);

const noReapplyAffiliateStatuses = new Set([
  'application_submitted',
  'application_pending',
  'approved',
  'approved_account',
  'approved_tracking',
  'pending',
  'email_verification_pending',
  'email_confirmation_required',
  'email_confirmed_login_required',
  'outreach_sent',
  'enrollment_requested',
  'browser_required_otp',
  'browser_required_portal_access',
  'browser_required_application_form',
  ...terminalAffiliateStatuses,
]);

const browserRequiredAffiliateStatuses = new Set([
  'browser_required_otp',
  'browser_required_portal_access',
  'browser_required_application_form',
]);

const genericRevenueReady = (tool) =>
  tool.affiliate_verified === true &&
  tool.affiliate_status === 'approved_tracking' &&
  typeof tool.affiliate_url === 'string' &&
  /^https?:\/\//i.test(tool.affiliate_url);

const targetedRevenueReady = (tool) => {
  if (tool.affiliate_verified !== true) return false;
  const toolPage = path.join(root, 'public', 'tool', `${tool.id}.html`);
  if (!fs.existsSync(toolPage)) return false;
  const html = fs.readFileSync(toolPage, 'utf8');
  return /<a\b[^>]*data-cta=["']affiliate["'][^>]*href=["']https?:\/\/[^"']+["'][^>]*rel=["'][^"']*sponsored[^"']*["'][^>]*>/i.test(html) ||
    /<a\b[^>]*rel=["'][^"']*sponsored[^"']*["'][^>]*data-cta=["']affiliate["'][^>]*href=["']https?:\/\/[^"']+["'][^>]*>/i.test(html);
};

const affiliateCoverage = tools
  .map((tool) => {
    const status = tool.affiliate_status || 'unclassified';
    const terminal = terminalAffiliateStatuses.has(status);
    const genericReady = genericRevenueReady(tool);
    const targetedReady = targetedRevenueReady(tool);
    const ready = genericReady || targetedReady;
    const browserRequired = !ready && !terminal && browserRequiredAffiliateStatuses.has(status);
    const doNotReapply = ready || terminal || noReapplyAffiliateStatuses.has(status);
    const directActionableGap = !ready && !terminal && !browserRequired && !doNotReapply;
    const watchOnlyGap = !ready && !terminal && !browserRequired && doNotReapply;
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
      genericRevenueReady: genericReady,
      targetedRevenueReady: targetedReady,
      revenueReady: ready,
      terminal,
      doNotReapply,
      browserRequired,
      directActionableGap,
      watchOnlyGap,
      blocker,
    };
  })
  .sort((a, b) => Number(b.revenueReady) - Number(a.revenueReady) || a.name.localeCompare(b.name));

const coverageCounts = affiliateCoverage.reduce((acc, item) => {
  acc.revenueReady += Number(item.revenueReady);
  acc.genericRevenueReady += Number(item.genericRevenueReady);
  acc.targetedRevenueReady += Number(item.targetedRevenueReady && !item.genericRevenueReady);
  acc.terminal += Number(item.terminal);
  acc.openMonetizationGaps += Number(!item.revenueReady && !item.terminal);
  acc.directActionableGaps += Number(item.directActionableGap);
  acc.browserRequiredGaps += Number(item.browserRequired);
  acc.watchOnlyGaps += Number(item.watchOnlyGap);
  acc.doNotReapply += Number(item.doNotReapply);
  acc.unclassifiedAffiliateStatus += Number(item.affiliateStatus === 'unclassified');
  acc.exactAffiliateUrlMissing += Number(!item.revenueReady && !item.terminal && !item.hasAffiliateUrl);
  acc.officialUnverified += Number(!item.officialVerified);
  acc.pricingUnverified += Number(!item.pricingVerified);
  return acc;
}, {
  revenueReady: 0,
  genericRevenueReady: 0,
  targetedRevenueReady: 0,
  terminal: 0,
  openMonetizationGaps: 0,
  directActionableGaps: 0,
  browserRequiredGaps: 0,
  watchOnlyGaps: 0,
  doNotReapply: 0,
  unclassifiedAffiliateStatus: 0,
  exactAffiliateUrlMissing: 0,
  officialUnverified: 0,
  pricingUnverified: 0,
});

for (const item of affiliateCoverage) {
  if (noReapplyAffiliateStatuses.has(item.affiliateStatus) && item.directActionableGap) {
    throw new Error(`Duplicate-application guard failed for ${item.id}: ${item.affiliateStatus}`);
  }
}

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
    genericRevenueReadyAffiliates: coverageCounts.genericRevenueReady,
    targetedRevenueReadyAffiliates: coverageCounts.targetedRevenueReady,
    openMonetizationGaps: coverageCounts.openMonetizationGaps,
    directActionableGaps: coverageCounts.directActionableGaps,
    browserRequiredGaps: coverageCounts.browserRequiredGaps,
    watchOnlyGaps: coverageCounts.watchOnlyGaps,
    doNotReapply: coverageCounts.doNotReapply,
    toolPages: files('tool').length,
    comparePages: files('compare').length,
    sitemapUrls: (sitemap.match(/<loc>/g) || []).length,
  },
  revenueFocus: {
    policy: 'prioritize_direct_existing_gaps_without_reapplying_waiting_states',
    allowNewTools: coverageCounts.directActionableGaps === 0,
    reason: coverageCounts.directActionableGaps === 0
      ? 'No directly actionable existing affiliate gap remains; waiting and browser-only states are protected from duplicate enrollment.'
      : `${coverageCounts.directActionableGaps} existing tools still have directly actionable affiliate gaps; ${coverageCounts.watchOnlyGaps} are watch-only and ${coverageCounts.browserRequiredGaps} require browser work.`,
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
console.log(`Admin snapshot: ${tools.length} tools, ${coverageCounts.revenueReady} revenue-ready affiliates (${coverageCounts.targetedRevenueReady} targeted-only), ${coverageCounts.directActionableGaps} direct gaps, ${coverageCounts.watchOnlyGaps} watch-only, ${coverageCounts.browserRequiredGaps} browser-required`);
