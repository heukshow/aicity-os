import assert from 'node:assert/strict';
import test from 'node:test';
import worker from '../src/entry.js';

const baseEnv = Object.freeze({
  ALLOWED_ORIGIN: 'https://coshuma.com',
  CHECKOUT_ENABLED: 'false',
});

test('health explicitly reports checkout closed during staging', async () => {
  const response = await worker.fetch(new Request('https://worker.example/health'), { ...baseEnv });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true, checkoutConfigured: false });
});

test('sponsored placements fail safe before D1 is available', async () => {
  const response = await worker.fetch(
    new Request('https://worker.example/v1/sponsored/placements?path=%2Ftool%2Fexample.html'),
    { ...baseEnv },
  );
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { placements: [], ready: false });
});

test('checkout creation remains unavailable while release gate is false', async () => {
  const request = new Request('https://worker.example/v1/orders', {
    method: 'POST',
    headers: { origin: 'https://coshuma.com', 'content-type': 'application/json' },
    body: JSON.stringify({ productId: 'tool_page_7' }),
  });
  const response = await worker.fetch(request, { ...baseEnv });
  assert.equal(response.status, 503);
  assert.deepEqual(await response.json(), { error: 'Checkout is unavailable' });
});

test('cross-origin preflight is rejected before any payment route', async () => {
  const response = await worker.fetch(new Request('https://worker.example/v1/orders', {
    method: 'OPTIONS',
    headers: { origin: 'https://evil.example' },
  }), { ...baseEnv });
  assert.equal(response.status, 403);
});

test('invalid sponsored page paths fail closed', async () => {
  const response = await worker.fetch(
    new Request('https://worker.example/v1/sponsored/placements?path=%2F%2Fevil.example'),
    { ...baseEnv },
  );
  assert.equal(response.status, 400);
});
