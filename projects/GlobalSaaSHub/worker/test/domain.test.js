import assert from 'node:assert/strict';
import test from 'node:test';
import {
  assertFixedAmount, assertProductAmount, canTransition, captureIsVerifiedPaid, getProduct,
  orderCreatePayload, SPONSORSHIP_PRODUCTS, validatePaidWebhook,
} from '../src/domain.js';

test('default create payload remains server-owned 49.00 USD', () => {
  const maliciousClientBody = { amount: { value: '0.01', currency_code: 'KRW' } };
  void maliciousClientBody;
  assert.deepEqual(orderCreatePayload().purchase_units[0].amount, {
    currency_code: 'USD', value: '49.00',
  });
});

test('all nine sponsorship products use server-owned price and duration', () => {
  assert.equal(Object.keys(SPONSORSHIP_PRODUCTS).length, 9);
  assert.deepEqual(getProduct('comparison_90'), {
    id: 'comparison_90', placement: 'comparison', durationDays: 90, amount: '399.00', label: 'Comparison Premium — 90 days',
  });
  assert.deepEqual(orderCreatePayload('buyer_intent_30').purchase_units[0].amount, {
    currency_code: 'USD', value: '99.00',
  });
  assert.throws(() => getProduct('client_invented_001'));
  assert.throws(() => assertProductAmount({ value: '19.00', currency_code: 'USD' }, 'tool_page_30'));
  assert.doesNotThrow(() => assertProductAmount({ value: '19.00', currency_code: 'USD' }, 'tool_page_7'));
});

test('provider amount validation fails closed', () => {
  assert.doesNotThrow(() => assertFixedAmount({ value: '49.00', currency_code: 'USD' }));
  assert.throws(() => assertFixedAmount({ value: '49.01', currency_code: 'USD' }));
  assert.throws(() => assertFixedAmount({ value: '49.00', currency_code: 'KRW' }));
});

test('unverified or incomplete capture cannot become paid', () => {
  assert.equal(captureIsVerifiedPaid({ status: 'APPROVED' }), false);
  assert.equal(captureIsVerifiedPaid({ status: 'COMPLETED', purchase_units: [] }), false);
  assert.equal(captureIsVerifiedPaid({
    status: 'COMPLETED', purchase_units: [{ payments: { captures: [{
      status: 'PENDING', amount: { value: '49.00', currency_code: 'USD' },
    }] } }],
  }), false);
});

test('verified completed capture must match selected product', () => {
  const order = {
    status: 'COMPLETED', purchase_units: [{ payments: { captures: [{
      status: 'COMPLETED', amount: { value: '129.00', currency_code: 'USD' },
    }] } }],
  };
  assert.equal(captureIsVerifiedPaid(order, 'tool_page_90'), true);
  assert.throws(() => captureIsVerifiedPaid(order, 'tool_page_30'));
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
    resource: { status: 'PENDING', amount: { value: '49.00', currency_code: 'USD' } },
  }));
  assert.throws(() => validatePaidWebhook({
    event_type: 'PAYMENT.CAPTURE.COMPLETED',
    resource: { status: 'COMPLETED', amount: { value: '1.00', currency_code: 'USD' } },
  }));
});
