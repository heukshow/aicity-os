import assert from 'node:assert/strict';

const rawBase = process.env.COSHUMA_PAYMENT_API_BASE_URL || process.argv[2] || '';
const base = rawBase.replace(/\/$/, '');
const origin = process.env.COSHUMA_ALLOWED_ORIGIN || 'https://coshuma.com';

if (!base.startsWith('https://')) {
  throw new Error('Provide an HTTPS Worker base URL as COSHUMA_PAYMENT_API_BASE_URL or argv[2].');
}

async function request(path, options = {}) {
  const response = await fetch(`${base}${path}`, {
    redirect: 'error',
    ...options,
  });
  const text = await response.text();
  let body = null;
  try { body = text ? JSON.parse(text) : null; } catch { body = text; }
  return { response, body };
}

const checks = [];
function pass(name, detail = '') {
  checks.push({ name, ok: true, detail });
  console.log(`PASS ${name}${detail ? ` — ${detail}` : ''}`);
}

{
  const { response, body } = await request('/health');
  assert.equal(response.status, 200);
  assert.equal(body?.ok, true);
  assert.equal(body?.checkoutConfigured, false, 'checkout must remain disabled during prelaunch verification');
  pass('health', 'checkoutConfigured=false');
}

{
  const path = encodeURIComponent('/best/verified-software-free-trials-deals.html');
  const { response, body } = await request(`/v1/sponsored/placements?path=${path}`, {
    headers: { origin, accept: 'application/json' },
  });
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('access-control-allow-origin'), origin);
  assert.ok(Array.isArray(body?.placements));
  assert.equal(typeof body?.ready, 'boolean');
  pass('sponsored placements endpoint', `ready=${body.ready}; placements=${body.placements.length}`);
}

{
  const { response } = await request('/v1/sponsored/placements?path=%2F%2Fevil.example', {
    headers: { origin, accept: 'application/json' },
  });
  assert.equal(response.status, 400);
  pass('invalid placement path fails closed');
}

{
  const { response } = await request('/v1/orders', {
    method: 'OPTIONS',
    headers: { origin: 'https://evil.example' },
  });
  assert.equal(response.status, 403);
  pass('cross-origin preflight rejected');
}

{
  const { response, body } = await request('/v1/orders', {
    method: 'POST',
    headers: { origin, 'content-type': 'application/json' },
    body: JSON.stringify({ productId: 'tool_page_7', amount: '0.01', currency: 'KRW' }),
  });
  assert.equal(response.status, 503, 'create-order must remain unavailable while CHECKOUT_ENABLED=false');
  assert.equal(body?.error, 'Checkout is unavailable');
  pass('payment creation gate', 'no PayPal order was created');
}

{
  const { response } = await request('/v1/advertiser/report?token=invalid-token', {
    headers: { origin, accept: 'application/json' },
  });
  assert.equal(response.status, 400);
  pass('report token validation fails closed');
}

{
  const { response } = await request('/v1/advertiser/assets', {
    method: 'POST',
    headers: { origin, 'content-type': 'application/json' },
    body: JSON.stringify({ token: 'invalid-token' }),
  });
  assert.equal(response.status, 400);
  pass('asset intake token validation fails closed');
}

{
  const { response } = await request('/v1/sponsored/events', {
    method: 'POST',
    headers: { origin, 'content-type': 'application/json' },
    body: JSON.stringify({
      eventType: 'sponsored_impression',
      campaignId: 'nonexistent',
      page: '/best/verified-software-free-trials-deals.html',
      destinationUrl: 'https://example.com/',
    }),
  });
  assert.ok([404, 502].includes(response.status), `expected a fail-closed 404/502, received ${response.status}`);
  pass('sponsored event rejects nonexistent campaign', `status=${response.status}`);
}

console.log(JSON.stringify({ ok: true, paymentPerformed: false, checks }, null, 2));
