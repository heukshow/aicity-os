import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { assertAudienceProjection, AUDIENCE_EVENTS } from './audience-projection-contract.mjs';

const path = process.env.DASHBOARD_OUTPUT_PATH;
if (!path) throw new Error('DASHBOARD_OUTPUT_PATH is required');
const body = fs.readFileSync(path, 'utf8');
const data = JSON.parse(body);
if (data.status !== 'live_google_connected' || data.measurement_status !== 'live_connected')
  throw new Error('Live snapshot unavailable; existing private snapshot is preserved');
const tokenUrl = new URL(process.env.ACTIONS_ID_TOKEN_REQUEST_URL);
tokenUrl.searchParams.set('audience', 'coshuma-private-analytics');
const tokenResponse = await fetch(tokenUrl, { headers: { Authorization: `Bearer ${process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN}` } });
if (!tokenResponse.ok) throw new Error(`OIDC request failed: ${tokenResponse.status}`);
const token = (await tokenResponse.json()).value;
const result = await fetch('https://globalsaashub-payments.qmfforfhem.workers.dev/internal/analytics-snapshot', {
  method: 'PUT', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body,
});
if (!result.ok) throw new Error(`Private snapshot upload failed: ${result.status}`);
console.log('Validated analytics snapshot stored behind owner authentication.');

// Reuse the exact workflow's short-lived OIDC identity. Never expose credentials
// or the private metrics payload in logs, artifacts, or public site files.
const endpoint = 'https://globalsaashub-payments.qmfforfhem.workers.dev/ops/audience-growth.json';
const verified = await fetch(endpoint, {
  headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(30000),
});
if (verified.status !== 200) throw new Error(`Audience production read failed: ${verified.status}`);
if (!verified.headers.get('content-type')?.includes('application/json'))
  throw new Error('Audience production response is not JSON');
if (!verified.headers.get('cache-control')?.includes('no-store'))
  throw new Error('Audience production response lacks no-store');
const payload = await verified.text();
try { assertAudienceProjection(JSON.parse(payload), data); }
catch { throw new Error('Audience production projection does not match the exact published 8-event source'); }
const anonymous = await fetch(endpoint, { signal: AbortSignal.timeout(30000) });
if (anonymous.status !== 401 || !anonymous.headers.get('cache-control')?.includes('no-store'))
  throw new Error('Anonymous audience access must remain 401/no-store');
const revenueDenied = await fetch(endpoint.replace('audience-growth.json', 'revenue-summary.json'), {
  headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(30000),
});
if (revenueDenied.status !== 401) throw new Error('Analytics OIDC identity must not gain revenue access');
const evidence = {
  checked_at: new Date().toISOString(),
  source_sha: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
  run_id: process.env.GITHUB_RUN_ID || null,
  authentication: 'existing_exact_analytics_workflow_oidc',
  http_status: verified.status, event_count: AUDIENCE_EVENTS.length,
  windows: ['7d', '30d'], exact_projection_match: true,
  anonymous_status: anonymous.status, revenue_oidc_status: revenueDenied.status,
  payload_sha256: createHash('sha256').update(payload).digest('hex'),
  collected_at: data.audience_growth.collected_at || null,
};
console.log('AUDIENCE_PROJECTION_VERIFIED ' + JSON.stringify(evidence));
if (process.env.GITHUB_STEP_SUMMARY)
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, '\n## Private audience production verification\n\n```json\n' + JSON.stringify(evidence, null, 2) + '\n```\n');
