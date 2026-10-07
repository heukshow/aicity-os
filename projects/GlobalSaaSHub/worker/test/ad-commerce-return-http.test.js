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
 assert.equal(r.status,200);assert.match(await r.text(),/approval was cancelled/);assert.equal(f.provider.calls.length,before);
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
async function scriptRun(view,{key='b'.repeat(64),fail=false}={}){
 const message={textContent:''},button={disabled:false,addEventListener(_name,fn){this.click=fn;}};const calls=[];
 runInNewContext(sandboxReturnScript(view),{document:{getElementById:id=>id==='return-status'?message:button},
  sessionStorage:{getItem:()=>key},fetch:async(path,init)=>{calls.push({path,init});if(fail)throw new Error('lost response');return {ok:true,json:async()=>({order:{state:'active'}})};},encodeURIComponent,JSON,Error});
 await nextTick();return {message,button,calls};
}
const view={orderId:'test-order',nextAction:'confirm_with_authenticated_post'};
test('return script without order access cannot make any request',async()=>{
 const r=await scriptRun(view,{key:null});assert.equal(r.calls.length,0);assert.match(r.message.textContent,/cannot charge/);
});
test('return script uses one authenticated capture POST and reports only server-confirmed status',async()=>{
 const r=await scriptRun(view);assert.equal(r.calls.length,1);assert.match(r.calls[0].path,/\/capture$/);
 assert.equal(r.calls[0].init.method,'POST');assert.equal(r.calls[0].init.headers.Authorization,'Bearer '+'b'.repeat(64));assert.match(r.message.textContent,/verified/);
});
test('cancel or expired return script never automatically sends a capture request',async()=>{
 for(const nextAction of ['show_status_without_charge','refresh_status','show_status']){const r=await scriptRun({...view,nextAction});assert.equal(r.calls.length,0);}
});
test('lost return response prompts status recovery; the retry button reconciles instead of recapturing',async()=>{
 const r=await scriptRun(view,{fail:true});assert.match(r.message.textContent,/do not pay again/);
 await r.button.click();assert.equal(r.calls.length,2);assert.match(r.calls[1].path,/\/reconcile$/);
});
