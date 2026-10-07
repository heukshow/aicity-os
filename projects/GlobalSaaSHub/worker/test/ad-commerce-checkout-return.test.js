// Offline redirect validation only; this does not run PayPal or exercise a browser navigation.
import test from 'node:test';
import assert from 'node:assert/strict';
import {sandboxReturnUrls,inspectSandboxReturn} from '../src/ad-commerce-checkout-return.js';
globalThis.fetch=()=>{throw new Error('Network forbidden in return tests');};
const origin='http://127.0.0.1:50001',now=Date.parse('2026-10-07T00:00:00.000Z');
function order(){return {id:'11111111-1111-4111-8111-111111111111',reference:'TEST-AD-11111111',access_hash:'b'.repeat(64),
 state:'checkout',hold_until:'2026-10-07T00:30:00.000Z',provider_order:'SYNTHETIC-ORDER',payment_environment:'sandbox',merchant_id:'SYNTHETIC-MERCHANT'};}
async function request(value=order(),flow='return',token=true){const urls=await sandboxReturnUrls(value,origin,now);const url=new URL(urls[flow==='return'?'return_url':'cancel_url']);if(token)url.searchParams.set('token',value.provider_order);return new Request(url);}
const inspect=(req,value,at=now)=>inspectSandboxReturn(req,value,{origin,now:at});
test('valid approval return requests authenticated confirmation, not payment success',async()=>{
 const o=order(),before=JSON.stringify(o),result=await inspect(await request(o),o);
 assert.equal(result.paymentVerified,false);assert.equal(result.nextAction,'confirm_with_authenticated_post');assert.equal(JSON.stringify(o),before);
});
test('return URLs are stable across fresh instances with persisted order data',async()=>{
 const o=order();assert.deepEqual(await sandboxReturnUrls(o,origin,now),await sandboxReturnUrls(JSON.parse(JSON.stringify(o)),origin,now+1000));
});
test('return links disclose neither the stored access digest nor customer details',async()=>{
 const o={...order(),email:'synthetic@example.com',company:'SYNTHETIC-COMPANY'},urls=JSON.stringify(await sandboxReturnUrls(o,origin,now));
 for(const value of [o.access_hash,o.email,o.company])assert.equal(urls.includes(value),false);
});
test('cancel navigation keeps order and inventory state unchanged',async()=>{
 const o=order(),before=JSON.stringify(o),result=await inspect(await request(o,'cancel'),o);assert.equal(result.browserOutcome,'cancelled');assert.equal(result.paymentVerified,false);assert.equal(result.nextAction,'show_status_without_charge');assert.equal(JSON.stringify(o),before);
});
test('cancellation without a provider token is still a signed nonfinancial return',async()=>{
 const o=order();const result=await inspect(await request(o,'cancel',false),o);assert.equal(result.browserOutcome,'cancelled');assert.equal(result.paymentVerified,false);
});
test('modified order id or approval token is rejected',async()=>{
 for(const [key,value] of [['order','other'],['token','OTHER-ORDER']]){const o=order(),url=new URL((await request(o)).url);url.searchParams.set(key,value);await assert.rejects(inspect(new Request(url),o));}
});
test('changing cancellation into approval fails its purpose-bound signature',async()=>{
 const o=order(),url=new URL((await request(o,'cancel')).url);url.searchParams.set('flow','return');await assert.rejects(inspect(new Request(url),o));
});
test('modified expiry or forged signature is rejected',async()=>{
 for(const [key,value] of [['expires','2026-10-08T00:30:00.000Z'],['state','a'.repeat(64)]]){const o=order(),url=new URL((await request(o)).url);url.searchParams.set(key,value);await assert.rejects(inspect(new Request(url),o));}
});
test('duplicate security parameters are rejected',async()=>{
 for(const key of ['order','flow','expires','state','token']){const o=order(),url=new URL((await request(o)).url);url.searchParams.append(key,url.searchParams.get(key));await assert.rejects(inspect(new Request(url),o));}
});
test('an expired return asks for current status and never signals capture readiness',async()=>{
 const o=order(),result=await inspect(await request(o),o,now+3600000);assert.equal(result.reservationExpired,true);assert.equal(result.nextAction,'refresh_status');assert.equal(result.paymentVerified,false);
});
test('browser-provided completed status cannot declare a payment',async()=>{
 const o=order(),url=new URL((await request(o)).url);url.searchParams.set('status','COMPLETED');url.searchParams.set('paid','true');const result=await inspect(new Request(url),o);assert.equal(result.paymentVerified,false);
});
test('foreign origins, ambiguous bases and live orders cannot use sandbox returns',async()=>{
 const o=order(),url=new URL((await request(o)).url);url.host='example.com';await assert.rejects(inspect(new Request(url),o));
 for(const base of ['ftp://example.com','https://user:pass@example.com','https://example.com/path','http://example.com'])await assert.rejects(sandboxReturnUrls(o,base,now));
 await assert.rejects(sandboxReturnUrls({...o,payment_environment:'live'},origin,now));
});
test('POST is not accepted as a side-effect-free browser return',async()=>{
 const o=order();await assert.rejects(inspect(new Request((await request(o)).url,{method:'POST'}),o));
});
test('only a stored verified active order gets an already-paid result',async()=>{
 const o=order(),req=await request(o);const result=await inspect(req,{...o,state:'active',capture_id:'SYNTHETIC-CAPTURE',payment_verified_at:'2026-10-07T00:05:00.000Z'});
 assert.equal(result.paymentVerified,true);assert.equal(result.nextAction,'show_status');
 const pending=await inspect(req,{...o,state:'active'});assert.equal(pending.paymentVerified,false);
});
