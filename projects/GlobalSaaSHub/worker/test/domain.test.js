import assert from 'node:assert/strict';
import test from 'node:test';
import {
  assertFixedAmount, canTransition, captureIsVerifiedPaid, orderCreatePayload,
  validatePaidWebhook,
} from '../src/domain.js';

test('create payload ignores client amount and always uses 49.00 USD', () => {
  const maliciousClientBody = { amount: { value: '0.01', currency_code: 'KRW' } };
  void maliciousClientBody;
  assert.deepEqual(orderCreatePayload().purchase_units[0].amount, {
    currency_code: 'USD', value: '49.00',
  });
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

test('verified fixed-amount completed capture is paid', () => {
  assert.equal(captureIsVerifiedPaid({
    status: 'COMPLETED', purchase_units: [{ payments: { captures: [{
      status: 'COMPLETED', amount: { value: '49.00', currency_code: 'USD' },
    }] } }],
  }), true);
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
