// Control-side read-only readiness check. No fetch, deployment, secret write or payment operation.
// Only the exact configuration-pending response is eligible for a bounded retry.
const PENDING = 'Isolated test configuration is required.';
const EVENT = 'PAYMENT.CAPTURE.COMPLETED';
const ID = /^[A-Za-z0-9_-]{1,128}$/;
export class SandboxReadinessError extends Error {
  constructor(code) { super(code); this.name = 'SandboxReadinessError'; this.code = code; }
}
const fail = code => { throw new SandboxReadinessError(code); };
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

export async function waitForPublicSandboxReadiness({
  requestPreflight, expectedWebhookId, secretWriteCompleted = false,
  maxAttempts = 5, sleep = pause, onAttempt = () => {},
} = {}) {
  if (secretWriteCompleted !== true || typeof requestPreflight !== 'function' ||
      typeof expectedWebhookId !== 'string' || !ID.test(expectedWebhookId) ||
      !Number.isInteger(maxAttempts) || maxAttempts < 1 || maxAttempts > 5 ||
      typeof sleep !== 'function' || typeof onAttempt !== 'function') fail('READINESS_INPUT_INVALID');
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    let response;
    try { response = await requestPreflight(); }
    catch { fail('READINESS_TRANSPORT_FAILED'); }
    const status = response?.status, body = response?.body;
    if (status === 200) {
      if (body?.verified !== true || body.applicationCount !== 1 || body.accountCount !== 0 ||
          body.webhookId !== expectedWebhookId || !Array.isArray(body.eventTypes) ||
          body.eventTypes.length !== 1 || body.eventTypes[0] !== EVENT ||
          typeof body.checkedAt !== 'string' || !Number.isFinite(Date.parse(body.checkedAt))) {
        fail('READINESS_RESPONSE_INVALID');
      }
      onAttempt({ attempt, status: 200, outcome: 'verified' });
      return { verified: true, applicationCount: 1, accountCount: 0,
        webhookId: body.webhookId, eventTypes: [EVENT], checkedAt: body.checkedAt, attempts: attempt };
    }
    // Never turn an authentication denial, unknown response or provider-policy failure into a retry.
    if (status === 401 || status === 403) fail('READINESS_ACCESS_DENIED');
    if (status !== 503 || !body || body.error !== PENDING) fail('READINESS_REJECTED');
    onAttempt({ attempt, status: 503, outcome: 'configuration_pending' });
    if (attempt === maxAttempts) fail('READINESS_CONFIGURATION_PENDING');
    try { await sleep(1000 * (2 ** (attempt - 1))); }
    catch { fail('READINESS_WAIT_CANCELLED'); }
  }
  fail('READINESS_CONFIGURATION_PENDING');
}
