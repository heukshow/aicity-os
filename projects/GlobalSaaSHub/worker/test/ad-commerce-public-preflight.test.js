// In-memory synthetic HTTP only. No PayPal account, secret, network or database access.
import test from 'node:test';
import assert from 'node:assert/strict';
import { assertSandboxWebhookRegistration } from '../src/ad-commerce-public-preflight.js';

const API = 'https://api-m.sandbox.paypal.com';
const ENV = { PAYPAL_ENVIRONMENT: 'sandbox', PAYPAL_CLIENT_ID: 'SYNTHETIC-CLIENT',
  PAYPAL_CLIENT_SECRET: 'SYNTHETIC-SECRET', PAYPAL_WEBHOOK_ID: 'SYNTHETIC-HOOK',
  SANDBOX_ORIGIN: 'https://isolated-test.example.invalid' };
const EVENT = 'PAYMENT.CAPTURE.COMPLETED';
const token = 'SYNTHETIC-ACCESS-TOKEN';
const json = value => new Response(JSON.stringify(value), { headers: { 'content-type': 'application/json' } });

function fixture(t) {
  t.mock.method(globalThis, 'fetch', () => { throw new Error('Real network forbidden'); });
  const state = {
    auth: { access_token: token, token_type: 'Bearer', expires_in: 300 },
    application: { webhooks: [{ id: ENV.PAYPAL_WEBHOOK_ID,
      url: ENV.SANDBOX_ORIGIN + '/sandbox/webhooks/paypal', event_types: [{ name: EVENT }],
      links: [{ href: API + '/v1/notifications/webhooks/' + ENV.PAYPAL_WEBHOOK_ID, rel: 'self', method: 'GET' }] }] },
    account: { webhooks: [] },
    calls: [], override: null,
  };
  state.fetchImpl = async (url, init) => {
    assert.equal(new URL(url).origin, API);
    assert.equal(init.redirect, 'error');
    assert.ok(init.signal instanceof AbortSignal);
    state.calls.push({ url, init });
    if (state.override) {
      const response = await state.override(url, init);
      if (response !== undefined) return response;
    }
    if (url === API + '/v1/oauth2/token') {
      assert.equal(init.method, 'POST');
      assert.equal(init.body, 'grant_type=client_credentials');
      assert.equal(init.headers.Authorization, 'Basic ' + btoa(ENV.PAYPAL_CLIENT_ID + ':' + ENV.PAYPAL_CLIENT_SECRET));
      return json(state.auth);
    }
    assert.equal(init.method, 'GET');
    assert.equal(init.headers.Authorization, 'Bearer ' + token);
    if (url === API + '/v1/notifications/webhooks?anchor_type=APPLICATION') return json(state.application);
    if (url === API + '/v1/notifications/webhooks?anchor_type=ACCOUNT') return json(state.account);
    assert.fail('Unexpected API path');
  };
  return state;
}

async function rejected(f, env = ENV) {
  await assert.rejects(assertSandboxWebhookRegistration(env, f.fetchImpl), error => {
    assert.equal(error.status, 503);
    assert.match(error.message, /^PayPal Sandbox webhook preflight failed \([A-Z_]+\)\.$/);
    for (const secret of [ENV.PAYPAL_CLIENT_ID, ENV.PAYPAL_CLIENT_SECRET, token, 'RAW-PROVIDER-DETAIL']) {
      assert.equal(error.message.includes(secret), false);
    }
    assert.equal(error.cause, undefined);
    return true;
  });
}

test('fresh OAuth plus APPLICATION and ACCOUNT reads return only safe registration evidence', async t => {
  const f = fixture(t), before = Date.now();
  const result = await assertSandboxWebhookRegistration(ENV, f.fetchImpl);
  assert.deepEqual(Object.keys(result).sort(),
    ['verified', 'applicationCount', 'accountCount', 'webhookId', 'eventTypes', 'checkedAt'].sort());
  assert.equal(result.verified, true);
  assert.equal(result.applicationCount, 1);
  assert.equal(result.accountCount, 0);
  assert.equal(result.webhookId, ENV.PAYPAL_WEBHOOK_ID);
  assert.deepEqual(result.eventTypes, [EVENT]);
  assert.ok(Date.parse(result.checkedAt) >= before && Date.parse(result.checkedAt) <= Date.now());
  assert.deepEqual(f.calls.map(call => [new URL(call.url).pathname + new URL(call.url).search, call.init.method]), [
    ['/v1/oauth2/token', 'POST'],
    ['/v1/notifications/webhooks?anchor_type=APPLICATION', 'GET'],
    ['/v1/notifications/webhooks?anchor_type=ACCOUNT', 'GET'],
  ]);
  const serialized = JSON.stringify(result);
  assert.equal(serialized.includes(ENV.PAYPAL_CLIENT_SECRET), false);
  assert.equal(serialized.includes(token), false);
});

test('registration is rechecked on every invocation and no prior success is cached', async t => {
  const f = fixture(t);
  await assertSandboxWebhookRegistration(ENV, f.fetchImpl);
  f.account.webhooks.push(structuredClone(f.application.webhooks[0]));
  await rejected(f);
  assert.equal(f.calls.filter(call => call.url.endsWith('/v1/oauth2/token')).length, 2);
  assert.equal(f.calls.length, 6);
});

for (const [name, patch] of [
  ['live environment', { PAYPAL_ENVIRONMENT: 'live' }],
  ['missing environment', { PAYPAL_ENVIRONMENT: undefined }],
  ['missing client', { PAYPAL_CLIENT_ID: '' }],
  ['missing secret', { PAYPAL_CLIENT_SECRET: '' }],
  ['malformed Basic client', { PAYPAL_CLIENT_ID: 'invalid:client' }],
  ['credential control characters', { PAYPAL_CLIENT_SECRET: 'secret\n' }],
  ['missing webhook ID', { PAYPAL_WEBHOOK_ID: undefined }],
  ['webhook path injection', { PAYPAL_WEBHOOK_ID: '../OTHER' }],
  ['HTTP origin', { SANDBOX_ORIGIN: 'http://isolated-test.example.invalid' }],
  ['origin path', { SANDBOX_ORIGIN: ENV.SANDBOX_ORIGIN + '/other' }],
  ['origin trailing slash', { SANDBOX_ORIGIN: ENV.SANDBOX_ORIGIN + '/' }],
  ['origin credentials', { SANDBOX_ORIGIN: 'https://user:pass@isolated-test.example.invalid' }],
  ['origin query', { SANDBOX_ORIGIN: ENV.SANDBOX_ORIGIN + '?x=1' }],
  ['nonstandard origin port', { SANDBOX_ORIGIN: ENV.SANDBOX_ORIGIN + ':8443' }],
  ['PayPal live receiver origin', { SANDBOX_ORIGIN: 'https://api-m.paypal.com' }],
]) {
  test('configuration rejects ' + name + ' before network access', async t => {
    const f = fixture(t);
    await rejected(f, { ...ENV, ...patch });
    assert.equal(f.calls.length, 0);
  });
}

test('explicit transport is required and global fetch is never used', async t => {
  const f = fixture(t);
  await assert.rejects(assertSandboxWebhookRegistration(ENV), /preflight failed/);
  assert.equal(f.calls.length, 0);
});

for (const [name, mutate] of [
  ['zero application registrations', f => { f.application.webhooks = []; }],
  ['extra application registration', f => { f.application.webhooks.push(structuredClone(f.application.webhooks[0])); }],
  ['wrong webhook ID', f => { f.application.webhooks[0].id = 'OTHER'; }],
  ['wrong receiver path', f => { f.application.webhooks[0].url += '/other'; }],
  ['live receiver URL', f => { f.application.webhooks[0].url = 'https://api-m.paypal.com/sandbox/webhooks/paypal'; }],
  ['extra event', f => { f.application.webhooks[0].event_types.push({ name: 'PAYMENT.CAPTURE.DENIED' }); }],
  ['duplicate event', f => { f.application.webhooks[0].event_types.push({ name: EVENT }); }],
  ['wildcard event', f => { f.application.webhooks[0].event_types[0].name = '*'; }],
  ['disabled event', f => { f.application.webhooks[0].event_types[0].status = 'DISABLED'; }],
  ['malformed event', f => { f.application.webhooks[0].event_types = [EVENT]; }],
  ['malformed list', f => { f.application = { webhooks: {} }; }],
  ['missing account list', f => { f.account = {}; }],
  ['nonempty account list', f => { f.account.webhooks = [{}]; }],
  ['pagination metadata', f => { f.application.total_pages = 2; }],
  ['next-page link', f => { f.application.links = [{ rel: 'next', href: API + '/v1/notifications/webhooks?page=2' }]; }],
  ['account pagination metadata', f => { f.account.next_page = '2'; }],
  ['paginated self link', f => { f.account.links = [{ rel: 'self', href: API + '/v1/notifications/webhooks?anchor_type=ACCOUNT&page=1' }]; }],
  ['live HATEOAS URL', f => { f.application.webhooks[0].links[0].href = 'https://api-m.paypal.com/v1/notifications/webhooks/SYNTHETIC-HOOK'; }],
  ['legacy live HATEOAS URL', f => { f.application.webhooks[0].links[0].href = 'https://api.paypal.com/v1/notifications/webhooks/SYNTHETIC-HOOK'; }],
  ['legacy Sandbox lookalike URL', f => { f.application.webhooks[0].links[0].href = 'https://api.sandbox.paypal.com.attacker.example.invalid/v1/notifications/webhooks/SYNTHETIC-HOOK'; }],
  ['modern Sandbox lookalike URL', f => { f.application.webhooks[0].links[0].href = 'https://api-m.sandbox.paypal.com.attacker.example.invalid/v1/notifications/webhooks/SYNTHETIC-HOOK'; }],
  ['insecure legacy Sandbox URL', f => { f.application.webhooks[0].links[0].href = 'http://api.sandbox.paypal.com/v1/notifications/webhooks/SYNTHETIC-HOOK'; }],
  ['legacy Sandbox URL with credentials', f => { f.application.webhooks[0].links[0].href = 'https://user@api.sandbox.paypal.com/v1/notifications/webhooks/SYNTHETIC-HOOK'; }],
  ['unexpected provider URL', f => { f.application.webhooks[0].links[0].href = 'https://attacker.example.invalid/path'; }],
  ['malformed links', f => { f.application.webhooks[0].links = {}; }],
  ['extra webhook fields', f => { f.application.webhooks[0].next = 'ignored'; }],
]) {
  test('registration rejects ' + name, async t => {
    const f = fixture(t); mutate(f); await rejected(f);
    assert.equal(f.calls.some(call => !call.url.startsWith(API + '/')), false);
  });
}

test('documented optional event metadata and nonpaginated sandbox self links are accepted', async t => {
  const f = fixture(t);
  Object.assign(f.application.webhooks[0].event_types[0], {
    status: 'ENABLED', description: 'Synthetic completed event', resource_versions: ['2.0'],
  });
  f.application.links = [{ rel: 'self', method: 'GET', href: API + '/v1/notifications/webhooks?anchor_type=APPLICATION' }];
  f.account.links = [{ rel: 'self', href: API + '/v1/notifications/webhooks?anchor_type=ACCOUNT' }];
  assert.equal((await assertSandboxWebhookRegistration(ENV, f.fetchImpl)).verified, true);
});

for (const [name, mutate] of [
  ['missing token', f => { delete f.auth.access_token; }],
  ['token header injection', f => { f.auth.access_token = 'token\r\nsecret'; }],
  ['wrong token type', f => { f.auth.token_type = 'Basic'; }],
  ['invalid token lifetime', f => { f.auth.expires_in = 0; }],
]) {
  test('authentication rejects ' + name, async t => {
    const f = fixture(t); mutate(f); await rejected(f); assert.equal(f.calls.length, 1);
  });
}

for (const stage of ['/v1/oauth2/token', 'anchor_type=APPLICATION', 'anchor_type=ACCOUNT']) {
  test('rejects redirect at ' + stage + ' without following it', async t => {
    const f = fixture(t);
    f.override = url => url.endsWith(stage) ? new Response(null, {
      status: 302, headers: { location: 'https://api-m.paypal.com/RAW-PROVIDER-DETAIL' },
    }) : undefined;
    await rejected(f);
    assert.equal(f.calls.some(call => call.url.includes('api-m.paypal.com')), false);
  });
}

for (const [name, response] of [
  ['HTTP error', () => new Response('RAW-PROVIDER-DETAIL', { status: 401 })],
  ['invalid JSON', () => new Response('RAW-PROVIDER-DETAIL', { headers: { 'content-type': 'application/json' } })],
  ['non-JSON content type', () => new Response('{}', { headers: { 'content-type': 'text/html' } })],
  ['array response', () => json([])],
  ['null response', () => json(null)],
  ['oversized declared response', () => new Response('{}', { headers: { 'content-type': 'application/json', 'content-length': '65537' } })],
  ['oversized streamed response', () => json({ value: 'x'.repeat(65536) })],
  ['already-followed redirect', () => { const r = json({}); Object.defineProperty(r, 'redirected', { value: true }); return r; }],
  ['unexpected final response URL', () => { const r = json({}); Object.defineProperty(r, 'url', { value: 'https://api-m.paypal.com/v1/oauth2/token' }); return r; }],
]) {
  test('fails closed with safe error for ' + name, async t => {
    const f = fixture(t); f.override = response; await rejected(f);
  });
}

test('transport and body-read failures never expose provider error text or credentials', async t => {
  const f = fixture(t);
  f.override = () => { throw new Error(ENV.PAYPAL_CLIENT_SECRET + token + 'RAW-PROVIDER-DETAIL'); };
  await rejected(f);
  f.override = () => new Response(new ReadableStream({
    start(controller) { controller.error(new Error(ENV.PAYPAL_CLIENT_SECRET + 'RAW-PROVIDER-DETAIL')); },
  }), { headers: { 'content-type': 'application/json' } });
  await rejected(f);
});

test('observed legacy Sandbox self/update/delete metadata passes without following any link', async t => {
  const f = fixture(t);
  f.application.webhooks[0].links = [
    { href: 'https://api.sandbox.paypal.com/v1/notifications/webhooks/' + ENV.PAYPAL_WEBHOOK_ID, rel: 'self', method: 'GET' },
    { href: 'https://api.sandbox.paypal.com/v1/notifications/webhooks/' + ENV.PAYPAL_WEBHOOK_ID, rel: 'update', method: 'PATCH' },
    { href: 'https://api.sandbox.paypal.com/v1/notifications/webhooks/' + ENV.PAYPAL_WEBHOOK_ID, rel: 'delete', method: 'DELETE' },
  ];
  const result = await assertSandboxWebhookRegistration(ENV, f.fetchImpl);
  assert.equal(result.verified, true);
  assert.equal(result.webhookId, ENV.PAYPAL_WEBHOOK_ID);
  assert.equal(result.applicationCount, 1);
  assert.equal(result.accountCount, 0);
  assert.deepEqual(result.eventTypes, [EVENT]);
  assert.equal(f.calls.length, 3);
  assert.equal(f.calls.every(call => new URL(call.url).origin === API), true);
});

test('legacy metadata host does not permit a changed network response origin', async t => {
  const f = fixture(t);
  f.override = url => {
    if (url !== API + '/v1/oauth2/token') return;
    const response = json(f.auth);
    Object.defineProperty(response, 'url', { value: 'https://api.sandbox.paypal.com/v1/oauth2/token' });
    return response;
  };
  await rejected(f);
  assert.equal(f.calls.length, 1);
});
