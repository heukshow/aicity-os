// Isolated development lifecycle for PR #1039. Never imported by the production worker.
// An explicitly supplied transport is mandatory. Mock tests are not PayPal sandbox evidence.
import { AdError, imageQuote } from './ad-commerce-domain.js';
import { sandboxReturnUrls } from './ad-commerce-checkout-return.js';
import {
  createSponsorshipPayPalOrder, capturePayPalOrder, getPayPalOrder, getPayPalCapture,
} from './paypal.js';

const API_ORIGIN = 'https://api-m.sandbox.paypal.com';
const approvalHosts = new Set(['sandbox.paypal.com', 'www.sandbox.paypal.com']);
const fail = (message, status = 409) => { throw new AdError(message, status); };
const identifier = value => typeof value === 'string' && /^[A-Za-z0-9_-]{1,128}$/.test(value);
const nonempty = value => typeof value === 'string' && value.trim().length > 0;

export class SandboxAdPayments {
  constructor(store, { env, fetchImpl, returnOrigin } = {}) {
    if (!store?.db?.batch || typeof store?.q !== 'function' || typeof store?.now !== 'function') {
      fail('An isolated advertisement store is required.', 503);
    }
    if (env?.PAYPAL_ENVIRONMENT !== 'sandbox' ||
        !['PAYPAL_CLIENT_ID', 'PAYPAL_CLIENT_SECRET', 'PAYPAL_MERCHANT_ID'].every(key => nonempty(env[key])) ||
        typeof fetchImpl !== 'function') {
      fail('Explicit sandbox credentials and a sandbox transport are required.', 503);
    }
    this.store = store;
    this.env = Object.freeze({
      PAYPAL_ENVIRONMENT: 'sandbox', PAYPAL_CLIENT_ID: env.PAYPAL_CLIENT_ID,
      PAYPAL_CLIENT_SECRET: env.PAYPAL_CLIENT_SECRET, PAYPAL_MERCHANT_ID: env.PAYPAL_MERCHANT_ID,
    });
    this.fetch = async (input, options = {}) => {
      const url = new URL(input);
      if (url.origin !== API_ORIGIN || url.username || url.password || url.hash) {
        fail('The isolated payment transport permits only the PayPal sandbox API.', 503);
      }
      const response = await fetchImpl(url.href, { ...options, redirect: 'error' });
      if (response?.redirected || (response?.url && new URL(response.url).origin !== API_ORIGIN)) {
        fail('A sandbox provider redirect was rejected.', 503);
      }
      return response;
    };
    // Stable provider request IDs also protect retries across instances/restarts.
    this.pending = new Map();
    this.returnOrigin = returnOrigin;
  }

  async serial(id, operation) {
    const previous = this.pending.get(id) || Promise.resolve();
    const current = previous.catch(() => {}).then(operation);
    this.pending.set(id, current);
    try { return await current; }
    finally { if (this.pending.get(id) === current) this.pending.delete(id); }
  }

  async provider(operation) {
    try { return await operation(); }
    catch (error) {
      if (error instanceof AdError) throw error;
      fail('Sandbox provider confirmation is unavailable. Preserve this order for reconciliation.', 503);
    }
  }

  quote(order) {
    let stored, expected;
    try {
      stored = JSON.parse(order.quote_json);
      expected = imageQuote({
        product: order.product, days: order.days,
        rotation: stored.slots?.find(slot => typeof slot === 'string' && slot.endsWith('-rotation')),
      });
    } catch { fail('The saved sandbox quote is invalid.'); }
    if (order.amount !== expected.amount || order.currency !== 'USD' ||
        order.catalog_version !== expected.version ||
        ['version', 'product', 'days', 'amount', 'currency'].some(key => stored[key] !== expected[key]) ||
        JSON.stringify(stored.slots) !== JSON.stringify(expected.slots)) {
      fail('The saved sandbox quote does not match its immutable terms.');
    }
    return expected;
  }

  async holds(order, at = this.store.now()) {
    const slots = this.quote(order).slots;
    const rows = (await this.store.q(
      'SELECT slot,expires_at FROM ad_sale_holds WHERE order_id=?', order.id,
    ).all()).results;
    if (!(order.hold_until > at) || rows.length !== slots.length ||
        slots.some(slot => !rows.some(row => row.slot === slot && row.expires_at > at))) {
      fail('Every reviewed position must have a valid reservation before checkout or capture.');
    }
    return slots;
  }

  localPayment(order) {
    if (!identifier(order.provider_order) || order.payment_environment !== 'sandbox' ||
        order.merchant_id !== this.env.PAYPAL_MERCHANT_ID) {
      fail('The stored payment is not bound to this sandbox merchant.');
    }
    this.quote(order);
  }

  async noStopEvent(order) {
    const event = await this.store.q(`SELECT id FROM ad_sale_events WHERE environment='sandbox'
      AND (provider_order=? OR EXISTS(SELECT 1 FROM json_each(capture_ids_json) WHERE value=?))
      AND (event_type IN('PAYMENT.CAPTURE.REFUNDED','PAYMENT.CAPTURE.REVERSED',
        'CHECKOUT.PAYMENT-APPROVAL.REVERSED') OR event_type LIKE 'CUSTOMER.DISPUTE.%') LIMIT 1`,
      order.provider_order, order.capture_id || null).first();
    if (event) fail('A verified stop event requires sandbox payment review.');
  }

  payload(order) {
    this.quote(order);
    return { intent: 'CAPTURE', purchase_units: [{
      reference_id: order.id, custom_id: order.id, invoice_id: order.reference,
      description: ('SANDBOX advertisement ' + order.product + ' / ' + order.days + ' days').slice(0, 127),
      payee: { merchant_id: this.env.PAYPAL_MERCHANT_ID },
      amount: { currency_code: 'USD', value: order.amount },
    }] };
  }

  binding(providerOrder, order, expectedId = order.provider_order) {
    const units = providerOrder?.purchase_units;
    if (!identifier(providerOrder?.id) || (expectedId && providerOrder.id !== expectedId) ||
        providerOrder.intent !== 'CAPTURE' || !Array.isArray(units) || units.length !== 1) {
      fail('Sandbox provider order identity does not match this advertisement.');
    }
    const unit = units[0];
    if (unit.reference_id !== order.id || unit.custom_id !== order.id || unit.invoice_id !== order.reference ||
        unit.payee?.merchant_id !== this.env.PAYPAL_MERCHANT_ID ||
        unit.amount?.currency_code !== 'USD' || unit.amount?.value !== order.amount) {
      fail('Sandbox provider amount, merchant or application binding does not match.');
    }
    return unit;
  }

  approval(providerOrder) {
    const link = providerOrder.links?.find(item => ['approve', 'payer-action'].includes(item.rel));
    let url;
    try { url = new URL(link?.href); } catch { fail('PayPal did not return a sandbox approval link.', 502); }
    if (url.protocol !== 'https:' || !approvalHosts.has(url.hostname) || url.port ||
        url.username || url.password || url.hash || url.pathname !== '/checkoutnow' ||
        url.searchParams.get('token') !== providerOrder.id) {
      fail('The returned approval link is not bound to this sandbox order.', 502);
    }
    return url.href;
  }

  checkout(id) { return this.serial(id, () => this.beginCheckout(id)); }

  async beginCheckout(id) {
    let order = await this.store.requireState(id, ['approved', 'checkout']);
    await this.holds(order);
    if (order.state === 'checkout') this.localPayment(order);
    const payload = this.payload(order);
    if (this.returnOrigin && !order.provider_order) {
      payload.payment_source = { paypal: { experience_context: {
        ...await sandboxReturnUrls(order, this.returnOrigin, this.store.clock().getTime()),
        brand_name: 'COSHUMA', shipping_preference: 'NO_SHIPPING', user_action: 'PAY_NOW',
      } } };
    }
    const providerOrder = await this.provider(() => order.provider_order
      ? getPayPalOrder(this.env, order.provider_order, this.fetch)
      : createSponsorshipPayPalOrder(this.env, 'ad-' + id.replaceAll('-', '') + '-create', payload, this.fetch));
    this.binding(providerOrder, order);
    if (!['CREATED', 'APPROVED', 'PAYER_ACTION_REQUIRED'].includes(providerOrder.status)) {
      fail('This sandbox order requires reconciliation before another checkout.');
    }
    const approvalUrl = this.approval(providerOrder);
    const at = this.store.now();
    await this.holds(order, at);
    if (order.state === 'approved') {
      const result = await this.store.db.batch([
        this.store.q(`UPDATE ad_sale_orders SET state='checkout',provider_order=?,merchant_id=?,
          payment_environment='sandbox',updated_at=? WHERE id=? AND state='approved'
          AND provider_order IS NULL AND hold_until>?`,
          providerOrder.id, this.env.PAYPAL_MERCHANT_ID, at, id, at),
        this.store.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
          SELECT ?,?,'sandbox_checkout_created','sandbox_service',?,? WHERE changes()=1`,
          crypto.randomUUID(), id, 'Sandbox provider order bound to reviewed reservation', at),
      ]);
      order = await this.store.get(id);
      if (result[0].meta.changes !== 1 &&
          !(order?.state === 'checkout' && order.provider_order === providerOrder.id)) {
        fail('The reservation changed while sandbox checkout was being prepared.');
      }
    }
    return { order: await this.store.get(id), approvalUrl };
  }

  capture(id) { return this.serial(id, () => this.finishCapture(id, true)); }
  reconcile(id, options = {}) { return this.serial(id, () => this.finishCapture(id, false, options)); }

  async finishCapture(id, allowCapture, { expectedCaptureIds, actor = 'sandbox_service' } = {}) {
    if (!['sandbox_service', 'sandbox_webhook', 'sandbox_webhook_retry'].includes(actor) ||
        (expectedCaptureIds !== undefined && (!Array.isArray(expectedCaptureIds) || expectedCaptureIds.length !== 1 ||
          !expectedCaptureIds.every(identifier)))) fail('Invalid sandbox reconciliation context.', 503);
    const captureMatches = value => expectedCaptureIds === undefined || expectedCaptureIds.includes(value);
    let order = await this.store.requireState(id, ['checkout', 'capturing', 'active', 'ended']);
    this.localPayment(order);
    await this.noStopEvent(order);
    if (['active', 'ended'].includes(order.state)) {
      if (!captureMatches(order.capture_id)) fail('The completed event does not match this sandbox capture.');
      return order;
    }
    // Before our first capture attempt, a known unapproved order must remain checkout.
    // A failed preflight read also cannot justify an indefinite capturing reservation.
    if (order.state === 'checkout') await this.holds(order);
    let providerOrder = await this.provider(() => getPayPalOrder(this.env, order.provider_order, this.fetch));
    const beforeUnit = this.binding(providerOrder, order);
    if (expectedCaptureIds !== undefined && (providerOrder.status !== 'COMPLETED' ||
        beforeUnit.payments?.captures?.length !== 1 || !captureMatches(beforeUnit.payments.captures[0]?.id))) {
      fail('The completed event does not match the provider-confirmed sandbox capture.');
    }
    if (providerOrder.status !== 'COMPLETED' &&
        (!allowCapture || providerOrder.status !== 'APPROVED' || (beforeUnit.payments?.captures?.length || 0) > 0)) {
      fail('Sandbox payment is not approved for capture; no new capture request was sent.');
    }
    if (order.state === 'checkout') {
      // Provider reads may cross the reservation deadline. Recheck before the atomic claim.
      const at = this.store.now(), slots = await this.holds(order, at);
      await this.noStopEvent(order);
      await this.store.db.batch([
        this.store.q(`UPDATE ad_sale_orders SET state='capturing',updated_at=?
          WHERE id=? AND state='checkout' AND hold_until>?
          AND (SELECT count(*) FROM ad_sale_holds WHERE order_id=? AND expires_at>?)=?`,
          at, id, at, id, at, slots.length),
        this.store.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
          SELECT ?,?,'sandbox_capture_started',?,?,? WHERE changes()=1`,
          crypto.randomUUID(), id, actor, 'Reservation retained until provider outcome is reconciled', at),
      ]);
      order = await this.store.get(id);
      if (['active', 'ended'].includes(order.state)) return order;
      if (order.state !== 'capturing') fail('The reservation changed before sandbox capture.');
    }
    // Once a capture can have been attempted, never release its reservation on uncertainty.
    // Retries read provider truth above before using the same stable capture request ID.
    if (providerOrder.status !== 'COMPLETED') {
      await this.noStopEvent(order);
      await this.provider(() => capturePayPalOrder(
        this.env, order.provider_order, 'ad-' + id.replaceAll('-', '') + '-capture', this.fetch,
      ));
      providerOrder = await this.provider(() => getPayPalOrder(this.env, order.provider_order, this.fetch));
    }
    const unit = this.binding(providerOrder, order);
    const captures = unit.payments?.captures;
    if (providerOrder.status !== 'COMPLETED' || !Array.isArray(captures) || captures.length !== 1 ||
        !identifier(captures[0]?.id)) fail('A single completed sandbox capture is required.');
    const item = captures[0];
    const capture = await this.provider(() => getPayPalCapture(this.env, item.id, this.fetch));
    const amountMatches = value => value?.currency_code === 'USD' && value?.value === order.amount;
    if (item.status !== 'COMPLETED' || capture?.status !== 'COMPLETED' || capture.id !== item.id ||
        !amountMatches(item.amount) || !amountMatches(capture.amount) ||
        capture.payee?.merchant_id !== this.env.PAYPAL_MERCHANT_ID ||
        capture.supplementary_data?.related_ids?.order_id !== order.provider_order ||
        (capture.invoice_id !== undefined && capture.invoice_id !== order.reference) ||
        (capture.custom_id !== undefined && capture.custom_id !== order.id) ||
        item.final_capture === false || capture.final_capture === false) {
      fail('Sandbox capture evidence does not match the quoted advertisement.');
    }
    const at = this.store.now(), until = new Date(Date.parse(at) + order.days * 86400000).toISOString();
    await this.store.db.batch([
      this.store.q(`UPDATE ad_sale_holds SET expires_at=? WHERE order_id=?
        AND EXISTS(SELECT 1 FROM ad_sale_orders WHERE id=? AND state='capturing'
          AND provider_order=? AND payment_environment='sandbox' AND merchant_id=?)`,
        until, id, id, order.provider_order, this.env.PAYPAL_MERCHANT_ID),
      this.store.q(`UPDATE ad_sale_orders SET state='active',capture_id=?,payment_verified_at=?,
        starts_at=?,ends_at=?,hold_until=?,updated_at=? WHERE id=? AND state='capturing'
        AND provider_order=? AND payment_environment='sandbox' AND merchant_id=?`,
        capture.id, at, at, until, until, at, id, order.provider_order, this.env.PAYPAL_MERCHANT_ID),
      this.store.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
        SELECT ?,?,'sandbox_payment_verified',?,?,? WHERE changes()=1`,
        crypto.randomUUID(), id, actor, 'Sandbox order and capture matched; all positions activated atomically', at),
    ]);
    const saved = await this.store.get(id);
    if (saved.state !== 'active' || saved.capture_id !== capture.id) {
      fail('Sandbox publication did not commit; preserve the payment for reconciliation.');
    }
    return saved;
  }

  async expire() {
    const at = this.store.now();
    const orders = (await this.store.q(`SELECT id FROM ad_sale_orders
      WHERE state='active' AND ends_at<=? AND payment_environment='sandbox' AND merchant_id=?`,
      at, this.env.PAYPAL_MERCHANT_ID).all()).results;
    let ended = 0;
    for (const { id } of orders) {
      const result = await this.store.db.batch([
        this.store.q(`UPDATE ad_sale_orders SET state='ended',updated_at=?
          WHERE id=? AND state='active' AND ends_at<=? AND payment_environment='sandbox' AND merchant_id=?`,
          at, id, at, this.env.PAYPAL_MERCHANT_ID),
        this.store.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
          SELECT ?,?,'sandbox_period_ended','sandbox_service',?,? WHERE changes()=1`,
          crypto.randomUUID(), id, 'Sandbox advertising period ended', at),
        this.store.q(`DELETE FROM ad_sale_holds WHERE order_id=?
          AND EXISTS(SELECT 1 FROM ad_sale_orders WHERE id=? AND state='ended' AND ends_at<=?)`, id, id, at),
      ]);
      ended += result[0].meta.changes;
    }
    return ended;
  }
}
