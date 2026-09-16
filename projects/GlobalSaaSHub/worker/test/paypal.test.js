import assert from 'node:assert/strict';
import test from 'node:test';
import { capturePayPalOrder } from '../src/paypal.js';

const env = Object.freeze({
  PAYPAL_ENVIRONMENT: 'sandbox',
  PAYPAL_CLIENT_ID: 'public-id',
  PAYPAL_CLIENT_SECRET: 'secret',
});

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

function tokenResponse() {
  return json({ access_token: 'token' });
}

test('capture is skipped when PayPal already reports the order completed', async () => {
  const calls = [];
  const fetchImpl = async (url, options = {}) => {
    calls.push({ url, method: options.method || 'GET' });
    if (url.endsWith('/v1/oauth2/token')) return tokenResponse();
    if (url.endsWith('/v2/checkout/orders/ORDER-1')) {
      return json({ status: 'COMPLETED', id: 'ORDER-1' });
    }
    throw new Error(`unexpected request ${url}`);
  };

  const result = await capturePayPalOrder(env, 'ORDER-1', 'capture-local-1', fetchImpl);
  assert.equal(result.status, 'COMPLETED');
  assert.equal(calls.some((call) => call.url.endsWith('/capture')), false);
});

test('capture failure recovers only when a fresh PayPal read confirms completion', async () => {
  let orderReads = 0;
  let capturePosts = 0;
  const fetchImpl = async (url, options = {}) => {
    if (url.endsWith('/v1/oauth2/token')) return tokenResponse();
    if (url.endsWith('/v2/checkout/orders/ORDER-2/capture')) {
      capturePosts += 1;
      return json({ name: 'ORDER_ALREADY_CAPTURED' }, 422);
    }
    if (url.endsWith('/v2/checkout/orders/ORDER-2')) {
      orderReads += 1;
      return orderReads === 1
        ? json({ status: 'APPROVED', id: 'ORDER-2' })
        : json({ status: 'COMPLETED', id: 'ORDER-2' });
    }
    throw new Error(`unexpected request ${url}`);
  };

  const result = await capturePayPalOrder(env, 'ORDER-2', 'capture-local-2', fetchImpl);
  assert.equal(result.status, 'COMPLETED');
  assert.equal(capturePosts, 1);
  assert.equal(orderReads, 2);
});

test('capture failure remains an error when provider state is not completed', async () => {
  const fetchImpl = async (url) => {
    if (url.endsWith('/v1/oauth2/token')) return tokenResponse();
    if (url.endsWith('/v2/checkout/orders/ORDER-3/capture')) return json({ error: 'failed' }, 500);
    if (url.endsWith('/v2/checkout/orders/ORDER-3')) return json({ status: 'APPROVED', id: 'ORDER-3' });
    throw new Error(`unexpected request ${url}`);
  };

  await assert.rejects(
    () => capturePayPalOrder(env, 'ORDER-3', 'capture-local-3', fetchImpl),
    /PayPal request failed \(500\)/,
  );
});
