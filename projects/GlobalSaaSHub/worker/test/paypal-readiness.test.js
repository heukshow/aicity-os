import assert from 'node:assert/strict';
import test from 'node:test';
import { checkPayPalReadiness, getPayPalOrder } from '../src/paypal.js';

const syntheticEnv = {
  PAYPAL_ENVIRONMENT: 'live', PAYPAL_CLIENT_ID: 'SYNTHETIC-CLIENT',
  PAYPAL_CLIENT_SECRET: 'SYNTHETIC-SECRET', PAYPAL_WEBHOOK_ID: 'SYNTHETIC-WEBHOOK',
};

const registeredEvents = [
  'PAYMENT.CAPTURE.COMPLETED', 'PAYMENT.CAPTURE.PENDING',
  'PAYMENT.CAPTURE.DENIED', 'PAYMENT.CAPTURE.DECLINED',
  'PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED',
  'CUSTOMER.DISPUTE.CREATED', 'CUSTOMER.DISPUTE.UPDATED', 'CUSTOMER.DISPUTE.RESOLVED',
];
const optionalEvent = 'CHECKOUT.PAYMENT-APPROVAL.REVERSED';

async function probe(eventNames) {
  const env = syntheticEnv;
  const expectedUrl = 'https://worker.example/v1/webhooks/paypal';
  const calls = [];
  const fetchImpl = async (url, options = {}) => {
    calls.push({ url, method: options.method || 'GET' });
    if (url === 'https://api-m.paypal.com/v1/oauth2/token') {
      assert.equal(options.method, 'POST');
      return new Response(JSON.stringify({ access_token: 'SYNTHETIC-TOKEN' }));
    }
    assert.equal(url, 'https://api-m.paypal.com/v1/notifications/webhooks/SYNTHETIC-WEBHOOK');
    assert.equal(options.method || 'GET', 'GET');
    return new Response(JSON.stringify({ url: expectedUrl, event_types: eventNames.map((name) => ({ name })) }));
  };
  const result = await checkPayPalReadiness(env, expectedUrl, fetchImpl);
  assert.equal(calls.length, 2, 'only authentication and webhook read are allowed');
  return result;
}

test('the nine capture/dispute subscriptions pass while the unoffered pre-capture event is optional', async () => {
  const result = await probe(registeredEvents);
  assert.equal(result.providerAuthenticationVerified, true);
  assert.equal(result.webhookUrlVerified, true);
  assert.equal(result.requiredEventsVerified, true);
  assert.deepEqual(result.missingRequiredEvents, []);
  assert.deepEqual(result.missingOptionalEvents, [optionalEvent]);
  assert.equal(result.merchantIdentityVerified, false);
  assert.equal(result.configurationOnly, true);
  assert.deepEqual(result.diagnostic, { stage: 'complete', code: 'complete', httpStatus: 200 });
});

test('a subscribed optional event is reported as present without changing required readiness', async () => {
  const result = await probe([...registeredEvents, optionalEvent]);
  assert.equal(result.requiredEventsVerified, true);
  assert.deepEqual(result.missingOptionalEvents, []);
});

test('the optional event cannot compensate for a missing refund subscription', async () => {
  const result = await probe([...registeredEvents.filter((name) => name !== 'PAYMENT.CAPTURE.REFUNDED'), optionalEvent]);
  assert.equal(result.requiredEventsVerified, false);
  assert.deepEqual(result.missingRequiredEvents, ['PAYMENT.CAPTURE.REFUNDED']);
  assert.deepEqual(result.missingOptionalEvents, []);
});

test('an all-events subscription satisfies both required and optional reports', async () => {
  const result = await probe(['*']);
  assert.equal(result.requiredEventsVerified, true);
  assert.deepEqual(result.missingRequiredEvents, []);
  assert.deepEqual(result.missingOptionalEvents, []);
});

test('OAuth failure reports only the authentication stage and HTTP status without reading webhooks', async () => {
  let calls = 0;
  const result = await checkPayPalReadiness(syntheticEnv, 'https://worker.example/v1/webhooks/paypal', async (url) => {
    calls++;
    assert.equal(url, 'https://api-m.paypal.com/v1/oauth2/token');
    return new Response(JSON.stringify({ error: 'invalid_client', error_description: 'SYNTHETIC-SECRET', debug_id: 'SYNTHETIC-DEBUG' }), { status: 401 });
  });
  assert.equal(calls, 1);
  assert.deepEqual(result, {
    providerAuthenticationVerified: false, webhookUrlVerified: false, requiredEventsVerified: false,
    merchantIdentityVerified: false, configurationOnly: true,
    diagnostic: { stage: 'authentication', code: 'authentication_http_error', httpStatus: 401 },
  });
  assert.doesNotMatch(JSON.stringify(result), /SYNTHETIC|invalid_client|debug_id|error_description/);
});

test('webhook 404 preserves verified OAuth while keeping webhook, merchant and payment unverified', async () => {
  const calls = [];
  const result = await checkPayPalReadiness(syntheticEnv, 'https://worker.example/v1/webhooks/paypal', async (url, options = {}) => {
    calls.push(options.method || 'GET');
    if (url.endsWith('/v1/oauth2/token')) return new Response(JSON.stringify({ access_token: 'SYNTHETIC-TOKEN' }));
    return new Response(JSON.stringify({ message: 'SYNTHETIC-WEBHOOK', debug_id: 'SYNTHETIC-DEBUG', client_secret: 'SYNTHETIC-SECRET' }), { status: 404 });
  });
  assert.deepEqual(calls, ['POST', 'GET', 'GET']);
  assert.deepEqual(result, {
    providerAuthenticationVerified: true, webhookUrlVerified: false, requiredEventsVerified: false,
    merchantIdentityVerified: false, configurationOnly: true,
    diagnostic: { stage: 'webhook_lookup', code: 'provider_http_error', httpStatus: 404 },
    webhookDiscovery: { status: 'failed', candidates: [], diagnostic: { stage: 'webhook_discovery', code: 'provider_http_error', httpStatus: 404 } },
  });
  assert.doesNotMatch(JSON.stringify(result), /SYNTHETIC|debug_id|client_secret|access_token|worker\.example/);
});

test('network and malformed responses retain their stage without exposing errors or claiming authentication too early', async () => {
  const cases = [
    { stage: 'authentication', code: 'network_error', status: null, fail: () => { throw new Error('SYNTHETIC-SECRET transport detail'); } },
    { stage: 'webhook_lookup', code: 'network_error', status: null, fail: () => { throw new Error('SYNTHETIC-WEBHOOK transport detail'); } },
    { stage: 'authentication', code: 'unknown_error', status: 200, fail: () => new Response('SYNTHETIC-MALFORMED-JSON') },
    { stage: 'authentication', code: 'unknown_error', status: 200, fail: () => new Response(JSON.stringify({ access_token: '  ' })) },
    { stage: 'webhook_lookup', code: 'unknown_error', status: 200, fail: () => new Response('SYNTHETIC-MALFORMED-JSON') },
  ];
  for (const entry of cases) {
    const result = await checkPayPalReadiness(syntheticEnv, 'https://worker.example/v1/webhooks/paypal', async (url) => {
      if (url.endsWith('/v1/oauth2/token') && entry.stage === 'webhook_lookup') return new Response(JSON.stringify({ access_token: 'SYNTHETIC-TOKEN' }));
      return entry.fail();
    });
    assert.equal(result.providerAuthenticationVerified, entry.stage === 'webhook_lookup');
    assert.equal(result.webhookUrlVerified, false);
    assert.equal(result.merchantIdentityVerified, false);
    assert.deepEqual(result.diagnostic, { stage: entry.stage, code: entry.code, httpStatus: entry.status });
    assert.doesNotMatch(JSON.stringify(result), /SYNTHETIC|transport detail|access_token/);
  }
});

test('ordinary payment reads still reject provider failures instead of returning readiness projections', async () => {
  await assert.rejects(getPayPalOrder(syntheticEnv, 'SYNTHETIC-ORDER', async () => new Response('{}', { status: 401 })), { message: 'PayPal authentication failed' });
  await assert.rejects(getPayPalOrder(syntheticEnv, 'SYNTHETIC-ORDER', async (url) => url.endsWith('/v1/oauth2/token')
    ? new Response(JSON.stringify({ access_token: 'SYNTHETIC-TOKEN' })) : new Response('{}', { status: 404 })), { message: 'PayPal request failed (404)' });
});

test('configured webhook 404 discovers exact URL candidates in the same app token without changing binding or readiness', async () => {
  const expectedUrl = 'https://worker.example/v1/webhooks/paypal';
  const env = { ...syntheticEnv, CHECKOUT_ENABLED: 'false' };
  const calls = [];
  const result = await checkPayPalReadiness(env, expectedUrl, async (url, options = {}) => {
    const path = new URL(url).pathname;
    calls.push([options.method || 'GET', path]);
    if (path === '/v1/oauth2/token') return new Response(JSON.stringify({ access_token: 'SYNTHETIC-TOKEN' }));
    assert.equal(options.headers.Authorization, 'Bearer SYNTHETIC-TOKEN', 'both reads reuse the same authenticated app token');
    if (path === '/v1/notifications/webhooks/SYNTHETIC-WEBHOOK') return new Response('{}', { status: 404 });
    assert.equal(url, 'https://api-m.paypal.com/v1/notifications/webhooks', 'default app scope only');
    return new Response(JSON.stringify({ webhooks: [
      { id: 'MATCH-1', url: expectedUrl, event_types: registeredEvents.map((name) => ({ name })), links: [{ href: 'SECRET-LINK' }] },
      { id: 'MATCH-2', url: expectedUrl, event_types: [{ name: 'PAYMENT.CAPTURE.COMPLETED' }], description: 'SECRET-DESCRIPTION' },
      { id: 'OTHER-SLASH', url: expectedUrl + '/', event_types: [{ name: '*' }] },
      { id: 'OTHER-QUERY', url: expectedUrl + '?secret=1', event_types: [{ name: '*' }] },
      { id: 'OTHER-HOST', url: 'https://another.example/v1/webhooks/paypal', event_types: [{ name: '*' }] },
    ], raw: 'SECRET-RESPONSE' }));
  });
  assert.deepEqual(calls, [['POST', '/v1/oauth2/token'], ['GET', '/v1/notifications/webhooks/SYNTHETIC-WEBHOOK'], ['GET', '/v1/notifications/webhooks']]);
  assert.equal(result.webhookDiscovery.status, 'found');
  assert.deepEqual(result.webhookDiscovery.candidates.map((candidate) => candidate.id), ['MATCH-1', 'MATCH-2']);
  assert.equal(result.webhookDiscovery.candidates[0].requiredEventsVerified, true);
  assert.equal(result.webhookDiscovery.candidates[1].requiredEventsVerified, false);
  assert.ok(result.webhookDiscovery.candidates[1].missingRequiredEvents.includes('PAYMENT.CAPTURE.REFUNDED'));
  assert.equal(result.providerAuthenticationVerified, true);
  assert.equal(result.webhookUrlVerified, false);
  assert.equal(result.requiredEventsVerified, false);
  assert.equal(result.merchantIdentityVerified, false);
  assert.equal(result.configurationOnly, true);
  assert.equal(result.diagnostic.httpStatus, 404);
  assert.equal(env.PAYPAL_WEBHOOK_ID, 'SYNTHETIC-WEBHOOK');
  assert.equal(env.CHECKOUT_ENABLED, 'false');
  assert.doesNotMatch(JSON.stringify(result), /SECRET|OTHER-|SYNTHETIC-TOKEN|SYNTHETIC-CLIENT|SYNTHETIC-SECRET|worker\.example|another\.example/);
});

test('webhook discovery does not broaden a non-404 failure into app enumeration', async () => {
  for (const status of [401, 403, 500]) {
    let calls = 0;
    const result = await checkPayPalReadiness(syntheticEnv, 'https://worker.example/v1/webhooks/paypal', async (url) => {
      calls++;
      if (url.endsWith('/v1/oauth2/token')) return new Response(JSON.stringify({ access_token: 'SYNTHETIC-TOKEN' }));
      assert.ok(url.endsWith('/webhooks/SYNTHETIC-WEBHOOK'));
      return new Response('{}', { status });
    });
    assert.equal(calls, 2);
    assert.equal(result.webhookDiscovery, undefined);
  }
});

test('discovery distinguishes no match from list failure and rejects unvalidated candidate IDs', async () => {
  const expectedUrl = 'https://worker.example/v1/webhooks/paypal';
  for (const [listResponse, expectedStatus, code] of [
    [() => new Response(JSON.stringify({ webhooks: [{ id: 'OTHER-ID', url: 'https://another.example', event_types: [{ name: '*' }] }] })), 'none', 'complete'],
    [() => new Response(JSON.stringify({ error: 'SECRET-PROVIDER-DETAIL' }), { status: 403 }), 'failed', 'provider_http_error'],
    [() => { throw new Error('SECRET-NETWORK-DETAIL'); }, 'failed', 'network_error'],
    [() => new Response(JSON.stringify({ webhooks: 'SECRET-MALFORMED-LIST' })), 'failed', 'unknown_error'],
    [() => new Response(JSON.stringify({ webhooks: [{ id: '<script>SECRET</script>', url: expectedUrl, event_types: [{ name: '*' }] }] })), 'failed', 'unknown_error'],
  ]) {
    const result = await checkPayPalReadiness(syntheticEnv, expectedUrl, async (url) => {
      if (url.endsWith('/v1/oauth2/token')) return new Response(JSON.stringify({ access_token: 'SYNTHETIC-TOKEN' }));
      if (url.endsWith('/webhooks/SYNTHETIC-WEBHOOK')) return new Response('{}', { status: 404 });
      return listResponse();
    });
    assert.equal(result.webhookDiscovery.status, expectedStatus);
    assert.deepEqual(result.webhookDiscovery.candidates, []);
    assert.equal(result.webhookDiscovery.diagnostic.code, code);
    assert.equal(result.webhookUrlVerified, false);
    assert.equal(result.requiredEventsVerified, false);
    assert.doesNotMatch(JSON.stringify(result), /SECRET|OTHER-ID|another\.example|<script>/);
  }
});
