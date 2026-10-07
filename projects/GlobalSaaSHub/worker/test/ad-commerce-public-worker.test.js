// Public test-entry integration in memory with synthetic fetch. No network or deployment.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import worker from '../src/ad-commerce-public-sandbox-worker.js';
import { createAdSandboxHandler, createPublicAdSandboxHandler } from '../src/ad-commerce-sandbox-http.js';
import { sandboxReturnUrls } from '../src/ad-commerce-checkout-return.js';
import { memoryStore, syntheticInput, syntheticPayPal, png, TEST_ENV, TEST_REVIEW_KEY } from './helpers/ad-commerce-fixtures.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';
const origin='https://coshuma-ads-sandbox-test.example.workers.dev';
const operatorKey='synthetic-operator-key-public-entry-tests-only',webhookId='SYNTHETIC-ISOLATED-WEBHOOK';
const response=value=>new Response(JSON.stringify(value),{headers:{'Content-Type':'application/json'}});
function fixture(t,{arrayBlobs=false}={}){
 const f=memoryStore();t.after(()=>f.close());
 for(const file of ['0001_webhook_retry.sql','0002_public_runtime.sql'])f.native.exec(readFileSync(new URL('../sandbox-migrations/'+file,import.meta.url),'utf8'));
 if(arrayBlobs){
  const original=f.db.prepare.bind(f.db);
  f.db.prepare=sql=>({bind(...values){
   const statement=original(sql).bind(...values),first=statement.first.bind(statement);
   return {...statement,async first(){const row=await first();if(row?.data)row.data=Array.from(row.data);return row;}};
  }});
 }
 const provider=syntheticPayPal(),network=[];let wrongRegistration=false;
 const env={...TEST_ENV,AD_SANDBOX_DB:f.db,SANDBOX_ISOLATION:'coshuma-ads-sandbox-v1',
  SANDBOX_DATABASE_LABEL:'coshuma-ads-sandbox-tests',SANDBOX_ORIGIN:origin,SANDBOX_REVIEW_KEY:TEST_REVIEW_KEY,
  SANDBOX_OPERATOR_KEY:operatorKey,PAYPAL_WEBHOOK_ID:webhookId,SANDBOX_BUILD:'synthetic-build'};
 t.mock.method(globalThis,'fetch',async(url,init={})=>{
  const target=new URL(url),method=init.method||'GET';
  if(target.origin!=='https://api-m.sandbox.paypal.com')throw new Error('External network forbidden');
  network.push({path:target.pathname,query:target.search,method});
  if(target.pathname==='/v1/oauth2/token')return response({access_token:'SYNTHETIC-TOKEN',token_type:'Bearer',expires_in:300});
  if(target.pathname==='/v1/notifications/webhooks'){
   if(target.searchParams.get('anchor_type')==='ACCOUNT')return response({webhooks:[]});
   return response({webhooks:[{id:webhookId,url:(wrongRegistration?'https://production.example':origin)+'/sandbox/webhooks/paypal',
     event_types:[{name:'PAYMENT.CAPTURE.COMPLETED'}]}]});
  }
  return provider.fetchImpl(url,init);
 });
 const call=(path,{method='GET',key,body,mime='application/json',headers={},environment=env,requestOrigin=origin}={})=>
  worker.fetch(new Request(requestOrigin+path,{method,headers:{Origin:requestOrigin,...(key?{Authorization:'Bearer '+key}:{}),
   ...(body!==undefined?{'Content-Type':mime}:{}),...headers},
   body:body===undefined?undefined:typeof body==='string'||ArrayBuffer.isView(body)?body:JSON.stringify(body)}),environment,{waitUntil(){}});
 return {...f,env,provider,network,call,setWrongRegistration(value){wrongRegistration=value;}};
}
async function prepared(f){
 const created=await f.call('/sandbox/orders',{method:'POST',key:operatorKey,body:syntheticInput()});
 assert.equal(created.status,201);const {order,accessToken}=await created.json();
 for(const role of ['logo','tool-primary']){
  const spec=AD_ASSET_SPECS[role];
  assert.equal((await f.call('/sandbox/orders/'+order.id+'/assets/'+role,{method:'PUT',key:accessToken,body:png(spec.width,spec.height),mime:'image/png'})).status,200);
 }
 assert.equal((await f.call('/sandbox/orders/'+order.id+'/submit',{method:'POST',key:accessToken})).status,200);
 assert.equal((await f.call('/sandbox/admin/orders/'+order.id+'/review',{method:'POST',key:TEST_REVIEW_KEY,
  body:{decision:'approve',notes:'Synthetic public-entry approval.',destinationChecked:true,claimsChecked:true}})).status,200);
 assert.equal((await f.call('/sandbox/orders/'+order.id+'/reserve',{method:'POST',key:accessToken})).status,200);
 return {id:order.id,token:accessToken};
}
const paymentPosts=network=>network.filter(call=>call.method==='POST'&&call.path.startsWith('/v2/'));

test('entry import does not generate random values outside a request context',async t=>{
 const random=t.mock.method(globalThis.crypto,'randomUUID',()=>{throw new Error('Random values prohibited during module import');});
 await import('../src/ad-commerce-public-sandbox-worker.js?global-scope-check');
 assert.equal(random.mock.callCount(),0);
});
test('public entry rejects live, production bindings, wrong isolation and non-test origins',async t=>{
 const f=fixture(t);
 for(const changes of [{PAYPAL_ENVIRONMENT:'live'},{ORDERS:{}},{SANDBOX_ISOLATION:'production'},
   {SANDBOX_OPERATOR_KEY:TEST_REVIEW_KEY},{SANDBOX_OPERATOR_KEY:''},{SANDBOX_REVIEW_KEY:''},
   {SANDBOX_DATABASE_LABEL:'production-orders'},{SANDBOX_ORIGIN:'https://coshuma.com'}]){
  assert.equal((await f.call('/health',{environment:{...f.env,...changes}})).status,503);
 }
 assert.equal(f.network.length,0);assert.equal((await f.call('/health',{requestOrigin:'https://foreign.example'})).status,403);
});
test('dedicated DB marker is required beyond sandbox-looking binding names',async t=>{
 const f=fixture(t);f.native.prepare("UPDATE ad_sandbox_runtime SET value='wrong' WHERE key='scope'").run();
 assert.equal((await f.call('/sandbox/catalog')).status,503);assert.equal(f.network.length,0);
});
test('original loopback stays local and public factory requires separate keys and HTTPS isolation',async t=>{
 const f=fixture(t),options={store:f.store,payments:{expire:async()=>0},reviewKey:TEST_REVIEW_KEY,environment:'sandbox'};
 assert.throws(()=>createAdSandboxHandler({...options,origin}));
 assert.throws(()=>createPublicAdSandboxHandler({...options,origin:'http://127.0.0.1:18473',isolation:'coshuma-ads-sandbox',operatorKey}));
 assert.throws(()=>createPublicAdSandboxHandler({...options,origin,isolation:'coshuma-ads-sandbox',operatorKey:TEST_REVIEW_KEY}));
 const local=createAdSandboxHandler({...options,origin:'http://127.0.0.1:18473'});
 const result=await local(new Request('http://127.0.0.1:18473/sandbox/orders',{method:'POST',
  headers:{Origin:'http://127.0.0.1:18473','Content-Type':'application/json'},body:JSON.stringify(syntheticInput())}));
 assert.equal(result.status,201);assert.equal(f.network.length,0);
});
test('public draft creation requires operator authentication and same origin',async t=>{
 const f=fixture(t);
 for(const key of [undefined,TEST_REVIEW_KEY,'wrong-key'])assert.equal((await f.call('/sandbox/orders',{method:'POST',key,body:syntheticInput()})).status,403);
 assert.equal((await f.call('/sandbox/orders',{method:'POST',key:operatorKey,body:syntheticInput(),headers:{Origin:'https://foreign.example'}})).status,403);
 assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_orders').get().n,0);assert.equal(f.network.length,0);
});
test('order data, upload, reviewer reads and operator evidence require precise credentials',async t=>{
 const f=fixture(t),draft=await f.store.createDraft(syntheticInput()),id=draft.order.id;
 for(const key of [undefined,operatorKey,TEST_REVIEW_KEY]){
  assert.equal((await f.call('/sandbox/orders/'+id,{key})).status,403);
  assert.equal((await f.call('/sandbox/orders/'+id+'/assets/logo',{method:'PUT',key,body:png(400,400),mime:'image/png'})).status,403);
 }
 assert.equal((await f.call('/sandbox/admin/orders/'+id,{key:draft.accessToken})).status,403);
 assert.equal((await f.call('/sandbox/ops/evidence',{key:TEST_REVIEW_KEY})).status,403);
 assert.equal((await f.call('/sandbox/ops/preflight')).status,403);
 assert.equal(f.network.length,0);assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_files').get().n,0);
});
test('unauthenticated checkout and capture do not trigger provider preflight calls',async t=>{
 const f=fixture(t),{id}=await prepared(f);f.network.length=0;
 for(const action of ['checkout','capture'])assert.equal((await f.call('/sandbox/orders/'+id+'/'+action,{method:'POST'})).status,403);
 assert.equal(f.network.length,0);
});
test('wrong webhook registration blocks PayPal order creation and capture of an existing order',async t=>{
 const f=fixture(t),{id,token}=await prepared(f);f.setWrongRegistration(true);
 assert.equal((await f.call('/sandbox/orders/'+id+'/checkout',{method:'POST',key:token})).status,503);
 assert.equal(paymentPosts(f.network).length,0);assert.equal((await f.store.get(id)).state,'approved');
 f.setWrongRegistration(false);assert.equal((await f.call('/sandbox/orders/'+id+'/checkout',{method:'POST',key:token})).status,200);
 f.provider.approve((await f.store.get(id)).provider_order);f.setWrongRegistration(true);f.network.length=0;
 assert.equal((await f.call('/sandbox/orders/'+id+'/capture',{method:'POST',key:token})).status,503);
 assert.equal(paymentPosts(f.network).length,0);assert.equal((await f.store.get(id)).state,'checkout');
});
test('encoded and duplicate-slash paths cannot bypass capture registration gating',async t=>{
 const f=fixture(t),{id,token}=await prepared(f);
 assert.equal((await f.call('/sandbox/orders/'+id+'/checkout',{method:'POST',key:token})).status,200);
 f.provider.approve((await f.store.get(id)).provider_order);f.setWrongRegistration(true);f.network.length=0;
 for(const path of ['/sandbox//orders/'+id+'/capture','/sandbox/orders/'+id+'/%63apture','/sandbox/orders/%'+id.charCodeAt(0).toString(16)+id.slice(1)+'/capture']){
  assert.ok((await f.call(path,{method:'POST',key:token})).status>=400);
 }
 assert.equal(paymentPosts(f.network).length,0);assert.equal((await f.store.get(id)).state,'checkout');
});
test('D1 array BLOBs return PNG bytes for reviewer and public active asset',async t=>{
 const f=fixture(t,{arrayBlobs:true}),{id,token}=await prepared(f);
 const expected=png(400,400),review=await f.call('/sandbox/admin/orders/'+id+'/assets/logo',{key:TEST_REVIEW_KEY});
 assert.equal(review.status,200);assert.equal(review.headers.get('content-type'),'image/png');
 assert.deepEqual(new Uint8Array(await review.arrayBuffer()),new Uint8Array(expected));assert.equal((await f.call('/sandbox/assets/'+id+'/logo')).status,404);
 assert.equal((await f.call('/sandbox/orders/'+id+'/checkout',{method:'POST',key:token})).status,200);
 f.provider.approve((await f.store.get(id)).provider_order);assert.equal((await f.call('/sandbox/orders/'+id+'/capture',{method:'POST',key:token})).status,200);
 const active=await f.call('/sandbox/assets/'+id+'/logo');assert.equal(active.status,200);
 assert.deepEqual(new Uint8Array(await active.arrayBuffer()),new Uint8Array(expected));
});
test('purchase and signed approval/cancel GETs cannot pay or mutate saved order state',async t=>{
 const f=fixture(t),{id,token}=await prepared(f);
 const page=await f.call('/sandbox/purchase');assert.equal(page.status,200);const html=await page.text();
 assert.match(html,/id="order-access"/);assert.equal(html.includes(token),false);
 assert.equal((await f.call('/sandbox/orders/'+id+'/checkout',{method:'POST',key:token})).status,200);
 const order=await f.store.get(id),urls=await sandboxReturnUrls(order,origin,Date.now());
 const signed=new URL(urls.return_url);signed.searchParams.set('token',order.provider_order);
 const before=f.native.prepare('SELECT count(*) n FROM ad_sale_audit').get().n;f.network.length=0;
 for(const target of [signed,new URL(urls.cancel_url)])assert.equal((await f.call(target.pathname+target.search)).status,200);
 assert.equal(f.network.length,0);assert.equal((await f.store.get(id)).state,'checkout');
 assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_audit').get().n,before);
 signed.searchParams.set('token','WRONG-PROVIDER-ORDER');assert.equal((await f.call(signed.pathname+signed.search)).status,403);
 assert.equal(f.network.length,0);
});
test('catalog GET is read-only when an active advertisement is past its end',async t=>{
 const f=fixture(t),{id,token}=await prepared(f);
 assert.equal((await f.call('/sandbox/orders/'+id+'/checkout',{method:'POST',key:token})).status,200);
 f.provider.approve((await f.store.get(id)).provider_order);assert.equal((await f.call('/sandbox/orders/'+id+'/capture',{method:'POST',key:token})).status,200);
 const end=new Date(Date.now()-1000).toISOString(),start=new Date(Date.parse(end)-30*86400000).toISOString();
 f.native.prepare('UPDATE ad_sale_orders SET starts_at=?,ends_at=? WHERE id=?').run(start,end,id);
 const before=f.native.prepare('SELECT count(*) n FROM ad_sale_audit').get().n;f.network.length=0;
 assert.equal((await f.call('/sandbox/catalog')).status,200);assert.equal((await f.store.get(id)).state,'active');
 assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_holds').get().n,1);
 assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_audit').get().n,before);assert.equal(f.network.length,0);
});
test('caller-selected clocks cannot affect customer paths or multi-order operator drain',async t=>{
 const f=fixture(t),draft=await f.store.createDraft(syntheticInput()),headers={'x-sandbox-clock-order':draft.order.id};
 assert.equal((await f.call('/sandbox/orders/'+draft.order.id,{key:operatorKey,headers})).status,403);
 assert.equal((await f.call('/sandbox/ops/drain',{method:'POST',key:operatorKey,headers})).status,403);
 assert.equal(f.network.length,0);
});
