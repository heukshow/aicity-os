import assert from 'node:assert/strict';
import test from 'node:test';
import { checkPayPalReadiness } from '../src/paypal.js';

const registeredEvents = [
  'PAYMENT.CAPTURE.COMPLETED', 'PAYMENT.CAPTURE.PENDING',
  'PAYMENT.CAPTURE.DENIED', 'PAYMENT.CAPTURE.DECLINED',
  'PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED',
  'CUSTOMER.DISPUTE.CREATED', 'CUSTOMER.DISPUTE.UPDATED', 'CUSTOMER.DISPUTE.RESOLVED',
];
const optionalEvent = 'CHECKOUT.PAYMENT-APPROVAL.REVERSED';

async function probe(eventNames) {
  const env = {
    PAYPAL_ENVIRONMENT: 'live', PAYPAL_CLIENT_ID: 'SYNTHETIC-CLIENT',
    PAYPAL_CLIENT_SECRET: 'SYNTHETIC-SECRET', PAYPAL_WEBHOOK_ID: 'SYNTHETIC-WEBHOOK',
  };
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
