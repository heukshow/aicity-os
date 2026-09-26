import fs from 'node:fs';
import { googleFetch } from './google_fetch_retry.mjs';
import crypto from 'node:crypto';

const outPath = process.env.DASHBOARD_OUTPUT_PATH;
const serviceRaw = process.env.GOOGLE_SERVICE_ACCOUNT_JSON || '';
const propertyId = String(process.env.GA_PROPERTY_ID || '552119661').trim();
const eventNames = ['return_visit', 'saved_tool_change', 'saved_tools_view'];

if (!outPath) throw new Error('DASHBOARD_OUTPUT_PATH is required');
const data = JSON.parse(fs.readFileSync(outPath, 'utf8'));
if (data.status !== 'live_google_connected' || data.measurement_status !== 'live_connected') {
  console.log('Audience Growth skipped: upstream snapshot is not fresh; existing private snapshot is preserved.');
  process.exit(0);
}

const emptyAudience = (status) => ({
  status,
  scope: 'first_party_direct_customer_asset_usage',
  events: eventNames,
  ranges: {
    '7d': Object.fromEntries(eventNames.map((name) => [name, { events: null, users: null }])),
    '30d': Object.fromEntries(eventNames.map((name) => [name, { events: null, users: null }])),
  },
});

if (!serviceRaw.trim()) {
  data.audience_growth = emptyAudience('credential_missing');
  fs.writeFileSync(outPath, JSON.stringify(data, null, 2) + '\n');
  process.exit(0);
}

let account;
try {
  account = JSON.parse(serviceRaw);
} catch {
  data.audience_growth = emptyAudience('credential_invalid');
  fs.writeFileSync(outPath, JSON.stringify(data, null, 2) + '\n');
  process.exit(0);
}

const b64url = (value) => Buffer.from(value).toString('base64url');
async function token() {
  const now = Math.floor(Date.now() / 1000);
  const header = b64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const claim = b64url(JSON.stringify({
    iss: account.client_email,
    scope: 'https://www.googleapis.com/auth/analytics.readonly',
    aud: 'https://oauth2.googleapis.com/token',
    iat: now,
    exp: now + 3600,
  }));
  const unsigned = `${header}.${claim}`;
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(unsigned);
  sign.end();
  const assertion = `${unsigned}.${sign.sign(account.private_key).toString('base64url')}`;
  const response = await googleFetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion,
    }),
  });
  if (!response.ok) throw new Error(`Google token ${response.status}`);
  return (await response.json()).access_token;
}

async function runReport(access, startDate) {
  const response = await googleFetch(`https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}:runReport`, {
    method: 'POST',
    headers: { authorization: `Bearer ${access}`, 'content-type': 'application/json' },
    body: JSON.stringify({
      dateRanges: [{ startDate, endDate: 'today' }],
      dimensions: [{ name: 'eventName' }],
      metrics: [{ name: 'eventCount' }, { name: 'activeUsers' }],
      dimensionFilter: {
        filter: {
          fieldName: 'eventName',
          inListFilter: { values: eventNames },
        },
      },
      limit: 10,
    }),
  });
  if (!response.ok) throw new Error(`GA4 audience event query ${response.status}`);
  const report = await response.json();
  if (report.metadata?.dataLossFromOtherRow || (report.rowCount && report.rowCount > (report.rows?.length || 0))) {
    throw new Error('Incomplete audience event report');
  }
  const result = Object.fromEntries(eventNames.map((name) => [name, { events: 0, users: 0 }]));
  for (const row of report.rows || []) {
    const name = row.dimensionValues?.[0]?.value;
    if (!result[name]) continue;
    result[name] = {
      events: Number(row.metricValues?.[0]?.value || 0),
      users: Number(row.metricValues?.[1]?.value || 0),
    };
  }
  return result;
}

try {
  const access = await token();
  const [sevenDays, thirtyDays] = await Promise.all([
    runReport(access, '6daysAgo'),
    runReport(access, '29daysAgo'),
  ]);
  data.audience_growth = {
    status: 'live_connected',
    scope: 'first_party_direct_customer_asset_usage',
    events: eventNames,
    ranges: { '7d': sevenDays, '30d': thirtyDays },
    collected_at: new Date().toISOString(),
  };
  fs.writeFileSync(outPath, JSON.stringify(data, null, 2) + '\n');
  console.log('Audience Growth first-party event snapshot appended to private analytics.');
} catch {
  data.audience_growth = emptyAudience('unavailable');
  fs.writeFileSync(outPath, JSON.stringify(data, null, 2) + '\n');
  console.log('Audience Growth first-party event query unavailable; private snapshot marked without exposing counts.');
}
