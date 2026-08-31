import snapshot from './admin-snapshot.json' with { type: 'json' };
import { fetchGoogleMetrics } from './google-analytics.js';

const PRIVATE_HEADERS = {
  'content-type': 'text/html; charset=utf-8',
  'cache-control': 'no-store, private',
  'x-robots-tag': 'noindex, nofollow, noarchive, nosnippet',
  'referrer-policy': 'no-referrer',
  'x-content-type-options': 'nosniff',
  'x-frame-options': 'DENY',
  'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
};

const escapeHtml = (value) => String(value ?? '').replace(/[&<>\"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

async function sha256(value) {
  const bytes = new TextEncoder().encode(value);
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
    .map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

function constantTimeEqual(left, right) {
  if (!left || !right || left.length !== right.length) return false;
  let mismatch = 0;
  for (let i = 0; i < left.length; i += 1) mismatch |= left.charCodeAt(i) ^ right.charCodeAt(i);
  return mismatch === 0;
}

async function sessionToken(env) {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(env.ADMIN_PASSWORD_SHA256), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const signature = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`${env.ADMIN_USERNAME}:${env.ADMIN_PATH}`));
  return [...new Uint8Array(signature)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
}

async function authorized(request, env) {
  if (!env.ADMIN_USERNAME || !env.ADMIN_PASSWORD_SHA256) return false;
  const cookie = request.headers.get('cookie') || '';
  const session = cookie.split(';').map((part) => part.trim()).find((part) => part.startsWith('coshuma_ops='))?.slice(12);
  if (session && constantTimeEqual(session, await sessionToken(env))) return true;
  const header = request.headers.get('authorization') || '';
  if (!header.startsWith('Basic ')) return false;
  try {
    const decoded = atob(header.slice(6));
    const separator = decoded.indexOf(':');
    if (separator < 1) return false;
    const username = decoded.slice(0, separator);
    const passwordHash = await sha256(decoded.slice(separator + 1));
    return constantTimeEqual(username, env.ADMIN_USERNAME)
      && constantTimeEqual(passwordHash, env.ADMIN_PASSWORD_SHA256.toLowerCase());
  } catch { return false; }
}

function loginPage(error = '') {
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>COSHUMA 비공개 로그인</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at 80% 0,#272057,transparent 36%),#070b14;color:#eef4ff;font:14px system-ui}.box{width:min(420px,calc(100% - 32px));padding:30px;border:1px solid #293650;border-radius:22px;background:#101827;box-shadow:0 24px 70px #0008}.eyebrow{color:#22d3ee;font-size:11px;font-weight:800;letter-spacing:.15em}h1{margin:7px 0 5px;font-size:26px}p{color:#96a5bb;margin:0 0 22px}label{display:block;margin:13px 0 6px;color:#cbd5e1;font-weight:700}input{width:100%;box-sizing:border-box;padding:13px;border:1px solid #34425d;border-radius:12px;background:#09111e;color:white;font:inherit;outline:none}input:focus{border-color:#8b5cf6;box-shadow:0 0 0 3px #8b5cf625}button{width:100%;margin-top:20px;padding:13px;border:0;border-radius:12px;background:linear-gradient(90deg,#7c3aed,#2563eb);color:white;font-weight:800;cursor:pointer}.error{padding:10px;border-radius:10px;background:#421b28;color:#fda4af;margin:12px 0}.lock{margin-top:16px;text-align:center;color:#718096;font-size:11px}</style></head><body><main class="box"><div class="eyebrow">비공개 운영 화면</div><h1>COSHUMA 운영센터</h1><p>소유자 인증 후 운영 데이터를 확인할 수 있습니다.</p>${error ? `<div class="error">${escapeHtml(error)}</div>` : ''}<form method="post"><label for="username">아이디</label><input id="username" name="username" autocomplete="username" required><label for="password">비밀번호</label><input id="password" name="password" type="password" autocomplete="current-password" required><button type="submit">안전하게 로그인</button></form><div class="lock">검색 차단 · 임시 저장 금지 · 서버 인증</div></main></body></html>`;
}

export function isAdminPath(url, env) {
  const base = String(env.ADMIN_PATH || '').replace(/\/$/, '');
  return Boolean(base && (url.pathname === base || url.pathname.startsWith(`${base}/`)));
}

const stateLabel = (status) => ({
  approved_tracking: '승인', approved: '승인', pending: '대기', rejected: '거절',
  program_closed_to_new_applicants: '모집 종료', closed: '종료',
}[status] || '확인 필요');

const statusClass = (status) => {
  const label = stateLabel(status);
  if (label === '승인') return 'ok';
  if (label === '대기') return 'warn';
  if (label === '거절' || label === '모집 종료' || label === '종료') return 'bad';
  return 'muted';
};

async function revenue(env) {
  if (!env.ORDERS) return { connected: false };
  try {
    const rows = await env.ORDERS.prepare("SELECT status, COUNT(*) count, COALESCE(SUM(CAST(amount AS REAL)),0) total FROM orders GROUP BY status").all();
    const values = Object.fromEntries((rows.results || []).map((row) => [row.status, row]));
    return {
      connected: true,
      actual: Number(values.paid?.total || 0),
      pending: Number(values.pending?.total || 0),
      paidCount: Number(values.paid?.count || 0),
    };
  } catch { return { connected: false }; }
}

const metricCard = (title, value, note, tone = '') => `<article class="card metric ${tone}"><span>${escapeHtml(title)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(note)}</small></article>`;
const empty = (label = '연결 안 됨') => `<span class="badge muted">${escapeHtml(label)}</span>`;
const compactList = (items, unit) => items?.length
  ? items.map((item) => `<div class="row"><b>${escapeHtml(item.name)}</b><span>${item.value}${unit}</span></div>`).join('')
  : '<div class="notice">새 데이터가 쌓이는 중입니다.</div>';

function render(data, money) {
  const affiliateRows = data.affiliates.map((item) => `<tr>
    <td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.id)}</small></td>
    <td><span class="badge ${statusClass(item.status)}">${escapeHtml(stateLabel(item.status))}</span></td>
    <td>${item.verified ? '<span class="badge ok">검증됨</span>' : empty('확인 필요')}</td>
    <td class="link">${escapeHtml(item.url || '연결 안 됨')}</td>
    <td>${escapeHtml(item.verifiedAt || '확인 필요')}</td>
  </tr>`).join('');
  const funnel = [
    ['구글 검색 노출', '연결 안 됨', 100], ['사이트 방문', '연결 안 됨', 76],
    ['도구 상세 페이지', '연결 안 됨', 52], ['제휴 버튼 클릭', '연결 안 됨', 31],
    ['전환 및 수익', money.connected ? `${money.paidCount}건` : '연결 안 됨', 15],
  ].map(([label, value, width], index) => `<div class="funnel-step" style="--w:${width}%"><span>${index + 1}</span><b>${label}</b><em>${value}</em></div>`).join('');
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive,nosnippet"><title>COSHUMA 운영센터</title><style>
  :root{color-scheme:dark;--bg:#070b14;--panel:#101827;--line:#223049;--text:#eef4ff;--muted:#91a0b7;--purple:#a78bfa;--cyan:#22d3ee;--green:#34d399;--amber:#fbbf24;--red:#fb7185}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 85% 0,#182044 0,transparent 34%),var(--bg);color:var(--text);font:14px/1.5 Inter,system-ui,sans-serif}.shell{max-width:1480px;margin:auto;padding:26px}.top{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-bottom:24px}.eyebrow{color:var(--cyan);font-weight:800;letter-spacing:.15em;text-transform:uppercase;font-size:11px}h1{font-size:30px;margin:4px 0}.top p,.sub,small{color:var(--muted)}.live{display:flex;gap:8px;align-items:center;padding:9px 13px;border:1px solid #245347;border-radius:999px;background:#0c261f;color:#7ee2bd}.dot{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 12px var(--green)}.grid{display:grid;gap:14px}.metrics{grid-template-columns:repeat(6,1fr);margin-bottom:14px}.card{background:linear-gradient(145deg,#111a2b,#0d1421);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 14px 36px #0004}.metric span{color:var(--muted);font-weight:700}.metric strong{display:block;font-size:26px;margin:10px 0 4px}.metric.accent{border-color:#4c3b83}.two{grid-template-columns:1.05fr .95fr;margin-bottom:14px}.three{grid-template-columns:1.2fr .8fr .8fr;margin-bottom:14px}h2{font-size:16px;margin:0 0 5px}h3{font-size:13px;color:var(--muted);margin:18px 0 8px}.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:14px}.badge{display:inline-flex;padding:4px 8px;border-radius:999px;font-size:11px;font-weight:800;white-space:nowrap}.ok{background:#123c31;color:#86efc7}.warn{background:#3a2d0e;color:#fcd66d}.bad{background:#421b28;color:#fca5b8}.muted{background:#202a3b;color:#adbacd}.funnel{display:grid;gap:8px}.funnel-step{position:relative;width:var(--w);min-width:52%;margin:auto;padding:11px 14px;background:linear-gradient(90deg,#5b45a8,#17677b);clip-path:polygon(5% 0,95% 0,100% 50%,95% 100%,5% 100%,0 50%);display:grid;grid-template-columns:26px 1fr auto;gap:8px;align-items:center}.funnel-step span{display:grid;place-items:center;width:22px;height:22px;background:#ffffff1c;border-radius:50%;font-size:11px}.funnel-step em{font-style:normal;color:#d7e4f7;font-size:12px}.list{display:grid;gap:9px}.row{display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid var(--line)}.row:last-child{border:0}.row b{font-size:13px}.row span{color:var(--muted);text-align:right}.quality{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}.quality div{padding:12px;border-radius:12px;background:#0a1220;border:1px solid var(--line)}.quality strong{display:block;font-size:20px}.table-card{overflow:hidden}.table-wrap{overflow:auto;margin:0 -18px -18px}table{width:100%;border-collapse:collapse;min-width:880px}th,td{text-align:left;padding:12px 18px;border-top:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em}td small{display:block}.link{max-width:300px;word-break:break-all;color:#a5b4fc}.notice{padding:13px;border:1px dashed #4c5870;background:#111827;border-radius:12px;color:#cbd5e1}.bar{height:7px;background:#243049;border-radius:9px;overflow:hidden;margin-top:7px}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--purple),var(--cyan));width:0}.footer{display:flex;justify-content:space-between;color:var(--muted);padding:18px 4px;font-size:12px}@media(max-width:1100px){.metrics{grid-template-columns:repeat(3,1fr)}.three{grid-template-columns:1fr 1fr}.three .table-card{grid-column:1/-1}}@media(max-width:760px){.shell{padding:16px}.top{align-items:flex-start;flex-direction:column}.metrics,.two,.three{grid-template-columns:1fr}.metric{display:grid;grid-template-columns:1fr auto;align-items:center}.metric strong{font-size:22px}.metric small{grid-column:1/-1}.three .table-card{grid-column:auto}.quality{grid-template-columns:1fr 1fr}.funnel-step{min-width:88%}.footer{flex-direction:column;gap:4px}}
  </style></head><body><main class="shell"><header class="top"><div><div class="eyebrow">비공개 운영 화면</div><h1>COSHUMA 운영센터</h1><p>검색 → 방문 → 도구 탐색 → 제휴 클릭 → 수익을 한 화면에서 점검합니다.</p></div><div class="live"><i class="dot"></i>비공개 인증 활성</div></header>
  <section class="grid metrics">
    ${metricCard('오늘 방문자',data.ga.connected?data.ga.today:'연결 오류','구글 애널리틱스 실시간 조회')}${metricCard('최근 7일 방문자',data.ga.connected?data.ga.sevenDays:'연결 오류','구글 애널리틱스 자동 조회')}${metricCard('최근 30일 방문자',data.ga.connected?data.ga.thirtyDays:'연결 오류',`제휴 클릭 ${data.ga.connected?data.ga.affiliateClicks:'—'}회`)}
    ${metricCard('구글 검색 노출',data.searchConsole.impressions.toLocaleString(),`${data.searchConsole.period} · 클릭 ${data.searchConsole.clicks}회`)}${metricCard('검색 클릭률 / 평균 순위',`${data.searchConsole.ctr} / ${data.searchConsole.averagePosition}`,`검색 콘솔 확인 ${data.searchConsole.checkedAt.slice(0,10)}`,'accent')}${metricCard('검증된 제휴 링크',data.counts.verifiedAffiliates,`전체 ${data.counts.totalTools}개 도구 중`,'accent')}
  </section>
  <section class="grid two"><article class="card"><div class="section-head"><div><h2>수익 퍼널</h2><div class="sub">외부 연동 전에는 숫자를 추정하지 않습니다.</div></div>${empty('부분 연결')}</div><div class="funnel">${funnel}</div></article>
  <article class="card"><div class="section-head"><div><h2>수익 및 지급</h2><div class="sub">결제 저장소에서 확인된 데이터만 표시</div></div>${money.connected?'<span class="badge ok">결제 저장소 연결됨</span>':empty()}</div><div class="quality"><div><span>확정 수익</span><strong>${money.connected?`$${money.actual.toFixed(2)}`:'—'}</strong></div><div><span>미완료 결제 시도</span><strong>${money.connected?`${Math.round(money.pending / 49)}건`:'—'}</strong></div><div><span>지급 완료</span><strong>확인 필요</strong></div><div><span>전환 건수</span><strong>${money.connected?money.paidCount:'—'}</strong></div></div><h3>연결 상태</h3><div class="list"><div class="row"><b>구글 애널리틱스 4</b>${empty(data.connections.ga4)}</div><div class="row"><b>구글 검색 콘솔</b>${empty(data.connections.searchConsole)}</div><div class="row"><b>제휴 프로그램 수익</b>${empty('연결 안 됨')}</div></div></article></section>
  <section class="grid three"><article class="card"><div class="section-head"><div><h2>검색 최적화 품질 상태</h2><div class="sub">저장소와 검색 콘솔의 실제 확인 결과</div></div><span class="badge ${data.seo.testsPassed?'ok':'bad'}">${data.seo.testsPassed?'통과':'확인 필요'}</span></div><div class="quality"><div><span>사이트맵 주소</span><strong>${data.counts.sitemapUrls}</strong></div><div><span>색인된 페이지</span><strong>${data.searchConsole.indexedPages}</strong></div><div><span>미색인 페이지</span><strong>${data.searchConsole.notIndexedPages}</strong></div><div><span>한글 혼입</span><strong>${data.seo.koreanLeakCount}</strong></div></div><h3>페이지 구성</h3><div class="list"><div class="row"><b>도구 페이지</b><span>${data.counts.toolPages}개</span></div><div class="row"><b>비교 페이지</b><span>${data.counts.comparePages}개</span></div>${['404 및 깨진 내부 링크','대표 주소 정합성','검색 로봇 설정'].map(label=>`<div class="row"><b>${label}</b><span class="badge ${data.seo.testsPassed?'ok':'muted'}">${data.seo.testsPassed?'통과':'확인 필요'}</span></div>`).join('')}</div></article>
  <article class="card"><div class="section-head"><div><h2>검색 및 방문 분석</h2><div class="sub">구글 API 자동 갱신</div></div><span class="badge ${data.ga.connected?'ok':'bad'}">${data.ga.connected?'연결됨':'연결 오류'}</span></div><h3>상위 검색어</h3><div class="list">${data.searchConsole.topQueries.map(item=>`<div class="row"><b>${escapeHtml(item.query)}</b><span>노출 ${item.impressions} · 클릭 ${item.clicks}</span></div>`).join('')}</div><h3>국가별 방문자</h3><div class="list">${compactList(data.ga.countries,'명')}</div><h3>유입 경로</h3><div class="list">${compactList(data.ga.sources,'명')}</div><h3>인기 페이지</h3><div class="list">${compactList(data.ga.pages,'회')}</div></article>
  <article class="card table-card"><div class="section-head"><div><h2>제휴 프로그램 우선순위</h2><div class="sub">검증된 제휴 도구를 먼저 표시</div></div><span class="badge ok">검증됨 ${data.counts.verifiedAffiliates}개</span></div><div class="table-wrap"><table><thead><tr><th>프로그램</th><th>상태</th><th>검증</th><th>고유 링크</th><th>최근 확인</th></tr></thead><tbody>${affiliateRows}</tbody></table></div></article></section>
  <footer class="footer"><span>스냅샷 생성: ${escapeHtml(data.generatedAt)}</span><span>응답 캐시 금지 · 검색 차단 · 서버 인증</span></footer></main></body></html>`;
}

export async function handleAdminRequest(request, env) {
  if (request.method === 'POST') {
    const form = await request.formData().catch(() => new FormData());
    const username = String(form.get('username') || '');
    const passwordHash = await sha256(String(form.get('password') || ''));
    const valid = constantTimeEqual(username, env.ADMIN_USERNAME || '')
      && constantTimeEqual(passwordHash, String(env.ADMIN_PASSWORD_SHA256 || '').toLowerCase());
    if (!valid) return new Response(loginPage('아이디 또는 비밀번호가 맞지 않습니다.'), { status: 401, headers: PRIVATE_HEADERS });
    const base = String(env.ADMIN_PATH).replace(/\/$/, '');
    return new Response(null, { status: 303, headers: {
      ...PRIVATE_HEADERS, location: base,
      'set-cookie': `coshuma_ops=${await sessionToken(env)}; Path=${base}; Max-Age=28800; HttpOnly; Secure; SameSite=Strict`,
    } });
  }
  if (!(await authorized(request, env))) {
    return new Response(loginPage(), { status: 200, headers: PRIVATE_HEADERS });
  }
  if (request.method !== 'GET' && request.method !== 'HEAD') return new Response('Method not allowed', { status: 405, headers: PRIVATE_HEADERS });
  let data = { ...snapshot, ga: { connected: false, today: 0, sevenDays: 0, thirtyDays: 0, affiliateClicks: 0, countries: [], sources: [], pages: [] } };
  try {
    const live = await fetchGoogleMetrics(env);
    data = { ...data, ...live, searchConsole: { ...snapshot.searchConsole, ...live.searchConsole } };
  } catch (error) {
    console.error('Google reporting API request failed', error?.message);
  }
  const body = request.method === 'HEAD' ? null : render(data, await revenue(env));
  return new Response(body, { status: 200, headers: PRIVATE_HEADERS });
}
