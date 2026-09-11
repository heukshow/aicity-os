export const SPONSORSHIP_CURRENCY = 'USD';
export const SPONSORSHIP_PRODUCTS = Object.freeze({
  tool_page_7: { id: 'tool_page_7', placement: 'tool_page', durationDays: 7, amount: '19.00', label: 'Tool Page Sponsored — 7 days' },
  tool_page_30: { id: 'tool_page_30', placement: 'tool_page', durationDays: 30, amount: '49.00', label: 'Tool Page Sponsored — 30 days' },
  tool_page_90: { id: 'tool_page_90', placement: 'tool_page', durationDays: 90, amount: '129.00', label: 'Tool Page Sponsored — 90 days' },
  buyer_intent_7: { id: 'buyer_intent_7', placement: 'buyer_intent', durationDays: 7, amount: '39.00', label: 'Buyer-Intent Featured — 7 days' },
  buyer_intent_30: { id: 'buyer_intent_30', placement: 'buyer_intent', durationDays: 30, amount: '99.00', label: 'Buyer-Intent Featured — 30 days' },
  buyer_intent_90: { id: 'buyer_intent_90', placement: 'buyer_intent', durationDays: 90, amount: '269.00', label: 'Buyer-Intent Featured — 90 days' },
  comparison_7: { id: 'comparison_7', placement: 'comparison', durationDays: 7, amount: '59.00', label: 'Comparison Premium — 7 days' },
  comparison_30: { id: 'comparison_30', placement: 'comparison', durationDays: 30, amount: '149.00', label: 'Comparison Premium — 30 days' },
  comparison_90: { id: 'comparison_90', placement: 'comparison', durationDays: 90, amount: '399.00', label: 'Comparison Premium — 90 days' },
});
export const DEFAULT_PRODUCT_ID = 'tool_page_30';
export const SPONSORSHIP_AMOUNT = SPONSORSHIP_PRODUCTS[DEFAULT_PRODUCT_ID].amount;
export const ORDER_STATES = Object.freeze(['created', 'pending', 'paid', 'failed', 'cancelled', 'refunded']);

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

export function getProduct(productId = DEFAULT_PRODUCT_ID) {
  const product = SPONSORSHIP_PRODUCTS[productId];
  if (!product) throw new Error('Invalid sponsorship product');
  return product;
}

export function assertProductAmount(amount, productId) {
  const product = getProduct(productId);
  if (!amount || amount.currency_code !== SPONSORSHIP_CURRENCY || amount.value !== product.amount) {
    throw new Error('Provider amount does not match the selected sponsorship product');
  }
}

export function assertFixedAmount(amount) {
  return assertProductAmount(amount, DEFAULT_PRODUCT_ID);
}

export function orderCreatePayload(productId = DEFAULT_PRODUCT_ID) {
  const product = getProduct(productId);
  return {
    intent: 'CAPTURE',
    purchase_units: [{
      reference_id: `coshuma-${product.id}`,
      description: `COSHUMA ${product.label}`,
      custom_id: product.id,
      amount: { currency_code: SPONSORSHIP_CURRENCY, value: product.amount },
    }],
  };
}

export function captureIsVerifiedPaid(order, productId = DEFAULT_PRODUCT_ID) {
  if (order?.status !== 'COMPLETED') return false;
  const captures = order.purchase_units?.flatMap((unit) => unit.payments?.captures || []) || [];
  if (captures.length === 0) return false;
  for (const capture of captures) {
    if (capture.status !== 'COMPLETED') return false;
    assertProductAmount(capture.amount, productId);
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

export function validatePaidWebhook(event, productId = DEFAULT_PRODUCT_ID) {
  if (webhookTarget(event) !== 'paid') return;
  if (event?.resource?.status !== 'COMPLETED') throw new Error('Capture webhook is not completed');
  assertProductAmount(event?.resource?.amount, productId);
}
