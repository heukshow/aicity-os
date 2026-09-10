import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {dateInZone,windowEnding,dateSeries} from '../dashboard-series.mjs';
test('calendar windows respect timezone and fill sparse days without changing window size',()=>{
 assert.equal(dateInZone(new Date('2026-09-10T00:30:00Z'),'America/Los_Angeles'),'2026-09-09');
 assert.deepEqual(windowEnding('2026-09-10',7),{start:'2026-09-04',end:'2026-09-10'});
 const rows=dateSeries([{date:'2026-08-01',users:100},{date:'2026-09-10',users:2}],windowEnding('2026-09-10',30),['users']);
 assert.equal(rows.length,30);assert.equal(rows[0].date,'2026-08-12');assert.equal(rows[0].users,0);assert.equal(rows.at(-1).users,2);
 assert.equal(dateSeries([],windowEnding('2026-09-10',1),['clicks'],'')[0].clicks,null);
});
function collect(extra={}){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'coshuma-fixture-'));const output=path.join(dir,'private.json');
 try{
  const run=spawnSync(process.execPath,['--import',new URL('./fixtures/google-reporting.mjs',import.meta.url).href,fileURLToPath(new URL('../generate_live_dashboard_data.mjs',import.meta.url))],{encoding:'utf8',env:{...process.env,...extra,DASHBOARD_OUTPUT_PATH:output}});
  assert.equal(run.status,0,run.stderr);return JSON.parse(fs.readFileSync(output,'utf8'));
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
}
test('full collector aligns dates, all affiliate totals and source queries; retains GSC trailing uncertainty',()=>{
 const d=collect();assert.equal(d.status,'live_google_connected');
 assert.equal(d.daily.length,90);assert.equal(d.affiliate_daily.length,90);assert.equal(d.sources_daily.google.length,30);
 assert.equal(d.windows['7d'].ga.start,'2026-09-04');assert.equal(d.windows['7d'].search.start,'2026-09-02');assert.equal(d.windows['7d'].search.end,'2026-09-08');
 assert.equal(d.ranges.today.affiliate_clicks,7);assert.equal(d.ranges['7d'].affiliate_clicks,12);assert.equal(d.ranges['30d'].affiliate_clicks,12);assert.equal(d.ranges['90d'].affiliate_clicks,17);
 assert.equal(d.ranges['7d'].users,2); // distinct aggregate, not sum of daily users
 assert.equal(d.search_daily.at(-1).clicks,null);assert.equal(d.search_daily.find(r=>r.date==='2026-09-05').clicks,0);
 assert.ok(Object.values(d.series_checks).every(v=>Object.values(v).every(x=>x===true)));
});
test('optional source query failure preserves live KPI and unrelated charts',()=>{
 const d=collect({FIXTURE_FAIL_SOURCE:'1'});assert.equal(d.status,'live_google_connected');assert.equal(d.series_status.sources_daily,'unavailable');assert.deepEqual(d.sources_daily,{});assert.equal(d.daily.length,90);assert.equal(d.ranges['7d'].affiliate_clicks,12);
});
test('optional daily query failure leaves totals usable and never invents zeros',()=>{
 const d=collect({FIXTURE_FAIL_DAILY:'1'});assert.equal(d.status,'live_google_connected');assert.deepEqual(d.daily,[]);assert.deepEqual(d.affiliate_daily,[]);assert.equal(d.ranges.today.affiliate_clicks,7);assert.equal(d.series_checks.today.views,null);
});
