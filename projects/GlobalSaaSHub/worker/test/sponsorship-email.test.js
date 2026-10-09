import assert from 'node:assert/strict';
import test from 'node:test';
import { approvalEmailConfigured, approvalResumeToken, sendApprovalEmail } from '../src/sponsorship-email.js';

const application = (changes = {}) => ({
  id: '12345678-1234-1234-1234-123456789abc',
  reference: 'COSHUMA-AD-20261010-12345678-1234-1234-1234-123456789abc',
  company_name: 'Synthetic Example Company',
  tool_name: 'Synthetic Example Tool',
  contact_email: 'advertiser@example.com',
  slot: 'tool-primary',
  duration_days: 30,
  amount: '49.00',
  currency: 'USD',
  creative_mode: 'image',
  review_status: 'approved',
  publication_status: 'draft',
  payment_status: 'unpaid',
  approved_at: '2026-10-10T00:00:00.000Z',
  ...changes,
});
const env = {
  RESEND_API_KEY: 'synthetic-resend-key',
  APPROVAL_LINK_SECRET: 'synthetic-approval-link-secret',
  ALLOWED_ORIGIN: 'https://coshuma.com',
};

test('approval resume token is stable for the same approval and changes with the approval timestamp', async () => {
  assert.equal(approvalEmailConfigured(env), true);
  const first = await approvalResumeToken(application(), env);
  const again = await approvalResumeToken(application(), env);
  const later = await approvalResumeToken(application({ approved_at: '2026-10-10T00:05:00.000Z' }), env);
  assert.match(first, /^[a-f0-9]{64}$/);
  assert.equal(first, again);
  assert.notEqual(first, later);
  assert.equal(await approvalResumeToken(application({ review_status: 'pending' }), env), null);
  assert.equal(approvalEmailConfigured({ ...env, RESEND_API_KEY: '' }), false);
});

test('approval email uses the exact quote, a fragment-only return token and stable provider idempotency', async () => {
  const app = application();
  const hold = { application_id: app.id, slot: app.slot, expires_at: '2099-10-10T00:30:00.000Z' };
  const calls = [];
  const fakeFetch = async (url, options) => {
    calls.push({ url: String(url), options });
    return new Response(JSON.stringify({ id: 'synthetic-message-id' }), {
      status: 200, headers: { 'content-type': 'application/json' },
    });
  };
  const sent = await sendApprovalEmail(app, hold, env, fakeFetch);
  assert.equal(sent.providerMessageId, 'synthetic-message-id');
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, 'https://api.resend.com/emails');
  assert.equal(calls[0].options.headers['idempotency-key'], 'coshuma-approval/' + app.id + '/' + app.approved_at);
  const body = JSON.parse(calls[0].options.body);
  assert.deepEqual(body.to, ['advertiser@example.com']);
  assert.equal(body.from, 'COSHUMA Advertising <support@coshuma.com>');
  assert.match(body.subject, /COSHUMA-AD-20261010/);
  assert.match(body.text, /USD 49\.00/);
  assert.match(body.text, /30 days/);
  assert.match(body.text, /Do not send a separate PayPal payment/);
  assert.doesNotMatch(body.text, /paypal\.me/i);
  assert.match(sent.returnUrl, /^https:\/\/coshuma\.com\/advertise\.html#coshuma-ad=/);
  assert.equal(new URL(sent.returnUrl).search, '');
  assert.ok(decodeURIComponent(new URL(sent.returnUrl).hash).includes(app.id));
});

test('approval email refuses stale holds and ineligible application states before provider contact', async () => {
  let calls = 0;
  const fakeFetch = async () => { calls += 1; return new Response('{}', { status: 200 }); };
  const app = application();
  for (const [row, hold] of [
    [application({ review_status: 'pending' }), { application_id: app.id, slot: app.slot, expires_at: '2099-10-10T00:30:00.000Z' }],
    [application({ payment_status: 'verified' }), { application_id: app.id, slot: app.slot, expires_at: '2099-10-10T00:30:00.000Z' }],
    [app, { application_id: app.id, slot: app.slot, expires_at: '2000-01-01T00:00:00.000Z' }],
  ]) await assert.rejects(() => sendApprovalEmail(row, hold, env, fakeFetch));
  assert.equal(calls, 0);
});


test('priority renewal email is explicitly labeled and signed access does not require the mail provider key', async () => {
  const parentId = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
  const app = application({ renewal_of_application_id: parentId });
  const token = await approvalResumeToken(app, { ...env, RESEND_API_KEY: '' });
  assert.match(token, /^[a-f0-9]{64}$/);
  let payload;
  const sent = await sendApprovalEmail(app, {
    application_id: app.id, slot: app.slot, expires_at: '2099-10-10T00:30:00.000Z'
  }, env, async (_url, options) => {
    payload = JSON.parse(options.body);
    return new Response(JSON.stringify({ id: 'synthetic-renewal-message' }), {
      status: 200, headers: { 'content-type': 'application/json' },
    });
  });
  assert.equal(sent.providerMessageId, 'synthetic-renewal-message');
  assert.match(payload.subject, /priority renewal/i);
  assert.match(payload.text, /advertising renewal/i);
  assert.match(payload.html, /priority renewal/i);
});
