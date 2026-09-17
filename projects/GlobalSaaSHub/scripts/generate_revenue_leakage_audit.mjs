import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = rel => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));

const truth = read('data/revenue-truth-2026-09-11.json');
const tools = read('data/tools.json');
const inventory = read('worker/src/revenue-inventory.json');

const APPROVED = new Set(['approved_tracking', 'approved', 'approved_account']);
const aliases = new Map([
  ['highlevel', 'gohighlevel'],
  ['text / livechat partner program', 'text'],
  ['murf ai', 'murf-ai'],
  ['gravity forms', 'gravity-forms'],
  ['really good emails / rge studio', 'really-good-emails'],
]);
const slug = value => String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const truthId = record => aliases.get(String(record.tool || '').toLowerCase()) || slug(record.tool);

const approvedTools = tools.filter(t =>
  t.affiliate_verified === true &&
  typeof t.affiliate_url === 'string' && t.affiliate_url.trim() &&
  APPROVED.has(t.affiliate_status)
);

const truthById = new Map();
for (const record of truth.records || []) {
  const id = truthId(record);
  const list = truthById.get(id) || [];
  list.push(record);
  truthById.set(id, list);
}

const inventoryById = new Map((inventory.programs || []).map(p => [p.id, p]));
const now = Date.now();
const ageDays = timestamp => timestamp ? Math.floor((now - Date.parse(timestamp)) / 86400000) : null;
const downstream = record => [
  'signups_referrals','trials','paid_customers','gross_sales_revenue',
  'commission_earned','commission_approved','commission_pending','payout_paid','payout_pending'
].some(k => record?.[k] !== null && record?.[k] !== undefined);

const rows = approvedTools.map(tool => {
  const records = (truthById.get(tool.id) || []).slice().sort((a,b) => Date.parse(b.evidence_timestamp) - Date.parse(a.evidence_timestamp));
  const latest = records[0] || null;
  const inv = inventoryById.get(tool.id) || null;
  const days = latest ? ageDays(latest.evidence_timestamp) : null;
  let priority;
  let reason;
  if (!latest) {
    priority = 'P0_UNCHECKED';
    reason = 'Approved tracked affiliate route has no revenue-truth evidence record.';
  } else if (days !== null && days > 7) {
    priority = 'P1_STALE';
    reason = `Latest revenue evidence is ${days} days old.`;
  } else if (!downstream(latest)) {
    priority = 'P1_PARTIAL';
    reason = 'Evidence exists but downstream signup/trial/customer/commission/payout fields are all unknown.';
  } else {
    priority = 'P2_COVERED';
    reason = 'Recent evidence-backed downstream revenue state exists.';
  }
  return {
    id: tool.id,
    name: tool.name,
    affiliate_status: tool.affiliate_status,
    tracking_url: tool.affiliate_url,
    network: inv?.network || latest?.network || null,
    account_id: inv?.account_id || null,
    portal_url: inv?.portal_url || null,
    priority,
    reason,
    latest_evidence_at: latest?.evidence_timestamp || null,
    evidence_age_days: days,
    evidence_source: latest?.evidence_source || null,
    evidence_id: latest?.evidence_id || null,
    latest_status: latest?.status || null,
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
  policy: {
    purpose: 'Detect approved monetized routes that can leak revenue because downstream affiliate metrics are missing or stale.',
    unknown_is_zero: false,
    public_output: false,
    no_reapplication: true,
    no_link_changes: true,
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
