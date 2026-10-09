// Minimal isolated Sandbox buyer entry; never imported by the production worker.
function purchaseBrowser() {
  'use strict';
  const element = id => document.getElementById(id);
  const idInput = element('order-id'), keyInput = element('order-access');
  const message = element('purchase-status'), detail = element('purchase-detail');
  const loadButton = element('load-order'), checkoutButton = element('start-checkout');
  const reserveButton = element('reserve-order'), checkButton = element('reconcile-order');
  let current = null, busy = false;
  const keyName = id => 'coshuma-sandbox-order:' + id;
  const markName = order => 'coshuma-sandbox-capture:' + order.id + ':' + order.provider_order;
  function controls() {
    idInput.disabled = busy;
    keyInput.disabled = busy;
    const valid = current && current.id === idInput.value.trim();
    loadButton.disabled = busy;
    reserveButton.disabled = busy || !valid || current.state !== 'approved';
    checkoutButton.disabled = busy || !valid || !['approved', 'checkout'].includes(current.state) ||
      !current.hold_until || Date.parse(current.hold_until) <= Date.now();
    checkButton.disabled = busy || !valid || !['checkout', 'capturing', 'active', 'ended'].includes(current.state);
    if (valid) { try { if (sessionStorage.getItem(markName(current))) checkoutButton.disabled = true; } catch { checkoutButton.disabled = true; } }
  }
  function display(order) {
    current = order;
    detail.textContent = '서버 주문: ' + order.id + ' · 상태: ' + order.state + ' · 금액: ' + order.amount + ' ' + order.currency +
      ' · 예약 만료: ' + (order.hold_until || '확보되지 않음') + ' · 광고 시작: ' + (order.starts_at || '확인되지 않음') +
      ' · 광고 종료: ' + (order.ends_at || '확인되지 않음');
  }
  function input() {
    const id = idInput.value.trim(), key = keyInput.value.trim();
    if (!/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(id) || !/^[a-f0-9]{64}$/.test(key)) {
      throw new Error('기존 시험 주문 ID와 주문 접근키를 입력하세요.');
    }
    return { id, key };
  }
  async function request(action) {
    const { id, key } = input();
    const response = await fetch('/sandbox/orders/' + encodeURIComponent(id) + (action ? '/' + action : ''), {
      method: action ? 'POST' : 'GET', headers: { Authorization: 'Bearer ' + key,
        ...(action ? { 'Content-Type': 'application/json' } : {}) },
      ...(action ? { body: '{}' } : {}), credentials: 'omit', cache: 'no-store', redirect: 'error',
    });
    const result = await response.json();
    if (!response.ok || result.order?.id !== id) throw new Error('기존 주문을 확인하지 못했습니다. 접근키와 서버 상태를 확인하세요.');
    display(result.order);
    return result;
  }
  function save() {
    const { id, key } = input();
    sessionStorage.setItem(keyName(id), key);
    sessionStorage.setItem('coshuma-sandbox-current-order', id);
    if (sessionStorage.getItem(keyName(id)) !== key) throw new Error('복귀 인증 저장에 실패했습니다. 결제 화면을 열지 않았습니다.');
  }
  async function run(fn) {
    if (busy) return;
    busy = true; controls();
    try { await fn(); }
    catch (error) { message.textContent = error.message || '결과가 불명확합니다. 새 결제를 만들지 말고 기존 주문을 확인하세요.'; }
    finally { busy = false; controls(); }
  }
  loadButton.addEventListener('click', () => run(async () => {
    await request(''); save();
    message.textContent = '주문 인증을 확인했습니다. 접근키는 이 탭의 세션에만 보관됩니다.';
  }));
  reserveButton.addEventListener('click', () => run(async () => {
    await request('reserve'); save(); message.textContent = '검수된 시험 광고 자리를 확보했습니다.';
  }));
  checkoutButton.addEventListener('click', () => run(async () => {
    await request(''); save();
    if (sessionStorage.getItem(markName(current))) throw new Error('이 주문은 결제 확정을 시도했습니다. 새 청구 없이 상태를 재조회하세요.');
    const result = await request('checkout'), url = new URL(result.approvalUrl);
    if (url.protocol !== 'https:' || !['sandbox.paypal.com', 'www.sandbox.paypal.com'].includes(url.hostname) ||
      url.port || url.username || url.password || url.hash || url.pathname !== '/checkoutnow' ||
      url.searchParams.getAll('token').length !== 1 || url.searchParams.get('token') !== result.order.provider_order) {
      throw new Error('이 주문에 연결된 PayPal Sandbox 승인 주소가 확인되지 않았습니다.');
    }
    save();
    message.textContent = 'PayPal Sandbox 구매자 승인 화면으로 이동합니다. 승인·취소 후 이 시험 서비스로 자동 복귀합니다.';
    location.assign(url.href);
  }));
  checkButton.addEventListener('click', () => run(async () => {
    await request('reconcile');
    message.textContent = ['active', 'ended'].includes(current.state) && current.capture_id && current.payment_verified_at
      ? '서버가 확인한 Sandbox 결제와 광고 상태입니다.' : '결제 완료가 아직 확인되지 않았습니다. 다시 결제하지 마세요.';
  }));
  for (const field of [idInput, keyInput]) field.addEventListener('input', () => { current = null; controls(); });
  try {
    const id = sessionStorage.getItem('coshuma-sandbox-current-order');
    if (id) { idInput.value = id; keyInput.value = sessionStorage.getItem(keyName(id)) || ''; }
  } catch { message.textContent = '세션 저장소를 사용할 수 없습니다. 복귀 인증을 보존할 수 없어 결제를 시작하지 마세요.'; }
  controls();
}
export function sandboxPurchaseScript() { return '(' + purchaseBrowser.toString() + ')();'; }
export function renderSandboxPurchasePage() {
  const nonce = crypto.randomUUID().replaceAll('-', '');
  const html = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<meta name="robots" content="noindex,nofollow"><title>COSHUMA PayPal Sandbox 시험 주문</title>' +
    '<body><main><h1>COSHUMA PayPal Sandbox 시험 주문</h1><p>격리된 시험 환경입니다. 합성 광고 자료와 Sandbox 시험 자금만 사용합니다.</p>' +
    '<p>기존 검수된 시험 주문을 연결하세요. 실제 계정 비밀번호나 관리자 키를 입력하지 마세요.</p>' +
    '<p><label for="order-id">시험 주문 ID</label><input id="order-id" autocomplete="off" spellcheck="false"></p>' +
    '<p><label for="order-access">이 주문의 접근키</label><input id="order-access" type="password" autocomplete="off" spellcheck="false"></p>' +
    '<button id="load-order" type="button">주문 인증·상태 확인</button><p id="purchase-status" role="status" aria-live="polite"></p>' +
    '<p id="purchase-detail"></p><p><button id="reserve-order" type="button" disabled>검수된 시험 자리 확보</button></p>' +
    '<p><button id="start-checkout" type="button" disabled>PayPal Sandbox 승인 화면으로 이동</button></p>' +
    '<p><button id="reconcile-order" type="button" disabled>새 청구 없이 기존 결제 재조회</button></p>' +
    '<p>승인 화면만으로 결제 완료를 표시하지 않습니다. 복귀 후 서버 검증 결과와 광고 시작·종료 시각을 확인합니다.</p>' +
    '</main><script nonce="' + nonce + '">' + sandboxPurchaseScript() + '</script></body></html>';
  return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store',
    'Referrer-Policy': 'no-referrer', 'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY', 'X-Robots-Tag': 'noindex,nofollow',
    'Content-Security-Policy': "default-src 'none'; script-src 'nonce-" + nonce + "'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'" } });
}
