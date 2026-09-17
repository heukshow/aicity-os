import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = rel => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));

const tools = read('data/tools.json');
const inventory = read('worker/src/revenue-inventory.json');
const accountEvidence = [
  read('data/partnerstack-account-revenue-2026-09-11.json'),
];

const APPROVED = new Set(['approved_tracking', 'approved', 'approved_account']);
const approvedTools = tools.filter(t =>
  t.affiliate_verified === true &&
  typeof t.affiliate_url === 'string' && t.affiliate_url.trim() &&
  APPROVED.has(t.affiliate_status)
);

const inventoryById = new Map((inventory.programs || []).map(p => [p.id, p]));
const accountEvidenceById = new Map(accountEvidence.map(e => [e.account_id, e]));
const now = Date.now();
const ageDays = timestamp => timestamp ? Math.floor((now - Date.parse(timestamp)) / 86400000) : null;
const downstream = evidence => {
  const metrics = evidence?.metrics || {};
  return [
    'signups_referrals','trials','paid_customers','gross_sales_revenue',
    'commission_earned','commission_approved','commission_pending','payout_paid','payout_pending',
    'network_reported_conversions'
  ].some(k => metrics[k] !== null && metrics[k] !== undefined);
};
const completeAccountRevenueCoverage = evidence => Boolean(
  evidence &&
  evidence.coverage?.rewards_complete === true &&
  evidence.coverage?.payouts_connected === true &&
  evidence.coverage?.payouts_complete === true &&
  evidence.reward_count === 0 &&
  evidence.commission_total === 0 &&
  evidence.commission_pending === 0 &&
  evidence.commission_paid === 0 &&
  evidence.payout_available === 0 &&
  evidence.payout_withdrawn === 0
);

const rows = approvedTools.map(tool => {
  const inv = inventoryById.get(tool.id) || null;
  const records = (inv?.evidence || []).slice().sort((a,b) => Date.parse(b.checked_at) - Date.parse(a.checked_at));
  const latest = records[0] || null;
  const account = inv?.account_id ? accountEvidenceById.get(inv.account_id) || null : null;
  const accountDays = account ? ageDays(account.checked_at) : null;
  const accountCovered = completeAccountRevenueCoverage(account) && accountDays !== null && accountDays <= 7;
  const days = latest ? ageDays(latest.checked_at) : null;
  let priority;
  let reason;
  let coverageType = 'tool';
  if (accountCovered) {
    priority = 'P2_COVERED';
    coverageType = 'account_revenue';
    reason = 'Recent authenticated account-wide evidence proves complete commission/payout coverage with zero rewards and zero commission/payout in this network snapshot; per-program signup/trial/customer counts remain unknown.';
  } else if (!latest) {
    priority = 'P0_UNCHECKED';
    reason = 'Approved tracked affiliate route has no dashboard/email/API revenue evidence in the combined baseline + current truth inventory.';
  } else if (days !== null && days > 7) {
    priority = 'P1_STALE';
    reason = `Latest revenue evidence is ${days} days old.`;
  } else if (!downstream(latest)) {
    priority = 'P1_PARTIAL';
    reason = 'Recent evidence exists but downstream signup/trial/customer/commission/payout metrics are all unknown.';
  } else {
    priority = 'P2_COVERED';
    reason = 'Recent evidence-backed downstream revenue state exists.';
  }
  const selectedTimestamp = accountCovered ? account.checked_at : (latest?.checked_at || null);
  const selectedAge = accountCovered ? accountDays : days;
  return {
    id: tool.id,
    name: tool.name,
    affiliate_status: tool.affiliate_status,
    tracking_url: tool.affiliate_url,
    network: inv?.network || latest?.network || account?.network || null,
    account_id: inv?.account_id || null,
    portal_url: inv?.portal_url || null,
    priority,
    reason,
    coverage_type: coverageType,
    latest_evidence_at: selectedTimestamp,
    evidence_age_days: selectedAge,
    evidence_source: accountCovered ? account.evidence_source : (latest?.source || null),
    evidence_id: accountCovered ? account.evidence_id : (latest?.evidence_id || null),
    latest_metrics: accountCovered ? {
      account_reward_count: account.reward_count,
      account_commission_total: account.commission_total,
      account_commission_pending: account.commission_pending,
      account_commission_paid: account.commission_paid,
      account_payout_available: account.payout_available,
      account_payout_withdrawn: account.payout_withdrawn,
      per_program_signups_referrals: null,
      per_program_trials: null,
      per_program_paid_customers: null,
    } : (latest?.metrics || null),
    evidence_records: records.length + (accountCovered ? 1 : 0),
  };
});

const rank = {P0_UNCHECKED:0, P1_STALE:1, P1_PARTIAL:2, P2_COVERED:3};
rows.sort((a,b) => rank[a.priority]-rank[b.priority] || (a.network||'').localeCompare(b.network||'') || a.name.localeCompare(b.name));

const groups = {};
for (const row of rows.filter(r => r.priority !== 'P2_COVERED')) {
  const key = row.account_id || row.network || row.id;
  if (!groups[key]) groups[key] = {account_id:key, network:row.network, portal_url:row.portal_url, tools:[]};
  groups[key].tools.push({id:row.id,name:row.name,priority:row.priority,reason:row.reason});
}

const counts = Object.fromEntries(['P0_UNCHECKED','P1_STALE','P1_PARTIAL','P2_COVERED'].map(k => [k, rows.filter(r => r.priority===k).length]));
const output = {
  generated_at: new Date().toISOString(),
  evidence_scope: 'Combined authenticated revenue-browser baseline, current revenue-truth records, and explicit account-wide commission/payout evidence.',
  policy: {
    purpose: 'Detect approved monetized routes that can leak revenue because downstream affiliate metrics are missing or stale.',
    unknown_is_zero: false,
    public_output: false,
    no_reapplication: true,
    no_link_changes: true,
    account_level_zero_does_not_imply_per_program_zero_signups: true,
  },
  summary: {
    approved_tracked_tools: rows.length,
    ...counts,
    unchecked_or_stale_or_partial: rows.filter(r => r.priority !== 'P2_COVERED').length,
    account_groups_to_check: Object.keys(groups).length,
  },
  account_groups: Object.values(groups),
  rows,
};

fs.writeFileSync(path.join(root, 'data/revenue-leakage-audit.json'), JSON.stringify(output, null, 2) + '\n');
console.log(`Revenue leakage audit: approved=${rows.length} unchecked=${counts.P0_UNCHECKED} stale=${counts.P1_STALE} partial=${counts.P1_PARTIAL} covered=${counts.P2_COVERED} account_groups=${Object.keys(groups).length}`);
