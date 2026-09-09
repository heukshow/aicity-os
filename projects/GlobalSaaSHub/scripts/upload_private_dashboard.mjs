import fs from 'node:fs';

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
