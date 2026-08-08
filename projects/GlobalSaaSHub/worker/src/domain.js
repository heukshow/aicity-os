export const SPONSORSHIP_AMOUNT = '49.00';
export const SPONSORSHIP_CURRENCY = 'USD';
export const ORDER_STATES = Object.freeze([
  'created', 'pending', 'paid', 'failed', 'cancelled', 'refunded',
]);

const TRANSITIONS = Object.freeze({
  created: new Set(['pending', 'failed', 'cancelled']),
  pending: new Set(['paid', 'failed', 'cancelled']),
  paid: new Set(['refunded']),
  failed: new Set(),
  cancelled: new Set(),
  refunded: new Set(),
});

export function canTransition(from, to) {
  return from === to || Boolean(TRANSITIONS[from]?.has(to));
}

export function assertFixedAmount(amount) {
  if (!amount || amount.currency_code !== SPONSORSHIP_CURRENCY || amount.value !== SPONSORSHIP_AMOUNT) {
    throw new Error('Provider amount does not match the fixed sponsorship price');
  }
}

export function orderCreatePayload() {
  return {
    intent: 'CAPTURE',
    purchase_units: [{
      reference_id: 'globalsaashub-sponsorship',
      description: 'GlobalSaaSHub one-time sponsorship',
      amount: { currency_code: SPONSORSHIP_CURRENCY, value: SPONSORSHIP_AMOUNT },
    }],
  };
}

export function captureIsVerifiedPaid(order) {
  if (order?.status !== 'COMPLETED') return false;
  const captures = order.purchase_units?.flatMap((unit) => unit.payments?.captures || []) || [];
  if (captures.length === 0) return false;
  for (const capture of captures) {
    if (capture.status !== 'COMPLETED') return false;
    assertFixedAmount(capture.amount);
  }
  return true;
}

export function webhookTarget(event) {
  const type = event?.event_type;
  if (type === 'PAYMENT.CAPTURE.COMPLETED') return 'paid';
  if (type === 'PAYMENT.CAPTURE.DENIED') return 'failed';
  if (type === 'PAYMENT.CAPTURE.REFUNDED' || type === 'PAYMENT.CAPTURE.REVERSED') return 'refunded';
  return null;
}

export function providerOrderIdFromWebhook(event) {
  return event?.resource?.supplementary_data?.related_ids?.order_id || null;
}

export function validatePaidWebhook(event) {
  if (webhookTarget(event) !== 'paid') return;
  if (event?.resource?.status !== 'COMPLETED') throw new Error('Capture webhook is not completed');
  assertFixedAmount(event?.resource?.amount);
}
