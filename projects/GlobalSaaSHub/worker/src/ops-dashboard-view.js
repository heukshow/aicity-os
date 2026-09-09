// The HTML and metric records remain in private D1 storage. Only rendering logic is bundled.
export function dashboardClient() {
  const $ = id => document.getElementById(id);
  const esc = v => String(v ?? '—').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let snapshot = null, partner = null, range = 'today';
  const number = v => v === null || v === undefined || !Number.isFinite(Number(v)) ? null : Number(v);
  const show = (id, v) => { $(id).textContent = v === null || v === undefined ? '—' : String(v); };
  const money = (v, currency = 'USD') => v === null ? '—' : `${currency} ${v.toFixed(2)}`;
  function connected() { return snapshot?.status === 'live_google_connected' && snapshot?.measurement_status === 'live_connected'; }
  function list(id, items, label = 'name', value = 'value', suffix = '') {
    $(id).innerHTML = items?.length ? items.slice(0, 8).map(x => `<div class="row"><div><strong>${esc(x[label])}</strong>${x.note ? `<small>${esc(x.note)}</small>` : ''}</div><span>${esc(x[value])}${suffix}</span></div>`).join('')
      : `<div class="row"><strong>${connected() ? '조회 기간에 기록 없음' : '데이터 확인 필요'}</strong><span>—</span></div>`;
  }
  function opportunities() {
    const rows = [];
    const add = (target, signal, action, status, cls = 'warn') => rows.push(`<tr><td>${rows.length+1}</td><td>${esc(target)}</td><td>${esc(signal)}</td><td>${esc(action)}</td><td><span class="pill ${cls}">${esc(status)}</span></td></tr>`);
    if (connected()) {
      add('GA4 / Search Console', `실데이터 연결됨 · 30일 제휴 클릭 ${snapshot.metrics?.affiliate_clicks_30d ?? '—'}회`, '아래 검색 페이지와 제휴 클릭 목적지를 기준으로 개선', '연결됨', 'ok');
      for (const page of (snapshot.search_pages || []).slice(0, 3))
        add(page.name, `검색 노출 ${page.value} · ${page.note || ''}`, '검색 노출·클릭률을 함께 보고 제목과 검색 의도 일치 여부 점검', '실데이터 확인', 'ok');
      for (const link of (snapshot.affiliate_links || []).slice(0, 2))
        add(link.name, `제휴 클릭 ${link.value}회 · ${link.date || ''}`, '해당 제휴 포털에서 가입·구매·커미션 발생 여부 확인', '전환 확인 필요');
    } else add('GA4 / Search Console', snapshot ? '실데이터 수집 상태 확인 필요' : '데이터를 불러오는 중', '최근 수집 작업과 인증 상태 확인', '확인 필요');
    if (partner?.connected)
      add('PartnerStack', `API 연결됨 · 이번 조회 보상 ${partner.rewardCount}건 / 프로그램 ${partner.partnershipCount}개`, 'PartnerStack 조회 범위만 확인됨. 다른 제휴 네트워크의 전환·수익은 별도 확인', '부분 연결', 'ok');
    else add('PartnerStack', partner ? partner.reason || 'API 조회 실패' : 'API 확인 중', '기존 PartnerStack API 연결 상태 확인', '확인 필요');
    add('전체 제휴 수익 통합', '네트워크 전체·선택 기간 기준 합계는 아직 미확인', '다른 네트워크의 검증된 전환·수익 자료를 연결한 뒤 합산', '통합 미완료');
    $('opportunities').innerHTML = rows.join('');
  }
  function render() {
    const m = snapshot?.metrics || {}, r = snapshot?.ranges?.[range] || {};
    const users = number(r.users), sessions = number(r.sessions), views = number(r.views), clicks = number(r.affiliate_clicks), revenue = number(r.verified_revenue);
    show('users', users); show('sessions', sessions); show('views', views); show('clicks', clicks);
    show('affiliateCtr', users > 0 && clicks !== null ? `${(clicks/users*100).toFixed(1)}%` : null);
    $('revenue').textContent = money(revenue, m.verified_revenue_currency || 'USD');
    $('revenueNote').textContent = '선택 기간·전체 네트워크의 검증된 수익만 합산';
    show('impressions', r.search_impressions); show('searchClicks', r.search_clicks); show('funnelUsers', users); show('funnelClicks', clicks);
    $('funnelRevenue').textContent = money(revenue, m.verified_revenue_currency || 'USD');
    const values = [number(r.search_impressions), number(r.search_clicks), users, clicks, revenue];
    const max = Math.max(1, ...values.filter(v => v !== null));
    ['barImpressions','barSearchClicks','barUsers','barAffiliate','barRevenue'].forEach((id, i) => $(id).style.width = values[i] === null || values[i] === 0 ? '0%' : `${Math.min(100, values[i]/max*100)}%`);
    list('sources', snapshot?.top_sources); list('pages', snapshot?.top_pages); list('queries', snapshot?.top_queries, 'name', 'value', ' 노출');
    $('gaApiState').textContent = snapshot?.connections?.ga4 || '데이터 확인 중';
    $('gscState').textContent = snapshot?.connections?.search_console || '데이터 확인 중';
    $('gaApiDot').className = $('gscDot').className = connected() ? 'ok' : 'warn';
    $('partnerState').textContent = partner?.connected ? `PartnerStack 연결됨 · 조회 보상 ${partner.rewardCount}건 · 기타 네트워크 미연결` : partner?.reason || 'PartnerStack 확인 중';
    $('revenueDot').className = partner?.connected ? 'ok' : 'warn';
    const records = [...(snapshot?.snapshot || [])];
    if (partner) records.push({ label: 'PartnerStack API', value: partner.connected ? `조회 보상 ${partner.rewardCount}건 / 프로그램 ${partner.partnershipCount}개` : partner.reason, period: partner.checkedAt || '확인 시각 미상', source: '첫 페이지 최대 250건씩 조회 · 전체 네트워크 합계 아님' });
    $('snapshotRows').innerHTML = records.length ? records.map(x=>`<tr><td>${esc(x.label)}</td><td>${esc(x.value)}</td><td>${esc(x.period)}</td><td>${esc(x.source)}</td></tr>`).join('') : '<tr><td colspan="4">데이터 확인 중</td></tr>';
    opportunities();
  }
  document.querySelectorAll('.tab').forEach(b => b.onclick = () => { document.querySelectorAll('.tab').forEach(x => x.classList.remove('active')); b.classList.add('active'); range = b.dataset.range; render(); });
  async function load(path) {
    const result = await fetch(path, { cache: 'no-store' });
    if (!result.ok) throw new Error(`HTTP ${result.status}`);
    return result.json();
  }
  render();
  load('/ops/traffic-revenue-data.json').then(data => { snapshot = data; $('generatedAt').textContent = `업데이트 ${data.generated_at || '시각 미확인'}`; render(); }).catch(() => { $('generatedAt').textContent = '데이터 조회 실패 · 새로고침 후 로그인 상태 확인'; render(); });
  load('/ops/partnerstack-summary.json').then(data => { partner = data; render(); }).catch(() => { partner = { connected: false, reason: 'PartnerStack API 조회 실패' }; render(); });
}

export function decorateOpsHtml(html) {
  const pattern = /<script>\s*\(\(\)\s*=>\s*\{[\s\S]*?<\/script>/;
  if (!pattern.test(html)) throw new Error('Dashboard script marker not found');
  return html.replace(pattern, () => `<script>(${dashboardClient.toString()})();</script>`)
    .replace(/<tbody id="opportunities">[\s\S]*?<\/tbody>/, '<tbody id="opportunities"><tr><td colspan="5">실데이터 확인 중</td></tr></tbody>');
}
