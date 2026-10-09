// Browser scripts executed in a VM with synthetic responses only; no navigation or real PayPal.
import test from 'node:test';
import assert from 'node:assert/strict';
import { runInNewContext } from 'node:vm';
import { setImmediate as nextTick } from 'node:timers/promises';
import { renderSandboxPurchasePage, sandboxPurchaseScript } from '../src/ad-commerce-sandbox-purchase-page.js';
import { sandboxReturnScript } from '../src/ad-commerce-sandbox-return-page.js';

const id='11111111-1111-4111-8111-111111111111', key='b'.repeat(64);
const stored={id,state:'approved',amount:'49.00',currency:'USD',hold_until:'2099-01-01T00:00:00.000Z'};
function fixture({storage=new Map(),denied=false,badUrl=false,storageFails=false,waitForFetch}={}){
 const ids=['order-id','order-access','purchase-status','purchase-detail','load-order','start-checkout','reserve-order','reconcile-order'];
 const elements=Object.fromEntries(ids.map(name=>[name,{value:'',textContent:'',disabled:false,
   addEventListener(event,fn){this[event]=fn;}}]));
 const calls=[],navigations=[];let order={...stored};
 const sessionStorage={getItem:name=>storage.get(name)||null,setItem(name,value){if(storageFails)throw new Error('Storage unavailable');storage.set(name,value);}};
 const fetch=async(path,init)=>{
  if(waitForFetch)await waitForFetch;
  calls.push({path,init});
  if(path.endsWith('/checkout'))order={...order,state:'checkout',provider_order:'SYNTHETIC-ORDER',payment_environment:'sandbox'};
  return {ok:!denied,json:async()=>({order,approvalUrl:badUrl?'https://www.paypal.com/checkoutnow?token=SYNTHETIC-ORDER':
    'https://www.sandbox.paypal.com/checkoutnow?token=SYNTHETIC-ORDER'})};
 };
 runInNewContext(sandboxPurchaseScript(),{document:{getElementById:name=>elements[name]},sessionStorage,fetch,
  location:{assign:url=>navigations.push(url)},URL,Date,Error,encodeURIComponent});
 elements['order-id'].value=id;elements['order-access'].value=key;
 return {elements,calls,navigations,storage,sessionStorage,fetch};
}
test('purchase page renders only isolated paths with no credentials and a restrictive policy',async()=>{
 const response=renderSandboxPurchasePage(),html=await response.text();
 assert.match(html,/PayPal Sandbox/);assert.match(html,/id="order-access" type="password"/);
 assert.equal(html.includes(key),false);assert.equal(html.includes('localStorage'),false);
 assert.equal(response.headers.get('referrer-policy'),'no-referrer');
 assert.match(response.headers.get('content-security-policy'),/connect-src 'self'/);
});
test('authenticated start saves access in sessionStorage and navigates same tab only to matching sandbox order',async()=>{
 const f=fixture();await f.elements['load-order'].click();await f.elements['start-checkout'].click();
 assert.equal(f.storage.get('coshuma-sandbox-order:'+id),key);
 assert.equal(f.storage.get('coshuma-sandbox-current-order'),id);
 assert.deepEqual(f.calls.map(call=>call.init.method),['GET','GET','POST']);
 assert.equal(f.calls[2].path,'/sandbox/orders/'+id+'/checkout');
 assert.equal(f.navigations.length,1);assert.match(f.navigations[0],/^https:\/\/www\.sandbox\.paypal\.com\/checkoutnow/);
 assert.equal(f.navigations[0].includes(key),false);
 for(const call of f.calls){assert.equal(call.path.includes(key),false);assert.equal(call.init.headers.Authorization,'Bearer '+key);}
});
test('invalid or denied order access never starts a provider checkout',async()=>{
 const invalid=fixture();invalid.elements['order-access'].value='wrong';await invalid.elements['load-order'].click();assert.equal(invalid.calls.length,0);
 const denied=fixture({denied:true});await denied.elements['load-order'].click();
 assert.equal(denied.calls.length,1);assert.equal(denied.elements['start-checkout'].disabled,true);assert.equal(denied.navigations.length,0);
});
test('unavailable session storage fails before checkout and never navigates',async()=>{
 const f=fixture({storageFails:true});await f.elements['start-checkout'].click();
 assert.equal(f.calls.length,1);assert.equal(f.calls[0].init.method,'GET');assert.equal(f.navigations.length,0);
});
test('a live provider approval URL is rejected without browser navigation',async()=>{
 const f=fixture({badUrl:true});await f.elements['start-checkout'].click();
 assert.equal(f.navigations.length,0);assert.match(f.elements['purchase-status'].textContent,/확인되지/);
});
test('capture-attempt marker prevents starting another checkout',async()=>{
 const f=fixture();await f.elements['start-checkout'].click();f.calls.length=0;f.navigations.length=0;
 f.storage.set('coshuma-sandbox-capture:'+id+':SYNTHETIC-ORDER','attempted');
 await f.elements['start-checkout'].click();assert.equal(f.calls.length,1);assert.equal(f.calls[0].init.method,'GET');
 assert.equal(f.navigations.length,0);assert.match(f.elements['purchase-status'].textContent,/새 청구 없이/);
});
test('the start page restores its last order and key within the same browser session',()=>{
 const storage=new Map([['coshuma-sandbox-current-order',id],['coshuma-sandbox-order:'+id,key]]);
 const f=fixture({storage});assert.equal(f.elements['order-id'].value,id);assert.equal(f.elements['order-access'].value,key);
 assert.equal(f.calls.length,0);
});
test('purchase and automatic return use the same saved order key without a URL credential handoff',async()=>{
 const f=fixture();await f.elements['start-checkout'].click();
 const nodes={};for(const name of ['return-status','order-detail','check-order'])nodes[name]={textContent:'',disabled:false,addEventListener(event,fn){this[event]=fn;}};
 const calls=[];const paid={...stored,state:'active',provider_order:'SYNTHETIC-ORDER',capture_id:'SYNTHETIC-CAPTURE',
  payment_environment:'sandbox',payment_verified_at:'2026-10-07T00:00:00.000Z',starts_at:'2026-10-07T00:00:00.000Z',ends_at:'2026-11-06T00:00:00.000Z'};
 runInNewContext(sandboxReturnScript({orderId:id,nextAction:'confirm_with_authenticated_post',browserOutcome:'returned'}),{
  document:{getElementById:name=>nodes[name]},sessionStorage:f.sessionStorage,fetch:async(path,init)=>{
   calls.push({path,init});return {ok:true,json:async()=>({order:init.method==='GET'?{...paid,state:'checkout',capture_id:null}:paid})};
  },Date,Error,JSON,encodeURIComponent});
 await nextTick();
 assert.deepEqual(calls.map(call=>call.init.method),['GET','POST']);assert.match(calls[1].path,/\/capture$/);
 assert.equal(calls[1].init.headers.Authorization,'Bearer '+key);assert.match(nodes['order-detail'].textContent,/2026-11-06/);
});

test('order ID and access key cannot be edited while authentication and saved-session handoff are pending',async()=>{
 let release;const waitForFetch=new Promise(resolve=>{release=resolve;});
 const f=fixture({waitForFetch});const pending=f.elements['load-order'].click();
 assert.equal(f.elements['order-id'].disabled,true);assert.equal(f.elements['order-access'].disabled,true);
 release();await pending;
 assert.equal(f.elements['order-id'].disabled,false);assert.equal(f.elements['order-access'].disabled,false);
 assert.equal(f.storage.get('coshuma-sandbox-order:'+id),key);
});
