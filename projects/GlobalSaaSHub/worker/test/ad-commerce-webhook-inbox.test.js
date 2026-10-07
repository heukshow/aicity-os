// Isolated SQLite and synthetic PayPal responses only; no actual provider calls.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, mkdtempSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { SandboxAdWebhooks } from '../src/ad-commerce-sandbox-webhooks.js';
import { SandboxAdPayments } from '../src/ad-commerce-sandbox-payments.js';
import { memoryStore, syntheticInput, syntheticPayPal, TEST_ENV } from './helpers/ad-commerce-fixtures.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';
const migration = readFileSync(new URL('../sandbox-migrations/0001_webhook_retry.sql', import.meta.url), 'utf8');
const ENV = { ...TEST_ENV, PAYPAL_WEBHOOK_ID: 'INBOX-SYNTHETIC-WEBHOOK' };
const HEADERS = { 'content-type': 'application/json', 'paypal-transmission-id': 'INBOX-TRANSMISSION',
  'paypal-transmission-time': '2026-10-07T01:00:00Z', 'paypal-cert-url': 'https://api-m.sandbox.paypal.com/certs/INBOX',
  'paypal-auth-algo': 'SHA256withRSA', 'paypal-transmission-sig': 'INBOX-SYNTHETIC-SIGNATURE' };
const request = event => new Request('https://isolated-sandbox.example/sandbox/webhooks/paypal',
  { method: 'POST', headers: HEADERS, body: typeof event === 'string' ? event : JSON.stringify(event) });
function fixture(t, { initialize = true, ...options } = {}) {
  t.mock.method(globalThis, 'fetch', () => { throw new Error('External network is forbidden'); });
  const f = memoryStore(), provider = syntheticPayPal(), signature = { result: 'SUCCESS', bodies: [] };
  t.after(() => f.close());
  if (initialize) f.native.exec(migration);
  const fetchImpl = async (url, init = {}) => {
    assert.equal(new URL(url).origin, 'https://api-m.sandbox.paypal.com');
    if (new URL(url).pathname === '/v1/notifications/verify-webhook-signature') {
      signature.bodies.push(init.body);
      if (signature.advanceMs) f.advance(signature.advanceMs);
      return new Response(JSON.stringify({ verification_status: signature.result }));
    }
    return provider.fetchImpl(url, init);
  };
  const payments = new SandboxAdPayments(f.store, { env: ENV, fetchImpl });
  const inboxOptions = { clock: () => f.store.clock(), baseDelayMs: 1000, ...options };
  const make = () => new SandboxAdWebhooks(f.store, payments, { env: ENV, fetchImpl, durableInbox: inboxOptions });
  const webhooks = make();
  async function checkout() {
    const { order } = await f.store.createDraft(syntheticInput());
    for (const role of ['logo', 'tool-primary']) {
      const spec = AD_ASSET_SPECS[role];
      f.native.prepare('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)').run(
        crypto.randomUUID(), order.id, role, 'image/png', spec.width, spec.height, 1, 'b'.repeat(64), Buffer.from('x'));
    }
    await f.store.submitDraft(order.id);
    await f.store.review(order.id, { reviewer: 'inbox-test', decision: 'approve', notes: 'Synthetic fixture only.',
      destinationChecked: true, claimsChecked: true });
    await f.store.reserveReviewedOrder(order.id);
    return (await payments.checkout(order.id)).order;
  }
  function complete(order) {
    const record = provider.records.get(order.provider_order), unit = record.order.purchase_units[0];
    record.capture = { id: 'SYNTHETIC-CAPTURE-' + order.provider_order, status: 'COMPLETED', final_capture: true,
      amount: unit.amount, payee: { merchant_id: ENV.PAYPAL_MERCHANT_ID }, custom_id: unit.custom_id,
      invoice_id: unit.invoice_id, supplementary_data: { related_ids: { order_id: order.provider_order } } };
    record.order.status = 'COMPLETED'; unit.payments = { captures: [record.capture] };
    return record.capture;
  }
  const event = (order, capture, id = 'INBOX-COMPLETED') => ({ id, event_type: 'PAYMENT.CAPTURE.COMPLETED',
    resource: { ...capture, supplementary_data: { related_ids: { order_id: order.provider_order } } } });
  const count = table => f.native.prepare('SELECT count(*) AS n FROM ' + table).get().n;
  const capturePosts = () => provider.calls.filter(call => call.method === 'POST' && call.path.endsWith('/capture')).length;
  return { ...f, provider, signature, payments, webhooks, make, checkout, complete, event, count, capturePosts };
}
test('missing sandbox migration fails receipt storage without acknowledging or persisting an event', async t => {
  const f = fixture(t, { initialize: false });
  const response = await f.webhooks.handle(request({ id: 'NO-MIGRATION', event_type: 'UNSUPPORTED.TEST', resource: {} }));
  assert.equal(response.status, 503); assert.equal((await response.json()).received, false); assert.equal(f.count('ad_sale_events'), 0);
});
test('receipt insert failure rolls back the legacy event row and returns failure', async t => {
  const f = fixture(t);
  f.native.exec("CREATE TRIGGER fail_receipt BEFORE INSERT ON ad_sandbox_webhook_receipts BEGIN SELECT RAISE(ABORT,'Synthetic disk failure'); END");
  const response = await f.webhooks.handle(request({ id: 'DB-FAIL', event_type: 'UNSUPPORTED.TEST', resource: {} }));
  assert.equal(response.status, 503); assert.equal((await response.json()).received, false);
  assert.equal(f.count('ad_sale_events'), 0); assert.equal(f.count('ad_sandbox_webhook_receipts'), 0);
});
test('signature failure stores no raw payload, event or retry work', async t => {
  const f = fixture(t); f.signature.result = 'FAILURE';
  assert.equal((await f.webhooks.handle(request({ id: 'BAD-SIGNATURE', event_type: 'UNSUPPORTED.TEST', resource: {} }))).status, 401);
  assert.equal(f.count('ad_sale_events'), 0); assert.equal(f.count('ad_sandbox_webhook_receipts'), 0);
});
test('verified exact raw body and headers are private while safe metadata is available', async t => {
  const f = fixture(t); await f.webhooks.ready();
  const raw = '{\n "id":"RAW-EXACT", "event_type":"UNSUPPORTED.TEST", "resource":{"v":1.00,"x":"\\u0061"}\n}';
  assert.equal((await f.webhooks.handle(request(raw))).status, 200);
  const row = await f.webhooks.inbox.row('RAW-EXACT');
  assert.equal(row.raw_event, raw); assert.equal(row.verification_status, 'SUCCESS');
  assert.equal(JSON.parse(row.signature_headers_json)['paypal-transmission-sig'], HEADERS['paypal-transmission-sig']);
  assert.ok(f.signature.bodies[0].endsWith('"webhook_event":' + raw + '}'));
  const safe = await f.webhooks.receipt('RAW-EXACT');
  assert.equal(safe.state, 'processed'); assert.equal(safe.verificationStatus, 'SUCCESS');
  assert.equal(JSON.stringify(safe).includes('INBOX-SYNTHETIC-SIGNATURE'), false);
  assert.equal('raw_event' in safe, false); assert.equal('signature_headers_json' in safe, false);
  assert.throws(() => f.native.prepare("UPDATE ad_sandbox_webhook_receipts SET raw_event='{}' WHERE id='RAW-EXACT'").run());
});
test('arrival and successful signature verification retain distinct observed timestamps', async t => {
  const f = fixture(t), before = f.store.now(); f.signature.advanceMs = 250;
  const event = { id: 'SEPARATE-STAGES', event_type: 'UNSUPPORTED.TEST', resource: {} };
  assert.equal((await f.webhooks.handle(request(event))).status, 200);
  const receipt = await f.webhooks.receipt(event.id);
  assert.equal(receipt.receivedAt, before); assert.equal(receipt.verifiedAt, f.store.now());
  assert.equal(Date.parse(receipt.verifiedAt) - Date.parse(receipt.receivedAt), 250);
});
test('completed delivery activates by provider reads and attributes the audit to the webhook', async t => {
  const f = fixture(t), order = await f.checkout(), capture = f.complete(order);
  const response = await f.webhooks.handle(request(f.event(order, capture)));
  assert.equal(response.status, 200, await response.clone().text());
  assert.equal((await f.store.get(order.id)).state, 'active'); assert.equal(f.capturePosts(), 0);
  assert.equal((await f.webhooks.receipt('INBOX-COMPLETED')).state, 'processed');
  assert.equal(f.native.prepare("SELECT actor FROM ad_sale_audit WHERE action='sandbox_payment_verified'").get().actor, 'sandbox_webhook');
});
test('provider-completed capture with lost response is activated by a webhook, without another charge', async t => {
  const f = fixture(t), order = await f.checkout(); f.provider.approve(order.provider_order);
  const original = f.payments.fetch;
  f.payments.fetch = async (url, init) => { const result = await original(url, init); if (new URL(url).pathname.endsWith('/capture')) throw new Error('Synthetic response loss'); return result; };
  await assert.rejects(f.payments.capture(order.id));
  assert.equal((await f.store.get(order.id)).state, 'capturing'); assert.equal(f.capturePosts(), 1);
  f.payments.fetch = original;
  const capture = f.provider.records.get(order.provider_order).capture;
  assert.equal((await f.webhooks.handle(request(f.event(order, capture)))).status, 200);
  const active = await f.store.get(order.id);
  assert.equal(active.state, 'active'); assert.equal(f.capturePosts(), 1);
  const duplicate = await f.make().handle(request(f.event(order, capture)));
  assert.equal(duplicate.status, 200); assert.equal((await duplicate.json()).duplicate, true);
  assert.equal((await f.store.get(order.id)).starts_at, active.starts_at); assert.equal(f.capturePosts(), 1);
});
test('event capture mismatch is rejected before capturing or active DB transitions', async t => {
  const f = fixture(t), order = await f.checkout(), capture = f.complete(order);
  const wrong = f.event(order, { ...capture, id: 'DIFFERENT-CAPTURE' });
  assert.equal((await f.webhooks.handle(request(wrong))).status, 503);
  assert.equal((await f.store.get(order.id)).state, 'checkout'); assert.equal(f.capturePosts(), 0);
  assert.equal(f.native.prepare("SELECT count(*) n FROM ad_sale_audit WHERE action IN('sandbox_capture_started','sandbox_payment_verified')").get().n, 0);
  assert.equal((await f.webhooks.receipt(wrong.id)).state, 'retry');
});
test('approved but uncaptured provider orders cannot be charged or published by the webhook', async t => {
  const f = fixture(t), order = await f.checkout(); f.provider.approve(order.provider_order);
  const event = f.event(order, { id: 'UNCONFIRMED-CAPTURE', amount: { value: order.amount, currency_code: 'USD' } });
  assert.equal((await f.webhooks.handle(request(event))).status, 503);
  assert.equal((await f.store.get(order.id)).state, 'checkout'); assert.equal(f.capturePosts(), 0);
});
test('unmatched verified event is retried after later order attachment by scheduled drain', async t => {
  const f = fixture(t);
  const event = { id: 'EARLY-COMPLETED', event_type: 'PAYMENT.CAPTURE.COMPLETED',
    resource: { id: 'SYNTHETIC-CAPTURE-SYNTHETIC-ORDER-1', amount: { value: '49.00', currency_code: 'USD' },
      supplementary_data: { related_ids: { order_id: 'SYNTHETIC-ORDER-1' } } } };
  assert.equal((await f.webhooks.handle(request(event))).status, 202);
  assert.equal((await f.webhooks.receipt(event.id)).state, 'retry');
  assert.equal(f.native.prepare('SELECT processed_at FROM ad_sale_events WHERE id=?').get(event.id).processed_at, null);
  const order = await f.checkout(); f.complete(order); f.advance(1000);
  const replacement = f.make(), result = await replacement.drain({ limit: 1 });
  assert.equal(result.processed, 1); assert.equal((await f.store.get(order.id)).state, 'active'); assert.equal(f.capturePosts(), 0);
  const receipt = await replacement.receipt(event.id);
  assert.equal(receipt.lastActor, 'sandbox_webhook_retry'); assert.equal(receipt.attempts, 2);
  assert.equal(f.native.prepare("SELECT actor FROM ad_sale_audit WHERE action='sandbox_payment_verified'").get().actor, 'sandbox_webhook_retry');
  const run = (await replacement.recentRuns())[0]; assert.equal(run.processed, 1); assert.ok(run.completed_at);
});
test('concurrent delivery instances claim once and preserve one activation period', async t => {
  const f = fixture(t), order = await f.checkout(), capture = f.complete(order), event = f.event(order, capture);
  const responses = await Promise.all([f.webhooks.handle(request(event)), f.make().handle(request(event))]);
  assert.ok(responses.every(response => [200, 202].includes(response.status)));
  assert.equal(f.count('ad_sandbox_webhook_receipts'), 1);
  assert.equal((await f.webhooks.receipt(event.id)).attempts, 1);
  assert.equal(f.native.prepare("SELECT count(*) n FROM ad_sale_audit WHERE action='sandbox_payment_verified'").get().n, 1);
  assert.equal(f.capturePosts(), 0);
});
test('an abandoned lease survives instance replacement and is reclaimed after its deadline', async t => {
  const f = fixture(t, { leaseMs: 1000 }), order = await f.checkout(), capture = f.complete(order), event = f.event(order, capture);
  await f.webhooks.inbox.receive(event, JSON.stringify(event), new Headers(HEADERS),
    { providerOrder: order.provider_order, captureIds: [capture.id] });
  assert.ok(await f.webhooks.inbox.claim(event.id, 'sandbox_webhook'));
  const replacement = f.make(); assert.equal((await replacement.drain()).claimed, 0);
  f.advance(1001); assert.equal((await replacement.drain()).processed, 1);
  assert.equal((await replacement.receipt(event.id)).attempts, 2); assert.equal(f.capturePosts(), 0);
});
test('attempt bound and retry delay prevent repeated deliveries from spinning provider processing', async t => {
  const f = fixture(t, { maxAttempts: 2 }), order = await f.checkout(), capture = f.complete(order), event = f.event(order, capture);
  let attempts = 0; f.payments.reconcile = async () => { attempts++; throw new Error('Synthetic outage'); };
  assert.equal((await f.webhooks.handle(request(event))).status, 503);
  assert.equal((await f.webhooks.handle(request(event))).status, 202); assert.equal(attempts, 1);
  f.advance(1000); assert.equal((await f.make().drain()).failed, 1); assert.equal(attempts, 2);
  const receipt = await f.webhooks.receipt(event.id);
  assert.equal(receipt.state, 'failed'); assert.equal(receipt.lastError, 'retry_attempts_exhausted'); assert.equal(receipt.processedAt, null);
  f.advance(3600000); assert.equal((await f.make().drain()).claimed, 0); assert.equal(attempts, 2);
});
test('deadline bound leaves unmatched event available for administrator review without marking processed', async t => {
  const f = fixture(t, { deadlineMs: 1000 });
  const event = { id: 'EXPIRED-EVENT', event_type: 'PAYMENT.CAPTURE.COMPLETED', resource: { id: 'UNKNOWN' } };
  assert.equal((await f.webhooks.handle(request(event))).status, 202);
  f.advance(1000); assert.equal((await f.make().drain()).claimed, 0);
  const receipt = await f.webhooks.receipt(event.id);
  assert.equal(receipt.state, 'failed'); assert.equal(receipt.lastError, 'retry_deadline_exceeded'); assert.equal(receipt.processedAt, null);
});
test('receipt completion storage failure can retry after activation without restarting the paid period', async t => {
  const f = fixture(t), order = await f.checkout(), capture = f.complete(order), event = f.event(order, capture);
  f.native.exec("CREATE TRIGGER fail_completion BEFORE UPDATE ON ad_sandbox_webhook_receipts WHEN NEW.state='processed' BEGIN SELECT RAISE(ABORT,'Synthetic receipt update failure'); END");
  assert.equal((await f.webhooks.handle(request(event))).status, 503);
  const active = await f.store.get(order.id); assert.equal(active.state, 'active');
  assert.equal((await f.webhooks.receipt(event.id)).state, 'retry');
  f.native.exec('DROP TRIGGER fail_completion'); f.advance(1000);
  assert.equal((await f.make().drain()).processed, 1);
  const after = await f.store.get(order.id);
  assert.equal(after.starts_at, active.starts_at); assert.equal(after.ends_at, active.ends_at); assert.equal(f.capturePosts(), 0);
  assert.equal(f.native.prepare("SELECT count(*) n FROM ad_sale_audit WHERE action='sandbox_payment_verified'").get().n, 1);
});
test('uncertain capturing stop event becomes explicit review state while preserving its reservation', async t => {
  const f = fixture(t), order = await f.checkout(); f.provider.approve(order.provider_order);
  const original = f.payments.fetch;
  f.payments.fetch = (url, init) => new URL(url).pathname.endsWith('/capture') ? Promise.reject(new Error('Synthetic unknown outcome')) : original(url, init);
  await assert.rejects(f.payments.capture(order.id));
  const event = { id: 'UNCERTAIN-STOP', event_type: 'CHECKOUT.PAYMENT-APPROVAL.REVERSED', resource: { order_id: order.provider_order } };
  assert.equal((await f.webhooks.handle(request(event))).status, 202);
  const receipt = await f.webhooks.receipt(event.id);
  assert.equal(receipt.state, 'failed'); assert.equal(receipt.lastError, 'uncertain_capture_requires_review');
  assert.equal((await f.store.get(order.id)).state, 'capturing'); assert.equal(f.count('ad_sale_holds'), 1);
});
test('semantic duplicates retain the original verified body and changed payload identities are rejected', async t => {
  const f = fixture(t), event = { id: 'IMMUTABLE-EVENT', event_type: 'UNSUPPORTED.TEST', resource: { amount: '1.00' } };
  const raw = JSON.stringify(event, null, 2);
  assert.equal((await f.webhooks.handle(request(raw))).status, 200);
  assert.equal((await f.webhooks.handle(request(JSON.stringify(event)))).status, 200);
  assert.equal((await f.webhooks.inbox.row(event.id)).raw_event, raw);
  const changed = { ...event, resource: { amount: '2.00' } };
  assert.equal((await f.webhooks.handle(request(changed))).status, 409);
  assert.equal((await f.webhooks.inbox.row(event.id)).raw_event, raw);
});
test('only valid bounded retry configuration and drain limits are accepted', async t => {
  const f = fixture(t);
  await assert.rejects(f.webhooks.drain({ limit: 0 }));
  await assert.rejects(f.webhooks.drain({ limit: 51 }));
  const runs = await f.webhooks.recentRuns(); assert.equal(runs.length, 2); assert.ok(runs.every(run => run.error_code === 'drain_unavailable'));
  assert.throws(() => new SandboxAdWebhooks(f.store, f.payments,
    { env: ENV, fetchImpl: f.payments.fetch, durableInbox: { maxAttempts: 0 } }));
});
test('a private disk inbox persists across separate processes and retries without a new signature request', t => {
  const base = resolve(tmpdir()), dir = mkdtempSync(join(base, 'coshuma-webhook-restart-'));
  const safeDir = resolve(dir);
  assert.ok(safeDir.startsWith(base + '\\') || safeDir.startsWith(base + '/'));
  t.after(() => { assert.ok(resolve(dir).startsWith(base)); rmSync(dir, { recursive: true, force: true }); });
  const child = fileURLToPath(new URL('./helpers/ad-commerce-webhook-restart-child.mjs', import.meta.url));
  const run = action => {
    const result = spawnSync(process.execPath, [child, action, join(dir, 'inbox.ad-sandbox.sqlite')], { encoding: 'utf8', timeout: 15000 });
    assert.equal(result.status, 0, result.stderr || result.stdout); return JSON.parse(result.stdout);
  };
  const received = run('receive'), recovered = run('drain');
  assert.notEqual(received.pid, recovered.pid); assert.equal(received.state, 'retry'); assert.equal(recovered.state, 'retry');
  assert.equal(received.attempts, 1); assert.equal(recovered.attempts, 2); assert.equal(recovered.rawPersisted, true);
  assert.equal(received.signatureRequests, 1); assert.equal(recovered.signatureRequests, 0);
  assert.equal(recovered.capturePosts, 0); assert.equal(recovered.drainCompleted, true);
});
