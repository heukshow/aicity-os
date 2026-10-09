// Signed HTTP returns + browser-script execution in a VM. No actual PayPal/network calls.
import test from 'node:test';
import assert from 'node:assert/strict';
import { runInNewContext } from 'node:vm';
import { setImmediate as nextTick } from 'node:timers/promises';
import { memoryStore, syntheticInput, syntheticPayPal, png, TEST_ENV, TEST_REVIEW_KEY } from './helpers/ad-commerce-fixtures.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';
import { SandboxAdPayments } from '../src/ad-commerce-sandbox-payments.js';
import { createAdSandboxHandler } from '../src/ad-commerce-sandbox-http.js';
import { sandboxReturnUrls } from '../src/ad-commerce-checkout-return.js';
import { sandboxReturnScript } from '../src/ad-commerce-sandbox-return-page.js';
const origin='http://127.0.0.1:18473';
globalThis.fetch=()=>{throw new Error('Real network forbidden');};
async function fixture(t){
  const f=memoryStore();t.after(()=>f.close());await f.store.ready();const provider=syntheticPayPal();let createdPayload;
  const payments=new SandboxAdPayments(f.store,{env:TEST_ENV,returnOrigin:origin,fetchImpl:async(url,init={})=>{
    if(init.method==='POST'&&new URL(url).pathname==='/v2/checkout/orders')createdPayload=JSON.parse(init.body);
    return provider.fetchImpl(url,init);
  }});
  const handle=createAdSandboxHandler({store:f.store,payments,reviewKey:TEST_REVIEW_KEY,environment:'sandbox',origin});
  const draft=await f.store.createDraft(syntheticInput());const id=draft.order.id,token=draft.accessToken;
  const call=(path,{method='POST',key=token,body='{}',mime='application/json'}={})=>handle(new Request(origin+path,{method,
    headers:{Origin:origin,'Content-Type':mime,...(key?{Authorization:'Bearer '+key}:{})},body:method==='GET'?undefined:body}));
  for(const role of ['logo','tool-primary']){
    const spec=AD_ASSET_SPECS[role];assert.equal((await call('/sandbox/orders/'+id+'/assets/'+role,{method:'PUT',body:png(spec.width,spec.height),mime:'image/png'})).status,200);
  }
  await f.store.submitDraft(id);await f.store.review(id,{reviewer:'test-reviewer',decision:'approve',notes:'Synthetic approved PNG only.',destinationChecked:true,claimsChecked:true});
  await f.store.reserveReviewedOrder(id);await payments.checkout(id);const order=await f.store.get(id);
  const urls=await sandboxReturnUrls(order,origin,f.store.clock().getTime());const approve=new URL(urls.return_url);approve.searchParams.set('token',order.provider_order);
  return {...f,provider,payments,handle,call,id,token,order,urls,approve,payload:()=>createdPayload};
}
test('order creation carries signed return and cancel URLs bound to the same saved order',async t=>{
 const f=await fixture(t),c=f.payload().payment_source.paypal.experience_context;
 assert.equal(c.return_url,f.urls.return_url);assert.equal(c.cancel_url,f.urls.cancel_url);assert.equal(c.user_action,'PAY_NOW');
 assert.equal(c.return_url.includes(f.token),false);assert.equal(c.return_url.includes(f.order.access_hash),false);
});
test('GET approval return renders a protected page without charging or changing order state',async t=>{
 const f=await fixture(t),before=f.provider.calls.length,r=await f.handle(new Request(f.approve));
 assert.equal(r.status,200);assert.match(r.headers.get('content-security-policy'),/script-src 'nonce-/);assert.equal(r.headers.get('referrer-policy'),'no-referrer');
 const html=await r.text();assert.match(html,/COSHUMA sandbox order status/);assert.equal(html.includes(f.token),false);assert.equal(html.includes(f.order.access_hash),false);
 assert.equal(f.provider.calls.length,before);assert.equal((await f.store.get(f.id)).state,'checkout');
});
test('cancel return does not capture, release reservation or falsely mark paid',async t=>{
 const f=await fixture(t),before=f.provider.calls.length,r=await f.handle(new Request(f.urls.cancel_url));
 assert.equal(r.status,200);assert.match(await r.text(),/구매자 승인이 취소/);assert.equal(f.provider.calls.length,before);
 assert.equal((await f.store.get(f.id)).state,'checkout');assert.equal(f.native.prepare('SELECT count(*) n FROM ad_sale_holds').get().n,1);
});
test('tampered state or mismatched PayPal token is rejected without financial calls',async t=>{
 const f=await fixture(t),before=f.provider.calls.length;
 for(const [key,value] of [['state','0'.repeat(64)],['token','WRONG-ORDER'],['order',crypto.randomUUID()]]){
  const url=new URL(f.approve);url.searchParams.set(key,value);assert.equal((await f.handle(new Request(url))).status,403);
 }
 assert.equal(f.provider.calls.length,before);
});
test('an authenticated POST completes only the matching approved order; reconciliation cannot charge again',async t=>{
 const f=await fixture(t);f.provider.approve(f.order.provider_order);
 assert.equal((await f.call('/sandbox/orders/'+f.id+'/capture',{key:null})).status,403);
 assert.equal((await f.call('/sandbox/orders/'+f.id+'/capture')).status,200);
 const before=f.provider.calls.filter(c=>c.method==='POST'&&c.path.endsWith('/capture')).length;
 assert.equal((await f.call('/sandbox/orders/'+f.id+'/reconcile')).status,200);
 assert.equal(before,1);assert.equal(f.provider.calls.filter(c=>c.method==='POST'&&c.path.endsWith('/capture')).length,1);
});
async function scriptRun(view,{key='b'.repeat(64),fail=false,storage=new Map(),state='checkout',deny=false,storageFails=false}={}){
 const message={textContent:''},detail={textContent:''},button={disabled:false,addEventListener(_name,fn){this.click=fn;}};const calls=[];
 const paid={id:view.orderId,state:'active',capture_id:'SYNTHETIC-CAPTURE',payment_environment:'sandbox',
   payment_verified_at:'2026-10-07T00:00:00.000Z',starts_at:'2026-10-07T00:00:00.000Z',ends_at:'2026-11-06T00:00:00.000Z'};
 const order={id:view.orderId,state,provider_order:'SYNTHETIC-ORDER',hold_until:'2099-01-01T00:00:00.000Z',...(state==='active'?paid:{})};
 const sessionStorage={getItem:name=>name.startsWith('coshuma-sandbox-order:')?key:storage.get(name),
   setItem(name,value){if(storageFails)throw new Error('denied');storage.set(name,value);}};
 runInNewContext(sandboxReturnScript(view),{document:{getElementById:id=>id==='return-status'?message:id==='order-detail'?detail:button},
  sessionStorage,fetch:async(path,init)=>{calls.push({path,init});if(fail&&init.method==='POST')throw new Error('lost response');
    return {ok:!deny,json:async()=>({order:init.method==='POST'?paid:order})};},encodeURIComponent,JSON,Error,Date});
 await nextTick();return {message,detail,button,calls,storage};
}
const view={orderId:'test-order',nextAction:'confirm_with_authenticated_post',browserOutcome:'returned',reservationExpired:false};

test('return script without order access cannot make any request',async()=>{
 const r=await scriptRun(view,{key:null});assert.equal(r.calls.length,0);assert.match(r.message.textContent,/접근키가 유실/);
});

test('return script reads owner state before one authenticated capture and shows verified period',async()=>{
 const r=await scriptRun(view);assert.equal(r.calls.length,2);assert.equal(r.calls[0].init.method,'GET');
 assert.match(r.calls[1].path,/\/capture$/);assert.equal(r.calls[1].init.method,'POST');
 assert.equal(r.calls[1].init.headers.Authorization,'Bearer '+'b'.repeat(64));assert.match(r.message.textContent,/서버에서 확인/);
 assert.match(r.detail.textContent,/2026-10-07T00:00:00.000Z/);assert.match(r.detail.textContent,/2026-11-06T00:00:00.000Z/);
 assert.equal(r.calls.some(call=>call.path.includes('b'.repeat(64))),false);
});

test('cancel and expired returns read state but never automatically capture',async()=>{
 for(const changed of [{nextAction:'show_status_without_charge',browserOutcome:'cancelled'},
   {nextAction:'refresh_status',reservationExpired:true},{nextAction:'show_status'}]){
   const r=await scriptRun({...view,...changed});assert.equal(r.calls.length,1);assert.equal(r.calls[0].init.method,'GET');
 }
});

test('late cancellation shows already verified state without reverting or posting',async()=>{
 const r=await scriptRun({...view,browserOutcome:'cancelled',nextAction:'show_status'},{state:'active'});
 assert.equal(r.calls.length,1);assert.match(r.message.textContent,/서버에서 확인/);
});

test('lost capture response retains an attempt marker and button reconciles without recapturing',async()=>{
 const r=await scriptRun(view,{fail:true});assert.match(r.message.textContent,/다시 결제하지/);
 await r.button.click();assert.deepEqual(r.calls.map(call=>call.init.method),['GET','POST','GET','POST']);
 assert.match(r.calls[1].path,/\/capture$/);assert.match(r.calls[3].path,/\/reconcile$/);
});

test('refresh after an ambiguous capture only reads and reconciles the original order',async()=>{
 const first=await scriptRun(view,{fail:true});
 const refresh=await scriptRun(view,{storage:first.storage});
 assert.equal(refresh.calls.length,2);assert.match(refresh.calls[1].path,/\/reconcile$/);
 assert.equal(refresh.calls.some(call=>call.path.endsWith('/capture')),false);
});

test('owner lookup denial or unavailable attempt storage prevents capture',async()=>{
 for(const options of [{deny:true},{storageFails:true}]){
  const r=await scriptRun(view,options);assert.equal(r.calls.length,1);assert.equal(r.calls[0].init.method,'GET');
 }
});

test('held and refunded states do not become capture requests after a stale valid redirect',async()=>{
 for(const state of ['held','refunded','cancelled']){
  const r=await scriptRun(view,{state});assert.equal(r.calls.length,1);assert.equal(r.calls[0].init.method,'GET');
 }
});

test('capture in progress reconciles after return without creating another capture',async()=>{
 const r=await scriptRun({...view,nextAction:'reconcile_existing_capture'},{state:'capturing'});
 assert.equal(r.calls.length,2);assert.match(r.calls[1].path,/\/reconcile$/);
});
