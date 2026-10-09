// Dedicated HTTPS Sandbox entry. Never imported by the production worker.
import { AdStore } from './ad-commerce-store.js';
import { SandboxAdPayments } from './ad-commerce-sandbox-payments.js';
import { SandboxAdWebhooks } from './ad-commerce-sandbox-webhooks.js';
import { createPublicAdSandboxHandler } from './ad-commerce-sandbox-http.js';
import { renderSandboxPurchasePage } from './ad-commerce-sandbox-purchase-page.js';
import { assertSandboxWebhookRegistration } from './ad-commerce-public-preflight.js';
import { AdError, digest } from './ad-commerce-domain.js';

const SCOPE='coshuma-ads-sandbox-v1';
let instanceId;
const API='https://api-m.sandbox.paypal.com';
const CUSTOM_ORIGINS=new Set(['https://ads-sandbox.coshuma.com','https://coshuma-ads-sandbox-gateway.pages.dev']);
const WORKERS_ORIGIN=/^https:\/\/coshuma-ads-sandbox-[a-z0-9-]+\.[a-z0-9-]+\.workers\.dev$/;
const publicOrigin=value=>CUSTOM_ORIGINS.has(value)||WORKERS_ORIGIN.test(value||'');
const legacyOrigin=value=>WORKERS_ORIGIN.test(value||'');
const reply=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{
 'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Referrer-Policy':'no-referrer',
 'X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'"}});
function boundary(env){
 if(env.PAYPAL_ENVIRONMENT!=='sandbox'||env.SANDBOX_ISOLATION!==SCOPE||env.ORDERS||
   !/^[A-Za-z0-9_-]{32,}$/.test(env.SANDBOX_REVIEW_KEY||'')||
   !/^[A-Za-z0-9_-]{32,}$/.test(env.SANDBOX_OPERATOR_KEY||'')||env.SANDBOX_OPERATOR_KEY===env.SANDBOX_REVIEW_KEY||
   !env.AD_SANDBOX_DB?.prepare||!/^coshuma-ads-sandbox-[a-z0-9-]+$/.test(env.SANDBOX_DATABASE_LABEL||'')||
   !publicOrigin(env.SANDBOX_ORIGIN)||(env.SANDBOX_LEGACY_ORIGIN&&!legacyOrigin(env.SANDBOX_LEGACY_ORIGIN))) {
  throw new AdError('Isolated test configuration is required.',503);
 }
}
async function operator(request,env){
 const value=/^Bearer ([A-Za-z0-9_-]{32,})$/.exec(request.headers.get('authorization')||'')?.[1];
 if(!value||!env.SANDBOX_OPERATOR_KEY||await digest(value)!==await digest(env.SANDBOX_OPERATOR_KEY))
  throw new AdError('Test operator authentication required.',403);
}
async function input(request){
 if(request.headers.get('content-type')!=='application/json')throw new AdError('JSON required.',415);
 const length=Number(request.headers.get('content-length')||0);
 if(length>4096)throw new AdError('Body too large.',413);
 const bytes=await request.arrayBuffer();if(bytes.byteLength>4096)throw new AdError('Body too large.',413);
 try{return JSON.parse(new TextDecoder().decode(bytes));}catch{throw new AdError('Invalid JSON.',400);}
}
async function runtime(env,request){
 boundary(env);
 instanceId ??= crypto.randomUUID();
 const db=env.AD_SANDBOX_DB;
 const marker=await db.prepare('SELECT value FROM ad_sandbox_runtime WHERE key=?').bind('scope').first();
 if(marker?.value!==SCOPE)throw new AdError('A dedicated test database is required.',503);
 const base=new AdStore(db,{environment:'sandbox'});
 await base.ready();
 const store=base;
 async function record(kind,data){
  await base.q('INSERT INTO ad_sandbox_evidence(id,kind,detail_json,instance_id,created_at) VALUES(?,?,?,?,?)',
   crypto.randomUUID(),kind,JSON.stringify(data),instanceId,new Date().toISOString()).run();
 }
 const transport=async(url,init={})=>{
  const target=new URL(url),method=init.method||'GET';
  const allowed=target.origin===API&&!target.username&&!target.password&&!target.hash&&(
   method==='POST'&&target.pathname==='/v1/oauth2/token'||
   method==='GET'&&target.pathname==='/v1/notifications/webhooks'||
   method==='POST'&&target.pathname==='/v1/notifications/verify-webhook-signature'||
   method==='POST'&&target.pathname==='/v2/checkout/orders'||
   method==='GET'&&/^\/v2\/checkout\/orders\/[A-Za-z0-9_-]+$/.test(target.pathname)||
   method==='POST'&&/^\/v2\/checkout\/orders\/[A-Za-z0-9_-]+\/capture$/.test(target.pathname)||
   method==='GET'&&/^\/v2\/payments\/captures\/[A-Za-z0-9_-]+$/.test(target.pathname));
  if(!allowed)throw new AdError('Only required Sandbox operations are allowed.',503);
  const response=await fetch(target.href,{...init,redirect:'manual',signal:AbortSignal.timeout(20000)});
  if((response.status>=300&&response.status<400)||response.headers.get('location')){
   await record('provider_response',{method,path:target.pathname,status:response.status,redirectRejected:true});
   throw new AdError('Provider redirects are not accepted.',503);
  }
  const detail={method,path:target.pathname,status:response.status};
  if(target.pathname==='/v1/notifications/verify-webhook-signature'){
   const result=await response.clone().json().catch(()=>({}));
   detail.verificationStatus=result.verification_status||'UNKNOWN';
  }
  await record('provider_response',detail);
  const match=/^\/v2\/checkout\/orders\/([A-Za-z0-9_-]+)\/capture$/.exec(target.pathname);
  if(match&&method==='POST'&&response.ok){
   const row=await base.q('SELECT f.order_id FROM ad_sandbox_faults f JOIN ad_sale_orders o ON o.id=f.order_id WHERE o.provider_order=? AND f.kind=? AND f.consumed_at IS NULL',
    match[1],'lose_capture_response').first();
   if(row){
    const claimed=await base.q('UPDATE ad_sandbox_faults SET consumed_at=? WHERE order_id=? AND kind=? AND consumed_at IS NULL',
     new Date().toISOString(),row.order_id,'lose_capture_response').run();
    if(claimed.meta.changes===1){
     await record('actual_capture_response_intentionally_lost',{orderId:row.order_id,providerOrder:match[1]});
     throw new AdError('The test capture response was lost; await verified webhook recovery.',503);
    }
   }
  }
  return response;
 };
 const payments=new SandboxAdPayments(store,{env,fetchImpl:transport,returnOrigin:env.SANDBOX_ORIGIN});
 const webhooks=new SandboxAdWebhooks(store,payments,{env,fetchImpl:transport,durableInbox:true});
 await webhooks.ready();
 return {base,store,payments,webhooks,record,transport};
}
async function execute(request,env,ctx){
 try{
  boundary(env);
  instanceId ??= crypto.randomUUID();
  const url=new URL(request.url);
  const primaryOrigin=url.origin===env.SANDBOX_ORIGIN;
  const legacyAllowed=url.origin===env.SANDBOX_LEGACY_ORIGIN&&(url.pathname==='/health'||url.pathname==='/sandbox/webhooks/paypal');
  if(!primaryOrigin&&!legacyAllowed)return reply({error:'Unexpected test origin.'},403);
  if(request.headers.has('x-sandbox-clock-order'))return reply({error:'A request-wide test clock is not permitted.'},403);
  let canonical;
  try{canonical=url.pathname.split('/').map(part=>encodeURIComponent(decodeURIComponent(part))).join('/');}
  catch{return reply({error:'Invalid path.'},400);}
  if(canonical!==url.pathname||url.pathname.includes('//')||url.pathname.endsWith('/'))return reply({error:'Canonical paths are required.'},400);
  if(url.pathname==='/health'&&request.method==='GET')return reply({environment:'sandbox',scope:SCOPE,instanceId,build:env.SANDBOX_BUILD||'unknown'});
  if(url.pathname==='/sandbox/purchase'&&request.method==='GET')return renderSandboxPurchasePage();
  const rt=await runtime(env,request);
  if(url.pathname.startsWith('/sandbox/ops/')){
   await operator(request,env);
   if(request.method==='POST'&&request.headers.get('origin')!==env.SANDBOX_ORIGIN)return reply({error:'Matching origin required.'},403);
   if(url.pathname==='/sandbox/ops/provider-probe'&&request.method==='GET'){
    try{
     const response=await rt.transport(API+'/v1/oauth2/token',{method:'POST',
      headers:{Authorization:'Basic '+btoa(env.PAYPAL_CLIENT_ID+':'+env.PAYPAL_CLIENT_SECRET),
       'Content-Type':'application/x-www-form-urlencoded',Accept:'application/json'},
      body:'grant_type=client_credentials'});
     return reply({ok:response.ok,status:response.status,redirected:response.redirected,
      type:response.type,hasLocation:response.headers.has('location')});
    }catch(error){
     return reply({ok:false,errorName:error?.name||'unknown',errorMessage:String(error?.message||'').slice(0,120)});
    }
   }
   if(url.pathname==='/sandbox/ops/preflight'&&request.method==='GET'){
    const result=await assertSandboxWebhookRegistration(env,rt.transport);
    await rt.record('registration_preflight',result);return reply(result);
   }
   if(url.pathname==='/sandbox/ops/evidence'&&request.method==='GET'){
    const evidence=(await rt.base.q('SELECT kind,detail_json,instance_id,created_at FROM ad_sandbox_evidence ORDER BY created_at DESC LIMIT 200').all()).results;
    return reply({instanceId,build:env.SANDBOX_BUILD,evidence});
   }
   if(url.pathname==='/sandbox/ops/receipt'&&request.method==='GET'){
    const id=url.searchParams.get('event');if(!id||!/^[A-Za-z0-9_-]{1,128}$/.test(id))return reply({error:'Event ID required.'},400);
    return reply({receipt:await rt.webhooks.receipt(id),instanceId,build:env.SANDBOX_BUILD});
   }
   if(url.pathname==='/sandbox/ops/drain'&&request.method==='POST'){
    return reply({result:await rt.webhooks.drain({limit:10})});
   }
   if(url.pathname==='/sandbox/ops/fault'&&request.method==='POST'){
    const data=await input(request);const order=await rt.base.get(data.orderId);
    if(data.kind!=='lose_capture_response'||!order||order.state!=='checkout')return reply({error:'A checkout test order is required.'},409);
    await rt.base.q('INSERT INTO ad_sandbox_faults(order_id,kind,created_at) VALUES(?,?,?) ON CONFLICT(order_id,kind) DO NOTHING',
     order.id,data.kind,new Date().toISOString()).run();
    return reply({armed:true,orderId:order.id});
   }
   if(url.pathname==='/sandbox/ops/renew-hold'&&request.method==='POST'){
    const data=await input(request);
    const order=await rt.payments.renewApprovedCheckout(data.orderId);
    await rt.record('checkout_reservation_renewed',{orderId:order.id,holdUntil:order.hold_until});
    return reply({orderId:order.id,state:order.state,holdUntil:order.hold_until,renewed:true});
   }
   if(url.pathname==='/sandbox/ops/expire-order'&&request.method==='POST'){
    const data=await input(request);const order=await rt.base.get(data.orderId);
    if(!order||order.state!=='active'||order.payment_environment!=='sandbox')return reply({error:'An active test order is required.'},409);
    const offset=Math.max(0,Date.parse(order.ends_at)-Date.now()+1000);
    await rt.base.q('INSERT INTO ad_sandbox_clocks(order_id,offset_ms) VALUES(?,?) ON CONFLICT(order_id) DO UPDATE SET offset_ms=excluded.offset_ms',order.id,offset).run();
    // Only this order is exposed to the accelerated clock; other orders use real time.
    const at=new Date(Date.now()+offset).toISOString();
    await rt.base.db.batch([
     rt.base.q("UPDATE ad_sale_orders SET state='ended',updated_at=? WHERE id=? AND state='active' AND ends_at<=?",at,order.id,at),
     rt.base.q("INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at) SELECT ?,?,'sandbox_period_ended','sandbox_test_clock','One-order accelerated expiry',? WHERE changes()=1",crypto.randomUUID(),order.id,at),
     rt.base.q("DELETE FROM ad_sale_holds WHERE order_id=? AND EXISTS(SELECT 1 FROM ad_sale_orders WHERE id=? AND state='ended')",order.id,order.id)
    ]);
    await rt.record('single_order_accelerated_expiry',{orderId:order.id,offset});
    return reply({orderId:order.id,state:(await rt.base.get(order.id)).state,accelerated:true});
   }
   return reply({error:'Unknown operator route.'},404);
  }
  const handler=createPublicAdSandboxHandler({store:rt.store,payments:rt.payments,webhooks:rt.webhooks,
   environment:'sandbox',origin:env.SANDBOX_ORIGIN,isolation:'coshuma-ads-sandbox',
   reviewKey:env.SANDBOX_REVIEW_KEY,operatorKey:env.SANDBOX_OPERATOR_KEY,
   beforePaymentMutation:async()=>{
    const result=await assertSandboxWebhookRegistration(env,rt.transport);
    await rt.record('registration_preflight',result);
   }});
  const handlerRequest=legacyAllowed?new Request(env.SANDBOX_ORIGIN+url.pathname+url.search,request):request;
  const response=await handler(handlerRequest);
  if(url.pathname==='/sandbox/webhooks/paypal'){
   await rt.record('webhook_http_result',{status:response.status});
  }
  return response;
 }catch(error){
  return reply({error:error instanceof AdError?error.message:'Public sandbox operation failed.'},error instanceof AdError?error.status:503);
 }
}
export default {
 fetch:execute,
 async scheduled(controller,env,ctx){
  const job=(async()=>{
   const rt=await runtime(env);
   const result=await rt.webhooks.drain({limit:10});
   const ended=await rt.payments.expire();
   await rt.record('scheduled_completed',{cron:controller.cron,result,ended});
  })();
  ctx.waitUntil(job);
 }
};
