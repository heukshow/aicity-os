import { getPayPalOrder, getPayPalCapture } from './paypal.js';
import { SponsorshipError } from './sponsorship-domain.js';

// Only called after PayPal webhook signature verification. Historical fixed-price
// orders keep receiving provider events even though their new-order endpoints retired.
export async function handleLegacyPayPalEvent(event, env, metadata, newPaymentCaptureIds = new Set()) {
  const providerRead = async (callback) => {
    try { return await callback(); } catch { throw new SponsorshipError('Historical payment provider evidence is unavailable', 502); }
  };
  const orders = new Map();
  const getOrder = async (id) => id ? env.ORDERS.prepare('SELECT * FROM orders WHERE provider_order_id=?').bind(id).first() : null;
  const direct = await getOrder(metadata.relatedOrderId);
  if (direct) orders.set(direct.provider_order_id, direct);
  const captureEvidence = new Map();
  for (const id of metadata.captureIds) {
    if (newPaymentCaptureIds.has(id)) continue;
    // Resolve older records that did not store a capture ID. No credentials or
    // raw provider response are returned to the caller or written to logs.
    const capture = await providerRead(() => getPayPalCapture(env, id));
    captureEvidence.set(id, capture);
    const order = await getOrder(capture.supplementary_data?.related_ids?.order_id);
    if (order) orders.set(order.provider_order_id, order);
  }
  if (!orders.size) return { matched: false };
  const duplicate = await env.ORDERS.prepare("SELECT 1 AS found FROM webhook_events WHERE event_id=? AND status='processed'").bind(event.id).first();
  if (duplicate) return { matched: true, duplicate: true };
  const statements = [];
  const now = new Date().toISOString();
  for (const legacy of orders.values()) {
    if (['PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED'].includes(event.event_type)) {
      // Keep the legacy refund semantics and preserve its original amount/history.
      statements.push(env.ORDERS.prepare("UPDATE orders SET status='refunded',updated_at=? WHERE provider_order_id=? AND status!='refunded'").bind(now, legacy.provider_order_id));
    } else if (['PAYMENT.CAPTURE.DENIED', 'PAYMENT.CAPTURE.DECLINED'].includes(event.event_type)) {
      statements.push(env.ORDERS.prepare("UPDATE orders SET status='failed',updated_at=? WHERE provider_order_id=? AND status IN ('created','pending')").bind(now, legacy.provider_order_id));
    } else if (['CHECKOUT.PAYMENT-APPROVAL.REVERSED', 'CHECKOUT.ORDER.VOIDED'].includes(event.event_type)) {
      // The documented pre-capture event uses resource.order_id. The older name
      // remains an input compatibility branch, not a claimed provider subscription.
      statements.push(env.ORDERS.prepare("UPDATE orders SET status='cancelled',updated_at=? WHERE provider_order_id=? AND status IN ('created','pending')").bind(now, legacy.provider_order_id));
    } else if (event.event_type === 'PAYMENT.CAPTURE.COMPLETED' && !['paid', 'refunded', 'failed', 'cancelled'].includes(legacy.status)) {
      if (env.PAYPAL_ENVIRONMENT !== 'live' || !env.PAYPAL_MERCHANT_ID) throw new SponsorshipError('Historical payment verification requires the expected live merchant', 503);
      const order = await providerRead(() => getPayPalOrder(env, legacy.provider_order_id));
      const unit = order.purchase_units?.length === 1 ? order.purchase_units[0] : null;
      const embedded = unit?.payments?.captures?.length === 1 ? unit.payments.captures[0] : null;
      const capture = embedded?.id ? captureEvidence.get(embedded.id) || await providerRead(() => getPayPalCapture(env, embedded.id)) : null;
      const amountMatches = (amount) => amount?.value === legacy.amount && amount.currency_code === legacy.currency;
      if (order.id !== legacy.provider_order_id || order.status !== 'COMPLETED'
          || unit?.payee?.merchant_id !== env.PAYPAL_MERCHANT_ID || !amountMatches(unit?.amount)
          || embedded?.status !== 'COMPLETED' || !amountMatches(embedded?.amount)
          || !capture || capture.id !== embedded.id || capture.status !== 'COMPLETED'
          || capture.payee?.merchant_id !== env.PAYPAL_MERCHANT_ID || !amountMatches(capture.amount)
          || capture.supplementary_data?.related_ids?.order_id !== legacy.provider_order_id) throw new SponsorshipError('Historical payment evidence did not verify', 409);
      statements.push(env.ORDERS.prepare("UPDATE orders SET status='pending',updated_at=? WHERE provider_order_id=? AND status='created'").bind(now, legacy.provider_order_id));
      statements.push(env.ORDERS.prepare("UPDATE orders SET status='paid',updated_at=? WHERE provider_order_id=? AND status='pending'").bind(now, legacy.provider_order_id));
    }
  }
  statements.push(env.ORDERS.prepare(`INSERT INTO webhook_events(event_id,event_type,status,received_at,processed_at) VALUES(?,?,'processed',?,?)
    ON CONFLICT(event_id) DO UPDATE SET status='processed',processed_at=excluded.processed_at`).bind(event.id, event.event_type, now, now));
  await env.ORDERS.batch(statements);
  return { matched: true, duplicate: false };
}
