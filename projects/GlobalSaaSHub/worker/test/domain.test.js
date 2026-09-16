import assert from 'node:assert/strict';
import test from 'node:test';
import {
  assertFixedAmount,
  assertProductAmount,
  canTransition,
  captureIsVerifiedPaid,
  getProduct,
  orderCreatePayload,
  SPONSORSHIP_PRODUCTS,
  validatePaidWebhook,
} from '../src/domain.js';

test('sponsorship catalog contains all nine server-owned products', () => {
  assert.equal(Object.keys(SPONSORSHIP_PRODUCTS).length, 9);
  assert.deepEqual(getProduct('tool_page_7'), {
    id: 'tool_page_7', placement: 'tool_page', durationDays: 7,
    amount: '19.00', label: 'Tool Page Sponsored — 7 days',
  });
  assert.equal(getProduct('comparison_90').amount, '399.00');
  assert.throws(() => getProduct('made_up_product'));
});

test('create payload uses selected server-owned product price', () => {
  const maliciousClientBody = { amount: { value: '0.01', currency_code: 'KRW' } };
  void maliciousClientBody;
  assert.deepEqual(orderCreatePayload('buyer_intent_30').purchase_units[0].amount, {
    currency_code: 'USD', value: '99.00',
  });
  assert.equal(orderCreatePayload('buyer_intent_30').purchase_units[0].custom_id, 'buyer_intent_30');
});

test('legacy default remains the original 49.00 USD product while checkout is migrated', () => {
  assert.deepEqual(orderCreatePayload().purchase_units[0].amount, {
    currency_code: 'USD', value: '49.00',
  });
  assert.doesNotThrow(() => assertFixedAmount({ value: '49.00', currency_code: 'USD' }));
});

test('provider amount validation fails closed for the selected product', () => {
  assert.doesNotThrow(() => assertProductAmount(
    { value: '149.00', currency_code: 'USD' }, 'comparison_30',
  ));
  assert.throws(() => assertProductAmount(
    { value: '149.01', currency_code: 'USD' }, 'comparison_30',
  ));
  assert.throws(() => assertProductAmount(
    { value: '149.00', currency_code: 'KRW' }, 'comparison_30',
  ));
});

test('unverified or incomplete capture cannot become paid', () => {
  assert.equal(captureIsVerifiedPaid({ status: 'APPROVED' }, 'tool_page_7'), false);
  assert.equal(captureIsVerifiedPaid({ status: 'COMPLETED', purchase_units: [] }, 'tool_page_7'), false);
  assert.equal(captureIsVerifiedPaid({
    status: 'COMPLETED', purchase_units: [{ payments: { captures: [{
      status: 'PENDING', amount: { value: '19.00', currency_code: 'USD' },
    }] } }],
  }, 'tool_page_7'), false);
});

test('verified selected-product completed capture is paid', () => {
  assert.equal(captureIsVerifiedPaid({
    status: 'COMPLETED', purchase_units: [{ payments: { captures: [{
      status: 'COMPLETED', amount: { value: '269.00', currency_code: 'USD' },
    }] } }],
  }, 'buyer_intent_90'), true);
});

test('capture with another product price fails closed', () => {
  assert.throws(() => captureIsVerifiedPaid({
    status: 'COMPLETED', purchase_units: [{ payments: { captures: [{
      status: 'COMPLETED', amount: { value: '39.00', currency_code: 'USD' },
    }] } }],
  }, 'buyer_intent_30'));
});

test('paid transition is allowed only from pending and paid only refunds', () => {
  assert.equal(canTransition('pending', 'paid'), true);
  assert.equal(canTransition('created', 'paid'), false);
  assert.equal(canTransition('paid', 'refunded'), true);
  assert.equal(canTransition('refunded', 'paid'), false);
});

test('unverified webhook content cannot authorize paid state', () => {
  assert.throws(() => validatePaidWebhook({
    event_type: 'PAYMENT.CAPTURE.COMPLETED',
    resource: { status: 'PENDING', amount: { value: '19.00', currency_code: 'USD' } },
  }, 'tool_page_7'));
  assert.throws(() => validatePaidWebhook({
    event_type: 'PAYMENT.CAPTURE.COMPLETED',
    resource: { status: 'COMPLETED', amount: { value: '1.00', currency_code: 'USD' } },
  }, 'tool_page_7'));
});
