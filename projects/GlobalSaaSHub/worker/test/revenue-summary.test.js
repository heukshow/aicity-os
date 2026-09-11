import test from 'node:test';
import assert from 'node:assert/strict';
import { summarizeRevenue, getRevenueSummary } from '../src/revenue-summary.js';
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
