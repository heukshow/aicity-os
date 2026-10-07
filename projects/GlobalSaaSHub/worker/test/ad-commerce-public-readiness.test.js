// Offline control-flow tests; no public origin access, deployment or payment credentials.
import test from 'node:test';
import assert from 'node:assert/strict';
import { waitForPublicSandboxReadiness } from '../src/ad-commerce-public-readiness.js';
const hook = 'SYNTHETIC-WEBHOOK';
const good = () => ({ status: 200, body: { verified: true, applicationCount: 1, accountCount: 0,
  webhookId: hook, eventTypes: ['PAYMENT.CAPTURE.COMPLETED'], checkedAt: new Date().toISOString() } });
const pending = () => ({ status: 503, body: { error: 'Isolated test configuration is required.' } });
function fixture(responses) {
  let calls = 0; const waits = [], observations = [];
  return { get calls() { return calls; }, waits, observations,
    options: { expectedWebhookId: hook, secretWriteCompleted: true,
      requestPreflight: async () => { const response = responses[Math.min(calls++, responses.length - 1)];
        if (response instanceof Error) throw response; return response; },
      sleep: async ms => { waits.push(ms); }, onAttempt: value => { observations.push(value); } } };
}
test('verified expected registration finishes without waiting', async () => {
  const f = fixture([good()]), result = await waitForPublicSandboxReadiness(f.options);
  assert.equal(result.verified, true); assert.equal(result.attempts, 1); assert.equal(f.calls, 1); assert.deepEqual(f.waits, []);
});
test('exact post-deployment configuration pending response retries reads only', async () => {
  const f = fixture([pending(), pending(), good()]);
  const result = await waitForPublicSandboxReadiness(f.options);
  assert.equal(result.attempts, 3); assert.deepEqual(f.waits, [1000, 2000]); assert.equal(f.calls, 3);
  assert.deepEqual(f.observations.map(x => x.outcome), ['configuration_pending', 'configuration_pending', 'verified']);
});
test('persistent missing configuration remains not-ready after a strict bounded wait', async () => {
  const f = fixture([pending()]);
  await assert.rejects(waitForPublicSandboxReadiness(f.options), /READINESS_CONFIGURATION_PENDING/);
  assert.equal(f.calls, 5); assert.deepEqual(f.waits, [1000, 2000, 4000, 8000]);
});
test('an explicit later check reuses supplied configuration and does not need a new secret write', async () => {
  const first = fixture([pending()]);
  await assert.rejects(waitForPublicSandboxReadiness({ ...first.options, maxAttempts: 1 }), /CONFIGURATION_PENDING/);
  const second = fixture([good()]);
  assert.equal((await waitForPublicSandboxReadiness(second.options)).verified, true); assert.equal(second.calls, 1);
});
for (const status of [401, 403]) test(`HTTP ${status} is never retried`, async () => {
  const f = fixture([{ status, body: { error: 'denied' } }, good()]);
  await assert.rejects(waitForPublicSandboxReadiness(f.options), /READINESS_ACCESS_DENIED/);
  assert.equal(f.calls, 1); assert.deepEqual(f.waits, []);
});
test('provider registration errors are not mistaken for propagation delay', async () => {
  const f = fixture([{ status: 503, body: { error: 'PayPal Sandbox webhook preflight failed (REGISTRATION).' } }, good()]);
  await assert.rejects(waitForPublicSandboxReadiness(f.options), /READINESS_REJECTED/);
  assert.equal(f.calls, 1); assert.deepEqual(f.waits, []);
});
test('generic failures and altered configuration messages are not retried', async () => {
  for (const response of [{ status: 500, body: {} }, { status: 503, body: {} },
    { status: 503, body: { error: 'Isolated test configuration is required. extra' } }, { status: 429, body: {} }]) {
    const f = fixture([response]); await assert.rejects(waitForPublicSandboxReadiness(f.options), /READINESS_REJECTED/);
    assert.equal(f.calls, 1); assert.deepEqual(f.waits, []);
  }
});
test('HTTP 200 alone cannot establish readiness', async () => {
  for (const patch of [{ verified: false }, { verified: 'true' }, { applicationCount: 2 }, { accountCount: 1 },
    { webhookId: 'OTHER' }, { eventTypes: [] }, { eventTypes: ['*'] }, { checkedAt: 'invalid' }]) {
    const response = good(); Object.assign(response.body, patch); const f = fixture([response]);
    await assert.rejects(waitForPublicSandboxReadiness(f.options), /READINESS_RESPONSE_INVALID/); assert.equal(f.calls, 1);
  }
});
test('transport rejection stops without retry or raw error disclosure', async () => {
  const f = fixture([new Error('SECRET_OR_BROWSER_ERROR')]);
  await assert.rejects(waitForPublicSandboxReadiness(f.options), error => error.message === 'READINESS_TRANSPORT_FAILED');
  assert.equal(f.calls, 1); assert.deepEqual(f.waits, []);
});
test('only completed secret-write workflow may request the check', async () => {
  for (const secretWriteCompleted of [false, undefined, null, 'true', 1]) {
    const f = fixture([good()]); await assert.rejects(waitForPublicSandboxReadiness({ ...f.options, secretWriteCompleted }), /READINESS_INPUT_INVALID/);
    assert.equal(f.calls, 0);
  }
});
test('attempt bounds and callback contracts are validated before requests', async () => {
  for (const patch of [{ maxAttempts: 0 }, { maxAttempts: 6 }, { maxAttempts: 1.5 }, { expectedWebhookId: '../bad' },
    { requestPreflight: null }, { sleep: null }, { onAttempt: null }]) {
    const f = fixture([good()]); await assert.rejects(waitForPublicSandboxReadiness({ ...f.options, ...patch }), /READINESS_INPUT_INVALID/);
    assert.equal(f.calls, 0);
  }
});
test('cancelled wait stops without a subsequent request', async () => {
  const f = fixture([pending(), good()]);
  await assert.rejects(waitForPublicSandboxReadiness({ ...f.options, sleep: async () => { throw new Error('cancel'); } }), /READINESS_WAIT_CANCELLED/);
  assert.equal(f.calls, 1);
});
test('returned result and observations exclude unrequested provider data', async () => {
  const response = good(); response.body.privateData = 'DO_NOT_EXPOSE'; const f = fixture([response]);
  const result = await waitForPublicSandboxReadiness(f.options);
  assert.equal(JSON.stringify({ result, observations: f.observations }).includes('DO_NOT_EXPOSE'), false);
});
