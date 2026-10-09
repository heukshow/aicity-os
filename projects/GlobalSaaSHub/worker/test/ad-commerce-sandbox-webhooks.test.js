// Synthetic signature/provider responses and SQLite :memory: only. Never real PayPal.
import test from 'node:test';
import assert from 'node:assert/strict';
import { SandboxAdPayments } from '../src/ad-commerce-sandbox-payments.js';
import { SandboxAdWebhooks } from '../src/ad-commerce-sandbox-webhooks.js';
import { memoryStore, syntheticInput, syntheticPayPal, TEST_ENV } from './helpers/ad-commerce-fixtures.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';

const ENV = { ...TEST_ENV, PAYPAL_WEBHOOK_ID: 'SYNTHETIC-SANDBOX-WEBHOOK' };
const HEADERS = { 'content-type': 'application/json', 'paypal-transmission-id': 'synthetic-transmission',
  'paypal-transmission-time': '2026-10-07T00:00:00Z', 'paypal-cert-url': 'https://api-m.sandbox.paypal.com/v1/notifications/certs/SYNTHETIC',
  'paypal-auth-algo': 'SHA256withRSA', 'paypal-transmission-sig': 'synthetic-signature-not-a-secret' };
const request = (event, headers = HEADERS) => new Request('http://127.0.0.1:8789/sandbox/webhooks/paypal',
  { method: 'POST', headers, body: typeof event === 'string' ? event : JSON.stringify(event) });

function fixture(t) {
  t.mock.method(globalThis, 'fetch', () => { throw new Error('Real network forbidden in synthetic webhook tests'); });
  const f = memoryStore(), provider = syntheticPayPal();
  t.after(() => f.close());
  const signature = { result: 'SUCCESS', fail: false, bodies: [], calls: [] };
  const fetchImpl = async (url, init = {}) => {
    const parsed = new URL(url); assert.equal(parsed.origin, 'https://api-m.sandbox.paypal.com');
    assert.equal(init.redirect, 'error');
    if (parsed.pathname === '/v1/notifications/verify-webhook-signature') {
      signature.calls.push(parsed.pathname); signature.bodies.push(init.body);
      if (signature.fail) throw new Error('Synthetic verification outage');
      return new Response(JSON.stringify({ verification_status: signature.result }), { headers: { 'content-type': 'application/json' } });
    }
    return provider.fetchImpl(url, init);
  };
  const payments = new SandboxAdPayments(f.store, { env: ENV, fetchImpl });
  const webhooks = new SandboxAdWebhooks(f.store, payments, { env: ENV, fetchImpl });
  const count = table => f.native.prepare('SELECT count(*) AS n FROM ' + table).get().n;
  async function checkout(rotation = false) {
    const slot = rotation ? 'tool-rotation' : 'tool-primary';
    const created = await f.store.createDraft(syntheticInput(slot, [slot]));
    for (const role of ['logo', slot]) {
      const spec = AD_ASSET_SPECS[role];
      // File bytes are synthetic metadata fixtures; upload validation is covered separately.
      f.native.prepare('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)').run(
        crypto.randomUUID(), created.order.id, role, 'image/png', spec.width, spec.height, 1, 'b'.repeat(64), Buffer.from('x'));
    }
    await f.store.submitDraft(created.order.id);
    await f.store.review(created.order.id, { reviewer: 'synthetic-reviewer', decision: 'approve',
      notes: 'Synthetic webhook test review.', destinationChecked: true, claimsChecked: true });
    await f.store.reserveReviewedOrder(created.order.id);
    return (await payments.checkout(created.order.id)).order;
  }
  async function active(rotation = false) {
    const order = await checkout(rotation);
    provider.approve(order.provider_order);
    return payments.capture(order.id);
  }
  function completeAtProvider(order) {
    const record = provider.records.get(order.provider_order), unit = record.order.purchase_units[0];
    record.capture = { id: 'SYNTHETIC-CAPTURE-' + order.provider_order, status: 'COMPLETED', final_capture: true,
      amount: unit.amount, payee: { merchant_id: ENV.PAYPAL_MERCHANT_ID },
      custom_id: unit.custom_id, invoice_id: unit.invoice_id,
      supplementary_data: { related_ids: { order_id: order.provider_order } } };
    record.order.status = 'COMPLETED'; unit.payments = { captures: [record.capture] };
    return record.capture;
  }
  const completed = (order, capture, id = 'SYNTHETIC-COMPLETED') => ({
    id, event_type: 'PAYMENT.CAPTURE.COMPLETED',
    resource: { ...capture, supplementary_data: { related_ids: { order_id: order.provider_order } } },
  });
  const eventRow = id => f.native.prepare("SELECT * FROM ad_sale_events WHERE environment='sandbox' AND id=?").get(id);
  return { ...f, provider, signature, fetchImpl, payments, webhooks, count, checkout, active, completeAtProvider, completed, eventRow };
}

test('webhook constructor requires sandbox, explicit webhook credentials and matching transport context', t => {
  const f = fixture(t);
  assert.throws(() => new SandboxAdWebhooks(f.store, f.payments, { env: { ...ENV, PAYPAL_ENVIRONMENT: 'live' }, fetchImpl: f.fetchImpl }));
  assert.throws(() => new SandboxAdWebhooks(f.store, f.payments, { env: { ...ENV, PAYPAL_WEBHOOK_ID: '' }, fetchImpl: f.fetchImpl }));
  assert.throws(() => new SandboxAdWebhooks(f.store, f.payments, { env: { ...ENV, PAYPAL_MERCHANT_ID: 'OTHER' }, fetchImpl: f.fetchImpl }));
  assert.throws(() => new SandboxAdWebhooks(f.store, f.payments, { env: ENV }));
});
test('webhook transport refuses external/live hosts, URL credentials and redirects', async t => {
  const f = fixture(t);
  for (const url of ['https://api-m.paypal.com/', 'https://example.com/', 'https://user:pass@api-m.sandbox.paypal.com/']) {
    await assert.rejects(f.webhooks.fetch(url));
  }
  const redirected = new SandboxAdWebhooks(f.store, f.payments, { env: ENV, fetchImpl: async () => ({ redirected: true }) });
  await assert.rejects(redirected.fetch('https://api-m.sandbox.paypal.com/'));
  assert.equal(f.provider.calls.length, 0); assert.equal(f.signature.calls.length, 0);
});
test('invalid signature or verification outage persists no event or order change', async t => {
  const f = fixture(t), order = await f.active(), event = { id: 'SYNTHETIC-BAD-SIG',
    event_type: 'PAYMENT.CAPTURE.REVERSED', resource: { id: order.capture_id } };
  f.signature.result = 'FAILURE';
  assert.equal((await f.webhooks.handle(request(event))).status, 401);
  assert.equal(f.count('ad_sale_events'), 0); assert.equal((await f.store.get(order.id)).state, 'active');
  f.signature.fail = true;
  assert.equal((await f.webhooks.handle(request(event))).status, 503);
  assert.equal(f.count('ad_sale_events'), 0);
});
test('missing signature headers, malformed JSON, bad MIME and oversized bodies never call verification', async t => {
  const f = fixture(t), event = { id: 'SYNTHETIC-BODY', event_type: 'PAYMENT.CAPTURE.COMPLETED', resource: {} };
  for (const name of Object.keys(HEADERS).filter(name => name.startsWith('paypal-'))) {
    const headers = { ...HEADERS }; delete headers[name];
    assert.equal((await f.webhooks.handle(request(event, headers))).status, 400);
  }
  assert.equal((await f.webhooks.handle(request('{'))).status, 400);
  assert.equal((await f.webhooks.handle(request(event, { ...HEADERS, 'content-type': 'text/plain' }))).status, 415);
  assert.equal((await f.webhooks.handle(request(' '.repeat(65537)))).status, 413);
  assert.equal((await f.webhooks.handle(request(event, { ...HEADERS, 'content-length': '65537' }))).status, 413);
  assert.equal(f.signature.calls.length, 0); assert.equal(f.count('ad_sale_events'), 0);
});
test('signature verification retains the exact validated raw event text', async t => {
  const f = fixture(t);
  const raw = '{\n  "id":"SYNTHETIC-RAW", "event_type":"UNSUPPORTED.TEST", "resource":{"n":1.00,"text":"\\u0061"}\n}';
  assert.equal((await f.webhooks.handle(request(raw))).status, 200);
  assert.ok(f.signature.bodies[0].endsWith('"webhook_event":' + raw + '}'));
  assert.ok(f.eventRow('SYNTHETIC-RAW').processed_at);
});
test('completed event reconciles a known provider completion without any capture POST', async t => {
  const f = fixture(t), order = await f.checkout(), capture = f.completeAtProvider(order);
  const response = await f.webhooks.handle(request(f.completed(order, capture)));
  assert.equal(response.status, 200, await response.clone().text());
  const body = await response.json(); assert.equal(body.processed, true);
  assert.equal((await f.store.get(order.id)).state, 'active');
  assert.equal(f.provider.calls.filter(call => call.method === 'POST' && call.path.endsWith('/capture')).length, 0);
  assert.ok(f.eventRow('SYNTHETIC-COMPLETED').processed_at);
});
test('failed completion processing retains durable event for a successful idempotent retry', async t => {
  const f = fixture(t), order = await f.checkout(), capture = f.completeAtProvider(order), event = f.completed(order, capture, 'SYNTHETIC-RETRY');
  const original = f.payments.reconcile.bind(f.payments);
  f.payments.reconcile = async () => { throw new Error('synthetic processing failure'); };
  const first = await f.webhooks.handle(request(event));
  assert.equal(first.status, 503); assert.equal(f.eventRow(event.id).processed_at, null);
  assert.equal((await f.store.get(order.id)).state, 'checkout');
  f.payments.reconcile = original;
  const retry = await f.webhooks.handle(request(event));
  assert.equal(retry.status, 200); assert.equal((await retry.json()).duplicate, true);
  assert.equal(f.count('ad_sale_events'), 1); assert.ok(f.eventRow(event.id).processed_at);
  assert.equal((await f.store.get(order.id)).state, 'active');
  assert.equal(f.provider.calls.filter(call => call.method === 'POST' && call.path.endsWith('/capture')).length, 0);
});
test('full refund by reliable capture up-link stops the order and deduplicates audit', async t => {
  const f = fixture(t), order = await f.active(), event = { id: 'SYNTHETIC-REFUND', event_type: 'PAYMENT.CAPTURE.REFUNDED',
    resource: { id: 'SYNTHETIC-REFUND-RESOURCE', amount: { currency_code: order.currency, value: order.amount },
      links: [{ rel: 'up', href: 'https://api-m.sandbox.paypal.com/v2/payments/captures/' + order.capture_id }] } };
  const first = await f.webhooks.handle(request(event)); assert.equal(first.status, 200);
  assert.equal((await f.store.get(order.id)).state, 'refunded'); assert.equal(f.count('ad_sale_holds'), 0);
  const audits = f.count('ad_sale_audit');
  const duplicate = await f.webhooks.handle(request(event)); assert.equal(duplicate.status, 200);
  assert.equal((await duplicate.json()).duplicate, true); assert.equal(f.count('ad_sale_events'), 1);
  assert.equal(f.count('ad_sale_audit'), audits);
  await assert.rejects(f.payments.reconcile(order.id));
  assert.equal(f.provider.calls.filter(call => /refund/.test(call.path)).length, 0);
});
test('partial refund holds the ad without falsely declaring a full refund', async t => {
  const f = fixture(t), order = await f.active(), event = { id: 'SYNTHETIC-PARTIAL', event_type: 'PAYMENT.CAPTURE.REFUNDED',
    resource: { id: 'SYNTHETIC-PARTIAL-REFUND', amount: { currency_code: 'USD', value: '1.00' },
      supplementary_data: { related_ids: { capture_id: order.capture_id, order_id: order.provider_order } } } };
  assert.equal((await f.webhooks.handle(request(event))).status, 200);
  assert.equal((await f.store.get(order.id)).state, 'held'); assert.equal(f.count('ad_sale_holds'), 0);
});
test('refund resource ID and unrelated up-links are never mistaken for capture identity', async t => {
  const f = fixture(t), order = await f.active();
  const event = { id: 'SYNTHETIC-UNMATCHED-REFUND', event_type: 'PAYMENT.CAPTURE.REFUNDED',
    resource: { id: order.capture_id, links: [
      { rel: 'up', href: 'https://api-m.paypal.com/v2/payments/captures/' + order.capture_id },
      { rel: 'up', href: 'https://example.com/v2/payments/captures/' + order.capture_id },
    ] } };
  const response = await f.webhooks.handle(request(event));
  assert.equal(response.status, 202); assert.equal((await f.store.get(order.id)).state, 'active');
  assert.equal(f.eventRow(event.id).capture_ids_json, '[]'); assert.equal(f.eventRow(event.id).processed_at, null);
  assert.ok(f.provider.calls.every(call => !call.path.includes(order.capture_id) || call.path.startsWith('/v2/payments/captures/')));
});
test('dispute capture hints stop only the matching sandbox merchant order', async t => {
  const f = fixture(t), left = await f.active(true), right = await f.active(true);
  const event = { id: 'SYNTHETIC-DISPUTE', event_type: 'CUSTOMER.DISPUTE.CREATED',
    resource: { disputed_transactions: [{ seller_transaction_id: left.capture_id }] } };
  assert.equal((await f.webhooks.handle(request(event))).status, 200);
  assert.equal((await f.store.get(left.id)).state, 'held'); assert.equal((await f.store.get(right.id)).state, 'active');
  assert.equal(f.count('ad_sale_holds'), 1);
});
test('events cannot mutate an order belonging to a different configured merchant', async t => {
  const f = fixture(t), order = await f.checkout();
  f.native.prepare("UPDATE ad_sale_orders SET merchant_id='OTHER-SYNTHETIC-MERCHANT' WHERE id=?").run(order.id);
  const event = { id: 'SYNTHETIC-OTHER-MERCHANT', event_type: 'CHECKOUT.PAYMENT-APPROVAL.REVERSED', resource: { order_id: order.provider_order } };
  assert.equal((await f.webhooks.handle(request(event))).status, 202);
  assert.equal((await f.store.get(order.id)).state, 'checkout'); assert.equal(f.count('ad_sale_holds'), 1);
});
test('verified unmatched stop event persists and blocks capture after provider attachment', async t => {
  const f = fixture(t), event = { id: 'SYNTHETIC-EARLY-STOP', event_type: 'CHECKOUT.PAYMENT-APPROVAL.REVERSED',
    resource: { order_id: 'SYNTHETIC-ORDER-1' } };
  assert.equal((await f.webhooks.handle(request(event))).status, 202);
  assert.equal(f.eventRow(event.id).processed_at, null);
  const order = await f.checkout(); f.provider.approve(order.provider_order);
  await assert.rejects(f.payments.capture(order.id));
  assert.equal(f.provider.calls.filter(call => call.path.endsWith('/capture')).length, 0);
  const retry = await f.webhooks.handle(request(event));
  assert.equal(retry.status, 200); assert.equal((await f.store.get(order.id)).state, 'held');
});
test('stop on an uncertain capturing order preserves its reservation and blocks activation', async t => {
  const f = fixture(t), order = await f.checkout(); f.provider.approve(order.provider_order);
  const originalFetch = f.payments.fetch;
  f.payments.fetch = async (url, init) => {
    if (new URL(url).pathname.endsWith('/capture')) throw new Error('synthetic capture attempt timeout');
    return originalFetch(url, init);
  };
  await assert.rejects(f.payments.capture(order.id));
  assert.equal((await f.store.get(order.id)).state, 'capturing');
  const event = { id: 'SYNTHETIC-INFLIGHT-STOP', event_type: 'CHECKOUT.PAYMENT-APPROVAL.REVERSED', resource: { order_id: order.provider_order } };
  const response = await f.webhooks.handle(request(event));
  assert.equal(response.status, 200); assert.equal((await response.json()).retainedCapturing, 1);
  assert.equal((await f.store.get(order.id)).state, 'capturing'); assert.equal(f.count('ad_sale_holds'), 1);
  f.advance(31 * 60000); assert.equal(await f.payments.expire(), 0); assert.equal(f.count('ad_sale_holds'), 1);
  await assert.rejects(f.payments.reconcile(order.id));
});
test('a reused event ID cannot replace the durable identity of a verified event', async t => {
  const f = fixture(t);
  const event = { id: 'SYNTHETIC-IDENTITY', event_type: 'PAYMENT.CAPTURE.REVERSED', resource: { id: 'SYNTHETIC-CAPTURE-ONE' } };
  assert.equal((await f.webhooks.handle(request(event))).status, 202);
  const changed = { ...event, resource: { id: 'SYNTHETIC-CAPTURE-TWO' } };
  assert.equal((await f.webhooks.handle(request(changed))).status, 409);
  assert.equal(f.eventRow(event.id).capture_ids_json, '["SYNTHETIC-CAPTURE-ONE"]');
});

test('official api.sandbox capture-link hints are parsed without fetching supplied links', async t => {
  const f = fixture(t), order = await f.active(), event = { id: 'SYNTHETIC-SANDBOX-ALIAS', event_type: 'PAYMENT.CAPTURE.REFUNDED',
    resource: { id: 'SYNTHETIC-REFUND-ALIAS', amount: { currency_code: order.currency, value: order.amount },
      links: [{ rel: 'up', href: 'https://api.sandbox.paypal.com/v2/payments/captures/' + order.capture_id }] } };
  const count = f.provider.calls.filter(call => call.path.startsWith('/v2/payments/captures/')).length;
  assert.equal((await f.webhooks.handle(request(event))).status, 200);
  assert.equal((await f.store.get(order.id)).state, 'refunded');
  assert.equal(f.provider.calls.filter(call => call.path.startsWith('/v2/payments/captures/')).length, count);
});
