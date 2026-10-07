// Side-effect-free sandbox return/cancel validation. A redirect is never proof of payment.
import { AdError } from './ad-commerce-domain.js';
const fail=()=>{throw new AdError('The checkout return does not match this order.',403);};
function trustedOrigin(value){
  let url;try{url=new URL(value);}catch{fail();}
  if(url.origin!==value||url.username||url.password||url.search||url.hash||
    !(url.protocol==='https:'||(url.protocol==='http:'&&['localhost','127.0.0.1','[::1]'].includes(url.hostname))))fail();
  return url.origin;
}
async function signature(order,origin,flow,expires){
  if(!/^[a-f0-9]{64}$/.test(order.access_hash||''))fail();
  const bytes=Uint8Array.from(order.access_hash.match(/../g),x=>parseInt(x,16));
  const key=await crypto.subtle.importKey('raw',bytes,{name:'HMAC',hash:'SHA-256'},false,['sign']);
  const message=['ad-return-v1',order.id,order.reference,origin,flow,expires].join('|');
  return Array.from(new Uint8Array(await crypto.subtle.sign('HMAC',key,new TextEncoder().encode(message))),b=>b.toString(16).padStart(2,'0')).join('');
}
function equal(a,b){if(typeof a!=='string'||a.length!==b.length)return false;let n=0;for(let i=0;i<a.length;i++)n|=a.charCodeAt(i)^b.charCodeAt(i);return n===0;}
export async function sandboxReturnUrls(order,origin,now=Date.now()){
  origin=trustedOrigin(origin);
  if(!['approved','checkout'].includes(order.state)||!order.hold_until||Date.parse(order.hold_until)<=now)fail();
  if(order.payment_environment&&order.payment_environment!=='sandbox')fail();
  const urls={};
  for(const flow of ['return','cancel']){
    const url=new URL('/sandbox/checkout-return',origin);
    for(const [key,value] of Object.entries({order:order.id,flow,expires:order.hold_until,state:await signature(order,origin,flow,order.hold_until)}))url.searchParams.set(key,value);
    urls[flow==='return'?'return_url':'cancel_url']=url.href;
  }
  return urls;
}
export async function inspectSandboxReturn(request,order,{origin,now=Date.now()}={}){
  origin=trustedOrigin(origin);
  const url=new URL(request.url);
  if(request.method!=='GET'||url.origin!==origin||url.pathname!=='/sandbox/checkout-return'||order.payment_environment!=='sandbox')fail();
  const query=url.searchParams,flow=query.get('flow'),expires=query.get('expires');
  for(const key of ['order','flow','expires','state'])if(query.getAll(key).length!==1)fail();
  if(!['return','cancel'].includes(flow)||query.get('order')!==order.id||!order.provider_order)fail();
  if(query.getAll('token').length>1||(flow==='return'&&!query.has('token'))||
    (query.has('token')&&query.get('token')!==order.provider_order))fail();
  const time=Date.parse(expires);
  if(!Number.isFinite(time)||new Date(time).toISOString()!==expires||!equal(query.get('state'),await signature(order,origin,flow,expires)))fail();
  // No GET can capture, refund, cancel an order, release inventory or declare an unverified payment.
  const verified=['active','ended'].includes(order.state)&&Boolean(order.capture_id)&&Number.isFinite(Date.parse(order.payment_verified_at));
  return {orderId:order.id,browserOutcome:flow==='cancel'?'cancelled':'returned',
    storedState:order.state,paymentVerified:verified,reservationExpired:time<=now,
    nextAction:verified?'show_status':flow==='cancel'?'show_status_without_charge':time<=now?'refresh_status':'confirm_with_authenticated_post'};
}
