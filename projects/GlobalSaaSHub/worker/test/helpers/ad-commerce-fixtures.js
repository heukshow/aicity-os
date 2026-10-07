// Local-only, synthetic fixtures. No network requests, disk database or production configuration.
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { deflateSync } from 'node:zlib';
import { AdStore } from '../../src/ad-commerce-store.js';
import { CATALOG_VERSION } from '../../src/ad-commerce-catalog.js';
export const TEST_MERCHANT = 'SYNTHETIC-MERCHANT';
export const TEST_REVIEW_KEY = 'synthetic-review-key-local-tests-only-v1';
export const TEST_ENV = Object.freeze({ PAYPAL_ENVIRONMENT: 'sandbox', PAYPAL_CLIENT_ID: 'SYNTHETIC-CLIENT',
  PAYPAL_CLIENT_SECRET: 'SYNTHETIC-SECRET', PAYPAL_MERCHANT_ID: TEST_MERCHANT });

export function memoryStore() {
  const native = new DatabaseSync(':memory:');
  native.exec('PRAGMA foreign_keys=ON');
  for (const file of ['0004_sponsorship_sales.sql', '0005_image_ad_fulfilment.sql']) {
    native.exec(readFileSync(new URL('../../migrations/' + file, import.meta.url), 'utf8'));
  }
  const db = { prepare(sql) { return { bind(...values) {
    const statement = native.prepare(sql);
    return {
      async first() { return statement.get(...values) ?? null; },
      async all() { return { results: statement.all(...values) }; },
      async run() { return { success: true, meta: { changes: Number(statement.run(...values).changes) } }; },
      exec() { return { success: true, meta: { changes: Number(statement.run(...values).changes) } }; },
    };
  } }; }, async batch(statements) {
    native.exec('BEGIN IMMEDIATE');
    try { const result = statements.map(statement => statement.exec()); native.exec('COMMIT'); return result; }
    catch (error) { native.exec('ROLLBACK'); throw error; }
  }};
  let time = Date.now();
  return { native, db, store: new AdStore(db, { environment: 'sandbox', clock: () => new Date(time) }),
    advance(ms) { time += ms; }, close() { native.close(); } };
}
export function syntheticInput(product = 'tool-primary', slots = ['tool-primary'], days = 30) {
  return { product, days, rightsConfirmed: true, termsVersion: CATALOG_VERSION,
    company: 'LOCAL SYNTHETIC TEST', productName: 'Synthetic software', email: 'test@example.com',
    claims: 'Synthetic test evidence only; no actual advertiser.',
    items: slots.map(slot => ({ slot, headline: 'Synthetic placement test', description: 'This is a local synthetic advertisement verification.',
      button: 'View test', alt: 'Synthetic solid-color test image', url: 'https://example.com/product' })) };
}
function crc32(bytes) {
  let crc = 0xffffffff;
  for (const b of bytes) { crc ^= b; for (let i = 0; i < 8; i++) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1)); }
  return (crc ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const name = Buffer.from(type), result = Buffer.alloc(12 + data.length);
  result.writeUInt32BE(data.length); name.copy(result, 4); data.copy(result, 8);
  result.writeUInt32BE(crc32(Buffer.concat([name, data])), result.length - 4);
  return result;
}
export function png(width, height) {
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(width); ihdr.writeUInt32BE(height, 4); ihdr[8] = 8; ihdr[9] = 6;
  const row = Buffer.alloc(1 + width * 4); row[0] = 0;
  for (let i = 1; i < row.length; i += 4) { row[i] = 50; row[i + 1] = 85; row[i + 2] = 140; row[i + 3] = 160; }
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]), chunk('IHDR', ihdr),
    chunk('IDAT', deflateSync(Buffer.concat(Array(height).fill(row)))), chunk('IEND', Buffer.alloc(0))]);
}
export function syntheticPayPal() {
  const records = new Map(), calls = [];
  let count = 0;
  const response = data => new Response(JSON.stringify(data), { headers: { 'Content-Type': 'application/json' } });
  const fetchImpl = async (url, init = {}) => {
    const target = new URL(url), method = init.method || 'GET';
    if (target.origin !== 'https://api-m.sandbox.paypal.com') throw new Error('Unexpected provider host; external network is disabled.');
    calls.push({ path: target.pathname, method });
    if (target.pathname === '/v1/notifications/verify-webhook-signature') return response({ verification_status: 'SUCCESS' });
    if (target.pathname === '/v1/oauth2/token') return response({ access_token: 'SYNTHETIC-TOKEN' });
    if (target.pathname === '/v2/checkout/orders' && method === 'POST') {
      const payload = JSON.parse(init.body), id = 'SYNTHETIC-ORDER-' + (++count);
      const order = { id, intent: payload.intent, status: 'CREATED', purchase_units: payload.purchase_units,
        links: [{ rel: 'approve', href: 'https://www.sandbox.paypal.com/checkoutnow?token=' + id }] };
      records.set(id, { order, capture: null });
      return response(order);
    }
    const match = /^\/v2\/checkout\/orders\/([^/]+)(\/capture)?$/.exec(target.pathname);
    if (match) {
      const record = records.get(decodeURIComponent(match[1]));
      if (!record) return new Response('{}', { status: 404 });
      if (match[2] && method === 'POST') {
        if (record.order.status !== 'APPROVED' && record.order.status !== 'COMPLETED') return new Response('{}', { status: 422 });
        const unit = record.order.purchase_units[0], id = 'SYNTHETIC-CAPTURE-' + record.order.id;
        record.capture = { id, status: 'COMPLETED', amount: unit.amount, payee: { merchant_id: TEST_MERCHANT },
          custom_id: unit.custom_id, invoice_id: unit.invoice_id, final_capture: true,
          supplementary_data: { related_ids: { order_id: record.order.id } } };
        record.order.status = 'COMPLETED';
        unit.payments = { captures: [record.capture] };
      }
      return response(record.order);
    }
    if (target.pathname.startsWith('/v2/payments/captures/')) {
      const id = decodeURIComponent(target.pathname.split('/').pop());
      const record = [...records.values()].find(item => item.capture?.id === id);
      return record ? response(record.capture) : new Response('{}', { status: 404 });
    }
    throw new Error('Unexpected synthetic provider request.');
  };
  return { fetchImpl, calls, records,
    approve(id) { const record = records.get(id); if (!record) throw new Error('Unknown synthetic order'); record.order.status = 'APPROVED'; } };
}
