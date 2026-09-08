let cachedToken = null;

const base64url = (value) => {
  const bytes = typeof value === 'string' ? new TextEncoder().encode(value) : new Uint8Array(value);
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
};

async function accessToken(env) {
  if (cachedToken && cachedToken.expiresAt > Date.now() + 60_000) return cachedToken.value;
  const account = JSON.parse(env.GOOGLE_SERVICE_ACCOUNT_JSON || '{}');
  if (!account.client_email || !account.private_key) throw new Error('Google service account is not configured');
  const now = Math.floor(Date.now() / 1000);
  const claim = {
    iss: account.client_email,
    scope: 'https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/webmasters.readonly',
    aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3600,
  };
  const unsigned = `${base64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }))}.${base64url(JSON.stringify(claim))}`;
  const der = Uint8Array.from(atob(account.private_key.replace(/-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|\s/g, '')), (c) => c.charCodeAt(0));
  const key = await crypto.subtle.importKey('pkcs8', der, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']);
  const signature = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, new TextEncoder().encode(unsigned));
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer', assertion: `${unsigned}.${base64url(signature)}` }),
  });
  if (!response.ok) throw new Error(`Google token request failed: ${response.status}`);
  const body = await response.json();
  cachedToken = { value: body.access_token, expiresAt: Date.now() + Number(body.expires_in || 3600) * 1000 };
  return cachedToken.value;
}

async function googlePost(url, token, body) {
  const response = await fetch(url, { method: 'POST', headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' }, body: JSON.stringify(body) });
  if (!response.ok) throw new Error(`Google API request failed: ${response.status}`);
  return response.json();
}

const value = (row, index = 0) => Number(row?.metricValues?.[index]?.value || 0);
const dimension = (row, index = 0) => row?.dimensionValues?.[index]?.value || '알 수 없음';
const yesterday = () => new Date(Date.now() - 86400000).toISOString().slice(0, 10);
const daysAgo = (days) => new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);

const gaRangeRequest = (startDate) => ({
  dateRanges: [{ startDate, endDate: 'today' }],
  metrics: [{ name: 'activeUsers' }, { name: 'sessions' }, { name: 'screenPageViews' }],
});

export async function fetchGoogleMetrics(env) {
  const token = await accessToken(env);
  const property = env.GA_PROPERTY_ID || '552119661';
  const gaBase = `https://analyticsdata.googleapis.com/v1beta/properties/${property}`;
  const site = env.GSC_SITE_URL || 'https://coshuma.com/';
  const gscBase = `https://searchconsole.googleapis.com/webmasters/v3/sites/${encodeURIComponent(site)}/searchAnalytics/query`;
  const endDate = yesterday();
  const searchStart = daysAgo(89);

  const [
    kpis, countries, sources, pages, affiliate, affiliatePages, daily,
    searchTotals, searchQueries, searchPages,
  ] = await Promise.all([
    googlePost(`${gaBase}:batchRunReports`, token, { requests: [gaRangeRequest('today'), gaRangeRequest('7daysAgo'), gaRangeRequest('30daysAgo'), gaRangeRequest('90daysAgo')] }),
    googlePost(`${gaBase}:runReport`, token, { dateRanges: [{ startDate: '30daysAgo', endDate: 'today' }], dimensions: [{ name: 'country' }], metrics: [{ name: 'activeUsers' }], orderBys: [{ metric: { metricName: 'activeUsers' }, desc: true }], limit: 10 }),
    googlePost(`${gaBase}:runReport`, token, { dateRanges: [{ startDate: '30daysAgo', endDate: 'today' }], dimensions: [{ name: 'sessionSource' }], metrics: [{ name: 'activeUsers' }, { name: 'sessions' }], orderBys: [{ metric: { metricName: 'activeUsers' }, desc: true }], limit: 10 }),
    googlePost(`${gaBase}:runReport`, token, { dateRanges: [{ startDate: '30daysAgo', endDate: 'today' }], dimensions: [{ name: 'pagePath' }], metrics: [{ name: 'screenPageViews' }, { name: 'activeUsers' }], orderBys: [{ metric: { metricName: 'screenPageViews' }, desc: true }], limit: 15 }),
    googlePost(`${gaBase}:runReport`, token, { dateRanges: [{ startDate: '30daysAgo', endDate: 'today' }], dimensions: [{ name: 'eventName' }], metrics: [{ name: 'eventCount' }], dimensionFilter: { filter: { fieldName: 'eventName', stringFilter: { matchType: 'EXACT', value: 'affiliate_click' } } } }),
    googlePost(`${gaBase}:runReport`, token, { dateRanges: [{ startDate: '30daysAgo', endDate: 'today' }], dimensions: [{ name: 'pagePath' }], metrics: [{ name: 'eventCount' }], dimensionFilter: { filter: { fieldName: 'eventName', stringFilter: { matchType: 'EXACT', value: 'affiliate_click' } } }, orderBys: [{ metric: { metricName: 'eventCount' }, desc: true }], limit: 15 }),
    googlePost(`${gaBase}:runReport`, token, { dateRanges: [{ startDate: '30daysAgo', endDate: 'today' }], dimensions: [{ name: 'date' }], metrics: [{ name: 'activeUsers' }, { name: 'sessions' }, { name: 'screenPageViews' }], orderBys: [{ dimension: { dimensionName: 'date' } }] }),
    googlePost(gscBase, token, { startDate: searchStart, endDate, rowLimit: 1 }),
    googlePost(gscBase, token, { startDate: searchStart, endDate, dimensions: ['query'], rowLimit: 250 }),
    googlePost(gscBase, token, { startDate: searchStart, endDate, dimensions: ['page'], rowLimit: 250 }),
  ]);

  const reports = kpis.reports || [];
  const range = (i) => ({ users: value(reports[i]?.rows?.[0], 0), sessions: value(reports[i]?.rows?.[0], 1), views: value(reports[i]?.rows?.[0], 2) });
  const affiliateClicks = value(affiliate.rows?.[0]);
  const total = searchTotals.rows?.[0] || {};
  const searchRows = searchQueries.rows || [];
  const searchPageRows = searchPages.rows || [];

  return {
    propertyId: String(property),
    checkedAt: new Date().toISOString(),
    ga: {
      connected: true,
      ranges: { today: range(0), sevenDays: range(1), thirtyDays: range(2), ninetyDays: range(3) },
      today: range(0).users,
      sevenDays: range(1).users,
      thirtyDays: range(2).users,
      affiliateClicks,
      countries: (countries.rows || []).map((row) => ({ name: dimension(row), users: value(row, 0) })),
      sources: (sources.rows || []).map((row) => ({ name: dimension(row), users: value(row, 0), sessions: value(row, 1) })),
      pages: (pages.rows || []).map((row) => ({ name: dimension(row), views: value(row, 0), users: value(row, 1) })),
      affiliatePages: (affiliatePages.rows || []).map((row) => ({ name: dimension(row), clicks: value(row, 0) })),
      daily: (daily.rows || []).map((row) => ({ date: dimension(row), users: value(row, 0), sessions: value(row, 1), views: value(row, 2) })),
    },
    searchConsole: {
      connected: true,
      period: `${searchStart} ~ ${endDate}`,
      impressions: Math.round(total.impressions || 0),
      clicks: Math.round(total.clicks || 0),
      ctr: `${(Number(total.ctr || 0) * 100).toFixed(2)}%`,
      averagePosition: Number(Number(total.position || 0).toFixed(1)),
      topQueries: searchRows.sort((a, b) => Number(b.impressions || 0) - Number(a.impressions || 0)).slice(0, 20).map((row) => ({ query: row.keys?.[0] || '알 수 없음', impressions: Math.round(row.impressions || 0), clicks: Math.round(row.clicks || 0), ctr: Number(row.ctr || 0), position: Number(row.position || 0) })),
      topPages: searchPageRows.sort((a, b) => Number(b.impressions || 0) - Number(a.impressions || 0)).slice(0, 20).map((row) => ({ page: row.keys?.[0] || '알 수 없음', impressions: Math.round(row.impressions || 0), clicks: Math.round(row.clicks || 0), ctr: Number(row.ctr || 0), position: Number(row.position || 0) })),
      checkedAt: new Date().toISOString(),
    },
  };
}
