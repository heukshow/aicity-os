import fs from 'node:fs';

const path = process.argv[2] || 'data/revenue-truth-2026-09-11.json';
const truth = JSON.parse(fs.readFileSync(path, 'utf8'));

const fail = message => { throw new Error(`Revenue truth validation failed: ${message}`); };
const numericFields = [
  'outbound_clicks', 'signups_referrals', 'trials', 'paid_customers',
  'gross_sales_revenue', 'commission_earned', 'commission_approved',
  'commission_pending', 'payout_paid', 'payout_pending',
];

if (!truth?.policy) fail('policy missing');
if (truth.policy.primary_kpi !== 'verified_revenue') fail('primary KPI must remain verified_revenue');
if (truth.policy.unknown_is_zero !== false) fail('unknown values must never be converted to zero');
if (truth.policy.infer_downstream_from_upstream !== false) fail('downstream stages must never be inferred');
if (truth.policy.generic_url_is_revenue_link !== false) fail('generic URLs must never be treated as revenue links');
if (!truth?.coverage || typeof truth.coverage.all_networks_complete !== 'boolean') fail('coverage status missing');
if (!Array.isArray(truth.records)) fail('records must be an array');

const seenEvidence = new Set();
for (const [index, record] of truth.records.entries()) {
  const id = `record ${index + 1} (${record?.tool || 'unknown tool'})`;
  if (!record || typeof record.tool !== 'string' || !record.tool.trim()) fail(`${id}: tool missing`);
  if (typeof record.network !== 'string' || !record.network.trim()) fail(`${id}: network missing`);
  if (typeof record.evidence_source !== 'string' || !record.evidence_source.trim()) fail(`${id}: evidence_source missing`);
  if (typeof record.evidence_id !== 'string' || !record.evidence_id.trim()) fail(`${id}: evidence_id missing`);
  if (typeof record.evidence_timestamp !== 'string' || !Number.isFinite(Date.parse(record.evidence_timestamp))) fail(`${id}: valid evidence_timestamp required`);
  if (seenEvidence.has(record.evidence_id)) fail(`${id}: duplicate evidence_id ${record.evidence_id}`);
  seenEvidence.add(record.evidence_id);

  for (const field of numericFields) {
    if (!(field in record)) continue;
    const value = record[field];
    if (value === null) continue;
    if (!Number.isFinite(Number(value)) || Number(value) < 0) fail(`${id}: ${field} must be null or a non-negative number`);
  }

  if (record.status === 'partial_verified') {
    const downstreamKnown = ['signups_referrals', 'trials', 'paid_customers', 'commission_earned', 'payout_paid']
      .filter(field => record[field] !== null && record[field] !== undefined);
    if (downstreamKnown.length && !record.note) fail(`${id}: partial record with downstream values requires explanatory note`);
  }
}

const totals = truth.verified_totals || {};
if (!truth.coverage.all_networks_complete) {
  for (const [field, value] of Object.entries(totals)) {
    if (field === 'note') continue;
    if (value !== null && value !== undefined) fail(`aggregate ${field} cannot be published while all-network coverage is incomplete`);
  }
}

console.log(`Revenue truth OK: ${truth.records.length} evidence-backed records; all-network coverage=${truth.coverage.all_networks_complete ? 'complete' : 'incomplete'}.`);
