import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { renderSponsorshipOps } from '../src/sponsorship-ops-view.js';

const application = (changes = {}) => ({
  applicationId: 'ad-123', reference: 'COSHUMA-ADS-20261004-123', companyName: 'Example Company', toolName: 'Example Tool',
  contactEmail: 'private-contact@example.com', quote: { amount: '99.00', currency: 'USD', durationDays: 7, slot: 'tool-primary', targetPage: '/tool/pipedrive.html' },
  status: 'ready_to_publish', paymentStatus: 'verified', reviewStatus: 'approved', publicationStatus: 'draft',
  paymentVerified: true, approved: true, paymentVerifiedAt: '2026-10-03T22:13:00Z', lastCheckedAt: '2026-10-03T22:14:00Z',
  destinationUrl: 'https://example.com/product', headline: 'Useful product', description: 'A factual description of the product.', ctaText: 'Learn more',
  ...changes,
});
const config = { intakeReady: true, paymentReady: true, configurationOnly: true, checks: { storageReady: true, checkoutEnabled: true, liveEnvironment: true, clientIdConfigured: true, clientSecretConfigured: true, webhookIdConfigured: true, merchantIdConfigured: true } };
const render = (row = application(), settings = config) => renderSponsorshipOps({ applications: [row], config: settings });
const buttonTag = (html, action) => html.match(new RegExp(`<button\\b[^>]*data-action="${action}"[^>]*>`))[0];

function element(properties = {}) {
  const listeners = new Map();
  return {
    textContent: '', disabled: false, checked: false, value: '', dataset: {}, attributes: {}, classes: new Set(),
    addEventListener(name, listener) { listeners.set(name, listener); },
    dispatch(name) { return listeners.get(name)?.(); },
    setAttribute(name, value) { this.attributes[name] = value; },
    classList: { toggle() {} },
    focus() { this.focused = true; },
    ...properties,
  };
}

function browser(html, response = async () => ({ ok: true, status: 200, json: async () => ({ status: 'ready_to_publish' }) })) {
  const nodes = new Map();
  for (const id of ['ops-result', 'connection-result', 'verify-readiness', 'refresh-ops']) nodes.set(id, element());
  nodes.set('sponsorship-ops', element({ dataset: { basePath: html.match(/data-base-path="([^"]+)"/)[1] } }));
  const allButtons = [nodes.get('verify-readiness')];
  const cards = [...html.matchAll(/<article class="application"[\s\S]+?<\/article>/g)].map(([block]) => {
    const controls = new Map();
    const dataset = {};
    for (const match of block.matchAll(/data-([a-z-]+)="([^"]*)"/g)) dataset[match[1].replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = match[2];
    for (const action of ['verify-payment', 'approve', 'reject', 'publish', 'pause']) {
      const node = element({ disabled: /\sdisabled(?:\s|>)/.test(buttonTag(block, action)) });
      controls.set(`[data-action="${action}"]`, node); allButtons.push(node);
    }
    for (const name of ['destination-checked', 'claims-checked', 'notes', 'starts-at']) controls.set(`[data-field="${name}"]`, element());
    controls.set('[data-result]', element());
    return element({ dataset, querySelector: (selector) => controls.get(selector) });
  });
  const requests = [];
  const state = { nodes, cards, requests, reloads: 0 };
  const context = {
    document: { getElementById: (id) => nodes.get(id), querySelectorAll: (selector) => selector === '[data-application]' ? cards : selector === 'button[data-action]' ? allButtons : [] },
    window: { location: { origin: 'https://worker.example', reload() { state.reloads++; } } },
    fetch: async (path, options) => { requests.push({ path, options }); return response(path, options); },
    URL, Date,
  };
  vm.runInNewContext(html.match(/<script>([\s\S]+)<\/script>/)[1], context);
  return state;
}
const control = (card, name) => card.querySelector(`[data-field="${name}"]`);
const action = (card, name) => card.querySelector(`[data-action="${name}"]`);

test('owner view renders only projected fields, escapes advertiser input and rejects unsafe links', () => {
  const attack = '</script><script>globalThis.stolen=1</script><img src=x onerror=alert(1)>';
  const html = render(application({
    companyName: attack, headline: attack, description: attack, reviewNotes: attack,
    destinationUrl: 'javascript:alert(1)', quote: { ...application().quote, targetPage: '//evil.example/path' },
    accessToken: 'DO-NOT-RENDER-TOKEN', rawPayPalPayment: { payer: 'DO-NOT-RENDER-PAYER' },
  }), { ...config, clientSecret: 'DO-NOT-RENDER-SECRET', checks: { clientSecretConfigured: true, token: 'DO-NOT-RENDER-CHECK-VALUE' } });
  assert.equal((html.match(/<script>/g) || []).length, 1);
  assert.match(html, /&lt;\/script&gt;&lt;script&gt;/);
  assert.doesNotMatch(html, /<img src=x|javascript:alert|href="\/\/evil|DO-NOT-RENDER|private-contact@example/);
  assert.match(html, /USD 99\.00/);
  assert.match(html, /2026\. 10\. 04\. 07:13:00 KST/);
  assert.match(html, /설정 준비됨 · 실제 연결 조회 전/);
  assert.match(html, /PayPal 비공개 인증 설정/);
  assert.match(html, /입금 검증 완료/);
  assert.doesNotMatch(html, /data-action="(?:capture|refund|charge|checkout|create-order)"/);
  assert.match(render(application({ paymentVerifiedAt: null })), /확인 기록 없음/);
});

test('publish is unavailable for unpaid, unapproved, stale, contradictory or already published records', () => {
  assert.doesNotMatch(buttonTag(render(), 'publish'), /\sdisabled/);
  for (const changes of [
    { paymentVerified: false }, { paymentVerified: 'true' }, { paymentStatus: 'pending' }, { paymentStatus: 'refunded' },
    { approved: false }, { approved: 'true' }, { reviewStatus: 'pending' }, { status: 'payment_review' },
    { publicationStatus: 'published' }, { publicationStatus: 'paused' }, { publicationStatus: 'ended' },
    { applicationId: '../another-application' },
  ]) assert.match(buttonTag(render(application(changes)), 'publish'), /\sdisabled/, JSON.stringify(changes));
  const checkoutClosed = { ...config, paymentReady: false, checks: { ...config.checks, checkoutEnabled: false } };
  assert.doesNotMatch(buttonTag(render(application(), checkoutClosed), 'publish'), /\sdisabled/);
  for (const key of ['storageReady', 'liveEnvironment', 'clientIdConfigured', 'clientSecretConfigured', 'webhookIdConfigured', 'merchantIdConfigured']) {
    for (const value of [false, undefined, 'true']) assert.match(buttonTag(render(application(), { ...checkoutClosed, checks: { ...checkoutClosed.checks, [key]: value } }), 'publish'), /\sdisabled/, key);
  }
  assert.match(buttonTag(render(application(), { ...config, checks: {} }), 'publish'), /\sdisabled/);
  const html = render(application({ publicationStatus: 'published', status: 'active' }));
  assert.doesNotMatch(buttonTag(html, 'pause'), /\sdisabled/);
  assert.match(buttonTag(html, 'reject'), /\sdisabled/);
});

test('review needs verified payment, both factual checks and a bounded note before posting approval', async () => {
  assert.match(render(), /data-field="notes" maxlength="1000"/);
  const state = browser(render(application({ approved: false, reviewStatus: 'pending', status: 'awaiting_ad_approval' })));
  const card = state.cards[0];
  assert.equal(state.requests.length, 0, 'opening the owner screen must not mutate anything');
  await action(card, 'approve').dispatch('click');
  assert.equal(state.requests.length, 0);
  control(card, 'destination-checked').checked = true;
  control(card, 'destination-checked').dispatch('change');
  assert.equal(action(card, 'approve').disabled, true);
  await action(card, 'approve').dispatch('click');
  assert.equal(state.requests.length, 0);
  control(card, 'claims-checked').checked = true;
  control(card, 'claims-checked').dispatch('change');
  assert.equal(action(card, 'approve').disabled, true);
  for (const notes of ['', '   ', 'x'.repeat(1001)]) {
    control(card, 'notes').value = notes;
    control(card, 'notes').dispatch('input');
    assert.equal(action(card, 'approve').disabled, true);
    await action(card, 'approve').dispatch('click');
    assert.equal(state.requests.length, 0);
  }
  control(card, 'notes').value = 'URL and claims checked.';
  control(card, 'notes').dispatch('input');
  assert.equal(action(card, 'approve').disabled, false);
  await action(card, 'approve').dispatch('click');
  assert.equal(state.requests.length, 1);
  const { path, options } = state.requests[0];
  assert.equal(path, '/ops/ads/applications/ad-123/review');
  assert.equal(options.method, 'POST');
  assert.equal(options.credentials, 'same-origin');
  assert.equal(options.mode, 'same-origin');
  assert.equal(options.redirect, 'error');
  assert.deepEqual(JSON.parse(options.body), { decision: 'approve', notes: 'URL and claims checked.', destinationChecked: true, claimsChecked: true });
  assert.equal(state.reloads, 1);

  const unpaid = browser(render(application({ paymentVerified: false, paymentStatus: 'pending' })));
  control(unpaid.cards[0], 'destination-checked').checked = true;
  control(unpaid.cards[0], 'claims-checked').checked = true;
  await action(unpaid.cards[0], 'approve').dispatch('click');
  assert.equal(unpaid.requests.length, 0);
});

test('publication converts the explicitly labelled Korea time to UTC and refuses incomplete payment state', async () => {
  const state = browser(render());
  control(state.cards[0], 'starts-at').value = '2099-01-02T00:30';
  await action(state.cards[0], 'publish').dispatch('click');
  assert.equal(state.requests[0].path, '/ops/ads/applications/ad-123/publish');
  assert.deepEqual(JSON.parse(state.requests[0].options.body), { startsAt: '2099-01-01T15:30:00.000Z' });
  for (const changes of [{ paymentVerified: false }, { approved: false }, { publicationStatus: 'paused' }]) {
    const blocked = browser(render(application(changes)));
    await action(blocked.cards[0], 'publish').dispatch('click');
    assert.equal(blocked.requests.length, 0);
  }
  const invalid = browser(render());
  control(invalid.cards[0], 'starts-at').value = '2099-02-31T12:00';
  await action(invalid.cards[0], 'publish').dispatch('click');
  assert.equal(invalid.requests.length, 0);
  assert.match(invalid.cards[0].querySelector('[data-result]').textContent, /올바른 한국 시간/);
});

test('connection check is read-only, projects evidence without claiming merchant or payment verification, and blocks external action paths', async () => {
  const state = browser(render(), async () => ({ ok: true, status: 200, json: async () => ({
    providerAuthenticationVerified: true, webhookUrlVerified: true, requiredEventsVerified: true,
    merchantIdentityVerified: false, configurationOnly: true, readinessVerifiedAt: '2026-10-03T22:15:00Z',
    accessToken: 'SECRET-RESPONSE', payer: { email: 'secret-payer@example.com' },
  }) }));
  await state.nodes.get('verify-readiness').dispatch('click');
  assert.equal(state.requests.length, 1);
  assert.equal(state.requests[0].path, '/ops/ads/verify-readiness');
  assert.equal(state.requests[0].options.body, '{}');
  const result = state.nodes.get('connection-result').textContent;
  assert.match(result, /PayPal 인증 조회: 확인/);
  assert.match(result, /결제 수신 업체 신원: 미확인/);
  assert.doesNotMatch(result, /SECRET-RESPONSE|secret-payer|입금 검증 완료/);
  for (const basePath of ['https://evil.example/ads', '//evil.example/ads', '/ops/../ads', '/ops/ads?redirect=evil', '/ops/%2e%2e/ads', '/owner\\evil/ads', '/owner//ads', '/owner/ads#fragment', '/owner/other']) {
    assert.throws(() => renderSponsorshipOps({ basePath }), /same-origin/);
  }
  const alias = browser(renderSponsorshipOps({ applications: [application()], config, basePath: '/synthetic-owner/ads/' }));
  await alias.nodes.get('verify-readiness').dispatch('click');
  assert.equal(alias.requests[0].path, '/synthetic-owner/ads/verify-readiness');
  assert.equal(alias.requests[0].options.credentials, 'same-origin');
  const tampered = browser(render().replace('data-base-path="/ops/ads"', 'data-base-path="//evil.example"'));
  await tampered.nodes.get('verify-readiness').dispatch('click');
  assert.equal(tampered.requests.length, 0);
});

test('uncertain responses are not retried, raw errors are not displayed, and double clicks send one request', async () => {
  let release;
  const pending = new Promise((resolve) => { release = resolve; });
  const state = browser(render(), async () => { await pending; throw new Error('SECRET-FAILED-RESPONSE'); });
  const first = action(state.cards[0], 'verify-payment').dispatch('click');
  const second = action(state.cards[0], 'verify-payment').dispatch('click');
  assert.equal(state.requests.length, 1);
  release();
  await Promise.all([first, second]);
  assert.equal(state.requests.length, 1);
  assert.equal(state.reloads, 0);
  const result = state.cards[0].querySelector('[data-result]');
  assert.equal(result.attributes.role, 'alert');
  assert.match(result.textContent, /다시 실행하기 전에/);
  assert.doesNotMatch(result.textContent, /SECRET-FAILED-RESPONSE/);

  const rejected = browser(render(), async () => ({ ok: false, status: 409, json: async () => ({ error: 'secret-provider-debug-data' }) }));
  await action(rejected.cards[0], 'publish').dispatch('click');
  assert.equal(rejected.reloads, 0);
  assert.match(rejected.cards[0].querySelector('[data-result]').textContent, /HTTP 409/);
  assert.doesNotMatch(rejected.cards[0].querySelector('[data-result]').textContent, /secret-provider-debug-data/);
});

test('readiness failures display fixed stage and HTTP diagnostics without rendering raw provider details', async () => {
  for (const [stage, code, httpStatus, label] of [
    ['authentication', 'authentication_http_error', 401, 'PayPal 인증 요청'],
    ['webhook_lookup', 'provider_http_error', 404, 'PayPal 알림 설정 조회'],
    ['webhook_lookup', 'network_error', null, 'PayPal 알림 설정 조회'],
  ]) {
    const state = browser(render(), async () => ({ ok: true, status: 200, json: async () => ({
      providerAuthenticationVerified: stage === 'webhook_lookup', webhookUrlVerified: false, requiredEventsVerified: false,
      merchantIdentityVerified: false, configurationOnly: true,
      diagnostic: { stage, code, httpStatus, raw: 'SECRET-DETAIL', error: 'SECRET-PROVIDER-ERROR', webhookId: 'SECRET-WEBHOOK-ID' },
    }) }));
    await state.nodes.get('verify-readiness').dispatch('click');
    const shown = state.nodes.get('connection-result').textContent;
    assert.match(shown, new RegExp(`진단 단계: ${label}`));
    if (httpStatus) assert.match(shown, new RegExp(`PayPal HTTP ${httpStatus}`));
    assert.match(state.nodes.get('ops-result').textContent, /완료하지 못했습니다/);
    assert.equal(state.nodes.get('ops-result').attributes.role, 'alert');
    assert.doesNotMatch(shown, /SECRET|입금 검증 완료/);
    assert.equal(state.requests.length, 1);
    assert.equal(state.reloads, 0);
  }
  const unexpected = browser(render(), async () => ({ ok: true, status: 200, json: async () => ({
    diagnostic: { stage: 'SECRET-STAGE', code: 'SECRET-CODE', httpStatus: 'SECRET-STATUS' },
  }) }));
  await unexpected.nodes.get('verify-readiness').dispatch('click');
  assert.doesNotMatch(unexpected.nodes.get('connection-result').textContent, /SECRET/);
});
