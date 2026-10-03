import assert from 'node:assert/strict';
import test from 'node:test';
import {
  CATALOG, captureIdFromRefundLink, paypalPayload, publicationPeriod, publicStatus, quoteFor,
  validateApplication, verifyPayPalPayment,
} from '../src/sponsorship-domain.js';

const MERCHANT = 'MERCHANT-EXPECTED';

function paymentFixture() {
  const application = {
    id: 'application-001', reference: 'COSHUMA-APPLICATION-001',
    company_name: 'Example Company', tool_name: 'Example Tool',
    slot: 'tool-primary', duration_days: 30, target_page: '/tool/pipedrive.html',
    amount: '49.00', currency: 'USD',
  };
  const capture = {
    id: 'CAPTURE-001', status: 'COMPLETED',
    amount: { value: '49.00', currency_code: 'USD' },
    payee: { merchant_id: MERCHANT },
    supplementary_data: { related_ids: { order_id: 'ORDER-001' } },
  };
  const order = {
    id: 'ORDER-001', status: 'COMPLETED',
    purchase_units: [{
      custom_id: application.id, invoice_id: application.reference,
      payee: { merchant_id: MERCHANT },
      amount: { value: '49.00', currency_code: 'USD' },
      payments: { captures: [structuredClone(capture)] },
    }],
  };
  return {
    application, order, capture,
    payment: { provider_order_id: 'ORDER-001', merchant_id: MERCHANT, environment: 'live' },
    merchantId: MERCHANT, environment: 'live',
  };
}

function applicationInput() {
  return {
    slot: 'tool-primary', durationDays: 30, targetPage: '/tool/pipedrive.html',
    companyName: ' Example Company ', toolName: 'Example Tool',
    contactEmail: 'advertiser@example.com', destinationUrl: 'https://example.com/product',
    headline: 'Example tool for sales teams',
    description: 'A factual description supplied by an authorised advertiser.',
    ctaText: 'View product', desiredStartDate: '2027-01-01', sellerAttestation: true,
  };
}

test('catalog quotes only the three approved page/slot pairs and fixed durations', () => {
  const expected = [
    ['tool-primary', '/tool/pipedrive.html', ['19.00', '49.00', '129.00']],
    ['buyer-intent-top', '/best/claap-sales-follow-up-ai.html', ['39.00', '99.00', '269.00']],
    ['compare-decision-premium', '/compare/semrush-vs-frase.html', ['59.00', '149.00', '399.00']],
  ];
  assert.equal(CATALOG.length, expected.length);
  for (const [slot, targetPage, prices] of expected) {
    assert.deepEqual(CATALOG.find((entry) => entry.slot === slot)?.allowedPages, [targetPage]);
    for (const [index, durationDays] of [7, 30, 90].entries()) {
      assert.deepEqual(quoteFor({ slot, durationDays, targetPage }), {
        slot, durationDays, targetPage, amount: prices[index], currency: 'USD',
      });
    }
  }
});

test('home, reserved pages, wildcards and unlisted page variants cannot be purchased', () => {
  const deniedPages = [
    '/', '/index.html', '/*', '*', '/tool/*', '/tool/gamma.html', '/tool/chatbase.html',
    '/best/gamma.html', '/best/chatbase.html', '/tool/claap.html', '/tool/not-listed.html',
    '/compare/frase-vs-semrush.html', '/tool/Pipedrive.html', '/tool/pipedrive.html/',
    '/tool/pipedrive.html?campaign=paid', '/tool/pipedrive.html#sponsored',
    '/tool/../tool/pipedrive.html', '/tool/%70ipedrive.html', '//coshuma.com/tool/pipedrive.html',
    'https://coshuma.com/tool/pipedrive.html', '', null,
  ];
  for (const entry of CATALOG) {
    for (const targetPage of deniedPages) {
      assert.throws(() => quoteFor({ slot: entry.slot, durationDays: 30, targetPage }), `${entry.slot}: ${targetPage}`);
    }
    for (const other of CATALOG.filter((candidate) => candidate.slot !== entry.slot)) {
      assert.throws(() => quoteFor({ slot: entry.slot, durationDays: 30, targetPage: other.allowedPages[0] }));
    }
  }
  for (const durationDays of [0, -7, 1, 29, 31, 180, 7.5, null, 'custom']) {
    assert.throws(() => quoteFor({ slot: 'tool-primary', targetPage: '/tool/pipedrive.html', durationDays }));
  }
  assert.throws(() => quoteFor({ slot: 'homepage', targetPage: '/', durationDays: 30 }));
});

test('application validates advertiser material and rejects client-owned prices', () => {
  const input = applicationInput();
  const validated = validateApplication(input);
  assert.equal(validated.companyName, 'Example Company');
  assert.equal(validated.toolName, input.toolName);
  assert.equal(validated.amount, '49.00');
  assert.equal(validated.currency, 'USD');
  assert.equal(validated.targetPage, '/tool/pipedrive.html');
  for (const field of ['amount', 'price', 'currency']) {
    assert.throws(() => validateApplication({ ...input, [field]: '0.01' }));
  }
  for (const changes of [
    { companyName: '' }, { toolName: '<script>alert(1)</script>' },
    { headline: 'Short\nheadline' }, { description: 'Too short' }, { ctaText: 'X' },
    { contactEmail: 'invalid-email' }, { sellerAttestation: false },
    { sellerAttestation: 'true' }, { desiredStartDate: '2027-02-30' },
    { desiredStartDate: 'not-a-date' },
  ]) {
    assert.throws(() => validateApplication({ ...input, ...changes }));
  }
  for (const destinationUrl of [
    'http://example.com', 'javascript:alert(1)', 'data:text/html,hello',
    'https://user:pass@example.com', 'https://localhost', 'https://intranet.local',
    'https://127.0.0.1', 'https://[::1]', 'https://internal',
  ]) {
    assert.throws(() => validateApplication({ ...input, destinationUrl }));
  }
});

test('PayPal order binds the server quote, application reference and recipient', () => {
  const { application } = paymentFixture();
  const payload = paypalPayload(application, MERCHANT);
  assert.equal(payload.intent, 'CAPTURE');
  assert.equal(payload.purchase_units.length, 1);
  const unit = payload.purchase_units[0];
  assert.deepEqual(unit.amount, { value: '49.00', currency_code: 'USD' });
  assert.equal(unit.custom_id, application.id);
  assert.equal(unit.invoice_id, application.reference);
  assert.equal(unit.payee.merchant_id, MERCHANT);
  assert.ok(unit.description.includes(application.company_name));
  assert.ok(unit.description.includes(application.tool_name));
  assert.throws(() => paypalPayload(application, ''));
});

test('complete matching live payment returns auditable provider evidence', () => {
  assert.deepEqual(verifyPayPalPayment(paymentFixture()), {
    captureId: 'CAPTURE-001', providerOrderId: 'ORDER-001', merchantId: MERCHANT,
    amount: '49.00', currency: 'USD', environment: 'live',
  });
});

test('payment verification rejects missing or mismatched order and application evidence', async (t) => {
  const invalidCases = [
    ['missing provider order', (f) => { delete f.order; }],
    ['uncompleted order', (f) => { f.order.status = 'APPROVED'; }],
    ['different provider order', (f) => { f.order.id = 'ORDER-OTHER'; }],
    ['missing stored provider order', (f) => { delete f.payment.provider_order_id; }],
    ['missing application binding', (f) => { delete f.order.purchase_units[0].custom_id; }],
    ['another application', (f) => { f.order.purchase_units[0].custom_id = 'application-other'; }],
    ['missing invoice reference', (f) => { delete f.order.purchase_units[0].invoice_id; }],
    ['another invoice reference', (f) => { f.order.purchase_units[0].invoice_id = 'COSHUMA-OTHER'; }],
    ['missing capture order binding', (f) => { delete f.capture.supplementary_data; }],
    ['capture for another order', (f) => { f.capture.supplementary_data.related_ids.order_id = 'ORDER-OTHER'; }],
    ['capture ID differs from the order', (f) => { f.capture.id = 'CAPTURE-OTHER'; }],
    ['missing capture ID', (f) => { delete f.capture.id; }],
    ['pending capture', (f) => { f.capture.status = 'PENDING'; }],
    ['pending capture inside order', (f) => { f.order.purchase_units[0].payments.captures[0].status = 'PENDING'; }],
    ['conflicting capture invoice', (f) => { f.capture.invoice_id = 'COSHUMA-OTHER'; }],
    ['conflicting capture application', (f) => { f.capture.custom_id = 'application-other'; }],
  ];
  for (const [name, change] of invalidCases) {
    await t.test(name, () => {
      const fixture = paymentFixture();
      change(fixture);
      assert.throws(() => verifyPayPalPayment(fixture));
    });
  }
});

test('every recipient and environment must match the configured live merchant', async (t) => {
  const invalidCases = [
    ['missing configured merchant', (f) => { f.merchantId = ''; }],
    ['missing recorded merchant', (f) => { delete f.payment.merchant_id; }],
    ['wrong recorded merchant', (f) => { f.payment.merchant_id = 'MERCHANT-OTHER'; }],
    ['missing order recipient', (f) => { delete f.order.purchase_units[0].payee; }],
    ['wrong order recipient', (f) => { f.order.purchase_units[0].payee.merchant_id = 'MERCHANT-OTHER'; }],
    ['missing capture recipient', (f) => { delete f.capture.payee; }],
    ['wrong capture recipient', (f) => { f.capture.payee.merchant_id = 'MERCHANT-OTHER'; }],
    ['sandbox runtime', (f) => { f.environment = 'sandbox'; }],
    ['missing runtime environment', (f) => { delete f.environment; }],
    ['sandbox recorded payment', (f) => { f.payment.environment = 'sandbox'; }],
    ['missing recorded environment', (f) => { delete f.payment.environment; }],
  ];
  for (const [name, change] of invalidCases) {
    await t.test(name, () => {
      const fixture = paymentFixture();
      change(fixture);
      assert.throws(() => verifyPayPalPayment(fixture));
    });
  }
});

test('the full order and capture totals must equal the stored amount and currency', async (t) => {
  const invalidCases = [
    ['missing order total', (f) => { delete f.order.purchase_units[0].amount; }],
    ['order underpayment', (f) => { f.order.purchase_units[0].amount.value = '0.01'; }],
    ['order overpayment', (f) => { f.order.purchase_units[0].amount.value = '98.00'; }],
    ['order currency mismatch', (f) => { f.order.purchase_units[0].amount.currency_code = 'EUR'; }],
    ['missing capture amount', (f) => { delete f.capture.amount; }],
    ['capture underpayment', (f) => { f.capture.amount.value = '0.01'; }],
    ['capture overpayment', (f) => { f.capture.amount.value = '98.00'; }],
    ['capture currency mismatch', (f) => { f.capture.amount.currency_code = 'EUR'; }],
    ['embedded capture amount mismatch', (f) => { f.order.purchase_units[0].payments.captures[0].amount.value = '0.01'; }],
    ['embedded capture currency mismatch', (f) => { f.order.purchase_units[0].payments.captures[0].amount.currency_code = 'EUR'; }],
    ['stored application price differs from catalog', (f) => {
      f.application.amount = '0.01';
      f.order.purchase_units[0].amount.value = '0.01';
      f.order.purchase_units[0].payments.captures[0].amount.value = '0.01';
      f.capture.amount.value = '0.01';
    }],
    ['missing purchase units', (f) => { f.order.purchase_units = []; }],
    ['additional purchase unit', (f) => { f.order.purchase_units.push(structuredClone(f.order.purchase_units[0])); }],
    ['missing order capture', (f) => { f.order.purchase_units[0].payments.captures = []; }],
    ['duplicate order capture', (f) => { f.order.purchase_units[0].payments.captures.push(structuredClone(f.capture)); }],
    ['split captures with matching total', (f) => {
      const first = structuredClone(f.capture);
      const second = structuredClone(f.capture);
      first.amount.value = '24.50';
      second.amount.value = '24.50';
      second.id = 'CAPTURE-002';
      f.order.purchase_units[0].payments.captures = [first, second];
    }],
  ];
  for (const [name, change] of invalidCases) {
    await t.test(name, () => {
      const fixture = paymentFixture();
      change(fixture);
      assert.throws(() => verifyPayPalPayment(fixture));
    });
  }
});

test('publication duration starts on activation and public status stops at expiry', () => {
  const now = new Date('2027-01-01T12:00:00.000Z');
  const period = publicationPeriod({ duration_days: 7 }, null, now);
  assert.deepEqual(period, { startsAt: '2027-01-01T12:00:00.000Z', endsAt: '2027-01-08T12:00:00.000Z' });
  assert.throws(() => publicationPeriod({ duration_days: 7 }, '2026-12-31T12:00:00.000Z', now));
  assert.throws(() => publicationPeriod({ duration_days: 7 }, 'invalid', now));
  const application = {
    payment_status: 'verified', review_status: 'approved', publication_status: 'published',
    starts_at: period.startsAt, ends_at: period.endsAt,
  };
  assert.equal(publicStatus(application, now), 'active');
  assert.equal(publicStatus(application, new Date(period.endsAt)), 'ended');
  assert.equal(publicStatus(application, new Date('2027-01-01T11:00:00.000Z')), 'scheduled');
  assert.equal(publicStatus({ ...application, payment_status: 'refunded' }, now), 'payment_reversed');
  assert.equal(publicStatus({ ...application, publication_status: 'paused' }, now), 'paused');
  assert.equal(publicStatus({ ...application, publication_status: 'draft', review_status: 'pending' }, now), 'awaiting_ad_approval');
});

test('refund capture hints accept only known live PayPal links and never fetch the supplied URL', (t) => {
  const network = t.mock.method(globalThis, 'fetch', () => assert.fail('A provider link must not be fetched'));
  const eventWith = (href, rel = 'up') => ({ resource: { links: [{ href, rel }] } });
  for (const host of ['api.paypal.com', 'api-m.paypal.com']) {
    assert.equal(captureIdFromRefundLink(eventWith(`https://${host}/v2/payments/captures/CAPTURE-123`)), 'CAPTURE-123');
  }
  for (const href of [
    'https://attacker.example/v2/payments/captures/CAPTURE-123',
    'https://api.paypal.com.attacker.example/v2/payments/captures/CAPTURE-123',
    'https://api-m.sandbox.paypal.com/v2/payments/captures/CAPTURE-123',
    'http://api.paypal.com/v2/payments/captures/CAPTURE-123',
    '//api.paypal.com/v2/payments/captures/CAPTURE-123',
    'https://user:password@api.paypal.com/v2/payments/captures/CAPTURE-123',
    'https://api.paypal.com:8443/v2/payments/captures/CAPTURE-123',
    'https://api.paypal.com/v2/payments/captures/CAPTURE-123?redirect=attacker',
    'https://api.paypal.com/v2/payments/captures/CAPTURE-123#fragment',
    'https://api.paypal.com/v2/payments/refunds/CAPTURE-123',
    'https://api.paypal.com/v2/payments/captures/CAPTURE-123/',
    'https://api.paypal.com/v2/payments/captures/CAPTURE-123/extra',
    'https://api.paypal.com/v2/payments/%63aptures/CAPTURE-123',
    'https://api.paypal.com/v2/payments/captures/CAPTURE%2F123',
    'https://api.paypal.com/v2/payments/captures/' + 'A'.repeat(129),
    'not a URL',
  ]) assert.equal(captureIdFromRefundLink(eventWith(href)), null, href);
  assert.equal(captureIdFromRefundLink(eventWith('https://api.paypal.com/v2/payments/captures/CAPTURE-123', 'self')), null);
  assert.equal(captureIdFromRefundLink({ resource: { links: {} } }), null);
  assert.equal(captureIdFromRefundLink({}), null);
  assert.equal(network.mock.callCount(), 0);
});
