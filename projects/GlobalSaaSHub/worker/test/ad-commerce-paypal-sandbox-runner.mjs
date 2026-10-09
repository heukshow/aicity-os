// Actual PayPal SANDBOX harness. Never imported by production; credentials/DB stay in process memory.
// Run from this checkout: node test/ad-commerce-paypal-sandbox-runner.mjs
import { createServer } from 'node:http';
import { SandboxAdPayments } from '../src/ad-commerce-sandbox-payments.js';
import { createAdSandboxHandler } from '../src/ad-commerce-sandbox-http.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';
import { memoryStore, syntheticInput, png } from './helpers/ad-commerce-fixtures.js';

const API = 'https://api-m.sandbox.paypal.com';
const nativeFetch = globalThis.fetch.bind(globalThis);
const sessionKey = crypto.randomUUID().replaceAll('-', '');
const reviewerKey = crypto.randomUUID().replaceAll('-', '') + crypto.randomUUID().replaceAll('-', '');
const trace = [], phase = [];
let origin, env, fixture, payments, handle, orderId, accessToken, shift = 0, busy = false;
let preflight = { status: 'not_started', applicationCount: null, accountCount: null, authenticationVerified: false };
const security = { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer', 'Cross-Origin-Resource-Policy': 'same-origin',
  'Content-Security-Policy': "default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'" };
function json(res, data, status = 200) {
  res.writeHead(status, { ...security, 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}
function fail(code) { const error = new Error(code); error.safeCode = code; throw error; }
function gate() { if (preflight.status !== 'passed' || !env) fail('PREFLIGHT_REQUIRED'); }
async function transport(input, init = {}) {
  const url = new URL(input), method = init.method || 'GET';
  const allowed = url.origin === API && !url.username && !url.password && !url.hash && (
    method === 'POST' && url.pathname === '/v1/oauth2/token' && !url.search ||
    method === 'GET' && url.pathname === '/v1/notifications/webhooks' &&
      ['?anchor_type=APPLICATION', '?anchor_type=ACCOUNT'].includes(url.search) ||
    method === 'POST' && url.pathname === '/v2/checkout/orders' && !url.search ||
    method === 'GET' && /^\/v2\/checkout\/orders\/[A-Za-z0-9_-]{1,128}$/.test(url.pathname) && !url.search ||
    method === 'POST' && /^\/v2\/checkout\/orders\/[A-Za-z0-9_-]{1,128}\/capture$/.test(url.pathname) && !url.search ||
    method === 'GET' && /^\/v2\/payments\/captures\/[A-Za-z0-9_-]{1,128}$/.test(url.pathname) && !url.search);
  if (!allowed) fail('SANDBOX_TRANSPORT_REJECTED');
  if (url.pathname.startsWith('/v2/')) gate();
  const entry = { method, path: url.pathname + url.search, status: null };
  trace.push(entry);
  try {
    const response = await nativeFetch(url.href, { ...init, redirect: 'error', signal: AbortSignal.timeout(20000) });
    entry.status = response.status;
    if (response.redirected || (response.url && new URL(response.url).origin !== API)) fail('SANDBOX_REDIRECT_REJECTED');
    return response;
  } catch { fail('SANDBOX_NETWORK_UNAVAILABLE'); }
}
async function checkConfiguration(fetchReadOnly = transport) {
  if (!env) fail('SETUP_REQUIRED');
  preflight = { status: 'checking', applicationCount: null, accountCount: null, authenticationVerified: false };
  try {
    const auth = await fetchReadOnly(API + '/v1/oauth2/token', { method: 'POST',
      headers: { Authorization: 'Basic ' + btoa(env.PAYPAL_CLIENT_ID + ':' + env.PAYPAL_CLIENT_SECRET),
        'Content-Type': 'application/x-www-form-urlencoded' }, body: 'grant_type=client_credentials' });
    if (!auth.ok) fail('SANDBOX_OAUTH_REJECTED');
    const authData = await auth.json();
    if (typeof authData.access_token !== 'string' || !authData.access_token.trim()) fail('SANDBOX_OAUTH_UNKNOWN');
    preflight.authenticationVerified = true;
    for (const [anchor, field] of [['APPLICATION', 'applicationCount'], ['ACCOUNT', 'accountCount']]) {
      const response = await fetchReadOnly(API + '/v1/notifications/webhooks?anchor_type=' + anchor, {
        headers: { Authorization: 'Bearer ' + authData.access_token, 'Content-Type': 'application/json' } });
      if (!response.ok) fail('WEBHOOK_' + anchor + '_LOOKUP_REJECTED');
      const data = await response.json();
      if (!Array.isArray(data.webhooks) ||
          (data.links !== undefined && (!Array.isArray(data.links) || data.links.some(link => link?.rel === 'next')))) {
        fail('WEBHOOK_' + anchor + '_LOOKUP_UNKNOWN');
      }
      preflight[field] = data.webhooks.length;
    }
    if (preflight.applicationCount !== 0 || preflight.accountCount !== 0) fail('EXISTING_WEBHOOKS_BLOCK_TEST');
    preflight.status = 'passed';
    phase.push({ stage: 'sandbox_oauth_and_zero_webhooks', at: new Date().toISOString() });
  } catch (error) { preflight.status = 'blocked'; preflight.code = error.safeCode || 'PREFLIGHT_UNKNOWN'; }
  return preflight;
}
async function body(req) {
  let size = 0; const chunks = [];
  for await (const part of req) { size += part.length; if (size > 8192) fail('BODY_TOO_LARGE'); chunks.push(part); }
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { fail('INVALID_JSON'); }
}
async function localCall(method, path, { key = accessToken, data, bytes } = {}) {
  const response = await handle(new Request(origin + '/sandbox' + path, { method,
    headers: { Origin: origin, ...(key ? { Authorization: 'Bearer ' + key } : {}),
      ...(bytes ? { 'Content-Type': 'image/png' } : data ? { 'Content-Type': 'application/json' } : {}) },
    body: bytes || (data ? JSON.stringify(data) : undefined) }));
  const result = await response.json();
  if (!response.ok) fail('LOCAL_' + path.split('/').at(-1).toUpperCase() + '_HTTP_' + response.status);
  return result;
}
async function prepare() {
  gate();
  if (orderId) fail('ONE_ORDER_ONLY');
  fixture = memoryStore();
  fixture.store.clock = () => new Date(Date.now() + shift);
  payments = new SandboxAdPayments(fixture.store, { env, fetchImpl: transport });
  handle = createAdSandboxHandler({ store: fixture.store, payments, reviewKey: reviewerKey, environment: 'sandbox', origin });
  const draft = await localCall('POST', '/orders', { key: null, data: syntheticInput() });
  orderId = draft.order.id; accessToken = draft.accessToken;
  for (const role of ['logo', 'tool-primary']) {
    const spec = AD_ASSET_SPECS[role];
    await localCall('PUT', '/orders/' + orderId + '/assets/' + role, { bytes: png(spec.width, spec.height) });
  }
  await localCall('POST', '/orders/' + orderId + '/submit');
  await localCall('POST', '/admin/orders/' + orderId + '/review', { key: reviewerKey,
    data: { decision: 'approve', destinationChecked: true, claimsChecked: true,
      notes: 'Controlled generated PNG and example.com synthetic material, reviewed for this isolated Sandbox test only.' } });
  await localCall('POST', '/orders/' + orderId + '/reserve');
  phase.push({ stage: 'synthetic_materials_reviewed_and_reserved', at: new Date().toISOString() });
}
async function report() {
  const order = orderId && fixture ? await fixture.store.get(orderId) : null;
  return { environment: 'actual_paypal_sandbox', database: 'local_memory_only', productionModified: false,
    actualWebhookDeliveryVerified: false, credentialsConfigured: !!env, preflight,
    order: order ? { id: order.id, state: order.state, amount: order.amount, currency: order.currency,
      providerOrder: order.provider_order, captureId: order.capture_id, paymentEnvironment: order.payment_environment,
      verifiedAt: order.payment_verified_at, startsAt: order.starts_at, endsAt: order.ends_at } : null,
    actualSandboxCaptureVerified: !!order?.payment_verified_at,
    expiryAccelerated: shift > 0, phase, trace };
}
const html = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">' +
  '<title>COSHUMA 실제 PayPal Sandbox 시험</title><style>body{font:16px system-ui;max-width:900px;margin:32px auto;padding:16px}label{display:block;margin:12px 0}input{width:95%;padding:8px}button,a{display:inline-block;margin:6px;padding:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f4f4;padding:16px}</style>' +
  '<h1>실제 PayPal Sandbox · 로컬 시험</h1><p>실제 돈을 사용하지 않습니다. 광고 자료는 합성 시험 자료이며 DB와 API 설정은 이 프로세스 메모리에만 있습니다. 운영 사이트에는 게시하지 않습니다.</p>' +
  '<p>기존 Sandbox 앱의 APPLICATION·ACCOUNT webhook 조회가 모두 0건으로 확인돼야 주문을 생성합니다. 공개 webhook 수신 시험은 포함하지 않습니다.</p>' +
  '<form id="setup" autocomplete="off"><label>Sandbox Client ID<input id="client" type="text" autocomplete="off" required></label>' +
  '<label>Sandbox Client Secret<input id="secret" type="password" autocomplete="off" required></label>' +
  '<label>Sandbox Business Merchant ID<input id="merchant" type="text" autocomplete="off" required></label>' +
  '<button id="setup-button">메모리에 설정 후 읽기 전용 연결 확인</button></form><p id="status" role="status">설정 대기</p>' +
  '<button id="preflight">연결 재조회</button><button id="prepare">합성 자료 제출·검수·예약</button>' +
  '<button id="checkout">Sandbox 결제 주문 생성</button><a id="approval" hidden target="_blank" rel="noopener noreferrer">PayPal Sandbox 구매자 승인 화면 열기</a>' +
  '<button id="capture">승인된 Sandbox 결제 확정·재조회</button><button id="expire">로컬 시계 30일 이동·기간 종료</button>' +
  '<button id="refresh">결과 새로 읽기</button><a href="/sandbox/preview/tool-primary" target="_blank" rel="noopener noreferrer">로컬 광고 게시 확인</a>' +
  '<pre id="report"></pre><script src="/ui.js"></script></html>';

const script = "\'use strict\';const sessionKey=" + JSON.stringify(sessionKey) + ";"+"\nconst $=id=>document.getElementById(id);let working=false,last;\nfunction render(data){last=data;$('report').textContent=JSON.stringify(data,null,2);\n  const gate=data?.preflight?.status==='passed',state=data?.order?.state;\n  $('setup-button').disabled=working||!!data?.credentialsConfigured;\n  $('preflight').disabled=working||!data?.credentialsConfigured||!!data?.order;\n  $('prepare').disabled=working||!gate||!!data?.order;\n  $('checkout').disabled=working||!gate||state!=='approved';\n  $('capture').disabled=working||!gate||!['checkout','capturing'].includes(state);\n  $('expire').disabled=working||state!=='active';}\nasync function request(path,data){const response=await fetch(path,{method:data===undefined?'GET':'POST',\n  headers:{'X-Session-Key':sessionKey,...(data===undefined?{}:{'Content-Type':'application/json'})},\n  body:data===undefined?undefined:JSON.stringify(data),credentials:'omit',cache:'no-store',redirect:'error'});\n  const value=await response.json();if(!response.ok)throw new Error(value.error||'REQUEST_FAILED');return value;}\nasync function run(fn){if(working)return;working=true;render(last);$('status').textContent='시험 처리 중';\n  try{const result=await fn();if(result?.approvalUrl){$('approval').href=result.approvalUrl;$('approval').hidden=false;}\n    render(await request('/report'));$('status').textContent=last.preflight.status==='blocked'?'연결 경계 확인 실패: 주문 생성 차단':'단계 완료';}\n  catch(error){$('status').textContent='시험 중단: '+error.message;try{render(await request('/report'));}catch{}}\n  finally{working=false;render(last);}}\n$('setup').addEventListener('submit',event=>{event.preventDefault();const data={clientId:$('client').value,clientSecret:$('secret').value,merchantId:$('merchant').value};\n  for(const id of ['client','secret','merchant'])$(id).value='';\n  run(async()=>{try{return await request('/api/setup',data);}finally{data.clientId='';data.clientSecret='';data.merchantId='';}});});\nfor(const action of ['preflight','prepare','checkout','capture','expire'])$(action).addEventListener('click',()=>run(()=>request('/api/'+action,{})));\n$('refresh').addEventListener('click',()=>run(()=>request('/report')));\nrequest('/report').then(render).catch(()=>{$('status').textContent='로컬 상태 조회 실패';});\n";

const server = createServer(async (req, res) => {
  try {
    if (req.headers.host !== new URL(origin).host) return json(res, { error: 'HOST_REJECTED' }, 403);
    const url = new URL(req.url, origin);
    if (req.headers.origin && req.headers.origin !== origin) return json(res, { error: 'ORIGIN_REJECTED' }, 403);
    if (req.method === 'GET' && url.pathname === '/') {
      res.writeHead(200, { ...security, 'Content-Type': 'text/html; charset=utf-8' }); res.end(html); return;
    }
    if (req.method === 'GET' && url.pathname === '/ui.js') {
      res.writeHead(200, { ...security, 'Content-Type': 'text/javascript; charset=utf-8' }); res.end(script); return;
    }
    if (req.method === 'GET' && ['/sandbox/preview/', '/sandbox/assets/'].some(prefix => url.pathname.startsWith(prefix))) {
      if (!handle) return json(res, { error: 'NO_LOCAL_ORDER' }, 404);
      const response = await handle(new Request(url, { method: 'GET' }));
      res.writeHead(response.status, Object.fromEntries(response.headers)); res.end(Buffer.from(await response.arrayBuffer())); return;
    }
    if (req.headers['x-session-key'] !== sessionKey) return json(res, { error: 'SESSION_REJECTED' }, 403);
    if (req.method === 'GET' && url.pathname === '/report') return json(res, await report());
    if (req.method !== 'POST' || req.headers.origin !== origin || req.headers['content-type'] !== 'application/json') {
      return json(res, { error: 'REQUEST_REJECTED' }, 403);
    }
    if (busy) return json(res, { error: 'OPERATION_IN_PROGRESS' }, 409);
    busy = true;
    try {
      const data = await body(req);
      if (url.pathname === '/api/setup') {
        if (env) fail('ALREADY_CONFIGURED');
        if (!['clientId', 'clientSecret', 'merchantId'].every(key => typeof data[key] === 'string' &&
            data[key].length >= 3 && data[key].length <= 512 && data[key] === data[key].trim() && !/[\r\n]/.test(data[key]))) fail('INVALID_SETUP');
        env = Object.freeze({ PAYPAL_ENVIRONMENT: 'sandbox', PAYPAL_CLIENT_ID: data.clientId,
          PAYPAL_CLIENT_SECRET: data.clientSecret, PAYPAL_MERCHANT_ID: data.merchantId });
        data.clientId = ''; data.clientSecret = ''; data.merchantId = '';
        await checkConfiguration(); return json(res, { preflight });
      }
      if (url.pathname === '/api/preflight') {
        if (orderId) fail('ORDER_ALREADY_STARTED');
        await checkConfiguration(); return json(res, { preflight });
      }
      gate();
      if (url.pathname === '/api/prepare') { await prepare(); return json(res, await report()); }
      if (!orderId) fail('PREPARE_REQUIRED');
      if (url.pathname === '/api/checkout') {
        const result = await localCall('POST', '/orders/' + orderId + '/checkout');
        phase.push({ stage: 'actual_sandbox_order_created', at: new Date().toISOString() });
        return json(res, { approvalUrl: result.approvalUrl, report: await report() });
      }
      if (url.pathname === '/api/capture') {
        await localCall('POST', '/orders/' + orderId + '/capture');
        phase.push({ stage: 'actual_sandbox_capture_verified_locally', at: new Date().toISOString() });
        return json(res, await report());
      }
      if (url.pathname === '/api/expire') {
        const order = await fixture.store.get(orderId);
        if (order.state !== 'active') fail('ACTIVE_ORDER_REQUIRED');
        shift += 30 * 86400000;
        await localCall('POST', '/admin/expire', { key: reviewerKey });
        phase.push({ stage: 'accelerated_local_expiry', at: new Date().toISOString() });
        return json(res, await report());
      }
      return json(res, { error: 'NOT_FOUND' }, 404);
    } finally { busy = false; }
  } catch (error) { json(res, { error: error.safeCode || 'LOCAL_SANDBOX_OPERATION_FAILED' }, 409); }
});
async function offlineSafetyChecks() {
  const { default: test } = await import('node:test');
  const { default: assert } = await import('node:assert/strict');
  const cases = [
    { name: 'OAuth rejection blocks readiness and orders', authStatus: 401, code: 'SANDBOX_OAUTH_REJECTED' },
    { name: 'missing OAuth token blocks readiness and orders', auth: {}, code: 'SANDBOX_OAUTH_UNKNOWN' },
    { name: 'APPLICATION hooks block orders', app: { webhooks: [{ id: 'TEST' }] }, code: 'EXISTING_WEBHOOKS_BLOCK_TEST' },
    { name: 'ACCOUNT hooks block orders', account: { webhooks: [{ id: 'TEST' }] }, code: 'EXISTING_WEBHOOKS_BLOCK_TEST' },
    { name: 'malformed APPLICATION response blocks orders', app: {}, code: 'WEBHOOK_APPLICATION_LOOKUP_UNKNOWN' },
    { name: 'malformed ACCOUNT response blocks orders', account: { webhooks: null }, code: 'WEBHOOK_ACCOUNT_LOOKUP_UNKNOWN' },
    { name: 'ACCOUNT lookup HTTP failure blocks orders', accountStatus: 403, code: 'WEBHOOK_ACCOUNT_LOOKUP_REJECTED' },
    { name: 'paginated results cannot imply zero hooks', app: { webhooks: [], links: [{ rel: 'next' }] }, code: 'WEBHOOK_APPLICATION_LOOKUP_UNKNOWN' },
    { name: 'only confirmed zero hooks in both scopes permits readiness', pass: true },
  ];
  for (const scenario of cases) await test(scenario.name, async () => {
    env = Object.freeze({ PAYPAL_ENVIRONMENT: 'sandbox', PAYPAL_CLIENT_ID: 'OFFLINE-CLIENT',
      PAYPAL_CLIENT_SECRET: 'OFFLINE-SECRET', PAYPAL_MERCHANT_ID: 'OFFLINE-MERCHANT' });
    const calls = [];
    const fake = async (url, init = {}) => {
      const path = new URL(url).pathname + new URL(url).search;
      calls.push({ method: init.method || 'GET', path });
      if (path === '/v1/oauth2/token') {
        return new Response(JSON.stringify(scenario.auth ?? { access_token: 'OFFLINE-TOKEN' }), { status: scenario.authStatus || 200 });
      }
      if (path === '/v1/notifications/webhooks?anchor_type=APPLICATION') {
        return new Response(JSON.stringify(scenario.app ?? { webhooks: [] }), { status: 200 });
      }
      if (path === '/v1/notifications/webhooks?anchor_type=ACCOUNT') {
        return new Response(JSON.stringify(scenario.account ?? { webhooks: [] }), { status: scenario.accountStatus || 200 });
      }
      assert.fail('Unexpected request: no actual provider or order endpoint is allowed in offline tests.');
    };
    const result = await checkConfiguration(fake);
    assert.equal(result.status, scenario.pass ? 'passed' : 'blocked');
    if (scenario.pass) {
      assert.equal(result.applicationCount, 0); assert.equal(result.accountCount, 0);
      assert.equal(result.authenticationVerified, true); assert.doesNotThrow(gate);
    } else {
      assert.equal(result.code, scenario.code); assert.throws(gate, /PREFLIGHT_REQUIRED/);
      const before = trace.length;
      await assert.rejects(transport(API + '/v2/checkout/orders', { method: 'POST' }), /PREFLIGHT_REQUIRED/);
      assert.equal(trace.length, before);
    }
    assert.equal(calls.some(call => call.path.startsWith('/v2/')), false);
    assert.equal(fixture, undefined); assert.equal(orderId, undefined);
    const safe = JSON.stringify(await report());
    for (const value of ['OFFLINE-CLIENT', 'OFFLINE-SECRET', 'OFFLINE-TOKEN', 'OFFLINE-MERCHANT']) assert.equal(safe.includes(value), false);
  });
  await test('live API and refund operations are rejected before transport', async () => {
    const before = trace.length;
    await assert.rejects(transport('https://api-m.paypal.com/v2/checkout/orders', { method: 'POST' }), /SANDBOX_TRANSPORT_REJECTED/);
    await assert.rejects(transport(API + '/v2/payments/captures/EXAMPLE/refund', { method: 'POST' }), /SANDBOX_TRANSPORT_REJECTED/);
    assert.equal(trace.length, before);
  });
  await test('browser script parses without executing or reading credentials', async () => {
    const { Script } = await import('node:vm');
    assert.doesNotThrow(() => new Script(script));
    assert.equal(script.includes('localStorage'), false);
    assert.equal(script.includes('sessionStorage'), false);
  });
  env = undefined;
}
if (process.argv.includes('--self-test')) {
  await offlineSafetyChecks();
} else {
  server.listen(0, '127.0.0.1', () => {
    origin = 'http://127.0.0.1:' + server.address().port;
    console.log('ACTUAL_PAYPAL_SANDBOX_LOCAL_URL=' + origin);
  });
  function close() { env = undefined; accessToken = undefined; server.close(() => { fixture?.close(); }); }
  process.on('SIGINT', close); process.on('SIGTERM', close);
}
