import assert from 'node:assert/strict';
import test from 'node:test';
import worker from '../src/index.js';
import { verifyPublisher } from '../src/private-ops.js';

const password = 'test-only-owner-password';
const hash = async s => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))].map(b => b.toString(16).padStart(2, '0')).join('');
async function setup() {
  let reads = 0;
  return { get reads() { return reads; }, env: { OPS_PASSWORD_SHA256: await hash(password), ORDERS: {
    prepare(sql) { return { bind(name) { return { async first() { if (sql.includes('login_limits')) return { attempts: 1 }; reads++; return { content: name.endsWith('.json') ? '{"private_metric":17,"revenue":{"paid":999},"audience_growth":{"status":"live_connected","scope":"first_party_direct_customer_asset_usage","events":["return_visit","saved_tool_change","saved_tools_view","saved_shortlist_share","buyer_intent_stage","compare_open","compare_tool_select","compare_cta_view"],"ranges":{"7d":{"return_visit":{"events":7,"users":3},"saved_tool_change":{"events":5,"users":2},"saved_tools_view":{"events":4,"users":2},"saved_shortlist_share":{"events":3,"users":2},"buyer_intent_stage":{"events":9,"users":4},"compare_open":{"events":6,"users":3},"compare_tool_select":{"events":4,"users":2},"compare_cta_view":{"events":2,"users":2}},"30d":{"return_visit":{"events":30,"users":12},"saved_tool_change":{"events":21,"users":8},"saved_tools_view":{"events":18,"users":7},"saved_shortlist_share":{"events":12,"users":6},"buyer_intent_stage":{"events":40,"users":15},"compare_open":{"events":24,"users":10},"compare_tool_select":{"events":16,"users":7},"compare_cta_view":{"events":8,"users":5}}},"collected_at":"2026-09-23T00:00:00.000Z"}}' : '<h1>Private dashboard marker</h1><script>(()=>{})();</script>', content_type: name.endsWith('.json') ? 'application/json' : 'text/html' }; } }; } }; },
  } } };
}
const url = 'https://worker.example/ops/traffic-revenue.html';
test('anonymous HTML and JSON fail closed without reading storage; spoofed headers do not authorize', async () => {
  const state = await setup();
  for (const path of ['traffic-revenue.html', 'traffic-revenue-data.json', 'audience-growth.json', 'revenue-seo-refresh.json', 'admin-affiliate-audit.json', 'partnerstack-summary.json', 'revenue.html', 'revenue-summary.json']) {
    const r = await worker.fetch(new Request(`https://worker.example/ops/${path}`, { headers: { 'cf-access-authenticated-user-email': 'support@coshuma.com', cookie: 'coshuma_ops=forged' } }), state.env);
    assert.equal(r.status, 401); assert.doesNotMatch(await r.text(), /private_metric|Private dashboard marker/);
    assert.equal(r.headers.get('cache-control'), 'no-store, private');
  }
  assert.equal(state.reads, 0);
});
test('only configured owner password permits content; expired and forged sessions are denied', async () => {
  const state = await setup();
  const page = await worker.fetch(new Request(url), state.env);
  const loginCookie = page.headers.get('set-cookie').split(';')[0];
  const csrf = (await page.text()).match(/name="csrf" value="([^"]+)"/)[1];
  const login = await worker.fetch(new Request(url, { method: 'POST', headers: { cookie: loginCookie, origin: 'null' }, body: new URLSearchParams({ username: 'support@coshuma.com', password, csrf }) }), state.env);
  assert.equal(login.status, 303);
  const cookie = login.headers.get('set-cookie').split(';')[0];
  assert.match(login.headers.get('set-cookie'), /HttpOnly; Secure; SameSite=Strict/);
  for (const path of ['traffic-revenue.html', 'traffic-revenue-data.json']) {
    const r = await worker.fetch(new Request(`https://worker.example/ops/${path}`, { headers: { cookie } }), state.env);
    assert.equal(r.status, 200); assert.match(await r.text(), /Private dashboard marker|private_metric/);
  }
  const audienceResponse = await worker.fetch(new Request('https://worker.example/ops/audience-growth.json', { headers: { cookie } }), state.env);
  assert.equal(audienceResponse.status, 200);
  const audience = await audienceResponse.json();
  assert.deepEqual(audience.events, ['return_visit', 'saved_tool_change', 'saved_tools_view', 'saved_shortlist_share', 'buyer_intent_stage', 'compare_open', 'compare_tool_select', 'compare_cta_view']);
  assert.deepEqual(audience.ranges['7d'].saved_shortlist_share, { events: 3, users: 2 });
  assert.deepEqual(audience.ranges['7d'].buyer_intent_stage, { events: 9, users: 4 });
  assert.deepEqual(audience.ranges['30d'].compare_cta_view, { events: 8, users: 5 });
  for (const badCookie of [cookie.replace(/=\d+\./, '=1.'), cookie + 'x']) {
    assert.equal((await worker.fetch(new Request(url, { headers: { cookie: badCookie } }), state.env)).status, 401);
  }
  const wrongUser = await worker.fetch(new Request(url, { method: 'POST', headers: { cookie: loginCookie }, body: new URLSearchParams({ username: 'outsider@example.com', password, csrf }) }), state.env);
  assert.equal(wrongUser.status, 401);
  const crossOrigin = await worker.fetch(new Request(url, { method: 'POST', headers: { origin: 'https://evil.example' }, body: new URLSearchParams({ username: 'support@coshuma.com', password }) }), state.env);
  assert.equal(crossOrigin.status, 403);
});
test('anonymous and invalid publishers cannot mutate private storage', async () => {
  const state = await setup();
  for (const authorization of ['', 'Bearer invalid']) {
    const r = await worker.fetch(new Request('https://worker.example/internal/analytics-snapshot', { method: 'PUT', headers: { authorization }, body: '{}' }), state.env);
    assert.equal(r.status, 401);
  }
  assert.equal(state.reads, 0);
});
test('publisher verifies signature, audience, exact workflow, repository IDs, branch and expiry', async () => {
  const keys = await crypto.subtle.generateKey({ name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1,0,1]), hash: 'SHA-256' }, true, ['sign', 'verify']);
  const jwk = { ...await crypto.subtle.exportKey('jwk', keys.publicKey), kid: 'test-private-ops', use: 'sig' };
  const fetcher = async () => new Response(JSON.stringify({ keys: [jwk] }));
  const now = Math.floor(Date.now()/1000);
  const claims = { iss: 'https://token.actions.githubusercontent.com', aud: 'coshuma-private-analytics', sub: 'repo:heukshow/aicity-os:ref:refs/heads/main', repository_id: '1158871708', repository_owner_id: '209299838', workflow_ref: 'heukshow/aicity-os/.github/workflows/coshuma-analytics-snapshot.yml@refs/heads/main', ref: 'refs/heads/main', event_name: 'schedule', iat: now, nbf: now, exp: now+300 };
  const encode = s => Buffer.from(JSON.stringify(s)).toString('base64url');
  async function token(change = {}) {
    const text = `${encode({ alg: 'RS256', kid: jwk.kid })}.${encode({ ...claims, ...change })}`;
    return `${text}.${Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5', keys.privateKey, new TextEncoder().encode(text))).toString('base64url')}`;
  }
  assert.equal(await verifyPublisher(await token(), fetcher), true);
  assert.equal(await verifyPublisher(await token({ workflow_ref: 'heukshow/aicity-os/.github/workflows/coshuma-paypal-live-readiness.yml@refs/heads/main', event_name: 'workflow_dispatch' }), fetcher), true);
  for (const change of [{ aud: 'wrong' }, { repository_id: 'fork' }, { workflow_ref: 'other' }, { ref: 'refs/heads/feature' }, { exp: now-1 }, { event_name: 'pull_request' }])
    assert.equal(await verifyPublisher(await token(change), fetcher), false);
  const signed = await token();
  assert.equal(await verifyPublisher(signed.slice(0,-8)+'AAAAAAAA', fetcher), false);
});

test('trusted analytics workflow may read only the audience projection with a valid OIDC token', async () => {
  const state = await setup();
  const keys = await crypto.subtle.generateKey({ name: 'RSASSA-PKCS1-v1_5', modulusLength: 2048, publicExponent: new Uint8Array([1,0,1]), hash: 'SHA-256' }, true, ['sign', 'verify']);
  const jwk = { ...await crypto.subtle.exportKey('jwk', keys.publicKey), kid: 'test-audience-read', use: 'sig' };
  const now = Math.floor(Date.now()/1000);
  const header = Buffer.from(JSON.stringify({ alg: 'RS256', kid: jwk.kid })).toString('base64url');
  const claims = Buffer.from(JSON.stringify({
    iss: 'https://token.actions.githubusercontent.com',
    aud: 'coshuma-private-analytics',
    sub: 'repo:heukshow/aicity-os:ref:refs/heads/main',
    repository_id: '1158871708',
    repository_owner_id: '209299838',
    workflow_ref: 'heukshow/aicity-os/.github/workflows/coshuma-analytics-snapshot.yml@refs/heads/main',
    ref: 'refs/heads/main',
    event_name: 'workflow_dispatch',
    iat: now,
    nbf: now,
    exp: now + 300,
  })).toString('base64url');
  const signed = `${header}.${claims}`;
  const token = `${signed}.${Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5', keys.privateKey, new TextEncoder().encode(signed))).toString('base64url')}`;
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async input => String(input).includes('/.well-known/jwks')
    ? new Response(JSON.stringify({ keys: [jwk] }))
    : originalFetch(input);
  try {
    const audience = await worker.fetch(new Request('https://worker.example/ops/audience-growth.json', {
      headers: { authorization: `Bearer ${token}` },
    }), state.env);
    assert.equal(audience.status, 200);
    const payload = await audience.json();
    assert.deepEqual(payload.events, ['return_visit', 'saved_tool_change', 'saved_tools_view', 'saved_shortlist_share', 'buyer_intent_stage', 'compare_open', 'compare_tool_select', 'compare_cta_view']);
    assert.equal(payload.revenue, undefined);
    assert.equal(payload.private_metric, undefined);

    const revenue = await worker.fetch(new Request('https://worker.example/ops/revenue-summary.json', {
      headers: { authorization: `Bearer ${token}` },
    }), state.env);
    assert.equal(revenue.status, 401);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
