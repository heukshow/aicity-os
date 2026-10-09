// Real process restart + disk SQLite, synthetic order/file metadata only. No provider/network calls.
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {openTestStore} from './helpers/ad-commerce-disk-adapter.js';
import {CATALOG_VERSION} from '../src/ad-commerce-catalog.js';
import {AD_ASSET_SPECS} from '../src/ad-asset-specs.js';
globalThis.fetch=()=>{throw new Error('Network is forbidden in persistence tests');};
function input(product='tool-primary',slots=['tool-primary']){return {
 product,days:30,rightsConfirmed:true,termsVersion:CATALOG_VERSION,company:'SYNTHETIC DISK TEST',productName:'Test product',email:'test@example.com',
 claims:'Synthetic persistence fixture, not a customer or a payment.',items:slots.map(slot=>({slot,headline:'Synthetic placement test',description:'Synthetic metadata used only to verify persistent order state.',button:'View test',alt:'Synthetic image metadata fixture',url:'https://example.com/test'}))
};}
const approval={reviewer:'synthetic-reviewer',decision:'approve',notes:'Synthetic state test only.',destinationChecked:true,claimsChecked:true};
async function prepare(f,product,slots){
 const created=await f.store.createDraft(input(product,slots));
 // One-byte blobs test database persistence, NOT valid image decoding or upload acceptance.
 for(const role of ['logo',...JSON.parse(created.order.quote_json).slots]){const s=AD_ASSET_SPECS[role];
  f.native.prepare('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)').run(crypto.randomUUID(),created.order.id,role,'image/png',s.width,s.height,1,'b'.repeat(64),Buffer.from('x'));
 }
 await f.store.submitDraft(created.order.id);await f.store.review(created.order.id,approval);return created.order.id;
}
function fixture(t){const dir=mkdtempSync(join(tmpdir(),'coshuma-persist-'));t.after(()=>rmSync(dir,{recursive:true,force:true}));return join(dir,'fixture.ad-sandbox.sqlite');}
function phase(db,action){const p=spawnSync(process.execPath,[fileURLToPath(import.meta.url),'--fixture-phase',action,db],{encoding:'utf8',timeout:15000});assert.equal(p.status,0,p.stderr||p.stdout);return JSON.parse(p.stdout);}
if(process.argv[2]==='--fixture-phase'){
 const action=process.argv[3],db=process.argv[4],f=openTestStore(db,{initialize:action==='prepare'});
 try{
  await f.store.ready();
  if(action==='prepare'){
   const id=await prepare(f);const order=await f.store.reserveReviewedOrder(id);
   console.log(JSON.stringify({id,state:order.state,holdUntil:order.hold_until,pid:process.pid}));
  }else{
   const order=f.native.prepare('SELECT * FROM ad_sale_orders ORDER BY created_at LIMIT 1').get();
   const before=f.native.prepare('SELECT count(*) n FROM ad_sale_audit').get().n;
   const reread=await f.store.reserveReviewedOrder(order.id);
   console.log(JSON.stringify({id:reread.id,state:reread.state,holdUntil:reread.hold_until,files:(await f.store.files(order.id)).length,
    holds:f.native.prepare('SELECT count(*) n FROM ad_sale_holds').get().n,auditUnchanged:before===f.native.prepare('SELECT count(*) n FROM ad_sale_audit').get().n,
    paymentUncreated:reread.provider_order===null,pid:process.pid}));
  }
 }finally{f.close();}
}else{
 test('a stopped process can be replaced without losing reviewed files, order or reservation',t=>{
  const db=fixture(t),first=phase(db,'prepare'),second=phase(db,'recover');
  assert.notEqual(first.pid,second.pid);assert.equal(first.id,second.id);assert.equal(first.holdUntil,second.holdUntil);
  assert.equal(second.state,'approved');assert.equal(second.files,2);assert.equal(second.holds,1);assert.equal(second.auditUnchanged,true);assert.equal(second.paymentUncreated,true);
 });
 test('disk draft stores only the access digest and preserves uncharged state',async t=>{
  const db=fixture(t),f=openTestStore(db,{initialize:true});const created=await f.store.createDraft(input());f.close();
  const g=openTestStore(db);try{const saved=await g.store.get(created.order.id);assert.equal(saved.state,'draft');assert.equal(saved.provider_order,null);assert.notEqual(saved.access_hash,created.accessToken);assert.equal(readFileSync(db).includes(Buffer.from(created.accessToken)),false);}finally{g.close();}
 });
 test('initialization refuses an existing database and leaves the original reservation untouched',t=>{
  const db=fixture(t),first=phase(db,'prepare');assert.throws(()=>openTestStore(db,{initialize:true}),/nonempty/);assert.equal(phase(db,'recover').id,first.id);
 });
 test('readiness detects a missing protection trigger after reopening',async t=>{
  const db=fixture(t),f=openTestStore(db,{initialize:true});f.native.exec('DROP TRIGGER ad_sale_capture_guard');f.close();
  const g=openTestStore(db);try{await assert.rejects(g.store.ready(),/protection/);}finally{g.close();}
 });
 test('missing explicit approval checks cannot produce approved state or audit on disk',async t=>{
  const db=fixture(t),f=openTestStore(db,{initialize:true});try{
   const {order}=await f.store.createDraft(input());for(const role of ['logo','tool-primary'])f.native.prepare('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)').run(crypto.randomUUID(),order.id,role,'image/png',400,400,1,'b'.repeat(64),Buffer.from('x'));
   await f.store.submitDraft(order.id);const before=f.native.prepare('SELECT count(*) n FROM ad_sale_audit').get().n;
   for(const value of [false,undefined,null,0,1,'true'])await assert.rejects(f.store.review(order.id,{...approval,claimsChecked:value}));
   assert.equal((await f.store.get(order.id)).state,'submitted');assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_audit').get().n,before);
  }finally{f.close();}
 });
 test('a competing bundle leaves no partial reservation after disk reopen',async t=>{
  const db=fixture(t),f=openTestStore(db,{initialize:true});const first=await prepare(f);await f.store.reserveReviewedOrder(first);
  const bundle=await prepare(f,'P2',['tool-primary','buyer-intent-top']);await assert.rejects(f.store.reserveReviewedOrder(bundle));f.close();
  const g=openTestStore(db);try{assert.equal(g.native.prepare('SELECT count(*) n FROM ad_sale_holds WHERE order_id=?').get(bundle).n,0);assert.equal((await g.store.get(bundle)).hold_until,null);}finally{g.close();}
 });
 test('shared capacity remains three across reopened instances',async t=>{
  const db=fixture(t);let f=openTestStore(db,{initialize:true});
  for(let i=0;i<3;i++){const id=await prepare(f,'tool-rotation',['tool-rotation']);await f.store.reserveReviewedOrder(id);f.close();f=openTestStore(db);}
  try{const fourth=await prepare(f,'tool-rotation',['tool-rotation']);await assert.rejects(f.store.reserveReviewedOrder(fourth));assert.equal((await f.store.availability()).find(x=>x.id==='tool-rotation').available,0);}finally{f.close();}
 });
 test('concurrent review commits exactly one review audit on persistent SQLite',async t=>{
  const db=fixture(t),f=openTestStore(db,{initialize:true});try{
   const {order}=await f.store.createDraft(input());for(const role of ['logo','tool-primary'])f.native.prepare('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)').run(crypto.randomUUID(),order.id,role,'image/png',400,400,1,'b'.repeat(64),Buffer.from('x'));
   await f.store.submitDraft(order.id);const results=await Promise.allSettled([f.store.review(order.id,approval),f.store.review(order.id,{...approval,decision:'reject'})]);
   assert.equal(results.filter(x=>x.status==='fulfilled').length,1);assert.equal(f.native.prepare("SELECT count(*) n FROM ad_sale_audit WHERE order_id=? AND action LIKE 'review_%'").get(order.id).n,1);
  }finally{f.close();}
 });
 test('cancelled orders cannot reserve a position after process restart',async t=>{
  const db=fixture(t),f=openTestStore(db,{initialize:true});const id=await prepare(f);f.native.prepare("UPDATE ad_sale_orders SET state='cancelled' WHERE id=?").run(id);f.close();
  const g=openTestStore(db);try{await assert.rejects(g.store.reserveReviewedOrder(id));assert.equal(g.native.prepare('SELECT count(*) n FROM ad_sale_holds').get().n,0);}finally{g.close();}
 });
}
