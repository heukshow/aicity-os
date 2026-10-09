import assert from 'node:assert/strict';
import test from 'node:test';
import { approvalEmail, issueResumeToken, sendApprovalEmail, verifyResumeToken } from '../src/sponsorship-email.js';

const APPLICATION = {
  id: '11111111-2222-4333-8444-555555555555',
  reference: 'COSHUMA-AD-20261009-11111111-2222-4333-8444-555555555555',
  company_name: 'Example Company',
  tool_name: 'Example Tool',
  contact_email: 'advertiser@example.com',
  slot: 'tool-primary',
  duration_days: 30,
  amount: '49.00',
  currency: 'USD',
};
const ENV = {
  AD_RESUME_LINK_SECRET: 'synthetic-resume-secret-0123456789-abcdefghijklmnopqrstuvwxyz',
  RESEND_API_KEY: 'synthetic-resend-api-key-for-offline-tests',
  AD_EMAIL_FROM: 'COSHUMA Ads <support@coshuma.com>',
};
const NOW = Date.parse('2026-10-09T12:00:00.000Z');

test('resume tokens are signed, scoped to one application and expire', async () => {
  const token = await issueResumeToken(APPLICATION, ENV, NOW, 3600000);
  assert.match(token, /^r1\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/);
  const verified = await verifyResumeToken(token, ENV, NOW + 1000);
  assert.equal(verified.applicationId, APPLICATION.id);
  await assert.rejects(() => verifyResumeToken(token + 'x', ENV, NOW + 1000), /Invalid application return link/);
  await assert.rejects(() => verifyResumeToken(token, ENV, NOW + 3600001), /expired/);
  await assert.rejects(() => verifyResumeToken(token, { ...ENV, AD_RESUME_LINK_SECRET: 'different-secret-0123456789-abcdefghijklmnopqrstuvwxyz' }, NOW + 1000), /Invalid/);
});

test('approval email contains exact order terms and only the signed COSHUMA return URL', async () => {
  const token = await issueResumeToken(APPLICATION, ENV, NOW);
  const url = 'https://coshuma.com/advertise.html#resume=' + encodeURIComponent(token);
  const email = approvalEmail(APPLICATION, url, '2026-10-10T12:00:00.000Z');
  assert.match(email.subject, /COSHUMA ad approved/);
  assert.match(email.text, /USD 49\.00/);
  assert.match(email.text, /30 days/);
  assert.match(email.text, /Do not send a separate PayPal transfer/);
  assert.ok(email.html.includes('Complete payment'));
  assert.ok(email.html.includes(url));
  assert.equal(email.html.includes(ENV.RESEND_API_KEY), false);
  assert.throws(() => approvalEmail(APPLICATION, 'https://attacker.example/#resume=x', '2026-10-10T12:00:00.000Z'), /cannot be prepared/);
});

test('Resend request is idempotent and never exposes the API key in the payload', async () => {
  const token = await issueResumeToken(APPLICATION, ENV, NOW);
  const url = 'https://coshuma.com/advertise.html#resume=' + encodeURIComponent(token);
  const calls = [];
  const fetcher = async (endpoint, options) => {
    calls.push({ endpoint, options });
    return new Response(JSON.stringify({ id: 'email-synthetic-1' }), { status: 200, headers: { 'content-type': 'application/json' } });
  };
  const result = await sendApprovalEmail(ENV, APPLICATION, url, '2026-10-10T12:00:00.000Z', fetcher);
  assert.equal(result.messageId, 'email-synthetic-1');
  assert.equal(calls.length, 1);
  assert.equal(calls[0].endpoint, 'https://api.resend.com/emails');
  assert.equal(calls[0].options.headers['idempotency-key'], 'coshuma-ad-approval/' + APPLICATION.id);
  assert.equal(calls[0].options.headers.authorization, 'Bearer ' + ENV.RESEND_API_KEY);
  const payload = JSON.parse(calls[0].options.body);
  assert.equal(payload.from, ENV.AD_EMAIL_FROM);
  assert.deepEqual(payload.to, [APPLICATION.contact_email]);
  assert.equal(JSON.stringify(payload).includes(ENV.RESEND_API_KEY), false);
});
