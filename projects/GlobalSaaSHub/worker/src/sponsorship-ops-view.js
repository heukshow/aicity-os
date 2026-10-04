const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));

const STATUS_LABELS = {
  awaiting_payment: '입금 확인 대기', payment_review: '결제 확인 필요', awaiting_ad_approval: '소재 검토 대기',
  ready_to_publish: '집행 준비 완료', scheduled: '집행 예약', active: '집행 중', paused: '집행 중지',
  ended: '집행 종료', rejected: '소재 반려', payment_reversed: '환불·결제 취소',
};
const PAYMENT_LABELS = { unpaid: '미결제', created: '결제 준비', pending: '결제 확인 대기', verified: '입금 검증 완료', review: '결제 재확인 필요', refunded: '환불·결제 취소' };
const REVIEW_LABELS = { pending: '검토 대기', approved: '소재 승인', rejected: '소재 반려' };
const PUBLICATION_LABELS = { draft: '집행 전', published: '집행 중 또는 예약', paused: '집행 중지', ended: '집행 종료' };
const SLOT_LABELS = { 'tool-primary': '도구 페이지 광고', 'buyer-intent-top': '구매 가이드 광고', 'compare-decision-premium': '비교 페이지 광고' };
const CHECK_LABELS = {
  storageReady: '신청·결제 저장소', checkoutEnabled: '운영 결제 사용', liveEnvironment: 'PayPal 운영 환경',
  clientIdConfigured: 'PayPal 앱 식별 설정', clientSecretConfigured: 'PayPal 비공개 인증 설정',
  webhookIdConfigured: '결제 알림 설정', merchantIdConfigured: '결제 수신 업체 설정',
};
const FULFILMENT_CHECKS = ['storageReady', 'liveEnvironment', 'clientIdConfigured', 'clientSecretConfigured', 'webhookIdConfigured', 'merchantIdConfigured'];

function fulfilmentReady(config) {
  return FULFILMENT_CHECKS.every((key) => config.checks?.[key] === true);
}

function checkedBasePath(value) {
  if (typeof value !== 'string' || !/^\/(?:[a-zA-Z0-9_-]+\/)*ads\/?$/.test(value)) {
    throw new TypeError('Sponsorship operations require a safe same-origin /ads path');
  }
  return value.replace(/\/$/, '');
}

function safeDestination(value) {
  if (typeof value !== 'string' || value.length > 1000) return null;
  try {
    const url = new URL(value);
    if (url.protocol !== 'https:' || url.username || url.password || !url.hostname.includes('.')
        || url.hostname === 'localhost' || url.hostname.endsWith('.local')
        || /^\d+(\.\d+){3}$/.test(url.hostname) || url.hostname.includes(':')) return null;
    return url.href;
  } catch { return null; }
}

function safeTargetPage(value) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//') || value.includes('\\')) return null;
  try {
    const url = new URL(value, 'https://coshuma.com');
    return url.origin === 'https://coshuma.com' && !url.username && !url.password ? url.href : null;
  } catch { return null; }
}

function timestamp(value) {
  if (typeof value !== 'string' || !/(Z|[+-]\d{2}:\d{2})$/i.test(value)) return '<span>확인 기록 없음</span>';
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return '<span>확인 기록 없음</span>';
  const label = new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23',
  }).format(date);
  return `<time datetime="${escapeHtml(date.toISOString())}">${escapeHtml(label)} KST</time>`;
}

function amountLabel(quote) {
  if (!quote || !/^[A-Z]{3}$/.test(quote.currency || '') || !/^\d+(?:\.\d{1,2})?$/.test(String(quote.amount ?? ''))) return '금액 확인 필요';
  const amount = Number(quote.amount);
  return Number.isFinite(amount) && amount > 0 ? `${quote.currency} ${amount.toFixed(2)}` : '금액 확인 필요';
}

function applicationState(application, config) {
  const validId = typeof application.applicationId === 'string' && /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/.test(application.applicationId);
  const paymentVerified = application.paymentVerified === true && application.paymentStatus === 'verified';
  const approved = application.approved === true && application.reviewStatus === 'approved';
  const published = application.publicationStatus === 'published';
  return {
    validId, paymentVerified, approved,
    canApprove: validId && paymentVerified && ['draft', 'paused', 'ended'].includes(application.publicationStatus) && !!safeDestination(application.destinationUrl),
    canReject: validId && ['draft', 'paused', 'ended'].includes(application.publicationStatus),
    canPublish: validId && paymentVerified && approved && application.status === 'ready_to_publish' && application.publicationStatus === 'draft' && fulfilmentReady(config),
    canPause: validId && published && application.status !== 'ended',
  };
}

function renderApplication(application, index, config) {
  const state = applicationState(application, config);
  const key = `application-${index}`;
  const destination = safeDestination(application.destinationUrl);
  const target = safeTargetPage(application.quote?.targetPage);
  const description = (label, content) => `<div><dt>${label}</dt><dd>${content}</dd></div>`;
  const disabled = (allowed) => allowed ? '' : ' disabled';
  const publication = STATUS_LABELS[application.status] || PUBLICATION_LABELS[application.publicationStatus] || '상태 확인 필요';
  let publishReason = '결제 검증과 소재 승인 후 집행할 수 있습니다.';
  if (state.canPublish) publishReason = '시작일을 비워 두면 지금 시작합니다. 저장된 상품 기간이 적용됩니다.';
  else if (application.publicationStatus === 'paused') publishReason = '중지한 광고입니다. 이 화면에서는 다시 집행하지 않습니다.';
  else if (application.publicationStatus !== 'draft') publishReason = '이미 집행되었거나 종료된 광고는 다시 집행하지 않습니다.';
  else if (!fulfilmentReady(config)) publishReason = '운영 결제 연결과 저장소를 확인한 뒤 집행할 수 있습니다.';
  return `<article class="application" id="${key}" data-application data-application-id="${escapeHtml(state.validId ? application.applicationId : '')}" data-can-approve="${state.canApprove}" data-can-publish="${state.canPublish}" data-can-reject="${state.canReject}" data-can-pause="${state.canPause}">
    <header class="application-heading"><div><p class="reference">주문 ${escapeHtml(application.reference || '주문번호 확인 필요')}</p><h3>${escapeHtml(application.companyName || '업체명 확인 필요')} <span>/</span> ${escapeHtml(application.toolName || '도구명 확인 필요')}</h3></div><span class="pill ${state.paymentVerified ? 'verified' : ''}">${escapeHtml(publication)}</span></header>
    <dl class="facts">
      ${description('청구 금액', `<strong>${escapeHtml(amountLabel(application.quote))}</strong><small>고객 결제 총액 기준</small>`)}
      ${description('상품 · 기간', `${escapeHtml(SLOT_LABELS[application.quote?.slot] || '광고 위치 확인 필요')} · ${escapeHtml([7, 30, 90].includes(application.quote?.durationDays) ? `${application.quote.durationDays}일` : '기간 확인 필요')}`)}
      ${description('입금 상태', `<strong>${escapeHtml(state.paymentVerified ? '입금 검증 완료' : application.paymentStatus === 'verified' ? '입금 검증 기록 확인 필요' : PAYMENT_LABELS[application.paymentStatus] || '결제 상태 확인 필요')}</strong>`)}
      ${description('소재 상태', escapeHtml(REVIEW_LABELS[application.reviewStatus] || '검토 상태 확인 필요'))}
      ${description('입금 검증 시각', timestamp(application.paymentVerifiedAt))}
      ${description('최근 결제 조회', timestamp(application.lastCheckedAt))}
      ${description('집행 시작', timestamp(application.startAt))}
      ${description('집행 종료', timestamp(application.endAt))}
    </dl>
    <section class="materials" aria-labelledby="${key}-materials"><h4 id="${key}-materials">제출된 광고 소재</h4>
      <p><b>제목</b> ${escapeHtml(application.headline || '제출된 제목 없음')}</p><p class="material-copy"><b>설명</b> ${escapeHtml(application.description || '제출된 설명 없음')}</p><p><b>버튼 문구</b> ${escapeHtml(application.ctaText || '제출된 문구 없음')}</p>
      <p><b>광고가 표시될 페이지</b> ${target ? `<a href="${escapeHtml(target)}" target="_blank" rel="noopener noreferrer">${escapeHtml(application.quote.targetPage)}</a>` : '<span>페이지 확인 필요</span>'}</p>
      <p><b>광고 연결 주소</b> ${destination ? `<a href="${escapeHtml(destination)}" target="_blank" rel="noopener noreferrer">${escapeHtml(destination)}</a>` : '<span class="warning">안전한 HTTPS 주소인지 확인이 필요합니다.</span>'}</p>
      <p><b>희망 시작일</b> ${escapeHtml(application.desiredStartDate || '지정하지 않음')}</p>
      ${application.reviewNotes ? `<p class="review-notes"><b>최근 검토 기록</b> ${escapeHtml(application.reviewNotes)}</p>` : ''}
    </section>
    <div class="workflow">
      <section aria-labelledby="${key}-payment"><h4 id="${key}-payment">1. 입금 확인</h4><p>저장된 PayPal 주문과 실제 결제 상태를 다시 조회합니다.</p><button type="button" data-action="verify-payment"${disabled(state.validId)}>입금 다시 확인</button></section>
      <section aria-labelledby="${key}-review"><h4 id="${key}-review">2. 소재 검토</h4><label class="check"><input type="checkbox" data-field="destination-checked"${disabled(state.canApprove)}> 연결 주소와 광고 내용을 직접 확인했습니다.</label><label class="check"><input type="checkbox" data-field="claims-checked"${disabled(state.canApprove)}> 광고의 표현과 주장을 확인했습니다.</label>
        <label for="${key}-notes">검토 메모 <span>(승인·반려 모두 필수 · 최대 1,000자)</span></label><textarea id="${key}-notes" data-field="notes" maxlength="1000" rows="3" placeholder="확인한 내용 또는 수정이 필요한 부분"${disabled(state.canReject)}></textarea>
        <div class="buttons"><button type="button" data-action="approve" disabled>소재 승인</button><button type="button" data-action="reject"${disabled(state.canReject)}>소재 반려</button></div><small>${state.canApprove ? '두 확인 항목을 모두 선택하고 검토 메모를 입력하면 승인할 수 있습니다.' : '입금 확인 및 현재 광고 상태를 확인한 뒤 소재를 승인할 수 있습니다.'}</small>
      </section>
      <section aria-labelledby="${key}-publish"><h4 id="${key}-publish">3. 광고 집행</h4><label for="${key}-start">시작일시 <span>(한국 시간 · 선택)</span></label><input id="${key}-start" type="datetime-local" data-field="starts-at"${disabled(state.canPublish)}><p id="${key}-publish-reason">${escapeHtml(publishReason)}</p><div class="buttons"><button type="button" data-action="publish" aria-describedby="${key}-publish-reason"${disabled(state.canPublish)}>광고 집행·예약</button><button type="button" data-action="pause"${disabled(state.canPause)}>광고 중지</button></div></section>
    </div><p class="action-result" role="status" aria-live="polite" data-result></p>
  </article>`;
}

export function sponsorshipOpsClient() {
  const root = document.getElementById('sponsorship-ops');
  const feedback = document.getElementById('ops-result');
  const connection = document.getElementById('connection-result');
  const basePath = root.dataset.basePath;
  const baseIsSafe = /^\/(?:[a-zA-Z0-9_-]+\/)*ads\/?$/.test(basePath);
  const cards = Array.from(document.querySelectorAll('[data-application]'));
  let busy = false;

  const field = (card, name) => card.querySelector(`[data-field="${name}"]`);
  const button = (card, action) => card.querySelector(`[data-action="${action}"]`);
  const resultNode = (card) => card ? card.querySelector('[data-result]') : feedback;
  function syncApproval(card) {
    const notes = field(card, 'notes').value.trim();
    button(card, 'approve').disabled = busy || card.dataset.canApprove !== 'true'
      || !field(card, 'destination-checked').checked || !field(card, 'claims-checked').checked || !notes || notes.length > 1000;
  }
  function message(card, value, error = false) {
    const node = resultNode(card);
    node.textContent = value;
    node.setAttribute('role', error ? 'alert' : 'status');
    node.classList.toggle('error', error);
  }
  function startValue(card) {
    const value = field(card, 'starts-at').value;
    if (!value) return {};
    if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?$/.test(value)) throw new Error('START_DATE');
    const local = value.length === 16 ? `${value}:00` : value;
    const date = new Date(`${local}+09:00`);
    if (!Number.isFinite(date.getTime()) || new Date(date.getTime() + 9 * 3600000).toISOString().slice(0, 19) !== local || date.getTime() < Date.now()) throw new Error('START_DATE');
    return { startsAt: date.toISOString() };
  }
  function responseStatus(data) {
    const value = data?.config || data;
    const parts = [
      ['PayPal 인증 조회', value?.providerAuthenticationVerified],
      ['결제 알림 주소 조회', value?.webhookUrlVerified],
      ['필수 결제 알림 구독', value?.requiredEventsVerified],
      ['결제 수신 업체 신원', value?.merchantIdentityVerified],
    ].map(([label, verified]) => `${label}: ${verified === true ? '확인' : '미확인'}`);
    const diagnostic = value?.diagnostic;
    const stages = { configuration: '연결 설정', authentication: 'PayPal 인증 요청', webhook_lookup: 'PayPal 알림 설정 조회', complete: '연결 조회' };
    const codes = {
      configuration_incomplete: '필수 연결 설정을 확인해야 합니다.',
      authentication_http_error: '인증 단계에서 PayPal 오류 응답을 받았습니다. 이 결과만으로 인증 정보 오류를 단정할 수 없습니다.',
      provider_http_error: 'PayPal 알림 설정 조회에서 오류 응답을 받았습니다.',
      network_error: '요청 응답을 받지 못했습니다. 연결 상태를 확인한 뒤 다시 조회하세요.',
      unknown_error: '예상한 응답을 확인하지 못했습니다. 원인은 아직 확인되지 않았습니다.',
      complete: '조회 요청을 마쳤습니다. 위 항목별 확인 결과를 확인하세요.',
    };
    if (diagnostic && Object.hasOwn(stages, diagnostic.stage) && Object.hasOwn(codes, diagnostic.code)) {
      const httpStatus = Number.isInteger(diagnostic.httpStatus) && diagnostic.httpStatus >= 100 && diagnostic.httpStatus <= 599 ? ` · PayPal HTTP ${diagnostic.httpStatus}` : '';
      parts.push(`진단 단계: ${stages[diagnostic.stage]}${httpStatus} · ${codes[diagnostic.code]}`);
    }
    if (typeof value?.readinessVerifiedAt === 'string' && /(Z|[+-]\d{2}:\d{2})$/i.test(value.readinessVerifiedAt) && Number.isFinite(Date.parse(value.readinessVerifiedAt))) {
      parts.push(`조회 시각: ${new Date(value.readinessVerifiedAt).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })} KST`);
    }
    parts.push('이 결과는 연결 조회 기록입니다. 광고별 실제 입금은 입금 상태에서 확인하세요.');
    connection.textContent = parts.join(' · ');
  }
  async function run(card, action) {
    if (busy || !baseIsSafe) return;
    const allowed = ['verify-readiness', 'verify-payment', 'approve', 'reject', 'publish', 'pause'];
    if (!allowed.includes(action) || (card && !/^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/.test(card.dataset.applicationId))) return;
    let body = {}, suffix = action;
    try {
      if (action === 'approve') {
        if (!card || card.dataset.canApprove !== 'true' || !field(card, 'destination-checked').checked || !field(card, 'claims-checked').checked) {
          message(card, '연결 주소와 광고 표현을 모두 확인한 뒤 승인하세요.', true); return;
        }
        const notes = field(card, 'notes').value.trim();
        if (!notes || notes.length > 1000) { message(card, '확인한 내용을 검토 메모에 1~1,000자로 입력하세요.', true); field(card, 'notes').focus(); return; }
        suffix = 'review'; body = { decision: 'approve', notes, destinationChecked: true, claimsChecked: true };
      } else if (action === 'reject') {
        if (!card || card.dataset.canReject !== 'true') return;
        const notes = field(card, 'notes').value.trim();
        if (!notes || notes.length > 1000) { message(card, '반려 사유를 검토 메모에 1~1,000자로 입력하세요.', true); field(card, 'notes').focus(); return; }
        suffix = 'review'; body = { decision: 'reject', notes, destinationChecked: field(card, 'destination-checked').checked, claimsChecked: field(card, 'claims-checked').checked };
      } else if (action === 'publish') {
        if (!card || card.dataset.canPublish !== 'true') { message(card, '입금 검증과 소재 승인, 운영 결제 준비 상태를 확인하세요.', true); return; }
        body = startValue(card);
      } else if (action === 'pause' && (!card || card.dataset.canPause !== 'true')) return;
      if (card && action === 'verify-readiness') return;
      if (!card && action !== 'verify-readiness') return;
      const path = card ? `${basePath}/applications/${encodeURIComponent(card.dataset.applicationId)}/${suffix}` : `${basePath}/verify-readiness`;
      const endpoint = new URL(path, window.location.origin);
      if (endpoint.origin !== window.location.origin) return;
      const buttons = Array.from(document.querySelectorAll('button[data-action]'));
      const before = buttons.map((item) => item.disabled);
      busy = true; buttons.forEach((item) => { item.disabled = true; });
      message(card, '확인 요청을 처리하고 있습니다.');
      try {
        const response = await fetch(endpoint.pathname, { method: 'POST', credentials: 'same-origin', mode: 'same-origin', cache: 'no-store', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(body), redirect: 'error' });
        let data = null;
        try { data = await response.json(); } catch { /* A login page or invalid response is not a successful operation. */ }
        if (!response.ok || !data || typeof data !== 'object' || Array.isArray(data) || data.ok === false) {
          const detail = response.status === 401 || response.status === 403 ? '소유자 로그인 상태를 확인하세요.' : response.status === 409 ? '현재 결제·소재·집행 상태를 새로고침해 확인하세요.' : '연결과 현재 상태를 확인한 뒤 다시 시도하세요.';
          message(card, `처리하지 못했습니다. ${detail} (HTTP ${response.status})`, true); return;
        }
        if (action === 'verify-readiness') {
          responseStatus(data);
          const incomplete = data?.diagnostic && data.diagnostic.code !== 'complete';
          message(card, incomplete ? '연결 조회를 완료하지 못했습니다. 위 진단 단계와 항목별 상태를 확인하세요.' : '결제 연결 조회가 끝났습니다. 위 항목별 확인 결과를 확인하세요.', !!incomplete);
        }
        else { message(card, '요청을 처리했습니다. 저장된 상태를 새로 조회합니다.'); window.location.reload(); }
      } catch {
        message(card, '응답을 확인하지 못했습니다. 다시 실행하기 전에 화면을 새로고침해 처리 결과를 확인하세요.', true);
      } finally {
        busy = false; buttons.forEach((item, index) => { item.disabled = before[index]; }); cards.forEach(syncApproval);
      }
    } catch (error) {
      message(card, error.message === 'START_DATE' ? '시작일시는 현재 이후의 올바른 한국 시간으로 입력하세요.' : '입력값을 확인하세요.', true);
    }
  }
  for (const card of cards) {
    field(card, 'destination-checked').addEventListener('change', () => syncApproval(card));
    field(card, 'claims-checked').addEventListener('change', () => syncApproval(card));
    field(card, 'notes').addEventListener('input', () => syncApproval(card));
    for (const action of ['verify-payment', 'approve', 'reject', 'publish', 'pause']) button(card, action).addEventListener('click', () => run(card, action));
    syncApproval(card);
  }
  document.getElementById('verify-readiness').addEventListener('click', () => run(null, 'verify-readiness'));
  document.getElementById('refresh-ops').addEventListener('click', () => window.location.reload());
}

export function renderSponsorshipOps({ applications = [], config = {}, basePath = '/ops/ads' } = {}) {
  const base = checkedBasePath(basePath);
  const rows = Array.isArray(applications) ? applications.filter((application) => application && typeof application === 'object' && !Array.isArray(application)) : [];
  const settings = config && typeof config === 'object' ? config : {};
  const verified = rows.filter((application) => applicationState(application, settings).paymentVerified).length;
  const awaitingReview = rows.filter((application) => applicationState(application, settings).paymentVerified && application.reviewStatus === 'pending').length;
  const onSite = rows.filter((application) => ['active', 'scheduled'].includes(application.status) && application.publicationStatus === 'published').length;
  const checks = Object.entries(CHECK_LABELS).filter(([key]) => typeof settings.checks?.[key] === 'boolean')
    .map(([key, label]) => `<li><span>${label}</span><strong class="${settings.checks[key] ? 'good' : 'warning'}">${settings.checks[key] ? '확인' : '확인 필요'}</strong></li>`).join('');
  const connectionLabel = settings.paymentReady === true ? (settings.configurationOnly === true ? '설정 준비됨 · 실제 연결 조회 전' : '운영 결제 준비 확인') : '운영 결제 준비 확인 필요';
  const summary = (label, count) => `<article><span>${label}</span><strong>${count}</strong></article>`;
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>COSHUMA 광고 운영 · 결제 확인</title><style>
  *{box-sizing:border-box}body{margin:0;background:#f3f5f9;color:#18273e;font:15px/1.6 system-ui,-apple-system,sans-serif}main{max-width:1320px;margin:auto;padding:30px}h1{font-size:30px;line-height:1.3;margin:6px 0 10px}h2{font-size:22px;margin:0 0 8px}h3{font-size:21px;margin:3px 0;overflow-wrap:anywhere}h3 span{color:#96a3b6;font-weight:400}h4{font-size:16px;margin:0 0 12px}p{margin:6px 0}a{color:#285ac2;overflow-wrap:anywhere}.top,.application-heading{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}.eyebrow{font-size:12px;letter-spacing:.14em;font-weight:700;color:#4265ba}nav,.buttons{display:flex;gap:10px;flex-wrap:wrap}button,nav a{font:inherit;padding:10px 14px;border:1px solid #cbd5e4;border-radius:8px;background:#fff;color:#263b59;text-decoration:none}button{cursor:pointer}button:disabled{color:#748093;background:#f2f4f7;cursor:not-allowed;opacity:.75}button[data-action=publish]:not(:disabled),button[data-action=approve]:not(:disabled){background:#315dde;color:#fff;border-color:#315dde}button[data-action=pause]:not(:disabled){color:#983328;border-color:#d6a5a0}button:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible{outline:3px solid #9bb5fd;outline-offset:3px}.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0 8px}.summary article,.connection,.application{background:#fff;border:1px solid #dde4ef;border-radius:14px;padding:22px}.summary span{color:#566882;font-size:13px}.summary strong{font-size:32px;display:block;margin-top:8px;font-variant-numeric:tabular-nums}.scope,small,.muted{color:#65738a;font-size:12px}small{display:block;margin-top:5px}.connection{margin:22px 0}.connection-actions{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:14px}.checks{list-style:none;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:9px 22px}.checks li{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid #e9edf4;padding:8px 0;font-size:13px}.good{color:#096442}.warning,.error{color:#9a3b1a}.applications{margin-top:28px}.application{margin-top:18px}.reference{font-size:12px;color:#58708e;overflow-wrap:anywhere}.pill{display:inline-block;white-space:nowrap;background:#fff1d6;color:#795400;padding:5px 10px;border-radius:16px;font-size:12px}.pill.verified{background:#e0f4ed;color:#096442}.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:18px 24px;margin:22px 0}.facts dt{font-size:12px;color:#65738a;margin-bottom:5px}.facts dd{margin:0;overflow-wrap:anywhere;font-size:14px}.facts dd strong{font-size:17px}.facts time{font-size:13px}.materials{border-top:1px solid #e5eaf2;border-bottom:1px solid #e5eaf2;padding:20px 0;overflow-wrap:anywhere}.materials p{font-size:14px}.materials b{display:inline-block;color:#566882;min-width:100px}.material-copy,.review-notes{white-space:pre-wrap}.workflow{display:grid;grid-template-columns:.85fr 1.4fr 1.1fr;gap:24px;margin-top:22px}.workflow section+section{border-left:1px solid #e5eaf2;padding-left:24px}.workflow p{font-size:13px;color:#65738a;margin:9px 0 14px}.workflow label{display:block;font-size:13px;margin:8px 0}.workflow label span{color:#65738a}.workflow .check{display:flex;gap:8px;align-items:flex-start;line-height:1.5}.check input{width:18px;height:18px;margin:2px 0 0;flex:none}textarea,input[type=datetime-local]{display:block;box-sizing:border-box;width:100%;font:inherit;font-size:14px;border:1px solid #cbd5e4;border-radius:8px;padding:10px;background:#fff;color:#18273e}textarea{resize:vertical;margin:6px 0 12px}textarea:disabled,input:disabled{background:#f3f5f9}.action-result{min-height:1.5em;font-size:13px;margin-top:16px}#ops-result,#connection-result{font-size:14px}.empty{background:#fff;border:1px solid #dde4ef;padding:30px;border-radius:14px}footer{margin-top:28px;color:#65738a;font-size:12px}@media(max-width:1000px){.facts{grid-template-columns:repeat(2,1fr)}.checks{grid-template-columns:repeat(2,1fr)}.workflow{grid-template-columns:1fr}.workflow section+section{border-left:0;border-top:1px solid #e5eaf2;padding:18px 0 0}}@media(max-width:700px){main{padding:16px}.top,.application-heading{display:block}.top nav{margin-top:18px}.summary{grid-template-columns:repeat(2,1fr)}.application,.connection{padding:18px}.pill{margin-top:10px}.facts{gap:16px}.checks{grid-template-columns:1fr}h1{font-size:26px}}
  </style></head><body><main id="sponsorship-ops" data-base-path="${escapeHtml(base)}"><header class="top"><div><div class="eyebrow">COSHUMA / ADS</div><h1>광고 운영 · 결제 확인</h1><p>주문별 입금 근거와 소재를 확인하고 광고를 집행합니다.</p></div><nav aria-label="운영 화면 이동"><a href="/ops/revenue.html">전체 수익</a><button type="button" id="refresh-ops">상태 새로고침</button></nav></header>
  <section class="summary" aria-label="조회된 광고 신청 현황">${summary('조회된 신청', rows.length)}${summary('입금 검증 완료', verified)}${summary('입금 확인 후 소재 검토 대기', awaitingReview)}${summary('집행 중 · 예약', onSite)}</section><p class="scope">현재 조회 목록 기준입니다. 입금 검증 건수는 은행 출금액이나 광고 성과를 뜻하지 않습니다.</p>
  <section class="connection" aria-labelledby="connection-title"><h2 id="connection-title">결제 연결 상태</h2><p><strong>${escapeHtml(connectionLabel)}</strong> · 광고 접수 ${settings.intakeReady === true ? '준비됨' : '확인 필요'}</p><p class="muted">연결 준비와 개별 광고의 실제 입금 확인은 각각 확인합니다.</p>${checks ? `<ul class="checks">${checks}</ul>` : '<p class="muted">세부 연결 확인 결과가 아직 없습니다.</p>'}<div class="connection-actions"><button type="button" id="verify-readiness" data-action="verify-readiness">PayPal 연결 조회</button><span class="muted">인증과 알림 등록 상태를 읽습니다.</span></div><p id="connection-result" role="status" aria-live="polite"></p><p id="ops-result" role="status" aria-live="polite"></p></section>
  <section class="applications" aria-labelledby="applications-title"><h2 id="applications-title">광고 신청 및 집행</h2><p class="muted">시간은 한국 시간(KST)입니다. 기록이 없는 날짜는 확인 기록 없음으로 표시합니다.</p>${rows.length ? rows.map((application, index) => renderApplication(application, index, settings)).join('') : '<p class="empty">현재 조회된 광고 신청이 없습니다.</p>'}</section><noscript><p role="alert">운영 작업에는 JavaScript가 필요합니다. 위 상태는 페이지를 불러온 시점의 기록입니다.</p></noscript><footer>소유자 전용 운영 화면 · 마지막 확인 시점을 기준으로 읽으세요.</footer></main><script>const __name=fn=>fn;(${sponsorshipOpsClient.toString()})();</script></body></html>`;
}
