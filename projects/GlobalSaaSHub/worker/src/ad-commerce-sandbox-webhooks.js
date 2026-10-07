// Isolated sandbox webhook processing. Not imported by any production entry point.
// Verified events are durable before order changes; no refund or capture POST is issued here.
import { AdError } from './ad-commerce-domain.js';
import { verifyPayPalWebhook } from './paypal.js';

const API = 'https://api-m.sandbox.paypal.com';
const LIMIT = 65536;
const HINT_ORIGINS = new Set([API, 'https://api.sandbox.paypal.com']);
const REQUIRED_HEADERS = ['paypal-transmission-id', 'paypal-transmission-time', 'paypal-cert-url',
  'paypal-auth-algo', 'paypal-transmission-sig'];
const ID = /^[A-Za-z0-9_-]{1,128}$/;
const nonempty = value => typeof value === 'string' && value.trim().length > 0;
const stopTypes = new Set(['PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED', 'CHECKOUT.PAYMENT-APPROVAL.REVERSED']);
const isStop = type => stopTypes.has(type) || type.startsWith('CUSTOMER.DISPUTE.');
const reply = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer' },
});
const fail = (message, status = 422) => { throw new AdError(message, status); };

async function rawBody(request) {
  if (request.headers.get('content-type')?.split(';')[0].trim().toLowerCase() !== 'application/json') {
    fail('A JSON webhook is required.', 415);
  }
  const declared = request.headers.get('content-length');
  if (declared && (!/^\d+$/.test(declared) || Number(declared) > LIMIT)) fail('Webhook is too large.', 413);
  const reader = request.body?.getReader();
  if (!reader) fail('Webhook body is required.', 400);
  const chunks = []; let length = 0;
  try {
    while (true) {
      const result = await reader.read();
      if (result.done) break;
      length += result.value.byteLength;
      if (length > LIMIT) { await reader.cancel(); fail('Webhook is too large.', 413); }
      chunks.push(result.value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(length); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  try { return new TextDecoder('utf-8', { fatal: true }).decode(bytes); }
  catch { fail('Webhook must be valid UTF-8.', 400); }
}

function related(event) {
  const resource = event.resource || {}, type = event.event_type;
  const captures = new Set();
  let providerOrder = null;
  const add = value => { if (typeof value === 'string' && ID.test(value)) captures.add(value); };
  const order = value => { if (typeof value === 'string' && ID.test(value)) providerOrder = value; };
  if (type.startsWith('PAYMENT.CAPTURE.')) {
    order(resource.supplementary_data?.related_ids?.order_id);
    if (type === 'PAYMENT.CAPTURE.REFUNDED') {
      // A refund resource.id identifies the refund, never the original capture.
      add(resource.supplementary_data?.related_ids?.capture_id);
      for (const link of Array.isArray(resource.links) ? resource.links : []) {
        if (link.rel !== 'up' || typeof link.href !== 'string') continue;
        try {
          const url = new URL(link.href);
          if (!HINT_ORIGINS.has(url.origin) || url.username || url.password || url.search || url.hash) continue;
          const match = /^\/v2\/payments\/captures\/([A-Za-z0-9_-]{1,128})$/.exec(url.pathname);
          if (match) add(match[1]);
        } catch { /* No supplied link is ever fetched. */ }
      }
    } else add(resource.id);
  } else if (type.startsWith('CUSTOMER.DISPUTE.')) {
    for (const transaction of Array.isArray(resource.disputed_transactions) ? resource.disputed_transactions : []) {
      add(transaction.seller_transaction_id);
    }
  } else if (type === 'CHECKOUT.PAYMENT-APPROVAL.REVERSED') order(resource.order_id);
  return { providerOrder, captureIds: [...captures].sort() };
}

export class SandboxAdWebhooks {
  constructor(store, payments, { env, fetchImpl } = {}) {
    const keys = ['PAYPAL_CLIENT_ID', 'PAYPAL_CLIENT_SECRET', 'PAYPAL_MERCHANT_ID', 'PAYPAL_WEBHOOK_ID'];
    if (!store?.db?.batch || typeof store.q !== 'function' || payments?.store !== store ||
        typeof payments.reconcile !== 'function' || env?.PAYPAL_ENVIRONMENT !== 'sandbox' ||
        !keys.every(key => nonempty(env[key])) || typeof fetchImpl !== 'function' ||
        payments.env?.PAYPAL_ENVIRONMENT !== 'sandbox' ||
        payments.env.PAYPAL_MERCHANT_ID !== env.PAYPAL_MERCHANT_ID ||
        payments.env.PAYPAL_CLIENT_ID !== env.PAYPAL_CLIENT_ID) {
      fail('An isolated store, matching sandbox payment configuration and explicit webhook transport are required.', 503);
    }
    this.store = store; this.payments = payments;
    this.env = Object.freeze(Object.fromEntries(['PAYPAL_ENVIRONMENT', ...keys].map(key => [key, env[key]])));
    this.fetch = async (input, options = {}) => {
      const url = new URL(input);
      if (url.origin !== API || url.username || url.password || url.hash) fail('Only the sandbox API is permitted.', 503);
      const response = await fetchImpl(url.href, { ...options, redirect: 'error' });
      if (response?.redirected || (response?.url && new URL(response.url).origin !== API)) {
        fail('Sandbox redirects are forbidden.', 503);
      }
      return response;
    };
  }

  async matching(ids) {
    return (await this.store.q(`SELECT * FROM ad_sale_orders WHERE payment_environment='sandbox'
      AND merchant_id=? AND ((? IS NOT NULL AND provider_order=?)
        OR (capture_id IS NOT NULL AND EXISTS(SELECT 1 FROM json_each(?) WHERE value=capture_id)))`,
      this.env.PAYPAL_MERCHANT_ID, ids.providerOrder, ids.providerOrder, JSON.stringify(ids.captureIds)).all()).results;
  }

  async stop(order, event) {
    // A capture request may have succeeded while its response was lost. Keep its position
    // reserved until separate provider reconciliation establishes the outcome.
    if (order.state === 'capturing') return { retainedCapturing: 1, stopped: 0 };
    if (!['checkout', 'active', 'ended', 'held'].includes(order.state)) return { retainedCapturing: 0, stopped: 0 };
    const fullRefund = ['PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED'].includes(event.event_type) &&
      event.resource?.amount?.currency_code === order.currency && event.resource?.amount?.value === order.amount;
    const state = fullRefund ? 'refunded' : 'held';
    if (order.state === 'held' && state === 'held') return { retainedCapturing: 0, stopped: 0 };
    const at = this.store.now();
    const result = await this.store.db.batch([
      this.store.q(`UPDATE ad_sale_orders SET state=?,updated_at=? WHERE id=? AND state=?
        AND payment_environment='sandbox' AND merchant_id=?`,
        state, at, order.id, order.state, this.env.PAYPAL_MERCHANT_ID),
      this.store.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
        SELECT ?,?,'sandbox_webhook_stopped','sandbox_webhook',?,? WHERE changes()=1`,
        crypto.randomUUID(), order.id, event.event_type + ' / ' + event.id, at),
      this.store.q(`DELETE FROM ad_sale_holds WHERE order_id=? AND EXISTS
        (SELECT 1 FROM ad_sale_orders WHERE id=? AND state IN('held','refunded','ended')
          AND payment_environment='sandbox' AND merchant_id=?)`,
        order.id, order.id, this.env.PAYPAL_MERCHANT_ID),
    ]);
    const saved = await this.store.get(order.id);
    if (saved.state === 'capturing') return { retainedCapturing: 1, stopped: 0 };
    if (!['held', 'refunded', 'cancelled', 'rejected'].includes(saved.state)) {
      fail('A stopped sandbox order requires another processing attempt.', 503);
    }
    return { retainedCapturing: 0, stopped: result[0].meta.changes };
  }

  async handle(request) {
    let durable = false;
    try {
      if (request.method !== 'POST') return reply({ error: 'Method not allowed.' }, 405);
      for (const header of REQUIRED_HEADERS) {
        const value = request.headers.get(header);
        if (!value?.trim() || value.length > 4096) fail('All PayPal signature headers are required.', 400);
      }
      const raw = await rawBody(request);
      let event;
      try { event = JSON.parse(raw); } catch { fail('Webhook contains invalid JSON.', 400); }
      if (!event || typeof event !== 'object' || Array.isArray(event) || typeof event.id !== 'string' || !ID.test(event.id) ||
          typeof event.event_type !== 'string' || !/^[A-Z][A-Z0-9_.-]{1,127}$/.test(event.event_type) ||
          !event.resource || typeof event.resource !== 'object' || Array.isArray(event.resource)) {
        fail('Webhook identity, event type and resource are required.', 400);
      }
      let signature;
      try { signature = await verifyPayPalWebhook(this.env, request.headers, event, this.fetch, raw); }
      catch { fail('Sandbox signature verification is unavailable.', 503); }
      if (signature?.verification_status !== 'SUCCESS') fail('Webhook signature was not verified.', 401);
      const ids = related(event), at = this.store.now(), capturesJson = JSON.stringify(ids.captureIds);
      const results = await this.store.db.batch([this.store.q(`INSERT INTO ad_sale_events
        (environment,id,event_type,provider_order,capture_ids_json,received_at)
        VALUES('sandbox',?,?,?,?,?) ON CONFLICT(environment,id) DO NOTHING`,
        event.id, event.event_type, ids.providerOrder, capturesJson, at)]);
      durable = true;
      const saved = await this.store.q("SELECT * FROM ad_sale_events WHERE environment='sandbox' AND id=?", event.id).first();
      if (saved.event_type !== event.event_type || saved.provider_order !== ids.providerOrder || saved.capture_ids_json !== capturesJson) {
        fail('A stored webhook identity cannot be changed.', 409);
      }
      const duplicate = results[0].meta.changes === 0;
      if (saved.processed_at) return reply({ received: true, processed: true, duplicate: true });
      const actionable = event.event_type === 'PAYMENT.CAPTURE.COMPLETED' || isStop(event.event_type);
      const orders = actionable ? await this.matching(ids) : [];
      if (actionable && orders.length === 0) {
        // A stop event arriving before local provider attachment still guards later capture.
        // Keep it unprocessed so a replay can reconcile a subsequently bound order.
        return reply({ received: true, processed: false, duplicate, matched: 0 }, 202);
      }
      let stopped = 0, retainedCapturing = 0;
      for (const order of orders) {
        if (isStop(event.event_type)) {
          const result = await this.stop(order, event);
          stopped += result.stopped; retainedCapturing += result.retainedCapturing;
        } else if (['checkout', 'capturing', 'active', 'ended'].includes(order.state)) {
          const reconciled = await this.payments.reconcile(order.id);
          if (!['active', 'ended'].includes(reconciled.state) ||
              (ids.captureIds.length && !ids.captureIds.includes(reconciled.capture_id))) {
            fail('Completed event and reconciled sandbox capture do not match.', 503);
          }
        }
      }
      await this.store.db.batch([this.store.q(`UPDATE ad_sale_events SET processed_at=?
        WHERE environment='sandbox' AND id=? AND processed_at IS NULL`, this.store.now(), event.id)]);
      return reply({ received: true, processed: true, duplicate, matched: orders.length, stopped, retainedCapturing });
    } catch (error) {
      if (durable) return reply({ received: true, processed: false,
        error: 'Verified event is saved; processing needs retry or sandbox review.' }, error?.status === 409 ? 409 : 503);
      return reply({ received: false, error: error instanceof AdError ? error.message : 'Sandbox webhook processing failed.' },
        error instanceof AdError ? error.status : 503);
    }
  }
}
