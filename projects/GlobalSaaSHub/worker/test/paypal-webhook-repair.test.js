import assert from 'node:assert/strict';
import test from 'node:test';
import { repairPayPalWebhookEvents } from '../src/paypal.js';

const ENV = { PAYPAL_ENVIRONMENT: 'live', CHECKOUT_ENABLED: 'false', PAYPAL_CLIENT_ID: 'SYNTHETIC-CLIENT', PAYPAL_CLIENT_SECRET: 'SYNTHETIC-SECRET', PAYPAL_WEBHOOK_ID: 'SYNTHETIC-OLD-ID' };
const CALLBACK = 'https://worker.example/v1/webhooks/paypal';
const ID = 'SYNTHETIC-CANDIDATE';
const REQUIRED = ['PAYMENT.CAPTURE.COMPLETED', 'PAYMENT.CAPTURE.PENDING', 'PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED', 'CUSTOMER.DISPUTE.CREATED', 'CUSTOMER.DISPUTE.UPDATED', 'CUSTOMER.DISPUTE.RESOLVED'];
const hook = (names = ['PAYMENT.CAPTURE.COMPLETED'], changes = {}) => ({ id: ID, url: CALLBACK, event_types: names.map((name) => ({ name })), ...changes });

// Every provider request is intercepted. These fixtures contain no real account data.
function provider(options = {}) {
  const state = { calls: [], patches: [], current: options.before || hook(), token: null, tokenCount: 0, readbackFailure: options.readbackFailure || false };
  const response = (body, status = 200) => new Response(JSON.stringify(body), { status });
  const fetchImpl = async (url, init = {}) => {
    const method = init.method || 'GET';
    const parsed = new URL(url);
    assert.equal(parsed.origin, 'https://api-m.paypal.com');
    const path = parsed.pathname;
    state.calls.push({ method, path });
    if (path === '/v1/oauth2/token') {
      assert.equal(method, 'POST');
      state.token = `SYNTHETIC-TOKEN-${++state.tokenCount}`;
      return response({ access_token: state.token });
    }
    assert.equal(init.headers.Authorization, `Bearer ${state.token}`, 'one token must cover the complete repair attempt');
    if (path === '/v1/notifications/webhooks') {
      assert.equal(method, 'GET');
      assert.equal(parsed.search, '', 'stay in default APPLICATION scope');
      return response(options.list ?? { webhooks: [options.listed || state.current] });
    }
    assert.equal(path, `/v1/notifications/webhooks/${ID}`, 'no financial or other registration endpoint is permitted');
    if (method === 'PATCH') {
      const payload = JSON.parse(init.body);
      state.patches.push(payload);
      assert.deepEqual(Object.keys(payload[0]).sort(), ['op', 'path', 'value']);
      assert.equal(payload.length, 1);
      assert.equal(payload[0].op, 'replace');
      assert.equal(payload[0].path, '/event_types');
      state.current = { ...state.current, event_types: payload[0].value };
      if (options.patchFailure) throw new Error('SECRET-PATCH-TRANSPORT-DETAIL');
      return response({ raw: 'SECRET-PATCH-RESPONSE' });
    }
    assert.equal(method, 'GET');
    if (state.patches.length && state.readbackFailure) {
      state.readbackFailure = false;
      return response({ raw: 'SECRET-READBACK-DETAIL' }, 500);
    }
    return response(state.patches.length && options.readback ? options.readback(state.current) : state.current);
  };
  return { state, fetchImpl, run: (env = ENV, expectedId = ID) => repairPayPalWebhookEvents(env, CALLBACK, expectedId, fetchImpl) };
}

function assertStillUnbound(result) {
  assert.equal(result.webhookUrlVerified, false);
  assert.equal(result.requiredEventsVerified, false);
  assert.equal(result.merchantIdentityVerified, false);
  assert.equal(result.configurationOnly, true);
  assert.equal(result.repair.bindingRequired, true);
  assert.doesNotMatch(JSON.stringify(result), /SYNTHETIC-TOKEN|SYNTHETIC-CLIENT|SYNTHETIC-SECRET|SECRET-|worker\.example/);
}

test('repair preserves the union of observed subscriptions and only replaces event_types before verified readback', async () => {
  const p = provider({ listed: hook(['BILLING.SUBSCRIPTION.CREATED']), before: hook(['PAYMENT.SALE.COMPLETED', 'PAYMENT.CAPTURE.COMPLETED']) });
  const result = await p.run();
  assert.equal(result.repair.status, 'updated');
  assert.equal(result.repair.candidateId, ID);
  assert.equal(result.repair.requiredEventsVerified, true);
  assertStillUnbound(result);
  const names = p.state.patches[0][0].value.map((event) => event.name);
  assert.deepEqual(new Set(names), new Set(['BILLING.SUBSCRIPTION.CREATED', 'PAYMENT.SALE.COMPLETED', ...REQUIRED, 'PAYMENT.CAPTURE.DENIED']));
  assert.ok(!names.includes('CHECKOUT.PAYMENT-APPROVAL.REVERSED'));
  assert.equal(p.state.current.url, CALLBACK);
  assert.deepEqual(p.state.calls.map(({ method, path }) => [method, path]), [
    ['POST', '/v1/oauth2/token'], ['GET', '/v1/notifications/webhooks'], ['GET', `/v1/notifications/webhooks/${ID}`],
    ['PATCH', `/v1/notifications/webhooks/${ID}`], ['GET', `/v1/notifications/webhooks/${ID}`],
  ]);
  assert.equal(ENV.PAYPAL_WEBHOOK_ID, 'SYNTHETIC-OLD-ID');
  assert.equal(ENV.CHECKOUT_ENABLED, 'false');
});

test('wildcard and already complete subscriptions are no-ops; existing DECLINED avoids adding DENIED', async () => {
  for (const names of [['*'], [...REQUIRED, 'PAYMENT.CAPTURE.DECLINED']]) {
    const p = provider({ before: hook(names) });
    const result = await p.run();
    assert.equal(result.repair.status, 'already_complete');
    assert.equal(result.repair.candidateId, ID);
    assert.equal(p.state.patches.length, 0);
    assert.equal(p.state.calls.length, 3);
    assertStillUnbound(result);
  }
  const p = provider({ before: hook(['PAYMENT.CAPTURE.DECLINED', 'CHECKOUT.PAYMENT-APPROVAL.REVERSED']) });
  assert.equal((await p.run()).repair.status, 'updated');
  const names = p.state.patches[0][0].value.map((event) => event.name);
  assert.ok(names.includes('PAYMENT.CAPTURE.DECLINED'));
  assert.ok(names.includes('CHECKOUT.PAYMENT-APPROVAL.REVERSED'), 'an already subscribed optional event is preserved');
  assert.ok(!names.includes('PAYMENT.CAPTURE.DENIED'));
});

test('ambiguous candidates, changed IDs or URLs and malformed provider data cannot reach PATCH', async () => {
  for (const options of [
    { list: { webhooks: [] } }, { list: { webhooks: [hook(), hook()] } },
    { list: { webhooks: [hook([], { id: 'SYNTHETIC-OTHER' })] } },
    { list: { webhooks: [hook([], { url: CALLBACK + '/' })] } }, { list: { webhooks: 'SECRET-MALFORMED' } },
    { before: hook([], { id: 'SYNTHETIC-OTHER' }), listed: hook() },
    { before: hook([], { url: CALLBACK + '?changed=true' }), listed: hook() },
    { before: hook([], { event_types: [{ name: '<script>SECRET</script>' }] }), listed: hook() },
    { before: hook(), listed: hook(['*']) },
  ]) {
    const p = provider(options);
    const result = await p.run();
    assert.equal(result.repair.status, 'failed');
    assert.equal(result.repair.requiredEventsVerified, false);
    assert.equal(result.diagnostic.code, 'candidate_mismatch');
    assert.equal(p.state.patches.length, 0);
    assertStillUnbound(result);
  }
  for (const env of [{ ...ENV, CHECKOUT_ENABLED: 'true' }, { ...ENV, CHECKOUT_ENABLED: undefined }]) {
    const p = provider();
    assert.equal((await p.run(env)).repair.status, 'failed');
    assert.equal(p.state.calls.length, 0);
  }
});

test('readback must preserve ID, URL, existing events and required events; raw failures remain redacted', async () => {
  for (const options of [
    { readback: (value) => ({ ...value, id: 'SYNTHETIC-OTHER' }) },
    { readback: (value) => ({ ...value, url: CALLBACK + '/' }) },
    { readback: (value) => ({ ...value, event_types: value.event_types.filter((event) => event.name !== 'PAYMENT.CAPTURE.REFUNDED') }) },
    { before: hook(['PAYMENT.SALE.COMPLETED']), readback: (value) => ({ ...value, event_types: value.event_types.filter((event) => event.name !== 'PAYMENT.SALE.COMPLETED') }) },
    { readbackFailure: true }, { patchFailure: true },
  ]) {
    const p = provider(options);
    const result = await p.run();
    assert.equal(p.state.patches.length, 1);
    assert.equal(result.repair.status, 'failed');
    assert.equal(result.repair.requiredEventsVerified, false);
    assertStillUnbound(result);
  }
});

test('a retry after uncertain readback starts with fresh list and GET, then no-ops if the first PATCH succeeded', async () => {
  const p = provider({ readbackFailure: true });
  const first = await p.run();
  assert.equal(first.repair.status, 'failed');
  const boundary = p.state.calls.length;
  const retry = await p.run();
  assert.equal(retry.repair.status, 'already_complete');
  assert.equal(p.state.patches.length, 1);
  assert.deepEqual(p.state.calls.slice(boundary).map(({ method, path }) => [method, path]), [
    ['POST', '/v1/oauth2/token'], ['GET', '/v1/notifications/webhooks'], ['GET', `/v1/notifications/webhooks/${ID}`],
  ]);
  assertStillUnbound(retry);
});
