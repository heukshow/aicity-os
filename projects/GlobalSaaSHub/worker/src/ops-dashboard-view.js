import { agencyLayout } from './ops-agency-layout.js';
// The HTML and metric records remain in private D1 storage. Only rendering logic is bundled.
export function dashboardClient() {
  const $ = id => document.getElementById(id);
  const esc = v => String(v ?? '—').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let snapshot = null, partner = null, range = '30d';
  const number = v => v === null || v === undefined || !Number.isFinite(Number(v)) ? null : Number(v);
  const show = (id, v) => { $(id).textContent = v === null || v === undefined ? '—' : String(v); };
  const money = (v, currency = 'USD') => v === null ? '—' : `${currency} ${v.toFixed(2)}`;
  function connected() { return snapshot?.status === 'live_google_connected' && snapshot?.measurement_status === 'live_connected'; }
  function calendarRows(rows, kind = 'ga', key = range) {
    const window = snapshot?.windows?.[key]?.[kind];
    if (!window) return [];
    const byDate = new Map((rows || []).filter(row=>row && typeof row.date === 'string').map(row=>[row.date,row]));
    const result=[];
    for(let date=window.start; date<=window.end && result.length<366; date=new Date(Date.parse(`${date}T00:00:00Z`)+86400000).toISOString().slice(0,10)) result.push(byDate.get(date)||{date});
    return result;
  }
  function windowLabel(kind, key = range) {
    const w=snapshot?.windows?.[key]?.[kind];
    return w ? `${w.start} ~ ${w.end}` : '조회 기간 확인 필요';
  }
  function sparkline(values, color) {
    const nums=(values||[]).map(number), finite=nums.filter(value=>value!==null);
    if (!finite.length) return '';
    const width=100,height=26,max=Math.max(...finite,1),min=Math.min(...finite,0),spread=max-min||1;
    const point=(value,i)=>({x:nums.length===1 ? 50 : i*width/(nums.length-1),y:height-(value-min)/spread*height});
    const groups=[];let group=[];
    nums.forEach((value,i)=>{if(value===null){if(group.length)groups.push(group);group=[];}else group.push(point(value,i));});
    if(group.length)groups.push(group);
    const paths=groups.map(points=>points.length===1 ? `<circle cx="${points[0].x.toFixed(1)}" cy="${points[0].y.toFixed(1)}" r="2" fill="${color}"/>` : `<polyline points="${points.map(p=>`${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>`).join('');
    const lastIndex=nums.findLastIndex(value=>value!==null),last=point(nums[lastIndex],lastIndex);
    return `<svg viewBox="-2 -3 104 32" width="100%" height="26" preserveAspectRatio="none" role="img" aria-label="일별 추이: ${finite.length}개 값, 빈 구간은 미확정 또는 조회 불가" style="display:block"><title>일별 값: ${nums.map(v=>v===null?'미확정':v).join(', ')}</title>${paths}<circle cx="${last.x.toFixed(1)}" cy="${last.y.toFixed(1)}" r="2" fill="${color}"/></svg>`;
  }
  function chart(series, field, color) {
    const html=sparkline(series.map(row=>row[field]),color);
    return html || '<span style="color:var(--muted);font-size:12px">확정 기록 미제공 또는 추이 조회 불가</span>';
  }
  // A segmented "who makes up this total" bar for the top sources, using
  // the same items list() already ranks — no extra data needed.
  function compositionBar(items) {
    if (!items || !items.length) return '';
    const colors = ['var(--cyan)', 'var(--purple)', 'var(--green)', 'var(--amber)', 'var(--red)'];
    const total = items.reduce((sum, x) => sum + (Number(x.value) || 0), 0);
    if (total <= 0) return '';
    const top = [...items].sort((a,b)=>(Number(b.value)||0)-(Number(a.value)||0)).slice(0, 5);
    const other = Math.max(0, total - top.reduce((sum, x) => sum + (Number(x.value) || 0), 0));
    const segments = top.map((x, i) => ({ label: x.name, value: Number(x.value) || 0, color: colors[i] || 'var(--muted)' }));
    if (other > 0) segments.push({ label: '기타(조회 목록 내)', value: other, color: 'var(--muted)' });
    const bars = segments.filter(s => s.value > 0).map(s => `<div style="width:${(s.value / total * 100).toFixed(2)}%;height:100%;background:${s.color}"></div>`).join('');
    const legend = segments.map(s => `<span style="display:inline-flex;align-items:center;gap:5px;font-size:11px;color:var(--muted);margin:6px 12px 0 0"><i style="width:9px;height:9px;border-radius:3px;background:${s.color};display:inline-block"></i>${esc(s.label)} ${esc(s.value)}</span>`).join('');
    return `<div style="font-size:11px;color:var(--muted);margin-bottom:6px">조회된 ${items.length}개 경로 내 사용자 집계 비중 · 중복 사용자 포함</div><div style="display:flex;width:100%;height:9px;border-radius:999px;overflow:hidden;background:var(--line);gap:2px">${bars}</div><div style="display:flex;flex-wrap:wrap">${legend}</div>`;
  }
  // Adds a chart container as the last child of a metric's own .card,
  // reusing whatever card markup the page already has instead of assuming
  // new hooks exist in the stored HTML template. Real DOM only (the unit
  // test's minimal fake nodes have no closest/insertAdjacentHTML, so this
  // silently no-ops there rather than throwing).
  function ensureSlot(anchorId, slotId, buildSection) {
    const anchor = $(anchorId);
    if (!anchor || typeof anchor.closest !== 'function') return null;
    let slot = typeof document.getElementById === 'function' ? document.getElementById(slotId) : null;
    if (slot) return slot;
    const card = anchor.closest('.card');
    if (!card || typeof card.insertAdjacentHTML !== 'function') return null;
    card.insertAdjacentHTML('beforeend', buildSection(slotId));
    return document.getElementById(slotId);
  }
  // New trend cards (제휴 클릭/검색 노출/검색 클릭) have no pre-existing
  // container in the stored template, so they're inserted once next to the
  // metrics grid — the one section every version of this template has had.
  function ensureMiniTrends() {
    if ($('miniTrends')) return $('miniTrends');
    if (typeof document.querySelector !== 'function') return null;
    const metricsSection = document.querySelector('section.grid.metrics, .metrics');
    if (!metricsSection || typeof metricsSection.insertAdjacentHTML !== 'function') return null;
    metricsSection.insertAdjacentHTML('afterend', `<section class="section grid three" id="miniTrends">
      <div class="card"><div class="section-title"><h2>제휴 클릭 추이</h2><span id="miniAffiliateRange"></span></div><div id="miniAffiliateChart"></div></div>
      <div class="card"><div class="section-title"><h2>검색 노출 추이</h2><span id="miniImpressionsRange"></span></div><div id="miniImpressionsChart"></div></div>
      <div class="card"><div class="section-title"><h2>검색 클릭 추이</h2><span id="miniClicksRange"></span></div><div id="miniClicksChart"></div></div>
    </section>`);
    return document.getElementById('miniTrends');
  }
  function pageLabel(value) {
    const label = esc(value);
    try {
      const path = String(value || '').trim();
      if (!path.startsWith('/') && !path.startsWith('https://')) return label;
      const url = new URL(path, 'https://coshuma.com');
      if (url.origin !== 'https://coshuma.com' || url.username || url.password) return label;
      return `<a href="${esc(url.href)}" rel="noopener noreferrer" style="color:inherit;text-decoration:underline;text-underline-offset:3px" title="해당 페이지 열기">${label}</a>`;
    } catch { return label; }
  }
  function list(id, items, label = 'name', value = 'value', suffix = '') {
    const search = String($(`filter-${id}`)?.value || '').toLowerCase();
    const sort = $(`sort-${id}`)?.value || 'desc';
    const filtered = (items || []).filter(x => `${x[label]} ${x.note || ''}`.toLowerCase().includes(search));
    filtered.sort((a,b) => sort === 'name' ? String(a[label]).localeCompare(String(b[label])) : (Number(a[value])-Number(b[value]))*(sort === 'asc' ? 1 : -1));
    // 유입 경로 표에만 있는, 기간 내 일별 방문자 추이 — 상위 5개 채널만 제공된다.
    const trendById = id === 'sources' ? (snapshot?.sources_daily || {}) : null;
    const trendHead = trendById ? '<th>추이</th>' : '';
    const rows = filtered.map(x => {
      const trendCell = trendById ? `<td>${sparkline(calendarRows(trendById[x[label]], 'ga', '30d').map(row=>row.users), 'var(--cyan)') || '<span style="color:var(--muted)">—</span>'}</td>` : '';
      return `<tr><td>${id === 'pages' ? pageLabel(x[label]) : esc(x[label])}${x.note ? `<small>${esc(x.note)}</small>` : ''}</td><td>${esc(x[value])}${suffix}</td>${trendCell}</tr>`;
    }).join('');
    const colspan = trendById ? 3 : 2;
    const composition = id === 'sources' ? compositionBar(items) : '';
    $(id).innerHTML = `${composition}<table class="performance-table"><thead><tr><th>${id === 'pages' ? '페이지' : id === 'queries' ? '검색어' : '채널'}</th><th>${id === 'pages' ? '조회' : id === 'queries' ? '노출' : '방문자'}</th>${trendHead}</tr></thead><tbody>${rows || `<tr><td colspan="${colspan}">${search ? '검색 결과 없음' : connected() ? '조회 기간에 기록 없음' : '데이터 확인 필요'}</td></tr>`}</tbody></table><div class="result-count">수집된 ${items?.length || 0}개 중 ${filtered.length}개 표시</div>`;
  }
  function opportunities() {
    const rows = [];
    const search = String($('actionFilter')?.value || '').toLowerCase();
    const add = (target, signal, action, status, cls = 'warn') => { if (`${target} ${signal} ${action} ${status}`.toLowerCase().includes(search)) rows.push(`<tr><td>${rows.length+1}</td><td>${pageLabel(target)}</td><td>${esc(signal)}</td><td>${esc(action)}</td><td><span class="pill ${cls}">${esc(status)}</span></td></tr>`); };
    if (connected()) {
      for (const page of (snapshot.search_pages || []).slice(0, 3))
        add(page.name, `검색 노출 ${page.value} · ${page.note || ''}`, '검색 노출·클릭률을 함께 보고 제목과 검색 의도 일치 여부 점검', '실데이터 확인', 'ok');
      for (const link of (snapshot.affiliate_links || []).slice(0, 2))
        add(link.name, `제휴 클릭 ${link.value}회 · ${link.date || ''}`, '해당 제휴 포털에서 가입·구매·커미션 발생 여부 확인', '전환 확인 필요');
    } else add('GA4 / Search Console', snapshot ? '실데이터 수집 상태 확인 필요' : '데이터를 불러오는 중', '최근 수집 작업과 인증 상태 확인', '확인 필요');
    if (partner && !partner.connected) add('PartnerStack', partner.reason || 'API 조회 실패', '기존 PartnerStack API 연결 상태 확인', '확인 필요');
    add('/ops/revenue.html', '전체 계정별 수익·지급·확인 시점을 통합 조회', '상단 전체 수익에서 계정별 확인 결과와 보고서 보기', '수익판 연결');
    $('opportunities').innerHTML = rows.join('') || '<tr><td colspan="5">검색 조건에 맞는 액션 없음</td></tr>';
  }
  function render() {
    const m = snapshot?.metrics || {}, r = snapshot?.ranges?.[range] || {};
    const users = number(r.users), sessions = number(r.sessions), views = number(r.views), clicks = number(r.affiliate_clicks), revenue = number(r.verified_revenue);
    show('users', users); show('sessions', sessions); show('views', views); show('clicks', clicks);
    const period = ({ today: '오늘', '7d': '최근 7일', '30d': '최근 30일', '90d': '최근 90일' })[range];
    for (const id of ['usersNote','sessionsNote','viewsNote']) show(id, connected() ? `${period} · GA4 실측` : 'GA4 데이터 확인 중');
    for(const id of ['usersNote','sessionsNote','viewsNote']) $(id).title=`${windowLabel('ga')} · ${snapshot?.timezones?.ga || ''} · 오늘 집계 중`;
    show('clicksNote', !connected() ? 'GA4 데이터 확인 중' : clicks === null ? `${period} 집계 미제공` : `${period} · affiliate_click 실측`);
    show('affiliateCtr', users > 0 && clicks !== null ? `${(clicks/users*100).toFixed(1)}%` : null);
    $('revenue').textContent = money(revenue, m.verified_revenue_currency || 'USD');
    $('revenueNote').textContent = revenue === null ? '전체 네트워크 통합 미완료 · 0원 아님' : `${period} · 검증된 수익`;
    show('impressions', r.search_impressions); show('searchClicks', r.search_clicks); show('funnelUsers', users); show('funnelClicks', clicks);
    $('funnelRevenue').textContent = money(revenue, m.verified_revenue_currency || 'USD');
    const values = [number(r.search_impressions), number(r.search_clicks), users, clicks, revenue];
    const max = Math.max(1, ...values.filter(v => v !== null));
    ['barImpressions','barSearchClicks','barUsers','barAffiliate','barRevenue'].forEach((id, i) => $(id).style.width = values[i] === null || values[i] === 0 ? '0%' : `${Math.min(100, values[i]/max*100)}%`);
    for(const id of ['impressions','searchClicks']) $(id).title=`${windowLabel('search')} · America/Los_Angeles · 확정치, 최신일 지연 가능`;
    list('sources', snapshot?.top_sources); list('pages', snapshot?.top_pages); list('queries', snapshot?.top_queries, 'name', 'value', ' 노출');
    const gaRows=calendarRows(snapshot?.daily);
    const affiliateRows=calendarRows(snapshot?.affiliate_daily);
    const searchRows=calendarRows(snapshot?.search_daily,'search');
    const trendColors = { users: 'var(--cyan)', sessions: 'var(--purple)', views: 'var(--green)', clicks: 'var(--amber)' };
    const trendSeries = {
      users: gaRows.map(d => d.users),
      sessions: gaRows.map(d => d.sessions),
      views: gaRows.map(d => d.views),
      clicks: affiliateRows.map(d => d.clicks),
    };
    for (const metricId of ['users', 'sessions', 'views', 'clicks']) {
      const slot = ensureSlot(metricId, `spark-${metricId}`, (slotId) => `<div class="spark-wrap" id="${slotId}" style="margin-top:8px"></div>`);
      if (slot) { slot.innerHTML = sparkline(trendSeries[metricId], trendColors[metricId]); slot.title=windowLabel('ga'); }
    }
    // 제휴 클릭/검색 노출/검색 클릭은 서로 스케일 차이가 커서 (수백 대 수십)
    // 하나의 축에 같이 그리면 작은 값이 눌려 보이므로, 각자 자기 스케일로
    // 그리는 작은 그래프 3개로 분리한다.
    const miniTrends = ensureMiniTrends();
    if (miniTrends) {
      $('miniAffiliateChart').innerHTML = chart(affiliateRows,'clicks','var(--amber)');
      $('miniImpressionsChart').innerHTML = chart(searchRows,'impressions','var(--purple)');
      $('miniClicksChart').innerHTML = chart(searchRows,'clicks','var(--cyan)');
      show('miniAffiliateRange', `${period} · 오늘 집계 중`);
      show('miniImpressionsRange', `${windowLabel('search')} · 확정치`);
      show('miniClicksRange', `${windowLabel('search')} · 확정치`);
      $('miniAffiliateRange').title=`${windowLabel('ga')} · ${snapshot?.timezones?.ga || ''}`;
      for(const id of ['miniImpressionsRange','miniClicksRange']) $(id).title='America/Los_Angeles · 최신 날짜 집계 지연 가능 · 빈 구간은 미확정';

    }
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
  for (const id of ['sources','pages','queries']) { if ($(`filter-${id}`)) $(`filter-${id}`).oninput = render; if ($(`sort-${id}`)) $(`sort-${id}`).onchange = render; }
  if ($('actionFilter')) $('actionFilter').oninput = opportunities;
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
  html = agencyLayout(html);
  html = html.replace('</header>', '<a class="btn" href="/ops/revenue.html">전체 수익 확인 →</a></header>');
  const pattern = /<script>\s*\(\(\)\s*=>\s*\{[\s\S]*?<\/script>/;
  if (!pattern.test(html)) throw new Error('Dashboard script marker not found');
  // Wrangler preserves function names with __name calls inside serialized functions.
  // Supply the identity helper in the browser scope rather than leaking a Worker-only dependency.
  return html.replace(pattern, () => `<script>(()=>{const __name=fn=>fn;(${dashboardClient.toString()})();})();</script>`)
    .replace(/<tbody id="opportunities">[\s\S]*?<\/tbody>/, '<tbody id="opportunities"><tr><td colspan="5">실데이터 확인 중</td></tr></tbody>');
}
