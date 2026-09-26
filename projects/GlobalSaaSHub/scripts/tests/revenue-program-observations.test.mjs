import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { programObservations, mergeProgramObservations } from '../revenue-program-observations.mjs';
const tools = [{id:'castmagic',name:'Castmagic'},{id:'teachable',name:'Teachable'}];
const evidence = { tool: 'Castmagic', checked_at: '2026-09-23T18:32:38Z', source: 'vendor-system-email', evidence_id: 'gmail:1a0cf8a8b7c21b67', metrics: { network_reported_unpaid_balance: 0, commission_earned: null, payout_paid: null } };
test('a program balance stays a balance; no currency, commission or period is invented', () => {
  const [row] = programObservations({accounts:[{evidence:[evidence]}]},tools);
  assert.equal(row.metrics.network_reported_unpaid_balance,0);
  assert.equal(row.metrics.commission_earned,null);
  assert.equal(row.currency,null);
  assert.equal(row.period,null);
});
test('account totals and failed or undated authentication attempts cannot become program truth', () => {
  assert.deepEqual(programObservations({accounts:[{account_id:'teachable',metrics:{commission_earned:0},evidence:[
    {...evidence,tool:'PartnerStack'}, {...evidence,checked_at:null}, {...evidence,metrics:{commission_earned:null}},
  ]}]},tools),[]);
});
test('current committed Castmagic evidence is consumed with other funnel stages still unknown', () => {
  const observations = JSON.parse(fs.readFileSync(new URL('../../worker/src/revenue-observations.json',import.meta.url)));
  const rows = programObservations(observations,tools);
  const castmagic = rows.find(x=>x.evidence_id==='gmail:1a0cf8a8b7c21b67');
  assert.equal(castmagic.metrics.network_reported_unpaid_balance,0);
  assert.equal(castmagic.metrics.paid_customers,null);
  assert.ok(!rows.some(x=>x.tool==='PartnerStack'));
});
test('same-evidence enrichment retains a balance without duplicating observations or joining periods', () => {
  const [row] = programObservations({accounts:[{evidence:[evidence]}]}, tools);
  const old = {...row,metrics:{commission_earned:null}};
  const merged = mergeProgramObservations([old],[row]);
  assert.equal(merged.length,1);
  assert.equal(merged[0].metrics.network_reported_unpaid_balance,0);
  assert.equal(merged[0].metrics.commission_earned,null);
  assert.equal(mergeProgramObservations([old],[{...row,checked_at:'2026-09-24T00:00:00Z'}]).length,2);
  const separate = mergeProgramObservations([{...old,period:'previous month'}],[{...row,period:'current balance'}]);
  assert.equal(separate.length,2);
  assert.equal(separate[0].period,'current balance');
  assert.throws(()=>mergeProgramObservations([{...row,metrics:{network_reported_unpaid_balance:5}}],[row]),/Conflicting/);
});
