import test from 'node:test';
import assert from 'node:assert/strict';
import { summarizeRevenue, getRevenueSummary } from '../src/revenue-summary.js';
import { fetchGoogleMetrics } from '../src/google-analytics.js';
import { revenuePage } from '../src/revenue-view.js';
const now='2026-09-11T03:00:00Z';
const programs=[{id:'one',name:'One',account_id:'ps',network:'PartnerStack'},{id:'two',name:'Two',account_id:'ps',network:'PartnerStack'},{id:'three',name:'Three',account_id:'native',network:'Native'}];
const live={account_id:'ps',connection:'connected',complete:true,checked_at:now,period:'lifetime',currency:'USD',metrics:{commission_earned:20,available:0}};
test('shared accounts count once; unknown and reward-paid do not become payouts',()=>{
  const s=summarizeRevenue(programs,[live],now);
  assert.equal(s.account_count,2);assert.equal(s.program_count,3);
  assert.deepEqual(s.totals.commission_earned.by_currency,{USD:20});
  assert.equal(s.totals.commission_earned.complete,false);
  assert.deepEqual(s.totals.available.by_currency,{USD:0});
  assert.deepEqual(s.totals.payout_paid.by_currency,{});
});
test('stale, future, partial and incompatible-window records never enter cumulative totals',()=>{
  for(const patch of [{checked_at:'2026-09-08T00:00:00Z'},{checked_at:'2026-09-12T00:00:00Z'},{complete:false},{period:'last_30_days'},{metrics:{commission_earned:null}},{metrics:{commission_earned:'0'}}]){
    const s=summarizeRevenue(programs,[{...live,...patch}],now);
    assert.deepEqual(s.totals.commission_earned.by_currency,{});
  }
});
test('currencies are never combined and all-account coverage is metric specific',()=>{
  const s=summarizeRevenue(programs,[live,{...live,account_id:'native',currency:'EUR',metrics:{commission_earned:5}}],now);
  assert.deepEqual(s.totals.commission_earned.by_currency,{USD:20,EUR:5});
  assert.equal(s.totals.commission_earned.complete,true);assert.equal(s.totals.available.complete,false);
});
test('API failures remain isolated from the direct-sales aggregate',async()=>{
  let sql='';
  const s=await getRevenueSummary({ORDERS:{prepare(q){sql=q;return {all:async()=>({success:true,results:[]})};}}});
  assert.match(sql,/GROUP BY currency/);assert.doesNotMatch(sql,/SELECT \*/);
  assert.equal(s.direct_sales.connection,'connected');assert.equal(s.direct_sales.empty,true);
  assert.equal(s.accounts.find(a=>a.account_id==='partnerstack-account').connection,'error');
});
test('overlapping snapshots and account totals remain separate instead of becoming historical revenue',()=>{
  const evidence=[
    {tool:'One',evidence_id:'daily',checked_at:now,period:'last_7_days',metrics:{outbound_clicks:5,signups_referrals:0}},
    {tool:'One',evidence_id:'monthly',checked_at:now,period:'last_30_days',metrics:{outbound_clicks:12}},
    {tool:'Account',evidence_id:'account',checked_at:null,period:'last_90_days',metrics:{outbound_clicks:30}},
  ];
  const s=summarizeRevenue([{...programs[0],evidence}], [{...live,evidence:[evidence[0]]}], now);
  assert.equal(s.historical.outbound_clicks.value,null);
  assert.equal(s.historical.outbound_clicks.status,'not_aggregated');
  assert.equal(s.historical.outbound_clicks.observed_records,3);
  assert.deepEqual(s.historical.outbound_clicks.records.map(r=>r.value),[5,12,30]);
  assert.equal(s.historical.signups_referrals.records[0].value,0);
  assert.equal(s.historical.trials.value,null);
  assert.equal(s.historical.trials.status,'unknown');
  assert.equal(s.historical.outbound_clicks.records[2].status,'unknown');
});
test('historical observations preserve currency and freshness without adding periods',()=>{
  const evidence=[{tool:'One',evidence_id:'old',period:'September',checked_at:'2026-09-01T00:00:00Z',currency:'USD',metrics:{commission_earned:4}},
    {tool:'One',evidence_id:'recent',period:'Lifetime',checked_at:now,currency:'EUR',metrics:{commission_earned:9}}];
  const h=summarizeRevenue([{...programs[0],evidence}],[],now).historical.commission_earned;
  assert.equal(h.value,null);
  assert.deepEqual(h.records.map(r=>[r.value,r.currency,r.status]),[[9,'EUR','current'],[4,'USD','stale']]);
  assert.doesNotMatch(revenuePage(),/과거 검증 합계/);
  assert.match(revenuePage(),/기간과 범위가 달라 합산하지 않습니다/);
});
test('missing analytics property fails before any credential or network access',async()=>{
  await assert.rejects(fetchGoogleMetrics({}),/GA_PROPERTY_ID must be explicitly configured/);
  await assert.rejects(fetchGoogleMetrics({GA_PROPERTY_ID:'unknown'}),/GA_PROPERTY_ID must be explicitly configured/);
});
