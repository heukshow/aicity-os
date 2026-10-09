// Local SQLite + synthetic provider responses only. No real PayPal API or credentials.
import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { AdStore } from '../src/ad-commerce-store.js';
import { SandboxAdPayments } from '../src/ad-commerce-sandbox-payments.js';
import { CATALOG_VERSION } from '../src/ad-commerce-catalog.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';

const ENV = { PAYPAL_ENVIRONMENT: 'sandbox', PAYPAL_CLIENT_ID: 'synthetic-client',
  PAYPAL_CLIENT_SECRET: 'synthetic-secret-not-a-credential', PAYPAL_MERCHANT_ID: 'SYNTHETIC-MERCHANT' };
const REVIEW = { reviewer: 'synthetic-reviewer', decision: 'approve', notes: 'Synthetic metadata only.',
  destinationChecked: true, claimsChecked: true };

function fixture(t) {
  t.mock.method(globalThis, 'fetch', () => { throw new Error('Real network forbidden by offline test'); });
  const native = new DatabaseSync(':memory:');
  native.exec('PRAGMA foreign_keys=ON');
  for (const file of ['0004_sponsorship_sales.sql', '0005_image_ad_fulfilment.sql']) {
    native.exec(readFileSync(new URL('../migrations/' + file, import.meta.url), 'utf8'));
  }
  t.after(() => native.close());
  const db = {
    prepare(sql) { return { bind(...values) {
      const statement = native.prepare(sql);
      return {
        async first() { return statement.get(...values) ?? null; },
        async all() { return { results: statement.all(...values) }; },
        run() { return { success: true, meta: { changes: Number(statement.run(...values).changes) } }; },
      };
    } }; },
    async batch(statements) {
      native.exec('BEGIN IMMEDIATE');
      try { const result = statements.map(statement => statement.run()); native.exec('COMMIT'); return result; }
      catch (error) { native.exec('ROLLBACK'); throw error; }
    },
  };
  let time = Date.now();
  const store = new AdStore(db, { environment: 'sandbox', clock: () => new Date(time) });
  const mock = { calls: [], orders: new Map(), captures: new Map(), createIds: new Map(), captureIds: new Map(),
    creates: 0, captureEffects: 0, timeoutAfterCapture: false, failOrderRead: false, onOrderRead: null, failCaptureBeforeEffect: false, onCaptureRead: null };
  const response = data => new Response(JSON.stringify(data), { headers: { 'content-type': 'application/json' } });
  const fetchImpl = async (url, options = {}) => {
    const parsed = new URL(url), method = options.method || 'GET';
    assert.equal(parsed.origin, 'https://api-m.sandbox.paypal.com');
    assert.equal(options.redirect, 'error');
    mock.calls.push({ method, path: parsed.pathname, requestId: options.headers?.['PayPal-Request-Id'] });
    if (parsed.pathname === '/v1/oauth2/token') return response({ access_token: 'synthetic-token' });
    if (parsed.pathname === '/v2/checkout/orders' && method === 'POST') {
      const requestId = options.headers['PayPal-Request-Id'];
      if (mock.createIds.has(requestId)) return response(mock.orders.get(mock.createIds.get(requestId)));
      const id = 'SYNTHETIC-ORDER-' + (++mock.creates), payload = JSON.parse(options.body);
      const order = { ...payload, id, status: 'CREATED',
        links: [{ rel: 'approve', href: 'https://www.sandbox.paypal.com/checkoutnow?token=' + id }] };
      mock.orders.set(id, order); mock.createIds.set(requestId, id);
      return response(order);
    }
    const orderMatch = /^\/v2\/checkout\/orders\/([^/]+)(\/capture)?$/.exec(parsed.pathname);
    if (orderMatch) {
      const order = mock.orders.get(orderMatch[1]); assert.ok(order);
      if (!orderMatch[2]) {
        if (mock.failOrderRead) throw new Error('synthetic read timeout');
        if (mock.onOrderRead) await mock.onOrderRead(order);
        return response(order);
      }
      assert.equal(method, 'POST');
      if (mock.failCaptureBeforeEffect) throw new Error('synthetic timeout during capture request');
      const requestId = options.headers['PayPal-Request-Id'];
      if (!mock.captureIds.has(requestId)) {
        assert.equal(order.status, 'APPROVED');
        const unit = order.purchase_units[0], id = 'SYNTHETIC-CAPTURE-' + (++mock.captureEffects);
        const capture = { id, status: 'COMPLETED', final_capture: true,
          amount: structuredClone(unit.amount), payee: { merchant_id: ENV.PAYPAL_MERCHANT_ID },
          invoice_id: unit.invoice_id, custom_id: unit.custom_id,
          supplementary_data: { related_ids: { order_id: order.id } } };
        mock.captures.set(id, capture); mock.captureIds.set(requestId, id);
        order.status = 'COMPLETED';
        unit.payments = { captures: [structuredClone(capture)] };
      }
      if (mock.timeoutAfterCapture) { mock.timeoutAfterCapture = false; throw new Error('synthetic response lost after capture'); }
      return response(order);
    }
    const captureMatch = /^\/v2\/payments\/captures\/([^/]+)$/.exec(parsed.pathname);
    if (captureMatch) {
      const capture = mock.captures.get(captureMatch[1]); assert.ok(capture);
      if (mock.onCaptureRead) await mock.onCaptureRead(capture, mock.orders.get(capture.supplementary_data.related_ids.order_id));
      return response(capture);
    }
    assert.fail('Unexpected synthetic request: ' + method + ' ' + parsed.pathname);
  };
  const payments = new SandboxAdPayments(store, { env: ENV, fetchImpl });
  const advance = ms => { time += ms; };
  const count = (table, id) => native.prepare('SELECT count(*) AS n FROM ' + table + (id ? ' WHERE order_id=?' : '')).get(...(id ? [id] : [])).n;
  async function prepared({ bundle = false, reserve = true, review = true } = {}) {
    const slots = bundle ? ['tool-primary', 'buyer-intent-top'] : ['tool-primary'];
    const { order } = await store.createDraft({ product: bundle ? 'P2' : 'tool-primary', days: 30,
      rightsConfirmed: true, termsVersion: CATALOG_VERSION, company: 'SYNTHETIC LOCAL TEST',
      productName: 'Synthetic application', email: 'test@example.com', claims: 'Synthetic metadata, not advertiser evidence.',
      items: slots.map(slot => ({ slot, headline: 'Synthetic image advertisement',
        description: 'Synthetic metadata to exercise an isolated payment lifecycle.',
        button: 'View product', alt: 'Synthetic placement test asset', url: 'https://example.com/product' })) });
    for (const role of ['logo', ...slots]) {
      const spec = AD_ASSET_SPECS[role];
      // One-byte blobs exercise database guards; this is deliberately not an image validator test.
      native.prepare('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)').run(
        crypto.randomUUID(), order.id, role, 'image/png', spec.width, spec.height, 1, 'b'.repeat(64), Buffer.from('x'));
    }
    await store.submitDraft(order.id);
    if (review) await store.review(order.id, REVIEW);
    if (reserve && review) await store.reserveReviewedOrder(order.id);
    return store.get(order.id);
  }
  async function checkout(options) {
    const order = await prepared(options), result = await payments.checkout(order.id);
    return { order: result.order, provider: mock.orders.get(result.order.provider_order), approvalUrl: result.approvalUrl };
  }
  function approve(provider) { provider.status = 'APPROVED'; }
  return { native, db, store, payments, mock, fetchImpl, advance, count, prepared, checkout, approve };
}

test('sandbox constructor refuses live, missing credentials and an implicit network transport', t => {
  const f = fixture(t);
  assert.throws(() => new SandboxAdPayments(f.store, { env: { ...ENV, PAYPAL_ENVIRONMENT: 'live' }, fetchImpl: f.fetchImpl }));
  assert.throws(() => new SandboxAdPayments(f.store, { env: ENV }));
  assert.throws(() => new SandboxAdPayments(f.store, { env: { ...ENV, PAYPAL_CLIENT_SECRET: '' }, fetchImpl: f.fetchImpl }));
  assert.equal(f.mock.calls.length, 0);
});

test('transport rejects live, unrelated hosts, credentials in URLs and redirects before disclosure', async t => {
  const f = fixture(t);
  for (const url of ['https://api-m.paypal.com/v2/checkout/orders', 'https://example.com/',
    'https://api-m.sandbox.paypal.com.evil.example/', 'https://user:pass@api-m.sandbox.paypal.com/']) {
    await assert.rejects(f.payments.fetch(url));
  }
  assert.equal(f.mock.calls.length, 0);
  const redirected = new SandboxAdPayments(f.store, { env: ENV, fetchImpl: async () => ({ redirected: true }) });
  await assert.rejects(redirected.fetch('https://api-m.sandbox.paypal.com/v2/checkout/orders'));
});

test('checkout requires completed review and every valid reservation without provider calls', async t => {
  const f = fixture(t);
  const submitted = await f.prepared({ review: false });
  await assert.rejects(f.payments.checkout(submitted.id));
  const unreserved = await f.prepared({ reserve: false });
  await assert.rejects(f.payments.checkout(unreserved.id));
  assert.equal(f.mock.calls.length, 0);
});

test('synthetic bundle progresses through checkout, capture, atomic activation and exact expiry', async t => {
  const f = fixture(t), { order, provider, approvalUrl } = await f.checkout({ bundle: true });
  assert.equal(order.state, 'checkout'); assert.equal(order.payment_verified_at, null);
  assert.match(approvalUrl, /^https:\/\/www\.sandbox\.paypal\.com\/checkoutnow\?token=/);
  const unit = provider.purchase_units[0];
  assert.equal(unit.reference_id, order.id); assert.equal(unit.custom_id, order.id);
  assert.equal(unit.invoice_id, order.reference); assert.equal(unit.amount.value, order.amount);
  f.approve(provider);
  const active = await f.payments.capture(order.id);
  assert.equal(active.state, 'active'); assert.equal(active.payment_environment, 'sandbox');
  assert.ok(active.payment_verified_at); assert.equal(f.count('ad_sale_holds', order.id), 2);
  const holds = f.native.prepare('SELECT expires_at FROM ad_sale_holds WHERE order_id=?').all(order.id);
  assert.ok(holds.every(hold => hold.expires_at === active.ends_at));
  assert.equal(Date.parse(active.ends_at) - Date.parse(active.starts_at), 30 * 86400000);
  f.advance(30 * 86400000 - 1); assert.equal(await f.payments.expire(), 0);
  f.advance(1); assert.equal(await f.payments.expire(), 1);
  assert.equal((await f.store.get(order.id)).state, 'ended'); assert.equal(f.count('ad_sale_holds', order.id), 0);
  assert.equal(await f.payments.expire(), 0);
  const calls = f.mock.calls.length;
  assert.equal((await f.payments.capture(order.id)).state, 'ended');
  assert.equal(f.mock.calls.length, calls);
});

test('checkout retries and concurrent instances use one provider order and one audit', async t => {
  const f = fixture(t), order = await f.prepared();
  const other = new SandboxAdPayments(f.store, { env: ENV, fetchImpl: f.fetchImpl });
  const results = await Promise.all([f.payments.checkout(order.id), other.checkout(order.id)]);
  assert.equal(results[0].order.provider_order, results[1].order.provider_order);
  assert.equal(f.mock.creates, 1);
  const retry = await f.payments.checkout(order.id);
  assert.equal(retry.order.provider_order, results[0].order.provider_order);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE action='sandbox_checkout_created'").get().n, 1);
  assert.equal(new Set(f.mock.calls.filter(call => call.path === '/v2/checkout/orders').map(call => call.requestId)).size, 1);
});

test('capture retries and concurrent instances never add a second charge or successful audit', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  const other = new SandboxAdPayments(f.store, { env: ENV, fetchImpl: f.fetchImpl });
  const results = await Promise.all([f.payments.capture(order.id), other.capture(order.id)]);
  assert.ok(results.every(result => result.state === 'active')); assert.equal(f.mock.captureEffects, 1);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE action='sandbox_payment_verified'").get().n, 1);
  const calls = f.mock.calls.length; await f.payments.capture(order.id);
  assert.equal(f.mock.calls.length, calls);
});

test('unapproved capture remains checkout and its expired reservation can be reclaimed', async t => {
  const f = fixture(t), { order, provider } = await f.checkout();
  await assert.rejects(f.payments.capture(order.id));
  assert.equal(f.mock.captureEffects, 0); assert.equal((await f.store.get(order.id)).state, 'checkout');
  assert.equal(f.mock.calls.filter(call => call.path.endsWith('/capture')).length, 0);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE action='sandbox_capture_started'").get().n, 0);
  f.advance(31 * 60000);
  const competitor = await f.prepared();
  assert.equal(f.count('ad_sale_holds', order.id), 0); assert.equal(f.count('ad_sale_holds', competitor.id), 1);
  f.approve(provider); const calls = f.mock.calls.length;
  await assert.rejects(f.payments.capture(order.id));
  assert.equal(f.mock.calls.length, calls); assert.equal(f.mock.captureEffects, 0);
});

test('lost capture response is reconciled after reservation expiry without another capture', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  f.mock.timeoutAfterCapture = true;
  await assert.rejects(f.payments.capture(order.id));
  assert.equal((await f.store.get(order.id)).state, 'capturing'); assert.equal(f.mock.captureEffects, 1);
  f.advance(31 * 60000);
  assert.equal(await f.payments.expire(), 0); assert.equal(f.count('ad_sale_holds', order.id), 1);
  const competitor = await f.prepared({ reserve: false });
  await assert.rejects(f.store.reserveReviewedOrder(competitor.id));
  const active = await f.payments.reconcile(order.id);
  assert.equal(active.state, 'active'); assert.equal(f.mock.captureEffects, 1);
  assert.equal(f.mock.calls.filter(call => call.path.endsWith('/capture')).length, 1);
});

test('failed preflight provider read leaves checkout and a later explicit capture can retry', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  f.mock.failOrderRead = true; await assert.rejects(f.payments.capture(order.id));
  assert.equal((await f.store.get(order.id)).state, 'checkout'); assert.equal(f.mock.captureEffects, 0);
  assert.equal(f.count('ad_sale_holds', order.id), 1);
  f.mock.failOrderRead = false; assert.equal((await f.payments.capture(order.id)).state, 'active');
  assert.equal(f.mock.captureEffects, 1);
});

test('provider-read reconciliation leaves approved checkout unchanged without charging', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  await assert.rejects(f.payments.reconcile(order.id));
  assert.equal(f.mock.captureEffects, 0); assert.equal((await f.store.get(order.id)).state, 'checkout');
});

test('expired checkout refuses capture without provider calls', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  f.advance(31 * 60000); const calls = f.mock.calls.length;
  await assert.rejects(f.payments.capture(order.id));
  assert.equal((await f.store.get(order.id)).state, 'checkout'); assert.equal(f.mock.calls.length, calls);
});

test('changed merchant cannot capture or reconcile a saved sandbox order', async t => {
  const f = fixture(t), { order } = await f.checkout(), calls = f.mock.calls.length;
  const changed = new SandboxAdPayments(f.store, { env: { ...ENV, PAYPAL_MERCHANT_ID: 'OTHER-SYNTHETIC-MERCHANT' }, fetchImpl: f.fetchImpl });
  await assert.rejects(changed.capture(order.id)); assert.equal(f.mock.calls.length, calls);
});

test('order identity, merchant, quote and application bindings are mandatory before charging', async t => {
  const patches = {
    id: order => { order.id = 'OTHER-ORDER'; },
    intent: order => { order.intent = 'AUTHORIZE'; },
    reference: order => { order.purchase_units[0].reference_id = 'another-application'; },
    custom: order => { order.purchase_units[0].custom_id = 'another-application'; },
    invoice: order => { order.purchase_units[0].invoice_id = 'another-invoice'; },
    merchant: order => { order.purchase_units[0].payee.merchant_id = 'another-merchant'; },
    amount: order => { order.purchase_units[0].amount.value = '0.01'; },
    currency: order => { order.purchase_units[0].amount.currency_code = 'EUR'; },
    units: order => { order.purchase_units.push(structuredClone(order.purchase_units[0])); },
  };
  for (const [name, patch] of Object.entries(patches)) await t.test(name, async t => {
    const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider); patch(provider);
    await assert.rejects(f.payments.capture(order.id));
    assert.equal(f.mock.captureEffects, 0); assert.equal((await f.store.get(order.id)).state, 'checkout');
  });
});

test('capture detail mismatches retain capturing and never publish', async t => {
  const patches = {
    id: capture => { capture.id = 'OTHER-CAPTURE'; },
    status: capture => { capture.status = 'PENDING'; },
    amount: capture => { capture.amount.value = '0.01'; },
    currency: capture => { capture.amount.currency_code = 'EUR'; },
    merchant: capture => { capture.payee.merchant_id = 'OTHER-MERCHANT'; },
    order: capture => { capture.supplementary_data.related_ids.order_id = 'OTHER-ORDER'; },
    invoice: capture => { capture.invoice_id = 'OTHER-INVOICE'; },
    custom: capture => { capture.custom_id = 'OTHER-APPLICATION'; },
    partial: capture => { capture.final_capture = false; },
  };
  for (const [name, patch] of Object.entries(patches)) await t.test(name, async t => {
    const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
    f.mock.onCaptureRead = capture => { patch(capture); };
    await assert.rejects(f.payments.capture(order.id));
    const saved = await f.store.get(order.id);
    assert.equal(saved.state, 'capturing'); assert.equal(saved.payment_verified_at, null);
    assert.equal(saved.starts_at, null); assert.equal(f.count('ad_sale_holds', order.id), 1);
  });
});

test('a live or mismatched approval link never reaches the applicant', async t => {
  const f = fixture(t), { order, provider } = await f.checkout();
  for (const href of ['https://www.paypal.com/checkoutnow?token=' + provider.id,
    'https://www.sandbox.paypal.com/checkoutnow?token=OTHER',
    'https://www.sandbox.paypal.com.evil.example/checkoutnow?token=' + provider.id]) {
    provider.links[0].href = href; await assert.rejects(f.payments.checkout(order.id));
  }
});

test('a verified stop event racing activation rolls back hold extension and publication', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  f.mock.onCaptureRead = capture => f.native.prepare(
    "INSERT INTO ad_sale_events(environment,id,event_type,provider_order,capture_ids_json,received_at) VALUES('sandbox',?,?,?,?,?)",
  ).run('SYNTHETIC-STOP', 'PAYMENT.CAPTURE.REVERSED', order.provider_order, JSON.stringify([capture.id]), f.store.now());
  await assert.rejects(f.payments.capture(order.id));
  const saved = await f.store.get(order.id);
  assert.equal(saved.state, 'capturing'); assert.equal(saved.payment_verified_at, null);
  assert.equal(f.native.prepare('SELECT expires_at FROM ad_sale_holds WHERE order_id=?').get(order.id).expires_at, order.hold_until);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE action='sandbox_payment_verified'").get().n, 0);
});

test('a missing bundle position prevents activation and rolls back extension of remaining holds', async t => {
  const f = fixture(t), { order, provider } = await f.checkout({ bundle: true }); f.approve(provider);
  f.mock.onCaptureRead = () => f.native.prepare("DELETE FROM ad_sale_holds WHERE order_id=? AND slot='buyer-intent-top'").run(order.id);
  await assert.rejects(f.payments.capture(order.id));
  assert.equal((await f.store.get(order.id)).state, 'capturing');
  assert.equal(f.native.prepare('SELECT expires_at FROM ad_sale_holds WHERE order_id=?').get(order.id).expires_at, order.hold_until);
});

test('a stop event on an already capturing order blocks a later charge attempt', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  f.mock.failCaptureBeforeEffect = true; await assert.rejects(f.payments.capture(order.id));
  f.mock.failCaptureBeforeEffect = false;
  f.native.prepare("INSERT INTO ad_sale_events(environment,id,event_type,provider_order,received_at) VALUES('sandbox',?,?,?,?)")
    .run('SYNTHETIC-CAPTURE-STOP', 'CUSTOMER.DISPUTE.CREATED', order.provider_order, f.store.now());
  const calls = f.mock.calls.length;
  await assert.rejects(f.payments.capture(order.id));
  assert.equal(f.mock.calls.length, calls); assert.equal(f.mock.captureEffects, 0);
  assert.equal((await f.store.get(order.id)).state, 'capturing'); assert.equal(f.count('ad_sale_holds', order.id), 1);
});

test('an existing pending provider capture cannot trigger another capture request', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  provider.purchase_units[0].payments = { captures: [{ id: 'SYNTHETIC-PENDING', status: 'PENDING' }] };
  await assert.rejects(f.payments.capture(order.id));
  assert.equal(f.mock.captureEffects, 0);
  assert.equal(f.mock.calls.filter(call => call.path.endsWith('/capture')).length, 0);
  assert.equal((await f.store.get(order.id)).state, 'checkout');
});

test('reservation expiry during provider preflight prevents transition and capture', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  f.mock.onOrderRead = () => { f.advance(31 * 60000); f.mock.onOrderRead = null; };
  await assert.rejects(f.payments.capture(order.id));
  assert.equal((await f.store.get(order.id)).state, 'checkout');
  assert.equal(f.mock.calls.filter(call => call.path.endsWith('/capture')).length, 0);
  assert.equal(f.mock.captureEffects, 0);
});

test('uncertain attempted capture retains its hold even when no effect can be confirmed', async t => {
  const f = fixture(t), { order, provider } = await f.checkout(); f.approve(provider);
  f.mock.failCaptureBeforeEffect = true; await assert.rejects(f.payments.capture(order.id));
  assert.equal((await f.store.get(order.id)).state, 'capturing'); assert.equal(f.mock.captureEffects, 0);
  f.advance(31 * 60000); assert.equal(await f.payments.expire(), 0);
  const competitor = await f.prepared({ reserve: false });
  await assert.rejects(f.store.reserveReviewedOrder(competitor.id));
  f.mock.failCaptureBeforeEffect = false;
  assert.equal((await f.payments.capture(order.id)).state, 'active'); assert.equal(f.mock.captureEffects, 1);
  const ids = f.mock.calls.filter(call => call.path.endsWith('/capture')).map(call => call.requestId);
  assert.equal(ids.length, 2); assert.equal(new Set(ids).size, 1);
});
