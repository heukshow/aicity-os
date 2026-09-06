import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tools = JSON.parse(fs.readFileSync(path.join(root, 'data/tools.json'), 'utf8'));

const terminalStatuses = new Set([
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
]);

const hasVerifiedTargetedAffiliateCta = (tool) => {
  if (tool.affiliate_verified !== true) return false;
  const toolPage = path.join(root, 'public', 'tool', `${tool.id}.html`);
  if (!fs.existsSync(toolPage)) return false;
  const html = fs.readFileSync(toolPage, 'utf8');
  return /<a\b[^>]*data-cta=["']affiliate["'][^>]*href=["']https?:\/\/[^"']+["'][^>]*rel=["'][^"']*sponsored[^"']*["'][^>]*>/i.test(html) ||
    /<a\b[^>]*rel=["'][^"']*sponsored[^"']*["'][^>]*data-cta=["']affiliate["'][^>]*href=["']https?:\/\/[^"']+["'][^>]*>/i.test(html);
};

const records = tools.map((tool) => {
  const status = tool.affiliate_status || 'unclassified';
  const hasAffiliateUrl = typeof tool.affiliate_url === 'string' && /^https?:\/\//i.test(tool.affiliate_url);
  const genericRevenueReady = tool.affiliate_verified === true && status === 'approved_tracking' && hasAffiliateUrl;
  const targetedRevenueReady = !genericRevenueReady && hasVerifiedTargetedAffiliateCta(tool);
  const revenueReady = genericRevenueReady || targetedRevenueReady;
  const terminal = terminalStatuses.has(status);
  let blocker = null;
  if (!revenueReady && !terminal) {
    if (status === 'unclassified') blocker = 'affiliate_status_unclassified';
    else if (!hasAffiliateUrl) blocker = 'exact_customer_affiliate_url_missing';
    else if (tool.affiliate_verified !== true) blocker = 'affiliate_evidence_not_verified';
    else blocker = `affiliate_status_${status}`;
  }
  return {
    id: tool.id,
    name: tool.name,
    affiliateStatus: status,
    affiliateVerified: tool.affiliate_verified === true,
    hasAffiliateUrl,
    genericRevenueReady,
    targetedRevenueReady,
    revenueReady,
    terminal,
    blocker,
    officialVerified: tool.official_verification_status === 'verified',
    pricingVerified: tool.pricing_verified === true,
    payoutSetupStatus: tool.payout_setup_status || null,
  };
});

const counts = records.reduce((acc, item) => {
  acc.totalTools += 1;
  acc.revenueReady += Number(item.revenueReady);
  acc.genericRevenueReady += Number(item.genericRevenueReady);
  acc.targetedRevenueReady += Number(item.targetedRevenueReady);
  acc.terminal += Number(item.terminal);
  acc.openMonetizationGaps += Number(!item.revenueReady && !item.terminal);
  acc.exactAffiliateUrlMissing += Number(!item.revenueReady && !item.terminal && !item.hasAffiliateUrl);
  acc.unclassifiedAffiliateStatus += Number(item.affiliateStatus === 'unclassified');
  acc.officialUnverified += Number(!item.officialVerified);
  acc.pricingUnverified += Number(!item.pricingVerified);
  acc.payoutNeedsReview += Number(item.revenueReady && item.payoutSetupStatus && item.payoutSetupStatus !== 'complete');
  return acc;
}, {
  totalTools: 0,
  revenueReady: 0,
  genericRevenueReady: 0,
  targetedRevenueReady: 0,
  terminal: 0,
  openMonetizationGaps: 0,
  exactAffiliateUrlMissing: 0,
  unclassifiedAffiliateStatus: 0,
  officialUnverified: 0,
  pricingUnverified: 0,
  payoutNeedsReview: 0,
});

const output = {
  generatedAt: new Date().toISOString(),
  policy: 'finish_existing_tool_affiliate_coverage_before_expansion',
  allowNewTools: counts.openMonetizationGaps === 0,
  counts,
  openGaps: records.filter((item) => !item.revenueReady && !item.terminal),
  revenueReady: records.filter((item) => item.revenueReady),
  terminal: records.filter((item) => item.terminal),
};

fs.writeFileSync(path.join(root, 'public/admin-affiliate-audit.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify(counts));
