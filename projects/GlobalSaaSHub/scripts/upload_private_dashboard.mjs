import fs from 'node:fs';

const path = process.env.DASHBOARD_OUTPUT_PATH;
const revenueTruthPath = process.env.REVENUE_TRUTH_PATH;
if (!path) throw new Error('DASHBOARD_OUTPUT_PATH is required');
if (!revenueTruthPath) throw new Error('REVENUE_TRUTH_PATH is required');

const data = JSON.parse(fs.readFileSync(path, 'utf8'));
if (data.status !== 'live_google_connected' || data.measurement_status !== 'live_connected')
  throw new Error('Live snapshot unavailable; existing private snapshot is preserved');

const truth = JSON.parse(fs.readFileSync(revenueTruthPath, 'utf8'));
if (!truth?.policy || truth.policy.unknown_is_zero !== false || truth.policy.infer_downstream_from_upstream !== false)
  throw new Error('Revenue truth policy must preserve unknown values and forbid downstream inference');
if (!truth?.coverage || typeof truth.coverage.all_networks_complete !== 'boolean' || !Array.isArray(truth.records))
  throw new Error('Revenue truth coverage/records are invalid');

const numericFields = [
  'outbound_clicks', 'signups_referrals', 'trials', 'paid_customers',
  'gross_sales_revenue', 'commission_earned', 'commission_approved',
  'commission_pending', 'payout_paid', 'payout_pending',
];
for (const [index, record] of truth.records.entries()) {
  if (!record || typeof record.tool !== 'string' || typeof record.network !== 'string'
    || typeof record.evidence_source !== 'string' || typeof record.evidence_timestamp !== 'string'
    || !Number.isFinite(Date.parse(record.evidence_timestamp)))
    throw new Error(`Revenue truth record ${index} is missing evidence identity/timestamp`);
  for (const field of numericFields) {
    if (!(field in record) || record[field] === null) continue;
    if (!Number.isFinite(Number(record[field])) || Number(record[field]) < 0)
      throw new Error(`Revenue truth record ${index} has invalid ${field}`);
  }
}

const totals = truth.verified_totals || {};
if (truth.coverage.all_networks_complete === false) {
  for (const [field, value] of Object.entries(totals)) {
    if (field === 'note') continue;
    if (value !== null && value !== undefined)
      throw new Error(`Incomplete all-network coverage cannot publish aggregate ${field}`);
  }
}

data.revenue_truth = {
  generated_at: truth.generated_at || null,
  coverage: truth.coverage,
  records: truth.records,
  verified_totals: totals,
};

const body = JSON.stringify(data);
const tokenUrl = new URL(process.env.ACTIONS_ID_TOKEN_REQUEST_URL);
tokenUrl.searchParams.set('audience', 'coshuma-private-analytics');
const tokenResponse = await fetch(tokenUrl, { headers: { Authorization: `Bearer ${process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN}` } });
if (!tokenResponse.ok) throw new Error(`OIDC request failed: ${tokenResponse.status}`);
const token = (await tokenResponse.json()).value;
const result = await fetch('https://globalsaashub-payments.qmfforfhem.workers.dev/internal/analytics-snapshot', {
  method: 'PUT', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body,
});
if (!result.ok) throw new Error(`Private snapshot upload failed: ${result.status}`);
console.log(`Validated analytics snapshot stored with ${truth.records.length} evidence-backed revenue records.`);
