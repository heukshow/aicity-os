import fs from 'node:fs';
import crypto from 'node:crypto';

const outPath = new URL('../public/ops/traffic-revenue-data.json', import.meta.url);
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
const iso = d => d.toISOString().slice(0,10);
const ago = n => iso(new Date(Date.now()-n*86400000));
const yesterday = ago(1);

try {
  const access = await token();
  const ga = `https://analyticsdata.googleapis.com/v1beta/properties/${propertyId}`;
  const gsc = `https://searchconsole.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/searchAnalytics/query`;
  const rangeReq = start => ({dateRanges:[{startDate:start,endDate:'today'}],metrics:[{name:'activeUsers'},{name:'sessions'},{name:'screenPageViews'}]});
  const affiliateEventFilter = {filter:{fieldName:'eventName',stringFilter:{matchType:'EXACT',value:'affiliate_click'}}};
  const [kpis,sources,pages,aff30,affPages,affLinks,gsc90,gscQueries,gscPages,gsc30,gsc7,gscToday] = await Promise.all([
    post(`${ga}:batchRunReports`,access,{requests:[rangeReq('today'),rangeReq('7daysAgo'),rangeReq('30daysAgo'),rangeReq('90daysAgo')]}),
    post(`${ga}:runReport`,access,{dateRanges:[{startDate:'30daysAgo',endDate:'today'}],dimensions:[{name:'sessionSource'}],metrics:[{name:'activeUsers'},{name:'sessions'}],orderBys:[{metric:{metricName:'activeUsers'},desc:true}],limit:15}),
    post(`${ga}:runReport`,access,{dateRanges:[{startDate:'30daysAgo',endDate:'today'}],dimensions:[{name:'pagePath'}],metrics:[{name:'screenPageViews'},{name:'activeUsers'}],orderBys:[{metric:{metricName:'screenPageViews'},desc:true}],limit:20}),
    post(`${ga}:runReport`,access,{dateRanges:[{startDate:'30daysAgo',endDate:'today'}],dimensions:[{name:'eventName'}],metrics:[{name:'eventCount'}],dimensionFilter:affiliateEventFilter}),
    post(`${ga}:runReport`,access,{dateRanges:[{startDate:'30daysAgo',endDate:'today'}],dimensions:[{name:'pagePath'}],metrics:[{name:'eventCount'}],dimensionFilter:affiliateEventFilter,orderBys:[{metric:{metricName:'eventCount'},desc:true}],limit:20}),
    post(`${ga}:runReport`,access,{dateRanges:[{startDate:'30daysAgo',endDate:'today'}],dimensions:[{name:'linkUrl'},{name:'linkText'}],metrics:[{name:'eventCount'}],dimensionFilter:affiliateEventFilter,orderBys:[{metric:{metricName:'eventCount'},desc:true}],limit:50}),
    post(gsc,access,{startDate:ago(89),endDate:yesterday,rowLimit:1}),
    post(gsc,access,{startDate:ago(89),endDate:yesterday,dimensions:['query'],rowLimit:250}),
    post(gsc,access,{startDate:ago(89),endDate:yesterday,dimensions:['page'],rowLimit:250}),
    post(gsc,access,{startDate:ago(29),endDate:yesterday,rowLimit:1}),
    post(gsc,access,{startDate:ago(6),endDate:yesterday,rowLimit:1}),
    post(gsc,access,{startDate:yesterday,endDate:yesterday,rowLimit:1})
  ]);
  const reports = kpis.reports || [];
  const gr = i => ({users:metric(reports[i]?.rows?.[0],0),sessions:metric(reports[i]?.rows?.[0],1),views:metric(reports[i]?.rows?.[0],2)});
  const gscTotals = x => ({search_impressions:Math.round(x.rows?.[0]?.impressions||0),search_clicks:Math.round(x.rows?.[0]?.clicks||0)});
  const click30 = metric(aff30.rows?.[0],0);
  const rToday = {...gr(0),affiliate_clicks:null,...gscTotals(gscToday),verified_revenue:null};
  const r7 = {...gr(1),affiliate_clicks:null,...gscTotals(gsc7),verified_revenue:null};
  const r30 = {...gr(2),affiliate_clicks:click30,...gscTotals(gsc30),verified_revenue:null};
  const r90 = {...gr(3),affiliate_clicks:null,...gscTotals(gsc90),verified_revenue:null};
  const data = {
    generated_at:new Date().toISOString(), status:'live_google_connected',
    connections:{ga4:`연결됨 · property ${propertyId}`,search_console:`연결됨 · ${siteUrl}`,partner_revenue:'네트워크별 연결 필요'},
    metrics:{today_users:rToday.users,today_users_note:`GA4 property ${propertyId}`,sessions_7d:r7.sessions,sessions_7d_note:'GA4 Data API 실집계',affiliate_clicks_30d:click30,affiliate_clicks_30d_note:'GA4 affiliate_click 30일 실집계',verified_revenue:null,verified_revenue_currency:'USD',verified_revenue_note:'파트너별 실제 수익 통합 미연결'},
    ranges:{today:rToday,'7d':r7,'30d':r30,'90d':r90},
    top_sources:(sources.rows||[]).map(x=>({name:dim(x),value:metric(x,0),note:`세션 ${metric(x,1)}`})),
    top_pages:(pages.rows||[]).map(x=>({name:dim(x),value:metric(x,0),note:`사용자 ${metric(x,1)}`})),
    affiliate_pages:(affPages.rows||[]).map(x=>({name:dim(x),value:metric(x,0),note:'제휴 클릭'})),
    affiliate_links:(affLinks.rows||[]).map(x=>({name:dim(x,0),value:metric(x,0),note:`링크 텍스트: ${dim(x,1)}`})),
    top_queries:(gscQueries.rows||[]).sort((a,b)=>(b.impressions||0)-(a.impressions||0)).slice(0,20).map(x=>({name:x.keys?.[0]||'알 수 없음',value:Math.round(x.impressions||0),note:`클릭 ${Math.round(x.clicks||0)} · CTR ${(Number(x.ctr||0)*100).toFixed(1)}% · 순위 ${Number(x.position||0).toFixed(1)}`})),
    search_pages:(gscPages.rows||[]).sort((a,b)=>(b.impressions||0)-(a.impressions||0)).slice(0,20).map(x=>({name:x.keys?.[0]||'알 수 없음',value:Math.round(x.impressions||0),note:`클릭 ${Math.round(x.clicks||0)} · CTR ${(Number(x.ctr||0)*100).toFixed(1)}%`})),
    snapshot:[
      {label:'GA4 Property ID',value:propertyId,period:'현재 실행',source:'Google Analytics Data API'},
      {label:'Search Console site',value:siteUrl,period:`${ago(89)} ~ ${yesterday}`,source:'Search Console API'},
      {label:'30일 제휴 클릭',value:String(click30),period:'최근 30일',source:'GA4 affiliate_click'},
      {label:'제휴 목적지 분석',value:String((affLinks.rows||[]).length),period:'최근 30일',source:'GA4 linkUrl/linkText'},
      {label:'데이터 생성 방식',value:'GitHub Actions 서버측 실집계',period:'현재',source:'scripts/generate_live_dashboard_data.mjs'}
    ]
  };
  write(data);
} catch (e) {
  console.error(e);
  write(empty('google_api_error', `Google API 연결 실패: ${String(e.message||e).slice(0,180)}`));
}
