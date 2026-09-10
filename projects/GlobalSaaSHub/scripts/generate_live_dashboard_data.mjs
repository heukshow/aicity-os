import { RANGE_LENGTHS, dateInZone, shiftDate, windowEnding, dateSeries } from './dashboard-series.mjs';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

import path from 'node:path';
const outPath = process.env.DASHBOARD_OUTPUT_PATH;
if (!outPath || !path.isAbsolute(outPath)) throw new Error('An absolute private DASHBOARD_OUTPUT_PATH is required');
const publicRoot = path.resolve(fileURLToPath(new URL('../public', import.meta.url)));
if (path.resolve(outPath).startsWith(publicRoot + path.sep)) throw new Error('Public output is forbidden');
const serviceRaw = process.env.GOOGLE_SERVICE_ACCOUNT_JSON || '';
const propertyId = String(process.env.GA_PROPERTY_ID || '552119661').trim();
const siteUrl = String(process.env.GSC_SITE_URL || 'https://coshuma.com/').trim();

const empty = (status, reason) => ({
  generated_at: new Date().toISOString(),
  status,
  connections: {
    ga4: reason,
    search_console: reason,
    partner_revenue: '네트워크별 연결 필요'
  },
  metrics: {
    today_users: null,
    today_users_note: reason,
    sessions_7d: null,
    sessions_7d_note: reason,
    affiliate_clicks_30d: null,
    affiliate_clicks_30d_note: reason,
    verified_revenue: null,
    verified_revenue_currency: 'USD',
    verified_revenue_note: '검증된 파트너/PayPal 수익 통합 미연결'
  },
  ranges: Object.fromEntries(['today','7d','30d','90d'].map(k => [k, { users:null, sessions:null, views:null, affiliate_clicks:null, search_impressions:null, search_clicks:null, verified_revenue:null }])),
  top_sources: [], top_pages: [], top_queries: [], affiliate_pages: [], affiliate_links: [], search_pages: [],
  daily: [], affiliate_daily: [], search_daily: [], sources_daily: {},
  snapshot: [
    { label:'GA4 Property ID', value:propertyId || '미설정', period:'현재 실행', source:'GitHub Actions env / fallback' },
    { label:'Search Console site', value:siteUrl || '미설정', period:'현재 실행', source:'GitHub Actions env / fallback' },
    { label:'실데이터 생성', value:status, period:'현재 실행', source:reason }
  ]
});

function write(data) {
  fs.writeFileSync(outPath, JSON.stringify(data, null, 2) + '\n');
  console.log(`dashboard snapshot written: ${data.status}`);
}

if (!serviceRaw.trim()) {
  write(empty('credential_missing', 'GitHub Actions에 GOOGLE_SERVICE_ACCOUNT_JSON secret이 없음'));
  process.exit(0);
}

let account;
try { account = JSON.parse(serviceRaw); }
catch { write(empty('credential_invalid', 'GOOGLE_SERVICE_ACCOUNT_JSON JSON 파싱 실패')); process.exit(0); }
if (!account.client_email || !account.private_key) {
  write(empty('credential_invalid', '서비스 계정 client_email/private_key 누락'));
  process.exit(0);
}

const b64url = (v) => Buffer.from(v).toString('base64url');
async function token() {
  const now = Math.floor(Date.now()/1000);
  const header = b64url(JSON.stringify({ alg:'RS256', typ:'JWT' }));
  const claim = b64url(JSON.stringify({
    iss: account.client_email,
    scope: 'https://www.googleapis.com/auth/analytics.readonly https://www.googleapis.com/auth/webmasters.readonly',
    aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now+3600
  }));
  const unsigned = `${header}.${claim}`;
  const sign = crypto.createSign('RSA-SHA256'); sign.update(unsigned); sign.end();
  const assertion = `${unsigned}.${sign.sign(account.private_key).toString('base64url')}`;
  const r = await fetch('https://oauth2.googleapis.com/token', { method:'POST', headers:{'content-type':'application/x-www-form-urlencoded'}, body:new URLSearchParams({grant_type:'urn:ietf:params:oauth:grant-type:jwt-bearer', assertion}) });
  if (!r.ok) throw new Error(`Google token ${r.status}`);
  return (await r.json()).access_token;
}
async function post(url, access, body) {
  const r = await fetch(url, {method:'POST', headers:{authorization:`Bearer ${access}`,'content-type':'application/json'}, body:JSON.stringify(body)});
  if (!r.ok) throw new Error(`${url} -> ${r.status}: ${(await r.text()).slice(0,200)}`);
  return r.json();
}
const metric = (row, i=0) => Number(row?.metricValues?.[i]?.value || 0);
const dim = (row, i=0) => row?.dimensionValues?.[i]?.value || '알 수 없음';
const gaDate = value => `${value.slice(0,4)}-${value.slice(4,6)}-${value.slice(6,8)}`;
try {
  const access = await token();
  const ga = `https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}`;
  const gsc = `https://searchconsole.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/searchAnalytics/query`;
  const metadata = await post(`${ga}:runReport`,access,{dateRanges:[{startDate:'today',endDate:'today'}],metrics:[{name:'activeUsers'}]});
  const gaZone = metadata.metadata?.timeZone;
  if (!gaZone) throw new Error('GA reporting timezone unavailable');
  const collected = new Date();
  const gaToday = dateInZone(collected, gaZone);
  const searchEnd = shiftDate(dateInZone(collected,'America/Los_Angeles'),-1);
  const windows = Object.fromEntries(Object.entries(RANGE_LENGTHS).map(([key,days])=>[key,{ga:windowEnding(gaToday,days),search:windowEnding(searchEnd,days)}]));
  const gaWindow = windows['90d'].ga, sourceWindow = windows['30d'].ga, searchWindow = windows['90d'].search;
  const dates = window => [{startDate:window.start,endDate:window.end}];
  const affiliateFilter = {filter:{fieldName:'eventName',stringFilter:{matchType:'EXACT',value:'affiliate_click'}}};
  const gaRequest = (window, metrics, extra={}) => ({dateRanges:dates(window),metrics:metrics.map(name=>({name})),...extra});
  const searchRequest = (window, extra={}) => ({startDate:window.start,endDate:window.end,dataState:'final',...extra});
  const statuses = {};
  const optional = async (name, request) => {
    try {
      const value = await request();
      if(value.metadata?.dataLossFromOtherRow || (value.rowCount && value.rowCount > (value.rows?.length || 0))) throw new Error('Incomplete series');
      statuses[name]='ok'; return value;
    } catch { statuses[name]='unavailable'; return null; }
  };
  const keys=Object.keys(RANGE_LENGTHS);
  const [kpis,affTotals,sources,pages,affPages,affLinks,gscTotalsByRange,gscQueries,gscPages,gaDaily,gaAffiliateDaily,gscDaily] = await Promise.all([
    post(`${ga}:batchRunReports`,access,{requests:keys.map(key=>gaRequest(windows[key].ga,['activeUsers','sessions','screenPageViews']))}),
    post(`${ga}:batchRunReports`,access,{requests:keys.map(key=>gaRequest(windows[key].ga,['eventCount'],{dimensionFilter:affiliateFilter}))}),
    post(`${ga}:runReport`,access,gaRequest(sourceWindow,['activeUsers','sessions'],{dimensions:[{name:'sessionSource'}],orderBys:[{metric:{metricName:'activeUsers'},desc:true}],limit:15})),
    post(`${ga}:runReport`,access,gaRequest(sourceWindow,['screenPageViews','activeUsers'],{dimensions:[{name:'pagePath'}],orderBys:[{metric:{metricName:'screenPageViews'},desc:true}],limit:20})),
    post(`${ga}:runReport`,access,gaRequest(sourceWindow,['eventCount'],{dimensionFilter:affiliateFilter,dimensions:[{name:'pagePath'}],orderBys:[{metric:{metricName:'eventCount'},desc:true}],limit:20})),
    post(`${ga}:runReport`,access,gaRequest(sourceWindow,['eventCount'],{dimensionFilter:affiliateFilter,dimensions:['pagePath','linkUrl','linkText','date'].map(name=>({name})),orderBys:[{metric:{metricName:'eventCount'},desc:true}],limit:30})),
    Promise.all(keys.map(key=>post(gsc,access,searchRequest(windows[key].search,{rowLimit:1})))),
    post(gsc,access,searchRequest(searchWindow,{dimensions:['query'],rowLimit:250})),
    post(gsc,access,searchRequest(searchWindow,{dimensions:['page'],rowLimit:250})),
    optional('daily',()=>post(`${ga}:runReport`,access,gaRequest(gaWindow,['activeUsers','sessions','screenPageViews'],{dimensions:[{name:'date'}],keepEmptyRows:true,orderBys:[{dimension:{dimensionName:'date'}}]}))),
    optional('affiliate_daily',()=>post(`${ga}:runReport`,access,gaRequest(gaWindow,['eventCount'],{dimensionFilter:affiliateFilter,dimensions:[{name:'date'}],keepEmptyRows:true,orderBys:[{dimension:{dimensionName:'date'}}]}))),
    optional('search_daily',()=>post(gsc,access,searchRequest(searchWindow,{dimensions:['date'],rowLimit:100})))
  ]);
  const sourceNames=(sources.rows||[]).slice(0,5).map(row=>dim(row));
  const sourceDaily=sourceNames.length ? await optional('sources_daily',()=>post(`${ga}:runReport`,access,gaRequest(sourceWindow,['activeUsers'],{dimensions:[{name:'date'},{name:'sessionSource'}],dimensionFilter:{filter:{fieldName:'sessionSource',inListFilter:{values:sourceNames}}},keepEmptyRows:true,limit:1000,orderBys:[{dimension:{dimensionName:'date'}}]}))) : {rows:[]};
  statuses.sources_daily ||= 'ok';
  const daily = gaDaily ? dateSeries((gaDaily.rows||[]).map(row=>({date:gaDate(dim(row)),users:metric(row,0),sessions:metric(row,1),views:metric(row,2)})),gaWindow,['users','sessions','views']) : [];
  const affiliate_daily = gaAffiliateDaily ? dateSeries((gaAffiliateDaily.rows||[]).map(row=>({date:gaDate(dim(row)),clicks:metric(row)})),gaWindow,['clicks']) : [];
  const searchRows=(gscDaily?.rows||[]).map(row=>({date:row.keys[0],impressions:Math.round(row.impressions||0),clicks:Math.round(row.clicks||0)}));
  // Missing trailing search dates may still be unprocessed. Never invent zeros for them.
  const confirmedSearchDate=searchRows.map(row=>row.date).sort().at(-1)||'';
  const search_daily=gscDaily ? dateSeries(searchRows,searchWindow,['impressions','clicks'],confirmedSearchDate) : [];
  const sources_daily=sourceDaily ? Object.fromEntries(sourceNames.map(name=>[name,dateSeries((sourceDaily.rows||[]).filter(row=>dim(row,1)===name).map(row=>({date:gaDate(dim(row)),users:metric(row)})),sourceWindow,['users'])])) : {};
  const ranges=Object.fromEntries(keys.map((key,i)=>{
    const row=kpis.reports?.[i]?.rows?.[0], search=gscTotalsByRange[i].rows?.[0];
    if(!kpis.reports?.[i] || !affTotals.reports?.[i]) throw new Error('Missing aggregate report');
    return [key,{users:metric(row,0),sessions:metric(row,1),views:metric(row,2),affiliate_clicks:metric(affTotals.reports[i].rows?.[0]),search_impressions:search ? Math.round(search.impressions||0) : null,search_clicks:search ? Math.round(search.clicks||0) : null,verified_revenue:null}];
  }));
  const series_checks={};
  for(const key of keys) {
    const w=windows[key].ga;
    const selected=rows=>rows.filter(row=>row.date>=w.start && row.date<=w.end);
    series_checks[key]={};
    for(const [field,rows,metricKey] of [['views',daily,'views'],['affiliate_clicks',affiliate_daily,'clicks']])
      series_checks[key][field]=rows.length ? selected(rows).reduce((sum,row)=>sum+row[metricKey],0)===ranges[key][field] : null;
    // Sessions and active users are not summed across dates: they can cross midnight or repeat.
  }
  const records=[
    {label:'GA4 Property ID',value:propertyId,period:gaZone,source:'Google Analytics Data API'},
    {label:'GA4 집계 기간',value:`${gaWindow.start} ~ ${gaWindow.end}`,period:'오늘 포함 · 오늘은 집계 중',source:gaZone},
    {label:'Search Console site',value:siteUrl,period:`${searchWindow.start} ~ ${searchWindow.end}`,source:'America/Los_Angeles · 확정 데이터 · 최신일 지연 가능'},
    {label:'검색 최신 기록일',value:confirmedSearchDate||'확정 기록 미제공',period:'검색 추이',source:'최신 누락 날짜는 0으로 표시하지 않음'},
    {label:'유입 구성비',value:`조회된 ${sources.rows?.length||0}개 경로 내 사용자 집계 비중`,period:`${sourceWindow.start} ~ ${sourceWindow.end}`,source:'전체 순방문자 구성비 아님 · 기타는 조회 목록의 나머지'},
    ...Object.entries(statuses).map(([name,status])=>({label:`추이 ${name}`,value:status==='ok'?'연결됨':'조회 실패 또는 불완전 응답',period:'이번 수집',source:'기존 KPI와 별도 처리'}))
  ];
  const data={
    generated_at:collected.toISOString(),status:'live_google_connected',measurement_status:'live_connected',
    connections:{ga4:`연결됨 · property ${propertyId}`,search_console:`연결됨 · ${siteUrl}`,partner_revenue:'네트워크별 연결 필요'},
    metrics:{today_users:ranges.today.users,today_users_note:`GA4 property ${propertyId}`,sessions_7d:ranges['7d'].sessions,sessions_7d_note:'GA4 Data API 실집계',affiliate_clicks_30d:ranges['30d'].affiliate_clicks,affiliate_clicks_30d_note:'GA4 affiliate_click 실집계',verified_revenue:null,verified_revenue_currency:'USD',verified_revenue_note:'파트너별 실제 수익 통합 미연결'},
    ranges,windows,timezones:{ga:gaZone,search:'America/Los_Angeles'},daily,affiliate_daily,search_daily,sources_daily,series_status:statuses,series_checks,
    top_sources:(sources.rows||[]).map(row=>({name:dim(row),value:metric(row),note:`세션 ${metric(row,1)}`})),
    top_pages:(pages.rows||[]).map(row=>({name:dim(row),value:metric(row),note:`사용자 ${metric(row,1)}`})),
    affiliate_pages:(affPages.rows||[]).map(row=>({name:dim(row),value:metric(row),note:'제휴 클릭'})),
    affiliate_links:(affLinks.rows||[]).map(row=>({page:dim(row),name:dim(row,1),value:metric(row),date:dim(row,3),note:`페이지 ${dim(row)} · 날짜 ${dim(row,3)} · 링크 텍스트: ${dim(row,2)}`})),
    top_queries:(gscQueries.rows||[]).sort((a,b)=>(b.impressions||0)-(a.impressions||0)).slice(0,20).map(row=>({name:row.keys?.[0]||'알 수 없음',value:Math.round(row.impressions||0),note:`클릭 ${Math.round(row.clicks||0)} · CTR ${(Number(row.ctr||0)*100).toFixed(1)}% · 순위 ${Number(row.position||0).toFixed(1)}`})),
    search_pages:(gscPages.rows||[]).sort((a,b)=>(b.impressions||0)-(a.impressions||0)).slice(0,20).map(row=>({name:row.keys?.[0]||'알 수 없음',value:Math.round(row.impressions||0),note:`클릭 ${Math.round(row.clicks||0)} · CTR ${(Number(row.ctr||0)*100).toFixed(1)}%`})),
    snapshot:records
  };
  write(data);
} catch {
  console.error('Google analytics collection failed; prior private snapshot is preserved.');
  write(empty('google_api_error','Google API 연결 실패'));
}
