import test from 'node:test';
import assert from 'node:assert/strict';
import { createAdSandboxHandler } from '../src/ad-commerce-sandbox-http.js';
import { SandboxAdPayments } from '../src/ad-commerce-sandbox-payments.js';
import { SandboxAdWebhooks } from '../src/ad-commerce-sandbox-webhooks.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';
import { memoryStore, syntheticInput, png, syntheticPayPal, TEST_REVIEW_KEY, TEST_ENV } from './helpers/ad-commerce-fixtures.js';
const origin = 'http://127.0.0.1:8789';
function fixture(t) {
  const f = memoryStore(), provider = syntheticPayPal();
  t.after(() => f.close());
  const payments = new SandboxAdPayments(f.store, { env: TEST_ENV, fetchImpl: provider.fetchImpl });
  const webhooks = new SandboxAdWebhooks(f.store, payments, { env: { ...TEST_ENV, PAYPAL_WEBHOOK_ID: 'SYNTHETIC-WEBHOOK' }, fetchImpl: provider.fetchImpl });
  const handle = createAdSandboxHandler({ store: f.store, payments, webhooks, reviewKey: TEST_REVIEW_KEY, environment: 'sandbox', origin });
  const call = (method, path, { token, body, bytes, contentType = 'image/png', requestOrigin = origin } = {}) =>
    handle(new Request(origin + '/sandbox' + path, { method, headers: {
      ...(token ? { Authorization: 'Bearer ' + token } : {}),
      ...(method !== 'GET' ? { Origin: requestOrigin } : {}),
      ...(bytes ? { 'Content-Type': contentType } : body !== undefined ? { 'Content-Type': 'application/json' } : {}),
    }, body: bytes || (body !== undefined ? JSON.stringify(body) : undefined) }));
  return { ...f, provider, payments, handle, call };
}
async function create(f, raw = syntheticInput()) {
  const response = await f.call('POST', '/orders', { body: raw });
  assert.equal(response.status, 201, await response.clone().text());
  return response.json();
}
async function upload(f, created) {
  const id = created.order.id, token = created.accessToken;
  for (const role of ['logo', ...JSON.parse(created.order.quote_json).slots]) {
    const spec = AD_ASSET_SPECS[role];
    const response = await f.call('PUT', '/orders/' + id + '/assets/' + role, { token, bytes: png(spec.width, spec.height) });
    assert.equal(response.status, 200, await response.clone().text());
  }
}
async function prepared(f, raw = syntheticInput()) {
  const created = await create(f, raw), id = created.order.id, token = created.accessToken;
  await upload(f, created);
  assert.equal((await f.call('POST', '/orders/' + id + '/submit', { token })).status, 200);
  assert.equal((await f.call('POST', '/admin/orders/' + id + '/review', { token: TEST_REVIEW_KEY,
    body: { decision: 'approve', destinationChecked: true, claimsChecked: true, notes: 'Synthetic review complete.' } })).status, 200);
  assert.equal((await f.call('POST', '/orders/' + id + '/reserve', { token })).status, 200);
  return created;
}
async function paid(f, created) {
  const id = created.order.id, token = created.accessToken;
  const checkout = await f.call('POST', '/orders/' + id + '/checkout', { token });
  assert.equal(checkout.status, 200, await checkout.clone().text());
  const result = await checkout.json();
  assert.ok(result.approvalUrl.startsWith('https://www.sandbox.paypal.com/'));
  f.provider.approve(result.order.provider_order);
  const capture = await f.call('POST', '/orders/' + id + '/capture', { token });
  assert.equal(capture.status, 200, await capture.clone().text());
  return (await capture.json()).order;
}

for (const [product, slots] of [['tool-primary', ['tool-primary']], ['P2', ['tool-primary', 'buyer-intent-top']]]) {
  test('synthetic HTTP lifecycle: ' + product + ' selection through actual PNG, review, mock payment, publication and expiry', async t => {
    const f = fixture(t);
    const catalog = await (await f.call('GET', '/catalog')).json();
    assert.equal(catalog.environment, 'sandbox'); assert.equal(catalog.slots.length, 8); assert.equal(catalog.bundles.length, 3);
    const created = await prepared(f, syntheticInput(product, slots));
    for (const slot of slots) assert.deepEqual((await (await f.call('GET', '/placements/' + slot)).json()).placements, []);
    const active = await paid(f, created);
    assert.equal(active.state, 'active'); assert.equal(active.payment_environment, 'sandbox');
    assert.equal(Date.parse(active.ends_at) - Date.parse(active.starts_at), 30 * 86400000);
    for (const slot of slots) {
      const listed = await (await f.call('GET', '/placements/' + slot)).json();
      assert.equal(listed.placements.length, 1);
      assert.doesNotMatch(JSON.stringify(listed), /access_hash|accessToken|test@example.com|SYNTHETIC-SECRET|capture_id/);
      const image = await f.call('GET', '/assets/' + active.id + '/' + slot);
      assert.equal(image.status, 200); assert.equal(image.headers.get('content-type'), 'image/png');
      assert.deepEqual(new Uint8Array(await image.arrayBuffer()), new Uint8Array(png(AD_ASSET_SPECS[slot].width, AD_ASSET_SPECS[slot].height)));
      const preview = await f.call('GET', '/preview/' + slot);
      assert.match(await preview.text(), /Sponsored — SANDBOX TEST/);
    }
    assert.equal((await f.call('POST', '/orders/' + active.id + '/capture', { token: created.accessToken })).status, 200); // Idempotent retry.
    assert.equal(f.provider.calls.filter(item => item.method === 'POST' && item.path.endsWith('/capture')).length, 1);
    f.advance(30 * 86400000);
    for (const slot of slots) {
      assert.equal((await (await f.call('GET', '/placements/' + slot)).json()).placements.length, 0);
      assert.equal((await f.call('GET', '/assets/' + active.id + '/' + slot)).status, 404);
    }
    const expired = await f.call('POST', '/admin/expire', { token: TEST_REVIEW_KEY });
    assert.equal(expired.status, 200);
    assert.equal((await f.store.get(active.id)).state, 'ended');
    assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_holds').get().n, 0);
  });
}
test('applicant bearer cannot read another order or impersonate reviewer', async t => {
  const f = fixture(t), a = await create(f), b = await create(f);
  assert.equal((await f.call('GET', '/orders/' + a.order.id, { token: b.accessToken })).status, 403);
  assert.equal((await f.call('POST', '/admin/orders/' + a.order.id + '/review', { token: a.accessToken,
    body: { reviewer: 'admin', decision: 'approve' } })).status, 403);
  assert.equal((await f.call('POST', '/admin/expire', { token: a.accessToken })).status, 403);
  assert.equal(f.provider.calls.length, 0);
});
test('invalid/oversized uploads return input errors without storing files', async t => {
  const f = fixture(t), created = await create(f), path = '/orders/' + created.order.id + '/assets/logo', token = created.accessToken;
  for (const [bytes, contentType, status] of [
    [Buffer.from('<svg/>'), 'image/svg+xml', 415], [Buffer.from('bad'), 'image/png', 422],
    [png(10, 10), 'image/png', 422], [Buffer.alloc(100001), 'image/png', 413],
  ]) assert.equal((await f.call('PUT', path, { token, bytes, contentType })).status, status);
  assert.equal((await f.store.files(created.order.id)).length, 0);
});
test('missing material, approval checks and reservation block payment before provider calls', async t => {
  const f = fixture(t), c = await create(f), token = c.accessToken, base = '/orders/' + c.order.id;
  assert.equal((await f.call('POST', base + '/submit', { token })).status, 409);
  assert.equal((await f.call('POST', base + '/checkout', { token })).status, 409);
  await upload(f, c); await f.call('POST', base + '/submit', { token });
  assert.equal((await f.call('POST', '/admin/orders/' + c.order.id + '/review', { token: TEST_REVIEW_KEY,
    body: { decision: 'approve', notes: 'Unchecked synthetic claims.', destinationChecked: false, claimsChecked: true } })).status, 422);
  assert.equal(f.provider.calls.length, 0);
});
test('upload after submission is locked and draft images are not public', async t => {
  const f = fixture(t), c = await prepared(f), token = c.accessToken;
  assert.equal((await f.call('PUT', '/orders/' + c.order.id + '/assets/logo', { token, bytes: png(400,400) })).status, 409);
  assert.equal((await f.call('GET', '/assets/' + c.order.id + '/logo')).status, 404);
});
test('foreign origins and live handlers are rejected without altering data', async t => {
  const f = fixture(t);
  assert.equal((await f.call('POST', '/orders', { body: syntheticInput(), requestOrigin: 'https://example.com' })).status, 403);
  assert.equal((await f.handle(new Request('http://attacker.invalid/sandbox/catalog'))).status, 403);
  assert.throws(() => createAdSandboxHandler({ store: f.store, payments: f.payments, reviewKey: TEST_REVIEW_KEY, environment: 'live', origin }));
  assert.throws(() => createAdSandboxHandler({ store: f.store, payments: f.payments, reviewKey: TEST_REVIEW_KEY, environment: 'sandbox', origin: 'https://coshuma.com' }));
  assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_orders').get().n, 0);
});
test('reservation expiry blocks provider checkout and leaves publication empty', async t => {
  const f = fixture(t), c = await prepared(f);
  f.advance(31 * 60000);
  assert.equal((await f.call('POST', '/orders/' + c.order.id + '/checkout', { token: c.accessToken })).status, 409);
  assert.equal(f.provider.calls.length, 0);
});
test('stored synthetic stop evidence hides public content even before cleanup', async t => {
  const f = fixture(t), c = await prepared(f), active = await paid(f, c);
  f.native.prepare("INSERT INTO ad_sale_events(environment,id,event_type,provider_order,received_at) VALUES('sandbox',?,?,?,?)")
    .run('SYNTHETIC-STOP', 'PAYMENT.CAPTURE.REVERSED', active.provider_order, f.store.now());
  assert.equal((await (await f.call('GET', '/placements/tool-primary')).json()).placements.length, 0);
  assert.equal((await f.call('GET', '/assets/' + active.id + '/logo')).status, 404);
});

test('authenticated reviewer can inspect submitted bytes before approval; applicant cannot', async t => {
  const f = fixture(t), c = await create(f); await upload(f, c);
  await f.call('POST', '/orders/' + c.order.id + '/submit', { token: c.accessToken });
  const path = '/admin/orders/' + c.order.id;
  assert.equal((await f.call('GET', path, { token: TEST_REVIEW_KEY })).status, 200);
  const image = await f.call('GET', path + '/assets/logo', { token: TEST_REVIEW_KEY });
  assert.equal(image.status, 200); assert.deepEqual(new Uint8Array(await image.arrayBuffer()), new Uint8Array(png(400, 400)));
  assert.equal((await f.call('GET', path + '/assets/logo', { token: c.accessToken })).status, 403);
});
test('new reservation reclaims ended campaign through demand-driven expiry', async t => {
  const f = fixture(t), first = await prepared(f), active = await paid(f, first);
  f.advance(30 * 86400000);
  const next = await prepared(f);
  assert.equal((await f.store.get(active.id)).state, 'ended');
  assert.equal(f.native.prepare('SELECT order_id FROM ad_sale_holds').get().order_id, next.order.id);
});
test('preview includes a nonce-protected timer for the exact campaign end', async t => {
  const f = fixture(t), c = await prepared(f), active = await paid(f, c);
  const response = await f.call('GET', '/preview/tool-primary'), html = await response.text();
  assert.match(response.headers.get('content-security-policy'), /script-src 'nonce-[a-z0-9]+'/);
  assert.ok(html.includes('const remainingAtRender=' + (Date.parse(active.ends_at) - f.store.clock().getTime())));
  assert.match(html, /querySelector\("article"\)\?\.remove\(\)/);
  assert.doesNotMatch(html, /accessToken|Authorization|SYNTHETIC-SECRET/);
});

test('HTTP webhook rejects missing signature headers and accepts a verified synthetic stop without browser Origin', async t => {
  const f = fixture(t), c = await prepared(f), active = await paid(f, c), path = origin + '/sandbox/webhooks/paypal';
  const event = { id: 'SYNTHETIC-HTTP-EVENT', event_type: 'PAYMENT.CAPTURE.REVERSED', resource: {
    id: active.capture_id, amount: { value: active.amount, currency_code: 'USD' },
    supplementary_data: { related_ids: { order_id: active.provider_order } } } };
  const unsigned = await f.handle(new Request(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(event) }));
  assert.equal(unsigned.status, 400); assert.equal((await f.store.get(active.id)).state, 'active');
  const headers = { 'Content-Type': 'application/json', 'paypal-transmission-id': 'SYNTHETIC-TRANSMISSION',
    'paypal-transmission-time': new Date().toISOString(), 'paypal-cert-url': 'https://api-m.sandbox.paypal.com/SYNTHETIC-CERT',
    'paypal-auth-algo': 'SHA256withRSA', 'paypal-transmission-sig': 'SYNTHETIC-SIGNATURE-NOT-REAL' };
  for (let n = 0; n < 2; n++) {
    const response = await f.handle(new Request(path, { method: 'POST', headers, body: JSON.stringify(event) }));
    assert.equal(response.status, 200, await response.clone().text());
  }
  assert.equal((await f.store.get(active.id)).state, 'refunded');
  assert.equal((await (await f.call('GET', '/placements/tool-primary')).json()).placements.length, 0);
  assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_events').get().n, 1);
  assert.equal(f.provider.calls.some(call => call.path.includes('/refund')), false);
});
