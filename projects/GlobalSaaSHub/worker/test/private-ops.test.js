import assert from 'node:assert/strict';
import test from 'node:test';
import worker from '../src/index.js';
import { verifyPublisher } from '../src/private-ops.js';

const password = 'test-only-owner-password';
const hash = async s => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))].map(b => b.toString(16).padStart(2, '0')).join('');
async function setup() {
  let reads = 0;
  return { get reads() { return reads; }, env: { OPS_PASSWORD_SHA256: await hash(password), ORDERS: {
    prepare(sql) { return { bind(name) { return { async first() { if (sql.includes('login_limits')) return { attempts: 1 }; reads++; return { content: name.endsWith('.json') ? '{"private_metric":17}' : '<h1>Private dashboard marker</h1>', content_type: name.endsWith('.json') ? 'application/json' : 'text/html' }; } }; } }; },
  } } };
}
const url = 'https://worker.example/ops/traffic-revenue.html';
test('anonymous HTML and JSON fail closed without reading storage; spoofed headers do not authorize', async () => {
  const state = await setup();
  for (const path of ['traffic-revenue.html', 'traffic-revenue-data.json', 'revenue-seo-refresh.json', 'admin-affiliate-audit.json']) {
    const r = await worker.fetch(new Request(`https://worker.example/ops/${path}`, { headers: { 'cf-access-authenticated-user-email': 'support@coshuma.com', cookie: 'coshuma_ops=forged' } }), state.env);
    assert.equal(r.status, 401); assert.doesNotMatch(await r.text(), /private_metric|Private dashboard marker/);
    assert.equal(r.headers.get('cache-control'), 'no-store, private');
  }
  assert.equal(state.reads, 0);
});
test('only configured owner password permits content; expired and forged sessions are denied', async () => {
  const state = await setup();
  const login = await worker.fetch(new Request(url, { method: 'POST', body: new URLSearchParams({ username: 'support@coshuma.com', password }) }), state.env);
  assert.equal(login.status, 303);
  const cookie = login.headers.get('set-cookie').split(';')[0];
  assert.match(login.headers.get('set-cookie'), /HttpOnly; Secure; SameSite=Strict/);
  for (const path of ['traffic-revenue.html', 'traffic-revenue-data.json']) {
    const r = await worker.fetch(new Request(`https://worker.example/ops/${path}`, { headers: { cookie } }), state.env);
    assert.equal(r.status, 200); assert.match(await r.text(), /Private dashboard marker|private_metric/);
  }
  for (const badCookie of [cookie.replace(/=\d+\./, '=1.'), cookie + 'x']) {
    assert.equal((await worker.fetch(new Request(url, { headers: { cookie: badCookie } }), state.env)).status, 401);
  }
  const wrongUser = await worker.fetch(new Request(url, { method: 'POST', body: new URLSearchParams({ username: 'outsider@example.com', password }) }), state.env);
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
  for (const change of [{ aud: 'wrong' }, { repository_id: 'fork' }, { workflow_ref: 'other' }, { ref: 'refs/heads/feature' }, { exp: now-1 }, { event_name: 'pull_request' }])
    assert.equal(await verifyPublisher(await token(change), fetcher), false);
  const signed = await token();
  assert.equal(await verifyPublisher(signed.slice(0,-8)+'AAAAAAAA', fetcher), false);
});
