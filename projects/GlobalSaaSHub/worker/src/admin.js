import snapshot from './admin-snapshot.json' with { type: 'json' };

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

async function authorized(request, env) {
  if (!env.ADMIN_USERNAME || !env.ADMIN_PASSWORD_SHA256) return false;
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

export function isAdminPath(url, env) {
  const base = String(env.ADMIN_PATH || '').replace(/\/$/, '');
  return Boolean(base && (url.pathname === base || url.pathname.startsWith(`${base}/`)));
}

const stateLabel = (status) => ({
  approved_tracking: '승인', approved: '승인', pending: '대기', rejected: '거절',
  program_closed_to_new_applicants: 'Closed', closed: 'Closed',
}[status] || '확인 필요');

const statusClass = (status) => {
  const label = stateLabel(status);
  if (label === '승인') return 'ok';
  if (label === '대기') return 'warn';
  if (label === '거절' || label === 'Closed') return 'bad';
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
const empty = (label = 'Not connected') => `<span class="badge muted">${escapeHtml(label)}</span>`;

function render(data, money) {
  const affiliateRows = data.affiliates.map((item) => `<tr>
    <td><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.id)}</small></td>
    <td><span class="badge ${statusClass(item.status)}">${escapeHtml(stateLabel(item.status))}</span></td>
    <td>${item.verified ? '<span class="badge ok">Verified</span>' : empty('확인 필요')}</td>
    <td class="link">${escapeHtml(item.url || 'Not connected')}</td>
    <td>${escapeHtml(item.verifiedAt || '확인 필요')}</td>
  </tr>`).join('');
  const funnel = [
    ['Google 검색 노출', 'Not connected', 100], ['사이트 방문', 'Not connected', 76],
    ['도구 페이지', 'Not connected', 52], ['Affiliate CTA', 'Not connected', 31],
    ['전환 / 수익', money.connected ? `${money.paidCount}건` : 'Not connected', 15],
  ].map(([label, value, width], index) => `<div class="funnel-step" style="--w:${width}%"><span>${index + 1}</span><b>${label}</b><em>${value}</em></div>`).join('');
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive,nosnippet"><title>COSHUMA 운영센터</title><style>
  :root{color-scheme:dark;--bg:#070b14;--panel:#101827;--line:#223049;--text:#eef4ff;--muted:#91a0b7;--purple:#a78bfa;--cyan:#22d3ee;--green:#34d399;--amber:#fbbf24;--red:#fb7185}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 85% 0,#182044 0,transparent 34%),var(--bg);color:var(--text);font:14px/1.5 Inter,system-ui,sans-serif}.shell{max-width:1480px;margin:auto;padding:26px}.top{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-bottom:24px}.eyebrow{color:var(--cyan);font-weight:800;letter-spacing:.15em;text-transform:uppercase;font-size:11px}h1{font-size:30px;margin:4px 0}.top p,.sub,small{color:var(--muted)}.live{display:flex;gap:8px;align-items:center;padding:9px 13px;border:1px solid #245347;border-radius:999px;background:#0c261f;color:#7ee2bd}.dot{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 12px var(--green)}.grid{display:grid;gap:14px}.metrics{grid-template-columns:repeat(6,1fr);margin-bottom:14px}.card{background:linear-gradient(145deg,#111a2b,#0d1421);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 14px 36px #0004}.metric span{color:var(--muted);font-weight:700}.metric strong{display:block;font-size:26px;margin:10px 0 4px}.metric.accent{border-color:#4c3b83}.two{grid-template-columns:1.05fr .95fr;margin-bottom:14px}.three{grid-template-columns:1.2fr .8fr .8fr;margin-bottom:14px}h2{font-size:16px;margin:0 0 5px}h3{font-size:13px;color:var(--muted);margin:18px 0 8px}.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:14px}.badge{display:inline-flex;padding:4px 8px;border-radius:999px;font-size:11px;font-weight:800;white-space:nowrap}.ok{background:#123c31;color:#86efc7}.warn{background:#3a2d0e;color:#fcd66d}.bad{background:#421b28;color:#fca5b8}.muted{background:#202a3b;color:#adbacd}.funnel{display:grid;gap:8px}.funnel-step{position:relative;width:var(--w);min-width:52%;margin:auto;padding:11px 14px;background:linear-gradient(90deg,#5b45a8,#17677b);clip-path:polygon(5% 0,95% 0,100% 50%,95% 100%,5% 100%,0 50%);display:grid;grid-template-columns:26px 1fr auto;gap:8px;align-items:center}.funnel-step span{display:grid;place-items:center;width:22px;height:22px;background:#ffffff1c;border-radius:50%;font-size:11px}.funnel-step em{font-style:normal;color:#d7e4f7;font-size:12px}.list{display:grid;gap:9px}.row{display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid var(--line)}.row:last-child{border:0}.row b{font-size:13px}.row span{color:var(--muted);text-align:right}.quality{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}.quality div{padding:12px;border-radius:12px;background:#0a1220;border:1px solid var(--line)}.quality strong{display:block;font-size:20px}.table-card{overflow:hidden}.table-wrap{overflow:auto;margin:0 -18px -18px}table{width:100%;border-collapse:collapse;min-width:880px}th,td{text-align:left;padding:12px 18px;border-top:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em}td small{display:block}.link{max-width:300px;word-break:break-all;color:#a5b4fc}.notice{padding:13px;border:1px dashed #4c5870;background:#111827;border-radius:12px;color:#cbd5e1}.bar{height:7px;background:#243049;border-radius:9px;overflow:hidden;margin-top:7px}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--purple),var(--cyan));width:0}.footer{display:flex;justify-content:space-between;color:var(--muted);padding:18px 4px;font-size:12px}@media(max-width:1100px){.metrics{grid-template-columns:repeat(3,1fr)}.three{grid-template-columns:1fr 1fr}.three .table-card{grid-column:1/-1}}@media(max-width:760px){.shell{padding:16px}.top{align-items:flex-start;flex-direction:column}.metrics,.two,.three{grid-template-columns:1fr}.metric{display:grid;grid-template-columns:1fr auto;align-items:center}.metric strong{font-size:22px}.metric small{grid-column:1/-1}.three .table-card{grid-column:auto}.quality{grid-template-columns:1fr 1fr}.funnel-step{min-width:88%}.footer{flex-direction:column;gap:4px}}
  </style></head><body><main class="shell"><header class="top"><div><div class="eyebrow">Private operations</div><h1>COSHUMA 운영센터</h1><p>검색 → 방문 → 도구 탐색 → 제휴 클릭 → 수익을 한 화면에서 점검합니다.</p></div><div class="live"><i class="dot"></i>비공개 인증 활성</div></header>
  <section class="grid metrics">
    ${metricCard('오늘 방문자','Not connected','GA4 연결 필요')}${metricCard('최근 7일','Not connected','GA4 연결 필요')}${metricCard('최근 30일','Not connected','GA4 연결 필요')}
    ${metricCard('Search Console','Not connected','API 인증 필요')}${metricCard('Affiliate CTA','Not connected','GA4 이벤트 연결 필요','accent')}${metricCard('Verified 링크',data.counts.verifiedAffiliates,`${data.counts.totalTools}개 도구 중`,'accent')}
  </section>
  <section class="grid two"><article class="card"><div class="section-head"><div><h2>수익 퍼널</h2><div class="sub">외부 연동 전에는 숫자를 추정하지 않습니다.</div></div>${empty('부분 연결')}</div><div class="funnel">${funnel}</div></article>
  <article class="card"><div class="section-head"><div><h2>수익 및 지급</h2><div class="sub">Worker D1에 확인된 결제 데이터만 표시</div></div>${money.connected?'<span class="badge ok">D1 연결됨</span>':empty()}</div><div class="quality"><div><span>실제 수익</span><strong>${money.connected?`$${money.actual.toFixed(2)}`:'—'}</strong></div><div><span>지급 대기</span><strong>${money.connected?`$${money.pending.toFixed(2)}`:'—'}</strong></div><div><span>지급 완료</span><strong>확인 필요</strong></div><div><span>전환 건수</span><strong>${money.connected?money.paidCount:'—'}</strong></div></div><h3>연동 상태</h3><div class="list"><div class="row"><b>Google Analytics 4</b>${empty(data.connections.ga4)}</div><div class="row"><b>Google Search Console</b>${empty(data.connections.searchConsole)}</div><div class="row"><b>Affiliate 네트워크 수익</b>${empty('Not connected')}</div></div></article></section>
  <section class="grid three"><article class="card"><div class="section-head"><div><h2>SEO 품질 상태</h2><div class="sub">저장소 기반 실제 검사 결과</div></div><span class="badge ${data.seo.testsPassed?'ok':'bad'}">${data.seo.testsPassed?'PASS':'확인 필요'}</span></div><div class="quality"><div><span>Sitemap URL</span><strong>${data.counts.sitemapUrls}</strong></div><div><span>Tool 페이지</span><strong>${data.counts.toolPages}</strong></div><div><span>Compare 페이지</span><strong>${data.counts.comparePages}</strong></div><div><span>한글 혼입</span><strong>${data.seo.koreanLeakCount}</strong></div></div><h3>검사 항목</h3><div class="list">${['404 / 깨진 내부링크','Canonical 정합성','robots.txt','공개 페이지 한글 혼입'].map(label=>`<div class="row"><b>${label}</b><span class="badge ${data.seo.testsPassed?'ok':'muted'}">${data.seo.testsPassed?'통과':'확인 필요'}</span></div>`).join('')}</div></article>
  <article class="card"><div class="section-head"><div><h2>유입 분석</h2><div class="sub">국가 · 소스 · 인기 페이지</div></div>${empty()}</div><div class="notice">GA4 Measurement ID와 Data API 자격 증명이 아직 확인되지 않았습니다. 연결 전까지 방문자·국가·소스·인기 페이지는 표시하지 않습니다.</div><h3>최근 SEO 변경</h3><div class="list">${data.recentSeoChanges.map(item=>`<div class="row"><b>${escapeHtml(item.title)}</b><span>${escapeHtml(item.date)}</span></div>`).join('')}</div></article>
  <article class="card table-card"><div class="section-head"><div><h2>Affiliate 우선순위</h2><div class="sub">Verified 도구를 먼저 표시</div></div><span class="badge ok">${data.counts.verifiedAffiliates} verified</span></div><div class="table-wrap"><table><thead><tr><th>프로그램</th><th>상태</th><th>검증</th><th>고유 링크</th><th>최근 확인</th></tr></thead><tbody>${affiliateRows}</tbody></table></div></article></section>
  <footer class="footer"><span>스냅샷 생성: ${escapeHtml(data.generatedAt)}</span><span>응답 캐시 금지 · 검색 차단 · 서버 인증</span></footer></main></body></html>`;
}

export async function handleAdminRequest(request, env) {
  if (!(await authorized(request, env))) {
    return new Response('Authentication required', { status: 401, headers: {
      ...PRIVATE_HEADERS, 'content-type': 'text/plain; charset=utf-8',
      'www-authenticate': 'Basic realm="COSHUMA Private Operations", charset="UTF-8"',
    } });
  }
  if (request.method !== 'GET' && request.method !== 'HEAD') return new Response('Method not allowed', { status: 405, headers: PRIVATE_HEADERS });
  const body = request.method === 'HEAD' ? null : render(snapshot, await revenue(env));
  return new Response(body, { status: 200, headers: PRIVATE_HEADERS });
}
