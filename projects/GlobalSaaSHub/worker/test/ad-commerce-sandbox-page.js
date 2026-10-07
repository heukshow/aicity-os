'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const labels = { logo: '로고', 'tool-primary': '도구 소개 고정', 'buyer-intent-top': '구매 의도 가이드 상단',
    'compare-decision-premium': '비교 결정 프리미엄', 'buyer-hub-fixed': '구매 가이드 목록 고정',
    'comparison-hub-fixed': '비교 목록 고정', 'tool-rotation': '도구 소개 회전',
    'guide-rotation': '가이드 회전', 'compare-rotation': '비교 회전' };
  let catalog, order, token, busy = false, reviewRead = false;
  const blobUrls = [];
  const node = (tag, text, className) => { const el = document.createElement(tag); if (text) el.textContent = text; if (className) el.className = className; return el; };
  function selectedSlots() {
    const bundle = catalog.bundles.find(item => item.id === $('product').value);
    return bundle ? [...bundle.slots, ...(bundle.choices.length ? [$('rotation').value] : [])] : [$('product').value];
  }
  function selection() {
    const bundle = catalog.bundles.find(item => item.id === $('product').value);
    $('rotation-field').hidden = !bundle?.choices.length;
    if (bundle) $('days').value = '30';
    $('days').disabled = !!bundle || !!order;
    $('selection-detail').textContent = '선택 자리: ' + selectedSlots().map(slot => labels[slot] || slot).join(', ') +
      (bundle ? ' · 묶음 상품은 30일만 가능합니다.' : '') + ' · 확정 금액은 서버가 계산합니다.';
  }
  async function api(path, { method = 'GET', body, key = token, raw = false } = {}) {
    if (!path.startsWith('/sandbox/') && !path.startsWith('/fixture/')) throw new Error('로컬 시험 경로만 허용됩니다.');
    const headers = {};
    if (key) headers.Authorization = 'Bearer ' + key;
    if (body !== undefined) headers['Content-Type'] = raw ? body.type || 'application/octet-stream' : 'application/json';
    const response = await fetch(path, { method, headers, body: body === undefined ? undefined : raw ? body : JSON.stringify(body),
      credentials: 'omit', cache: 'no-store', redirect: 'error' });
    if (!response.ok) { const data = await response.json().catch(() => ({})); throw new Error(data.error || 'HTTP ' + response.status); }
    return response.headers.get('content-type')?.startsWith('image/') ? response.blob() : response.json();
  }
  function render() {
    const state = order?.state;
    const enabled = { 'create-draft': !!catalog && !order, 'upload-assets': state === 'draft', 'submit-order': state === 'draft',
      'refresh-order': !!order, 'read-review': !!order, 'approve-review': state === 'submitted' && reviewRead && $('destination-checked').checked && $('claims-checked').checked,
      reserve: state === 'approved', checkout: state === 'approved' && !!order.hold_until, 'mock-approve': state === 'checkout',
      capture: state === 'checkout', expire: !!order };
    for (const [id, allow] of Object.entries(enabled)) $(id).disabled = busy || !allow;
    if (order) $('order-status').textContent = '시험 주문 ' + order.id + ' · 상태: ' + state + ' · 서버 금액: ' + order.amount + ' ' + order.currency +
      (order.ends_at ? ' · 종료: ' + order.ends_at : '');
  }
  async function run(action) {
    if (busy) return;
    busy = true; render(); $('status').textContent = '로컬 합성 시험 처리 중…';
    try { const message = await action(); $('status').textContent = message || '로컬 합성 단계가 완료되었습니다.'; }
    catch (error) { $('status').textContent = '시험 요청 오류: ' + error.message; }
    finally { busy = false; render(); }
  }
  const action = (id, fn) => $(id).addEventListener('click', () => run(fn));
  function update(result) {
    if (result.order) order = result.order;
    if (result.files) $('file-details').textContent = '서버에 저장된 시험 파일\n' + JSON.stringify(result.files, null, 2);
    render();
  }
  async function refresh() { update(await api('/sandbox/orders/' + order.id)); }
  function assetInputs() {
    $('asset-inputs').replaceChildren();
    for (const role of ['logo', ...JSON.parse(order.quote_json).slots]) {
      const spec = catalog.assetSpecs[role], field = node('div', '', 'field'), input = node('input');
      input.id = 'asset-' + role; input.type = 'file'; input.accept = 'image/png'; input.dataset.role = role;
      const label = node('label', (labels[role] || role) + ' PNG · ' + spec.width + '×' + spec.height + ' · 최대 ' + spec.maxBytes + ' bytes');
      label.htmlFor = input.id; field.append(label, input); $('asset-inputs').append(field);
    }
    $('uploads-section').hidden = false;
    $('preview-links').replaceChildren();
    for (const slot of JSON.parse(order.quote_json).slots) {
      const link = node('a', (labels[slot] || slot) + ' 로컬 게시 확인', 'btn secondary');
      link.href = '/sandbox/preview/' + encodeURIComponent(slot); link.target = '_blank'; link.rel = 'noopener noreferrer';
      $('preview-links').append(link);
    }
  }
  $('draft-form').addEventListener('submit', event => { event.preventDefault(); run(async () => {
    const result = await api('/sandbox/orders', { method: 'POST', body: {
      product: $('product').value, days: Number($('days').value), rotation: $('rotation').value,
      rightsConfirmed: $('rights').checked, termsVersion: catalog.version,
      company: $('company').value, productName: $('product-name').value, email: $('email').value, claims: $('claims').value,
      items: selectedSlots().map(slot => ({ slot, headline: $('headline').value, description: $('description').value,
        alt: $('alt').value, url: $('destination').value, button: $('button-text').value })),
    } });
    token = result.accessToken; update(result); assetInputs();
    // Same-tab PayPal return can recover only this sandbox order's generated access key.
    try { sessionStorage.setItem('coshuma-sandbox-order:' + order.id, token); } catch { /* Missing access never authorizes a return-page charge. */ }
    for (const input of $('draft-form').elements) input.disabled = true;
    return '합성 초안 생성 완료. 자리별 실제 PNG 시험 파일을 선택하세요.';
  }); });
  action('upload-assets', async () => {
    let count = 0;
    for (const input of $('asset-inputs').querySelectorAll('input[type=file]')) {
      if (!input.files.length) continue;
      update(await api('/sandbox/orders/' + order.id + '/assets/' + encodeURIComponent(input.dataset.role),
        { method: 'PUT', body: input.files[0], raw: true })); count++;
    }
    if (!count) throw new Error('PNG 시험 파일을 먼저 선택하세요.');
    reviewRead = false; return count + '개 PNG 파일이 서버 검증을 통과했습니다.';
  });
  action('refresh-order', async () => { await refresh(); return '현재 서버 주문 상태를 확인했습니다.'; });
  for (const name of ['submit', 'reserve', 'checkout', 'capture']) {
    action(name === 'submit' ? 'submit-order' : name, async () => {
      update(await api('/sandbox/orders/' + order.id + '/' + name, { method: 'POST' }));
      return '로컬 합성 ' + name + ' 완료 · 상태: ' + order.state;
    });
  }
  action('read-review', async () => {
    const key = $('review-key').value, path = '/sandbox/admin/orders/' + order.id;
    if (!key) throw new Error('로컬 시험용 검수자 키가 필요합니다.');
    const result = await api(path, { key });
    $('review-details').textContent = JSON.stringify(result, null, 2);
    for (const url of blobUrls.splice(0)) URL.revokeObjectURL(url);
    $('review-images').replaceChildren();
    for (const file of result.files) {
      const blob = await api(path + '/assets/' + encodeURIComponent(file.role), { key });
      const url = URL.createObjectURL(blob), figure = node('figure', '', 'placement-image'), image = node('img');
      blobUrls.push(url); image.src = url; image.alt = (labels[file.role] || file.role) + ' 검수 이미지';
      figure.append(image, node('figcaption', (labels[file.role] || file.role) + ' · ' + file.width + '×' + file.height));
      $('review-images').append(figure);
    }
    reviewRead = true; return '별도 검수자 권한으로 제출 자료와 PNG를 조회했습니다.';
  });
  action('approve-review', async () => {
    update(await api('/sandbox/admin/orders/' + order.id + '/review', { method: 'POST', key: $('review-key').value,
      body: { decision: 'approve', notes: 'Synthetic local reviewer confirmation only.',
        destinationChecked: $('destination-checked').checked, claimsChecked: $('claims-checked').checked } }));
    return '합성 검수 승인 완료. 자리 확보를 진행할 수 있습니다.';
  });
  action('mock-approve', async () => {
    if (!order.provider_order) throw new Error('모의 결제 주문을 먼저 생성하세요.');
    await api('/fixture/approve/' + encodeURIComponent(order.provider_order), { method: 'POST' }); await refresh();
    return '로컬 모의 구매자 승인 완료. 실제 PayPal 승인은 아닙니다.';
  });
  action('expire', async () => {
    await api('/fixture/expire', { method: 'POST', key: $('review-key').value }); await refresh();
    return '합성 시계를 30일 이동하고 기간 종료를 처리했습니다. 로컬 게시 확인 링크에서 결과를 확인하세요.';
  });
  for (const id of ['destination-checked', 'claims-checked']) $(id).addEventListener('change', render);
  for (const id of ['product', 'days', 'rotation']) $(id).addEventListener('change', selection);
  window.addEventListener('pagehide', () => { for (const url of blobUrls) URL.revokeObjectURL(url); });
  if (location.protocol !== 'http:' || !['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) {
    $('status').textContent = '이 시험 화면은 HTTP loopback에서만 실행됩니다.'; return;
  }
  run(async () => {
    catalog = await api('/sandbox/catalog');
    for (const product of [...catalog.slots, ...catalog.bundles]) {
      const option = node('option', product.id + ' · ' + (labels[product.id] || product.name)); option.value = product.id; $('product').append(option);
    }
    for (const slot of catalog.slots.filter(item => item.mode === 'rotating')) {
      const option = node('option', labels[slot.id]); option.value = slot.id; $('rotation').append(option);
    }
    selection(); return '로컬 상품 준비 완료 · 합성 기본값이 입력되어 있습니다.';
  });
})();
