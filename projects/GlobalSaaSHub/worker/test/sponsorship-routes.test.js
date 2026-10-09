import assert from 'node:assert/strict';
import test from 'node:test';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import worker from '../src/index.js';
import { retryPendingApprovalEmails } from '../src/sponsorship.js';

// All identifiers, credentials and provider responses below are synthetic. Fetch is
// replaced in every test; no test can fall through to a real provider or account.
const ORIGIN = 'https://coshuma.com';
const MERCHANT = 'SYNTHETIC-MERCHANT';
const PASSWORD = 'synthetic-owner-password-not-a-credential';
const sha256 = (value) => createHash('sha256').update(value).digest('hex');
const OWNER = `Basic ${Buffer.from(`owner@example.com:${PASSWORD}`).toString('base64')}`;
const INPUT = {
  companyName: 'Synthetic Example Company', toolName: 'Synthetic Example Tool',
  contactEmail: 'advertiser@example.com', destinationUrl: 'https://example.com/product',
  slot: 'tool-primary', durationDays: 30, targetPage: '/tool/pipedrive.html',
  headline: 'A synthetic tool advertisement',
  description: 'Synthetic material used only to exercise the offline advertising workflow.',
  ctaText: 'View product', sellerAttestation: true,
};
const MIGRATION = [
  '0001_orders.sql', '0002_private_ops.sql', '0003_sponsored_campaigns.sql', '0004_sponsorship_sales.sql',
  '0006_sponsorship_image_assets.sql',
].map((name) => readFileSync(new URL(`../migrations/${name}`, import.meta.url), 'utf8')).join('\n');

// Python's bundled SQLite keeps these integration tests compatible with Node 20/22.
// Each invocation opens the same temporary database; D1 batch is one transaction.
const SQLITE = String.raw`
import json, sqlite3, sys
db = sqlite3.connect(sys.argv[1])
db.row_factory = sqlite3.Row
db.execute('PRAGMA foreign_keys=ON')
request = json.load(sys.stdin)
try:
    results = []
    if 'script' in request:
        db.executescript(request['script'])
    else:
        with db:
            for statement in request['statements']:
                before = db.total_changes
                cursor = db.execute(statement['sql'], statement.get('values', []))
                rows = [dict(row) for row in cursor.fetchall()] if cursor.description else []
                results.append({'success': True, 'results': rows, 'meta': {'changes': db.total_changes - before}})
    print(json.dumps({'results': results}))
except Exception as error:
    print(json.dumps({'error': str(error)}))
finally:
    db.close()
`;

function sqliteD1(t, migrated = true) {
  const directory = mkdtempSync(join(tmpdir(), 'coshuma-offline-routes-'));
  const database = join(directory, 'synthetic.sqlite');
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const execute = (request) => {
    const result = JSON.parse(execFileSync(process.platform === 'win32' ? 'python' : 'python3', ['-c', SQLITE, database], {
      input: JSON.stringify(request), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], timeout: 10000,
    }));
    if (result.error) throw new Error(result.error);
    return result.results;
  };
  const db = {
    prepare(sql) {
      return {
        sql, values: [],
        bind(...values) { return { ...this, values }; },
        async all() { return execute({ statements: [this] })[0]; },
        async run() { return execute({ statements: [this] })[0]; },
        async first(column) {
          const row = execute({ statements: [this] })[0].results[0] || null;
          return column && row ? row[column] : row;
        },
      };
    },
    async batch(statements) { return execute({ statements }); },
    exec(script) { execute({ script }); },
  };
  if (migrated) db.exec(MIGRATION);
  return db;
}

function fixture(t, { migrated = true, checkout = false } = {}) {
  const unexpected = [];
  const fetchMock = t.mock.method(globalThis, 'fetch', async (url) => {
    unexpected.push(String(url));
    throw new Error('Unexpected network request blocked by offline test');
  });
  t.after(() => assert.deepEqual(unexpected, [], 'unmocked network calls must never occur'));
  const db = sqliteD1(t, migrated);
  const env = {
    ORDERS: db, ALLOWED_ORIGIN: ORIGIN, CHECKOUT_ENABLED: String(checkout),
    PAYPAL_ENVIRONMENT: 'live', PAYPAL_CLIENT_ID: 'synthetic-client-id',
    PAYPAL_CLIENT_SECRET: 'synthetic-client-secret', PAYPAL_WEBHOOK_ID: 'synthetic-webhook-id',
    PAYPAL_MERCHANT_ID: MERCHANT, ADMIN_PATH: '/synthetic-owner',
    ADMIN_USERNAME: 'owner@example.com', ADMIN_PASSWORD_SHA256: sha256(PASSWORD),
    OPS_PASSWORD_SHA256: sha256('synthetic-ops-password'),
  };
  async function request(path, { method = 'GET', body, rawBody, headers = {} } = {}) {
    const init = { method, headers: { ...headers } };
    if (body !== undefined || rawBody !== undefined) {
      init.body = rawBody === undefined ? JSON.stringify(body) : rawBody;
      init.headers['content-type'] ??= 'application/json';
    }
    if (method === 'POST') init.headers.origin ??= ORIGIN;
    const response = await worker.fetch(new Request(`${ORIGIN}${path}`, init), env);
    const json = await response.json();
    return { response, json, status: response.status };
  }
  async function create(changes = {}) {
    const result = await request('/v1/sponsorship/applications', { method: 'POST', body: { ...INPUT, ...changes } });
    assert.equal(result.status, 201, JSON.stringify(result.json));
    return result.json;
  }
  const advertiser = (application) => ({ authorization: `Bearer ${application.accessToken}` });
  const ownerAction = (application, action, body = {}) => request(`/synthetic-owner/ads/applications/${application.applicationId}/${action}`, {
    method: 'POST', headers: { authorization: OWNER }, body,
  });
  return { db, env, fetchMock, request, create, advertiser, ownerAction };
}

function mockPayPal(f, { signature = 'SUCCESS' } = {}) {
  const state = { signature, orders: new Map(), captures: new Map(), created: [], captured: [], calls: [], verificationBodies: [], failure: null, onCaptureRead: null };
  f.fetchMock.mock.mockImplementation(async (url, options = {}) => {
    const parsed = new URL(url);
    assert.equal(parsed.origin, 'https://api-m.paypal.com', 'only synthetic live-environment URLs are accepted');
    const path = parsed.pathname;
    const method = options.method || 'GET';
    state.calls.push({ path, method });
    const response = (data, status = 200) => new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json' } });
    if (state.failure === path) return response({ error: 'synthetic provider failure' }, 503);
    if (path === '/v1/oauth2/token' && method === 'POST') return response({ access_token: 'synthetic-access-token' });
    if (path === '/v1/notifications/verify-webhook-signature' && method === 'POST') {
      state.verificationBodies.push(options.body);
      const payload = JSON.parse(options.body);
      assert.equal(payload.webhook_id, 'synthetic-webhook-id');
      return response({ verification_status: state.signature });
    }
    if (path === '/v2/checkout/orders' && method === 'POST') {
      const payload = JSON.parse(options.body);
      const id = `SYNTHETIC-ORDER-${state.orders.size + 1}`;
      const order = { ...payload, id, status: 'APPROVED' };
      state.orders.set(id, order);
      state.created.push({ payload, requestId: options.headers['PayPal-Request-Id'] });
      return response(order, 201);
    }
    const orderMatch = /^\/v2\/checkout\/orders\/([^/]+)(\/capture)?$/.exec(path);
    if (orderMatch && state.orders.has(orderMatch[1])) {
      const order = state.orders.get(orderMatch[1]);
      if (orderMatch[2] && method === 'POST') {
        state.captured.push({ orderId: order.id, requestId: options.headers['PayPal-Request-Id'] });
        const capture = {
          id: `SYNTHETIC-CAPTURE-${state.captures.size + 1}`, status: 'COMPLETED',
          amount: structuredClone(order.purchase_units[0].amount), payee: { merchant_id: MERCHANT },
          supplementary_data: { related_ids: { order_id: order.id } },
        };
        order.status = 'COMPLETED';
        order.purchase_units[0].payments = { captures: [structuredClone(capture)] };
        state.captures.set(capture.id, capture);
      } else assert.equal(method, 'GET');
      return response(order);
    }
    const captureMatch = /^\/v2\/payments\/captures\/([^/]+)$/.exec(path);
    if (captureMatch && state.captures.has(captureMatch[1]) && method === 'GET') {
      if (state.onCaptureRead) await state.onCaptureRead(captureMatch[1]);
      return response(state.captures.get(captureMatch[1]));
    }
    assert.fail(`Unconfigured synthetic provider operation: ${method} ${path}`);
  });
  return state;
}

async function orderAndCapture(f, application) {
  const base = `/v1/sponsorship/applications/${application.applicationId}`;
  const headers = f.advertiser(application);
  const order = await f.request(`${base}/order`, { method: 'POST', body: {}, headers });
  assert.equal(order.status, 201, JSON.stringify(order.json));
  const captured = await f.request(`${base}/capture`, { method: 'POST', body: { orderId: order.json.orderId }, headers });
  assert.equal(captured.status, 200, JSON.stringify(captured.json));
  assert.equal(captured.json.paymentVerified, true);
  return order.json.orderId;
}

async function publishedApplication(f, changes = {}) {
  const app = await f.create(changes);
  const orderId = await orderAndCapture(f, app);
  assert.equal((await f.ownerAction(app, 'review', {
    decision: 'approve', notes: 'Synthetic material reviewed for offline route test', destinationChecked: true, claimsChecked: true,
  })).status, 200);
  assert.equal((await f.ownerAction(app, 'publish')).status, 200);
  const { capture_id: captureId } = await f.db.prepare('SELECT capture_id FROM sponsorship_payments WHERE application_id=?').bind(app.applicationId).first();
  return { app, orderId, captureId };
}

const paymentEvent = (f, event) => f.request('/v1/webhooks/paypal', { method: 'POST', body: event, headers: { origin: '' } });

async function legacyOrder(f, paypal, suffix, status = 'pending') {
  const orderId = `SYNTHETIC-LEGACY-ORDER-${suffix}`;
  const captureId = `SYNTHETIC-LEGACY-CAPTURE-${suffix}`;
  const now = '2026-10-04T00:00:00.000Z';
  await f.db.prepare(`INSERT INTO orders(id,provider_order_id,provider,status,amount,currency,created_at,updated_at)
    VALUES(?,?,'paypal',?,'49.00','USD',?,?)`).bind(`synthetic-legacy-${suffix}`, orderId, status, now, now).run();
  const capture = {
    id: captureId, status: 'COMPLETED', amount: { value: '49.00', currency_code: 'USD' },
    payee: { merchant_id: MERCHANT }, supplementary_data: { related_ids: { order_id: orderId } },
  };
  const order = { id: orderId, status: 'COMPLETED', purchase_units: [{
    payee: { merchant_id: MERCHANT }, amount: { value: '49.00', currency_code: 'USD' },
    payments: { captures: [structuredClone(capture)] },
  }] };
  paypal.orders.set(orderId, order);
  paypal.captures.set(captureId, capture);
  const completion = { id: `SYNTHETIC-LEGACY-COMPLETION-${suffix}`, event_type: 'PAYMENT.CAPTURE.COMPLETED', resource: {
    id: captureId, supplementary_data: { related_ids: { order_id: orderId } },
  } };
  return { orderId, captureId, order, capture, completion };
}

test('financial GETs require owner authentication before disclosing storage or accepting an audience bearer', async (t) => {
  const f = fixture(t);
  delete f.env.ORDERS;
  const audienceBearer = `Bearer ${Buffer.from(JSON.stringify({ alg: 'RS256' })).toString('base64url')}.${Buffer.from(JSON.stringify({ aud: 'coshuma-private-analytics', sub: 'synthetic-publisher' })).toString('base64url')}.synthetic-signature`;
  for (const path of ['/ops/ads/config', '/ops/ads/applications', '/synthetic-owner/ads/config', '/synthetic-owner/ads/applications']) {
    for (const headers of [{}, { authorization: audienceBearer }]) {
      const result = await f.request(path, { headers });
      assert.equal(result.status, 401);
      assert.deepEqual(Object.keys(result.json), ['error']);
      assert.equal(result.response.headers.get('cache-control'), 'no-store');
    }
  }
  const basicOnOps = await f.request('/ops/ads/config', { headers: { authorization: OWNER } });
  assert.equal(basicOnOps.status, 401, 'ops financial access does not accept a private-admin Basic credential');
  assert.equal(f.fetchMock.mock.callCount(), 0);
});

test('public writes reject foreign origins and oversized declared or streamed JSON before saving', async (t) => {
  const f = fixture(t);
  for (const headers of [{ origin: 'https://attacker.example' }, { origin: '' }]) {
    assert.equal((await f.request('/v1/sponsorship/applications', { method: 'POST', body: INPUT, headers })).status, 403);
  }
  for (const options of [
    { body: INPUT, headers: { 'content-length': '16385' } },
    { rawBody: JSON.stringify({ ...INPUT, padding: 'x'.repeat(17000) }) },
    { rawBody: JSON.stringify({ ...INPUT, padding: 'x'.repeat(17000) }), headers: { 'content-length': '1' } },
  ]) assert.equal((await f.request('/v1/sponsorship/applications', { method: 'POST', ...options })).status, 413);
  assert.equal((await f.request('/v1/sponsorship/applications', { method: 'POST', body: INPUT, headers: { 'content-type': 'text/plain' } })).status, 415);
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_applications').first()).n, 0);
  assert.equal(f.fetchMock.mock.callCount(), 0);
});

test('missing D1 tables or publish guards fail config closed with 503 and false readiness', async (t) => {
  const f = fixture(t, { migrated: false, checkout: true });
  for (const state of ['no binding', 'empty database', 'missing trigger']) {
    if (state === 'no binding') delete f.env.ORDERS;
    else f.env.ORDERS = f.db;
    if (state === 'missing trigger') {
      f.db.exec(MIGRATION);
      f.db.exec('DROP TRIGGER sponsorship_publish_guard;');
    }
    const result = await f.request('/v1/sponsorship/config');
    assert.equal(result.status, 503, state);
    assert.equal(result.json.intakeReady, false, state);
    assert.equal(result.json.paymentReady, false, state);
    assert.equal('publicClientId' in result.json, false);
    const privateResult = await f.request('/synthetic-owner/ads/config', { headers: { authorization: OWNER } });
    assert.equal(privateResult.status, 503);
    assert.equal(privateResult.json.checks.storageReady, false);
    const placement = await f.request('/v1/sponsored/placements?path=/tool/pipedrive.html');
    assert.equal(placement.status, 503);
    assert.deepEqual({ ready: placement.json.ready, placements: placement.json.placements }, { ready: false, placements: [] });
  }
  assert.equal(f.fetchMock.mock.callCount(), 0);
});

test('paused checkout accepts an application, persists only the token hash and requires its bearer for status', async (t) => {
  const f = fixture(t);
  const config = await f.request('/v1/sponsorship/config');
  assert.equal(config.status, 200);
  assert.equal(config.json.intakeReady, true);
  assert.equal(config.json.paymentReady, false);
  assert.equal('publicClientId' in config.json, false);
  const app = await f.create();
  assert.match(app.accessToken, /^[a-f0-9]{64}$/);
  assert.equal(app.paymentVerified, false);
  assert.equal(app.status, 'awaiting_payment');
  assert.equal(app.quote.amount, '49.00');
  const persisted = await f.db.prepare('SELECT * FROM sponsorship_applications WHERE id=?').bind(app.applicationId).first();
  assert.equal(persisted.access_token_hash, sha256(app.accessToken));
  assert.equal(JSON.stringify(persisted).includes(app.accessToken), false);
  assert.equal(persisted.company_name, INPUT.companyName);
  assert.equal(persisted.tool_name, INPUT.toolName);
  const path = `/v1/sponsorship/applications/${app.applicationId}`;
  for (const headers of [{}, { authorization: `Bearer ${'0'.repeat(64)}` }, { authorization: OWNER }]) {
    assert.equal((await f.request(path, { headers })).status, 401);
  }
  const another = await f.create({ toolName: 'Another synthetic tool' });
  assert.equal((await f.request(path, { headers: f.advertiser(another) })).status, 401);
  const status = await f.request(path, { headers: f.advertiser(app) });
  assert.equal(status.status, 200);
  assert.equal(status.json.applicationId, app.applicationId);
  for (const privateField of ['accessToken', 'access_token_hash', 'contactEmail', 'paymentEvidence', 'reviewNotes']) {
    assert.equal(privateField in status.json, false, privateField);
  }
  assert.equal(f.fetchMock.mock.callCount(), 0);
});

test('paused checkout rejects order and capture without contacting PayPal or creating a payment', async (t) => {
  const f = fixture(t);
  const app = await f.create();
  for (const action of ['order', 'capture']) {
    const result = await f.request(`/v1/sponsorship/applications/${app.applicationId}/${action}`, {
      method: 'POST', body: { orderId: 'SYNTHETIC-UNCREATED' }, headers: f.advertiser(app),
    });
    assert.equal(result.status, 503);
    assert.match(result.json.error, /application is saved/i);
  }
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_payments').first()).n, 0);
  assert.equal(f.fetchMock.mock.callCount(), 0);
});

test('active order creation binds the server quote and owner action requires the same origin', async (t) => {
  const f = fixture(t, { checkout: true });
  const paypal = mockPayPal(f);
  const app = await f.create();
  const path = `/v1/sponsorship/applications/${app.applicationId}/order`;
  const options = { method: 'POST', body: {}, headers: f.advertiser(app) };
  const first = await f.request(path, options);
  const again = await f.request(path, options);
  assert.equal(first.status, 201);
  assert.equal(again.status, 200);
  assert.equal(again.json.orderId, first.json.orderId);
  assert.equal(paypal.created.length, 1, 'a retry reuses the saved provider order');
  const unit = paypal.created[0].payload.purchase_units[0];
  assert.deepEqual(unit.amount, { currency_code: 'USD', value: '49.00' });
  assert.equal(unit.custom_id, app.applicationId);
  assert.equal(unit.invoice_id, app.reference);
  assert.equal(unit.payee.merchant_id, MERCHANT);
  assert.ok(unit.description.includes(INPUT.companyName) && unit.description.includes(INPUT.toolName));
  assert.match(paypal.created[0].requestId, /^[a-f0-9]{32}-c$/);
  assert.equal(paypal.created[0].requestId.length, 34);
  const before = paypal.calls.length;
  const mismatch = await f.request(`/v1/sponsorship/applications/${app.applicationId}/capture`, {
    method: 'POST', headers: f.advertiser(app), body: { orderId: 'SYNTHETIC-OTHER-ORDER' },
  });
  assert.equal(mismatch.status, 409);
  const crossOrigin = await f.request(`/synthetic-owner/ads/applications/${app.applicationId}/review`, {
    method: 'POST', headers: { authorization: OWNER, origin: 'https://attacker.example' },
    body: { decision: 'reject', notes: 'Synthetic rejected material' },
  });
  assert.equal(crossOrigin.status, 403);
  assert.equal(paypal.calls.length, before);
  assert.equal((await f.db.prepare('SELECT review_status FROM sponsorship_applications WHERE id=?').bind(app.applicationId).first()).review_status, 'pending');
});

test('invalid webhook signatures save nothing, and valid duplicate events remain idempotent while checkout is paused', async (t) => {
  const f = fixture(t);
  const paypal = mockPayPal(f, { signature: 'FAILURE' });
  const event = { id: 'SYNTHETIC-EVENT-UNRELATED', event_type: 'PAYMENT.CAPTURE.COMPLETED', resource: { id: 'SYNTHETIC-UNRELATED-CAPTURE' } };
  paypal.captures.set(event.resource.id, {
    id: event.resource.id, supplementary_data: { related_ids: { order_id: 'SYNTHETIC-UNRELATED-ORDER' } },
  });
  const post = () => f.request('/v1/webhooks/paypal', { method: 'POST', body: event, headers: { origin: 'https://synthetic-provider.example' } });
  assert.equal((await post()).status, 401);
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_webhook_events').first()).n, 0);
  paypal.signature = 'SUCCESS';
  assert.deepEqual((await post()).json, { accepted: true, matched: false, legacy: false });
  assert.deepEqual((await post()).json, { accepted: true, duplicate: true });
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_webhook_events').first()).n, 1);
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_payments').first()).n, 0);
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_audit_log').first()).n, 0);
});

test('paid, approved and published remain separate gates; a verified refund removes the ad and cannot be replayed into activation', async (t) => {
  const f = fixture(t, { checkout: true });
  const paypal = mockPayPal(f);
  const app = await f.create();
  const review = { decision: 'approve', notes: 'Synthetic destination and claims reviewed', destinationChecked: true, claimsChecked: true };
  assert.equal((await f.ownerAction(app, 'review', review)).status, 409);
  assert.equal((await f.ownerAction(app, 'publish')).status, 409);
  assert.equal(paypal.calls.length, 0, 'unpaid applications never trigger a provider request');
  const orderId = await orderAndCapture(f, app);
  const placements = () => f.request('/v1/sponsored/placements?path=/tool/pipedrive.html');
  assert.deepEqual((await placements()).json.placements, []);
  assert.equal((await f.ownerAction(app, 'publish')).status, 409, 'verified payment alone is insufficient');
  assert.equal((await f.ownerAction(app, 'review', { ...review, claimsChecked: false })).status, 422);
  const approved = await f.ownerAction(app, 'review', review);
  assert.equal(approved.status, 200);
  assert.equal(approved.json.status, 'ready_to_publish');
  assert.deepEqual((await placements()).json.placements, [], 'approval alone does not expose an ad');
  const checksBefore = paypal.calls.filter((call) => call.path.startsWith('/v2/payments/captures/')).length;
  const published = await f.ownerAction(app, 'publish');
  assert.equal(published.status, 200, JSON.stringify(published.json));
  assert.equal(published.json.status, 'active');
  assert.equal(Date.parse(published.json.endAt) - Date.parse(published.json.startAt), 30 * 86400000);
  assert.equal(paypal.calls.filter((call) => call.path.startsWith('/v2/payments/captures/')).length, checksBefore + 1, 'publication refreshes provider evidence');
  const visible = (await placements()).json.placements;
  assert.equal(visible.length, 1);
  assert.equal(visible[0].campaignId, app.applicationId);
  assert.equal(visible[0].label, 'Sponsored');
  assert.equal(visible[0].paymentVerified, true);
  assert.equal(visible[0].approved, true);
  assert.equal(JSON.stringify(visible).includes(INPUT.contactEmail), false);
  assert.equal((await f.ownerAction(app, 'publish')).status, 409, 'repeated publish cannot extend the paid period');
  const saved = await f.db.prepare('SELECT ends_at FROM sponsorship_applications WHERE id=?').bind(app.applicationId).first();
  assert.equal(saved.ends_at, published.json.endAt);

  f.env.CHECKOUT_ENABLED = 'false';
  const captureId = (await f.db.prepare('SELECT capture_id FROM sponsorship_payments WHERE application_id=?').bind(app.applicationId).first()).capture_id;
  const event = { id: 'SYNTHETIC-REFUND-EVENT', event_type: 'PAYMENT.CAPTURE.REFUNDED', resource: {
    id: 'SYNTHETIC-REFUND-ID', links: [{ rel: 'up', href: `https://api.paypal.com/v2/payments/captures/${captureId}` }],
  } };
  const webhook = (body) => f.request('/v1/webhooks/paypal', { method: 'POST', body, headers: { origin: '' } });
  assert.deepEqual((await webhook(event)).json, { accepted: true, matched: true, legacy: false });
  assert.deepEqual((await webhook(event)).json, { accepted: true, duplicate: true });
  assert.deepEqual((await placements()).json.placements, []);
  assert.equal((await f.ownerAction(app, 'verify-payment')).status, 409);
  assert.equal((await f.ownerAction(app, 'publish')).status, 409);
  const late = { id: 'SYNTHETIC-LATE-COMPLETION', event_type: 'PAYMENT.CAPTURE.COMPLETED', resource: {
    id: captureId, supplementary_data: { related_ids: { order_id: orderId } },
  } };
  assert.equal((await webhook(late)).status, 200);
  const final = await f.request(`/v1/sponsorship/applications/${app.applicationId}`, { headers: f.advertiser(app) });
  assert.equal(final.json.paymentVerified, false);
  assert.equal(final.json.paymentStatus, 'refunded');
  assert.equal(final.json.publicationStatus, 'paused');
  assert.equal(final.json.status, 'payment_reversed');
  assert.equal((await f.db.prepare("SELECT COUNT(*) AS n FROM sponsorship_audit_log WHERE application_id=? AND action='payment_reversed'").bind(app.applicationId).first()).n, 1);
  assert.deepEqual((await placements()).json.placements, []);
});

test('provider failure blocks publication, and mismatched captured amounts revoke local verification', async (t) => {
  const f = fixture(t, { checkout: true });
  const paypal = mockPayPal(f);
  const app = await f.create();
  const orderId = await orderAndCapture(f, app);
  assert.equal((await f.ownerAction(app, 'review', {
    decision: 'approve', notes: 'Synthetic material reviewed before provider failure', destinationChecked: true, claimsChecked: true,
  })).status, 200);
  const capture = [...paypal.captures.values()][0];
  paypal.failure = `/v2/payments/captures/${capture.id}`;
  const unavailable = await f.ownerAction(app, 'publish');
  assert.equal(unavailable.status, 502);
  assert.equal((await f.db.prepare('SELECT publication_status FROM sponsorship_applications WHERE id=?').bind(app.applicationId).first()).publication_status, 'draft');
  paypal.failure = null;
  capture.amount.value = '0.01';
  const mismatch = await f.ownerAction(app, 'verify-payment');
  assert.equal(mismatch.status, 409);
  const status = await f.request(`/v1/sponsorship/applications/${app.applicationId}`, { headers: f.advertiser(app) });
  assert.equal(status.json.paymentVerified, false);
  assert.equal(status.json.paymentStatus, 'review');
  assert.equal((await f.ownerAction(app, 'review', {
    decision: 'approve', notes: 'Synthetic attempted review', destinationChecked: true, claimsChecked: true,
  })).status, 409);
  const placements = await f.request('/v1/sponsored/placements?path=/tool/pipedrive.html');
  assert.deepEqual(placements.json.placements, []);
  assert.equal((await f.db.prepare('SELECT state FROM sponsorship_payments WHERE provider_order_id=?').bind(orderId).first()).state, 'review');
});

test('webhook signature verification preserves the original JSON whitespace, Unicode escape and numeric spelling', async (t) => {
  const f = fixture(t);
  const paypal = mockPayPal(f);
  const rawBody = String.raw`{
    "id": "SYNTHETIC-RAW-EVENT",
    "event_type": "SYNTHETIC.UNRELATED",
    "resource": { "escaped": "\u0041", "value": 1e2 }
  }
`;
  const result = await f.request('/v1/webhooks/paypal', { method: 'POST', rawBody, headers: {
    origin: '', 'paypal-transmission-id': 'SYNTHETIC-TRANSMISSION',
    'paypal-transmission-time': '2026-10-04T00:00:00Z', 'paypal-transmission-sig': 'SYNTHETIC-SIGNATURE',
  } });
  assert.equal(result.status, 200, JSON.stringify(result.json));
  assert.equal(paypal.verificationBodies.length, 1);
  const outgoing = paypal.verificationBodies[0];
  const marker = '"webhook_event":';
  assert.equal(outgoing.slice(outgoing.indexOf(marker) + marker.length, -1), rawBody);
  const parsed = JSON.parse(outgoing);
  assert.equal(parsed.webhook_id, 'synthetic-webhook-id');
  assert.equal(parsed.transmission_id, 'SYNTHETIC-TRANSMISSION');
  assert.equal(parsed.transmission_sig, 'SYNTHETIC-SIGNATURE');
  assert.deepEqual(parsed.webhook_event, JSON.parse(rawBody));
  assert.equal(parsed.webhook_event.resource.escaped, 'A');
  assert.equal(parsed.webhook_event.resource.value, 100);
  assert.equal(paypal.calls.filter((call) => call.path.startsWith('/v2/')).length, 0);
});

test('verified advertiser capture reuses stored status without provider calls and order is blocked outside awaiting_payment', async (t) => {
  const f = fixture(t, { checkout: true });
  const paypal = mockPayPal(f);
  const app = await f.create();
  const orderId = await orderAndCapture(f, app);
  assert.match(paypal.captured[0].requestId, /^[a-f0-9]{32}-p$/);
  assert.equal(paypal.captured[0].requestId.length, 34);
  assert.equal(paypal.captured[0].requestId.slice(0, -2), paypal.created[0].requestId.slice(0, -2));
  assert.notEqual(paypal.captured[0].requestId, paypal.created[0].requestId);
  const path = `/v1/sponsorship/applications/${app.applicationId}`;
  const headers = f.advertiser(app);
  for (const expected of ['awaiting_ad_approval', 'ready_to_publish', 'active']) {
    if (expected === 'ready_to_publish') assert.equal((await f.ownerAction(app, 'review', {
      decision: 'approve', notes: 'Synthetic reviewed material', destinationChecked: true, claimsChecked: true,
    })).status, 200);
    if (expected === 'active') assert.equal((await f.ownerAction(app, 'publish')).status, 200);
    const before = paypal.calls.length;
    const captured = await f.request(`${path}/capture`, { method: 'POST', headers, body: { orderId } });
    assert.equal(captured.status, 200);
    assert.equal(captured.json.status, expected);
    assert.equal(captured.json.paymentVerified, true);
    assert.equal((await f.request(`${path}/capture`, { method: 'POST', headers, body: { orderId: 'SYNTHETIC-WRONG-ORDER' } })).status, 409);
    assert.equal((await f.request(`${path}/order`, { method: 'POST', headers, body: {} })).status, 409);
    assert.equal(paypal.calls.length, before, `${expected}: advertiser retries must not query or mutate the provider`);
  }
  assert.equal(paypal.created.length, 1);
});

test('one dispute holds both published payments, deduplicates captures, and records dedupe only after a failed second stop is retried', async (t) => {
  const f = fixture(t, { checkout: true });
  const paypal = mockPayPal(f);
  const first = await publishedApplication(f);
  const second = await publishedApplication(f, {
    toolName: 'Second synthetic product', slot: 'buyer-intent-top', targetPage: '/best/claap-sales-follow-up-ai.html',
  });
  const event = { id: 'SYNTHETIC-TWO-PAYMENT-DISPUTE', event_type: 'CUSTOMER.DISPUTE.CREATED', resource: {
    supplementary_data: { related_ids: { order_id: first.orderId, capture_id: first.captureId } },
    disputed_transactions: [first.captureId, first.captureId, second.captureId, second.captureId].map((id) => ({ seller_transaction_id: id })),
  } };
  const originalBatch = f.db.batch.bind(f.db);
  const attemptedStops = [];
  let failSecond = true;
  t.mock.method(f.db, 'batch', async (statements) => {
    const stop = statements.find((statement) => /^\s*UPDATE sponsorship_payments SET state=\?/.test(statement.sql)
      && statement.values.includes('hold:CUSTOMER.DISPUTE.CREATED'));
    if (stop) {
      const id = stop.values.find((value) => value === first.app.applicationId || value === second.app.applicationId);
      attemptedStops.push(id);
      if (id === second.app.applicationId && failSecond) {
        failSecond = false;
        throw new Error('Synthetic failure while stopping the second payment');
      }
    }
    return originalBatch(statements);
  });
  f.env.CHECKOUT_ENABLED = 'false';
  const countEvent = () => f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_webhook_events WHERE event_id=?').bind(event.id).first();
  const readApplication = (id) => f.db.prepare('SELECT payment_status,publication_status FROM sponsorship_applications WHERE id=?').bind(id).first();
  const beforeProvider = paypal.calls.length;
  const failed = await paymentEvent(f, event);
  assert.equal(failed.status, 503);
  assert.deepEqual(attemptedStops, [first.app.applicationId, second.app.applicationId]);
  assert.equal((await countEvent()).n, 0, 'a partial attempt must remain retryable');
  assert.deepEqual(await readApplication(first.app.applicationId), { payment_status: 'review', publication_status: 'paused' });
  assert.deepEqual(await readApplication(second.app.applicationId), { payment_status: 'verified', publication_status: 'published' });

  const retried = await paymentEvent(f, event);
  assert.equal(retried.status, 200, JSON.stringify(retried.json));
  assert.deepEqual(retried.json, { accepted: true, matched: true, legacy: false });
  assert.deepEqual(attemptedStops, [first.app.applicationId, second.app.applicationId, first.app.applicationId, second.app.applicationId]);
  assert.equal((await countEvent()).n, 1);
  for (const item of [first, second]) {
    assert.deepEqual(await readApplication(item.app.applicationId), { payment_status: 'review', publication_status: 'paused' });
    const payment = await f.db.prepare('SELECT state,verification_reason FROM sponsorship_payments WHERE application_id=?').bind(item.app.applicationId).first();
    assert.deepEqual(payment, { state: 'review', verification_reason: 'hold:CUSTOMER.DISPUTE.CREATED' });
    const page = item.app.quote.targetPage;
    assert.deepEqual((await f.request(`/v1/sponsored/placements?path=${encodeURIComponent(page)}`)).json.placements, []);
  }
  const savedEvent = await f.db.prepare('SELECT capture_ids_json FROM sponsorship_webhook_events WHERE event_id=?').bind(event.id).first();
  assert.deepEqual(JSON.parse(savedEvent.capture_ids_json), [first.captureId, second.captureId]);
  const duplicate = await paymentEvent(f, event);
  assert.deepEqual(duplicate.json, { accepted: true, duplicate: true });
  assert.equal(attemptedStops.length, 4, 'an acknowledged duplicate must not stop either payment again');
  assert.equal(paypal.calls.slice(beforeProvider).filter((call) => call.path.startsWith('/v2/')).length, 0);
});

test('signed legacy refunds update the original fixed-price order and history while checkout is paused; late completion cannot resurrect it', async (t) => {
  const f = fixture(t);
  const paypal = mockPayPal(f);
  const legacy = await legacyOrder(f, paypal, 'REFUND', 'paid');
  await f.db.prepare(`INSERT INTO webhook_events(event_id,event_type,status,received_at,processed_at)
    VALUES(?,'PAYMENT.CAPTURE.COMPLETED','processed',?,?)`).bind('SYNTHETIC-HISTORICAL-EVENT', '2026-10-03T00:00:00Z', '2026-10-03T00:00:00Z').run();
  const read = () => f.db.prepare('SELECT * FROM orders WHERE provider_order_id=?').bind(legacy.orderId).first();
  const original = await read();
  const event = { id: 'SYNTHETIC-LEGACY-REFUND', event_type: 'PAYMENT.CAPTURE.REFUNDED', resource: {
    id: 'SYNTHETIC-LEGACY-REFUND-ID', supplementary_data: { related_ids: { capture_id: legacy.captureId } },
  } };
  const refunded = await paymentEvent(f, event);
  assert.equal(refunded.status, 200, JSON.stringify(refunded.json));
  assert.deepEqual(refunded.json, { accepted: true, matched: true, legacy: true });
  const saved = await read();
  assert.equal(saved.status, 'refunded');
  for (const field of ['id', 'provider_order_id', 'provider', 'amount', 'currency', 'created_at']) assert.equal(saved[field], original[field], field);
  const history = await f.db.prepare('SELECT event_id,event_type,status,processed_at FROM webhook_events ORDER BY event_id').all();
  assert.equal(history.results.length, 2);
  assert.equal(history.results.find((row) => row.event_id === 'SYNTHETIC-HISTORICAL-EVENT').status, 'processed');
  const refundHistory = history.results.find((row) => row.event_id === event.id);
  assert.equal(refundHistory.event_type, event.event_type);
  assert.equal(refundHistory.status, 'processed');
  assert.ok(Number.isFinite(Date.parse(refundHistory.processed_at)));
  assert.deepEqual((await paymentEvent(f, event)).json, { accepted: true, duplicate: true });
  assert.equal((await read()).updated_at, saved.updated_at);
  assert.equal((await paymentEvent(f, legacy.completion)).status, 200);
  assert.equal((await read()).status, 'refunded');
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM webhook_events').first()).n, 3);
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM orders').first()).n, 1);
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_payments').first()).n, 0);
});

test('legacy completion requires matching gross totals, currency, order, capture and merchant before recording paid history', async (t) => {
  const f = fixture(t);
  const paypal = mockPayPal(f);
  const invalid = [
    ['gross', (row) => { row.capture.amount.value = '0.01'; }],
    ['currency', (row) => { row.order.purchase_units[0].amount.currency_code = 'EUR'; }],
    ['order', (row) => { row.order.id = 'SYNTHETIC-DIFFERENT-ORDER'; }],
    ['capture', (row) => { row.capture.id = 'SYNTHETIC-DIFFERENT-CAPTURE'; }],
    ['order merchant', (row) => { row.order.purchase_units[0].payee.merchant_id = 'SYNTHETIC-OTHER-MERCHANT'; }],
    ['capture merchant', (row) => { row.capture.payee.merchant_id = 'SYNTHETIC-OTHER-MERCHANT'; }],
    ['capture order binding', (row) => { row.capture.supplementary_data.related_ids.order_id = 'SYNTHETIC-DIFFERENT-ORDER'; }],
  ];
  for (const [index, [label, change]] of invalid.entries()) {
    const legacy = await legacyOrder(f, paypal, `INVALID-${index}`);
    change(legacy);
    const result = await paymentEvent(f, legacy.completion);
    assert.equal(result.status, 409, `${label}: ${JSON.stringify(result.json)}`);
    assert.equal((await f.db.prepare('SELECT status FROM orders WHERE provider_order_id=?').bind(legacy.orderId).first()).status, 'pending', label);
    assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM webhook_events WHERE event_id=?').bind(legacy.completion.id).first()).n, 0, label);
    assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_webhook_events WHERE event_id=?').bind(legacy.completion.id).first()).n, 0, label);
  }
  const valid = await legacyOrder(f, paypal, 'MATCHING', 'created');
  const accepted = await paymentEvent(f, valid.completion);
  assert.equal(accepted.status, 200, JSON.stringify(accepted.json));
  assert.deepEqual(accepted.json, { accepted: true, matched: true, legacy: true });
  assert.equal((await f.db.prepare('SELECT status FROM orders WHERE provider_order_id=?').bind(valid.orderId).first()).status, 'paid');
  assert.equal((await f.db.prepare('SELECT status FROM webhook_events WHERE event_id=?').bind(valid.completion.id).first()).status, 'processed');
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_payments').first()).n, 0);
});

test('signed legacy order cancellation is preserved against a later completion event', async (t) => {
  const f = fixture(t);
  const paypal = mockPayPal(f);
  const legacy = await legacyOrder(f, paypal, 'CANCEL');
  const event = { id: 'SYNTHETIC-LEGACY-CANCELLATION', event_type: 'CHECKOUT.PAYMENT-APPROVAL.REVERSED', resource: { order_id: legacy.orderId } };
  const result = await paymentEvent(f, event);
  assert.equal(result.status, 200, JSON.stringify(result.json));
  assert.equal(result.json.legacy, true);
  assert.equal((await f.db.prepare('SELECT status FROM orders WHERE provider_order_id=?').bind(legacy.orderId).first()).status, 'cancelled');
  for (const terminal of ['paid', 'refunded']) {
    const row = await legacyOrder(f, paypal, `CANCEL-${terminal}`, terminal);
    const reversal = { id: `SYNTHETIC-APPROVAL-REVERSED-${terminal}`, event_type: 'CHECKOUT.PAYMENT-APPROVAL.REVERSED', resource: { order_id: row.orderId } };
    assert.equal((await paymentEvent(f, reversal)).status, 200);
    assert.equal((await f.db.prepare('SELECT status FROM orders WHERE provider_order_id=?').bind(row.orderId).first()).status, terminal);
  }
  assert.equal((await f.db.prepare('SELECT status FROM webhook_events WHERE event_id=?').bind(event.id).first()).status, 'processed');
  assert.equal((await paymentEvent(f, legacy.completion)).status, 200);
  assert.equal((await f.db.prepare('SELECT status FROM orders WHERE provider_order_id=?').bind(legacy.orderId).first()).status, 'cancelled');
});

test('a signed dispute arriving during capture verification cannot reactivate the ad or add a verified-payment audit', async (t) => {
  const f = fixture(t, { checkout: true });
  const paypal = mockPayPal(f);
  const current = await publishedApplication(f);
  const countVerified = () => f.db.prepare("SELECT COUNT(*) AS n FROM sponsorship_audit_log WHERE application_id=? AND action='payment_verified'").bind(current.app.applicationId).first();
  const before = (await countVerified()).n;
  const event = { id: 'SYNTHETIC-DISPUTE-DURING-VERIFY', event_type: 'CUSTOMER.DISPUTE.CREATED', resource: {
    disputed_transactions: [{ seller_transaction_id: current.captureId }],
  } };
  paypal.onCaptureRead = async (id) => {
    assert.equal(id, current.captureId);
    paypal.onCaptureRead = null;
    const stopped = await paymentEvent(f, event);
    assert.equal(stopped.status, 200, JSON.stringify(stopped.json));
  };
  const result = await f.ownerAction(current.app, 'verify-payment');
  assert.equal(result.status, 409, JSON.stringify(result.json));
  const saved = await f.db.prepare('SELECT payment_status,publication_status FROM sponsorship_applications WHERE id=?').bind(current.app.applicationId).first();
  assert.deepEqual(saved, { payment_status: 'review', publication_status: 'paused' });
  assert.equal((await countVerified()).n, before, 'a blocked verification must not log payment_verified');
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_webhook_events WHERE event_id=?').bind(event.id).first()).n, 1);
  assert.deepEqual((await f.request('/v1/sponsored/placements?path=/tool/pipedrive.html')).json.placements, []);
  const providerCalls = paypal.calls.length;
  assert.equal((await f.ownerAction(current.app, 'verify-payment')).status, 409);
  assert.equal(paypal.calls.length, providerCalls, 'a stored hold is rejected before provider verification');
});

test('a pending event cannot erase a dispute hold while its event record is still in flight', async (t) => {
  const f = fixture(t, { checkout: true });
  const paypal = mockPayPal(f);
  const app = await f.create();
  const orderId = await orderAndCapture(f, app);
  assert.equal((await f.ownerAction(app, 'review', {
    decision: 'approve', notes: 'Synthetic approved draft for concurrent webhook regression', destinationChecked: true, claimsChecked: true,
  })).status, 200);
  const { capture_id: captureId } = await f.db.prepare('SELECT capture_id FROM sponsorship_payments WHERE application_id=?').bind(app.applicationId).first();
  const countVerified = () => f.db.prepare("SELECT COUNT(*) AS n FROM sponsorship_audit_log WHERE application_id=? AND action='payment_verified'").bind(app.applicationId).first();
  const verifiedBefore = (await countVerified()).n;
  const disputeEvent = { id: 'SYNTHETIC-DISPUTE-RECORD-IN-FLIGHT', event_type: 'CUSTOMER.DISPUTE.CREATED', resource: {
    disputed_transactions: [{ seller_transaction_id: captureId }],
  } };
  let recordReached;
  let releaseRecord;
  const reached = new Promise((resolve) => { recordReached = resolve; });
  const resume = new Promise((resolve) => { releaseRecord = resolve; });
  const originalPrepare = f.db.prepare.bind(f.db);
  t.mock.method(f.db, 'prepare', (sql) => {
    const statement = originalPrepare(sql);
    if (sql.startsWith('INSERT INTO sponsorship_webhook_events')) {
      const originalRun = statement.run;
      statement.run = async function () {
        if (this.values[1] === disputeEvent.id && this.values[2] === disputeEvent.event_type) {
          recordReached();
          await resume;
        }
        return originalRun.call(this);
      };
    }
    return statement;
  });
  const dispute = paymentEvent(f, disputeEvent);
  let publish;
  let publishProviderCalls;
  try {
    assert.equal(await Promise.race([reached.then(() => true), dispute.then(() => false)]), true,
      'the dispute must reach the controlled record gate before completing');
    const held = await f.db.prepare('SELECT state,verification_reason FROM sponsorship_payments WHERE application_id=?').bind(app.applicationId).first();
    assert.deepEqual(held, { state: 'review', verification_reason: 'hold:CUSTOMER.DISPUTE.CREATED' });
    assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_webhook_events WHERE event_id=?').bind(disputeEvent.id).first()).n, 0);
    const pending = await paymentEvent(f, { id: 'SYNTHETIC-PENDING-DURING-DISPUTE', event_type: 'PAYMENT.CAPTURE.PENDING', resource: {
      id: captureId, supplementary_data: { related_ids: { order_id: orderId } },
    } });
    assert.equal(pending.status, 200, JSON.stringify(pending.json));
    const providerBefore = paypal.calls.length;
    publish = await f.ownerAction(app, 'publish');
    publishProviderCalls = paypal.calls.length - providerBefore;
  } finally {
    releaseRecord();
    const result = await dispute;
    assert.equal(result.status, 200, JSON.stringify(result.json));
  }
  assert.equal(publish.status, 409, 'the earlier signed dispute must still block publication before its dedupe record is saved');
  assert.equal(publishProviderCalls, 0, 'the persistent hold rejects publication before contacting the provider');
  const saved = await f.db.prepare(`SELECT a.payment_status,a.publication_status,p.verification_reason
    FROM sponsorship_applications a JOIN sponsorship_payments p ON p.application_id=a.id WHERE a.id=?`).bind(app.applicationId).first();
  assert.deepEqual(saved, { payment_status: 'review', publication_status: 'draft', verification_reason: 'hold:CUSTOMER.DISPUTE.CREATED' });
  assert.equal((await countVerified()).n, verifiedBefore);
  assert.equal((await f.db.prepare("SELECT COUNT(*) AS n FROM sponsorship_audit_log WHERE application_id=? AND action='published'").bind(app.applicationId).first()).n, 0);
  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_webhook_events WHERE event_id IN (?,?)').bind(disputeEvent.id, 'SYNTHETIC-PENDING-DURING-DISPUTE').first()).n, 2);
  assert.deepEqual((await f.request('/v1/sponsored/placements?path=/tool/pipedrive.html')).json.placements, []);
});


test('webhook subscription repair requires an authenticated same-origin owner and paused checkout', async (t) => {
  const f = fixture(t);
  const path = '/synthetic-owner/ads/repair-webhook-events';
  const body = { expectedCandidateId: 'SYNTHETIC-CANDIDATE' };
  const auth = { authorization: OWNER };
  assert.equal((await f.request(path, { method: 'POST', body })).status, 401);
  assert.equal((await f.request('/ops/ads/repair-webhook-events', { method: 'POST', body, headers: auth })).status, 401);
  assert.equal((await f.request(path, { method: 'POST', body, headers: { ...auth, origin: 'https://attacker.example' } })).status, 403);
  assert.equal((await f.request(path, { method: 'POST', body, headers: { ...auth, 'content-type': 'text/plain' } })).status, 415);
  for (const invalid of [{}, { ...body, url: 'https://attacker.example' }, { expectedCandidateId: '../wrong' }]) {
    assert.equal((await f.request(path, { method: 'POST', body: invalid, headers: auth })).status, 422);
  }
  f.env.CHECKOUT_ENABLED = 'true';
  assert.equal((await f.request(path, { method: 'POST', body, headers: auth })).status, 409);
  assert.equal(f.fetchMock.mock.callCount(), 0, 'all guards must reject before contacting PayPal');
  f.env.CHECKOUT_ENABLED = 'false';
  const calls = [];
  const candidate = { id: body.expectedCandidateId, url: `${ORIGIN}/v1/webhooks/paypal`, event_types: [{ name: '*' }] };
  f.fetchMock.mock.mockImplementation(async (url, options = {}) => {
    const parsed = new URL(url);
    assert.equal(parsed.origin, 'https://api-m.paypal.com');
    const operation = `${options.method || 'GET'} ${parsed.pathname}`;
    calls.push(operation);
    let data;
    if (operation === 'POST /v1/oauth2/token') data = { access_token: 'synthetic-repair-token' };
    else {
      assert.equal(options.headers.Authorization, 'Bearer synthetic-repair-token');
      if (operation === 'GET /v1/notifications/webhooks') data = { webhooks: [candidate] };
      else if (operation === `GET /v1/notifications/webhooks/${candidate.id}`) data = candidate;
      else assert.fail(`Unexpected provider operation: ${operation}`);
    }
    return new Response(JSON.stringify(data), { headers: { 'content-type': 'application/json' } });
  });
  const result = await f.request(path, { method: 'POST', body, headers: auth });
  assert.equal(result.status, 200);
  assert.equal(result.json.repair.status, 'already_complete');
  assert.equal(result.json.repair.requiredEventsVerified, true);
  assert.equal(result.json.repair.bindingRequired, true);
  assert.equal(result.json.webhookUrlVerified, false);
  assert.equal(result.json.requiredEventsVerified, false);
  assert.equal(result.json.merchantIdentityVerified, false);
  assert.equal(result.json.paymentReady, false);
  assert.equal(result.json.checks.checkoutEnabled, false);
  assert.deepEqual(calls, ['POST /v1/oauth2/token', 'GET /v1/notifications/webhooks', `GET /v1/notifications/webhooks/${candidate.id}`]);
  assert.equal(f.env.PAYPAL_WEBHOOK_ID, 'synthetic-webhook-id');
  assert.equal(f.env.CHECKOUT_ENABLED, 'false');
});

test('image advertising enforces upload-review-reserve-payment-publication order', async (t) => {
  const f = fixture(t, { checkout: true });
  const paypal = mockPayPal(f);
  const created = await f.request('/v1/ads/applications', { method: 'POST', body: INPUT });
  assert.equal(created.status, 201, JSON.stringify(created.json));
  assert.equal(created.json.creativeMode, 'image');
  assert.equal(created.json.status, 'preparing_materials');
  const app = {
    applicationId: created.json.applicationId,
    accessToken: created.json.accessToken,
  };
  const headers = { authorization: `Bearer ${app.accessToken}` };
  const base = `/v1/ads/applications/${app.applicationId}`;

  const earlyOrder = await f.request(base + '/order', { method: 'POST', body: {}, headers });
  assert.equal(earlyOrder.status, 409);
  assert.equal(paypal.calls.length, 0);

  f.db.exec(`INSERT INTO sponsorship_assets(id,application_id,role,mime,width,height,byte_size,sha256,data)
    VALUES('synthetic-logo-${app.applicationId}','${app.applicationId}','logo','image/png',400,400,1,'synthetic-logo-sha',X'00');
    INSERT INTO sponsorship_assets(id,application_id,role,mime,width,height,byte_size,sha256,data)
    VALUES('synthetic-main-${app.applicationId}','${app.applicationId}','tool-primary','image/png',600,600,1,'synthetic-main-sha',X'00');`);

  const submitted = await f.request(base + '/submit', { method: 'POST', body: {}, headers });
  assert.equal(submitted.status, 200, JSON.stringify(submitted.json));
  assert.equal(submitted.json.status, 'awaiting_review');

  const beforeReview = await f.request(base + '/order', { method: 'POST', body: {}, headers });
  assert.equal(beforeReview.status, 409);
  assert.equal(paypal.calls.length, 0);

  const reviewed = await f.ownerAction(app, 'review', {
    decision: 'approve',
    notes: 'Synthetic image materials, destination and claims reviewed.',
    destinationChecked: true,
    claimsChecked: true,
  });
  assert.equal(reviewed.status, 200, JSON.stringify(reviewed.json));
  assert.equal(reviewed.json.status, 'awaiting_payment');
  assert.equal(reviewed.json.reservationActive, true);

  const order = await f.request(base + '/order', { method: 'POST', body: {}, headers });
  assert.equal(order.status, 201, JSON.stringify(order.json));
  assert.equal(paypal.created.length, 1);

  const captured = await f.request(base + '/capture', {
    method: 'POST', body: { orderId: order.json.orderId }, headers,
  });
  assert.equal(captured.status, 200, JSON.stringify(captured.json));
  assert.equal(captured.json.paymentVerified, true);
  assert.equal(captured.json.status, 'active');
  assert.equal(captured.json.publicationStatus, 'published');

  const placements = await f.request('/v1/sponsored/placements?path=%2Ftool%2Fpipedrive.html');
  assert.equal(placements.status, 200);
  assert.equal(placements.json.placements.length, 1);
  assert.equal(placements.json.placements[0].creativeMode, 'image');
  assert.match(placements.json.placements[0].imageUrl, /\/v1\/ads\/assets\//);
  assert.match(placements.json.placements[0].logoUrl, /\/v1\/ads\/assets\//);

  assert.equal((await f.db.prepare('SELECT COUNT(*) AS n FROM sponsorship_holds WHERE application_id=?').bind(app.applicationId).first()).n, 0);
});


test('approved image application emails a signed payment-resume link once and accepts it for checkout status', async (t) => {
  const f = fixture(t, { checkout: true });
  f.env.RESEND_API_KEY = 'synthetic-resend-key';
  f.env.APPROVAL_LINK_SECRET = 'synthetic-approval-link-secret';
  const sent = [];
  f.fetchMock.mock.mockImplementation(async (url, options = {}) => {
    assert.equal(String(url), 'https://api.resend.com/emails');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers['idempotency-key'].startsWith('coshuma-approval/'), true);
    sent.push(JSON.parse(options.body));
    return new Response(JSON.stringify({ id: 'synthetic-resend-message' }), {
      status: 200, headers: { 'content-type': 'application/json' },
    });
  });

  const created = await f.request('/v1/ads/applications', { method: 'POST', body: INPUT });
  assert.equal(created.status, 201, JSON.stringify(created.json));
  const app = { applicationId: created.json.applicationId, accessToken: created.json.accessToken };
  const headers = f.advertiser(app);
  const base = '/v1/ads/applications/' + app.applicationId;
  f.db.exec(`INSERT INTO sponsorship_assets(id,application_id,role,mime,width,height,byte_size,sha256,data)
    VALUES('mail-logo-${app.applicationId}','${app.applicationId}','logo','image/png',400,400,1,'mail-logo-sha',X'00');
    INSERT INTO sponsorship_assets(id,application_id,role,mime,width,height,byte_size,sha256,data)
    VALUES('mail-main-${app.applicationId}','${app.applicationId}','tool-primary','image/png',600,600,1,'mail-main-sha',X'00');`);
  assert.equal((await f.request(base + '/submit', { method: 'POST', body: {}, headers })).status, 200);

  const reviewed = await f.ownerAction(app, 'review', {
    decision: 'approve',
    notes: 'Synthetic approval notification test.',
    destinationChecked: true,
    claimsChecked: true,
  });
  assert.equal(reviewed.status, 200, JSON.stringify(reviewed.json));
  assert.equal(reviewed.json.status, 'awaiting_payment');
  assert.equal(reviewed.json.approvalNotification.action, 'approval_email_sent');
  assert.equal(sent.length, 1);
  assert.deepEqual(sent[0].to, [INPUT.contactEmail]);
  const returnUrl = sent[0].text.split('\n').find((line) => line.startsWith('https://coshuma.com/advertise.html#coshuma-ad='));
  assert.ok(returnUrl);
  const decoded = decodeURIComponent(new URL(returnUrl).hash.slice('#coshuma-ad='.length));
  const [applicationId, resumeToken] = decoded.split('.');
  assert.equal(applicationId, app.applicationId);
  assert.match(resumeToken, /^[a-f0-9]{64}$/);

  const resumed = await f.request(base, { headers: { authorization: 'Bearer ' + resumeToken } });
  assert.equal(resumed.status, 200);
  assert.equal(resumed.json.applicationId, app.applicationId);
  assert.equal(resumed.json.status, 'awaiting_payment');

  const retried = await retryPendingApprovalEmails(f.env);
  assert.equal(retried.attempted, 1);
  assert.equal(retried.sent, 0);
  assert.equal(sent.length, 1, 'sent audit marker plus Resend idempotency prevent duplicate email');
  assert.equal((await f.db.prepare("SELECT COUNT(*) AS n FROM sponsorship_audit_log WHERE application_id=? AND action='approval_email_sent'")
    .bind(app.applicationId).first()).n, 1);
});
