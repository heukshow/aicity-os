import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';
import { publicStatus, CATALOG } from '../../worker/src/sponsorship-domain.js';

const source = readFileSync(new URL('../../public/sponsorship-sales.js', import.meta.url), 'utf8');
const context = { module: { exports: {} }, URL };
vm.runInNewContext(source, context);
const { paymentAvailable, validDestination, validQuote, emailDraft, safeAnalyticsLink, statusText, approvalAccessFromHash } = context.module.exports;

const ready = { intakeReady: true, paymentReady: true, publicClientId: 'public-test-client' };
const unpaid = { status: 'awaiting_payment', paymentReady: true, paymentVerified: false };

test('PayPal stays closed unless both readiness checks, a public client ID and an unpaid application allow it', () => {
  assert.equal(paymentAvailable(ready, unpaid), true);
  for (const config of [null, {}, { ...ready, paymentReady: false }, { ...ready, paymentReady: 'true' },
    { ...ready, intakeReady: false }, { ...ready, publicClientId: '' }]) {
    assert.equal(paymentAvailable(config, unpaid), false);
  }
  for (const app of [null, {}, { ...unpaid, paymentReady: false }, { ...unpaid, paymentReady: 'true' },
    { ...unpaid, paymentVerified: true }, { ...unpaid, status: 'unexpected' }]) {
    assert.equal(paymentAvailable(ready, app), false);
  }
});

test('all actual backend public states agree with the browser checkout and status display', () => {
  const base = { payment_status: 'unpaid', review_status: 'pending', publication_status: 'unpublished', starts_at: null, ends_at: null };
  const cases = [
    [{ ...base }, 'awaiting_payment', false, false],
    [{ ...base, payment_status: 'review' }, 'payment_review', false, false],
    [{ ...base, payment_status: 'verified' }, 'awaiting_ad_approval', true, false],
    [{ ...base, payment_status: 'verified', review_status: 'approved' }, 'ready_to_publish', true, true],
    [{ ...base, payment_status: 'verified', review_status: 'approved', publication_status: 'published', starts_at: '2026-10-05T00:00:00.000Z', ends_at: '2026-10-12T00:00:00.000Z' }, 'scheduled', true, true],
    [{ ...base, payment_status: 'verified', review_status: 'approved', publication_status: 'published', starts_at: '2026-10-03T00:00:00.000Z', ends_at: '2026-10-10T00:00:00.000Z' }, 'active', true, true],
    [{ ...base, payment_status: 'verified', publication_status: 'ended' }, 'ended', true, true],
    [{ ...base, payment_status: 'verified', publication_status: 'paused' }, 'paused', true, true],
    [{ ...base, review_status: 'rejected' }, 'rejected', false, false],
    [{ ...base, payment_status: 'refunded' }, 'payment_reversed', false, false]
  ];
  for (const [row, expected, verified, approved] of cases) {
    const status = publicStatus(row, new Date('2026-10-04T00:00:00.000Z'));
    assert.equal(status, expected);
    const application = { status, paymentVerified: verified, approved, paymentReady: true };
    assert.equal(paymentAvailable(ready, application), expected === 'awaiting_payment', status);
    assert.notEqual(statusText(application), 'Current application status requires confirmation', status);
  }
  assert.equal(statusText({ status: 'active', paymentVerified: true, approved: true }), 'Placement active');
  assert.equal(statusText({ status: 'ended', paymentVerified: true, approved: true }), 'Placement period ended');
  assert.match(statusText({ status: 'active', paymentVerified: false, approved: true }), /could not be confirmed/);
});

test('a quote for a different page, duration or currency cannot submit the current application', () => {
  const choice = { slot: 'tool-primary', durationDays: 30, targetPage: '/tool/pipedrive.html' };
  const quote = { ...choice, amount: '49.00', currency: 'USD' };
  assert.equal(validQuote(quote, choice), true);
  for (const mismatch of [{ currency: 'EUR' }, { amount: '0.00' }, { amount: '-49.00' }, { amount: '49' },
    { durationDays: 90 }, { slot: 'buyer-intent-top' }, { targetPage: '/' }]) {
    assert.equal(validQuote({ ...quote, ...mismatch }, choice), false);
  }
});

test('public fallback price choices are synchronized with the real backend catalog', () => {
  const html = readFileSync(new URL('../../public/advertise.html', import.meta.url), 'utf8');
  const published = JSON.parse(html.match(/<script id="sponsorship-public-catalog" type="application\/json">([\s\S]*?)<\/script>/)[1]);
  assert.equal(published.currency, 'USD');
  const items = (catalog) => catalog.map(({ slot, prices, allowedPages }) => ({ slot, prices, allowedPages }));
  assert.deepEqual(items(published.catalog), items(CATALOG));
});

test('email application drafts never become payment evidence or analytics payloads', () => {
  const fields = { companyName: 'Example Co', toolName: 'Example Tool', contactEmail: 'private@example.test',
    slot: 'tool-primary', durationDays: 30, targetPage: '/tool/pipedrive.html', destinationUrl: 'https://example.test/product',
    headline: 'Example product', description: 'Example description of the product.', ctaText: 'Learn more', desiredStartDate: '' };
  const draft = emailDraft(fields);
  assert.match(draft, /Company name: Example Co/);
  assert.match(draft, /Tool or product name: Example Tool/);
  assert.match(draft, /unique order reference before requesting payment/);
  assert.match(draft, /not a reservation or proof of payment/);
  const href = 'mailto:support@coshuma.com?subject=Example&body=' + encodeURIComponent(draft);
  assert.equal(safeAnalyticsLink(href), 'mailto:support@coshuma.com');
  assert.equal(safeAnalyticsLink('https://coshuma.com/advertise.html'), 'https://coshuma.com/advertise.html');
});

test('approval email fragments restore only a bounded application id and signed token', () => {
  const id = '12345678-1234-1234-1234-123456789abc';
  const token = 'a'.repeat(64);
  assert.deepEqual(approvalAccessFromHash('#coshuma-ad=' + encodeURIComponent(id + '.' + token)), {
    applicationId: id, accessToken: token,
  });
  for (const value of [
    '', '#coshuma-ad=', '#coshuma-ad=' + id, '#coshuma-ad=' + id + '.short',
    '#coshuma-ad=' + id + '.' + 'z'.repeat(64), '#other=' + id + '.' + token,
    '#coshuma-ad=' + encodeURIComponent('../' + id + '.' + token),
  ]) assert.equal(approvalAccessFromHash(value), null, value);
});

test('destination checks reject credentials, plain HTTP and local network addresses', () => {
  assert.equal(validDestination('https://example.com/product?campaign=ads'), true);
  for (const value of ['http://example.com', 'javascript:alert(1)', 'https://user:pass@example.com',
    'https://localhost', 'https://127.0.0.1', 'https://10.0.0.2', 'https://192.168.0.2',
    'https://172.16.0.2', 'https://169.254.0.1', 'https://host.local', 'https://[::1]/']) {
    assert.equal(validDestination(value), false, value);
  }
});
