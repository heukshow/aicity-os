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
  assert.deepEqual(calls, ['POST', 'GET']);
  assert.deepEqual(result, {
    providerAuthenticationVerified: true, webhookUrlVerified: false, requiredEventsVerified: false,
    merchantIdentityVerified: false, configurationOnly: true,
    diagnostic: { stage: 'webhook_lookup', code: 'provider_http_error', httpStatus: 404 },
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
