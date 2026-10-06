import {catalog,AdError,sha256,text,quote,validateMaterials,verifyPayment} from './ad-sales-domain.js';
import {authorized} from './admin.js';
import {checkPayPalReadiness,createSponsorshipPayPalOrder,getPayPalOrder,getPayPalCapture,capturePayPalOrder} from './paypal.js';
import {SponsorshipRepository} from './sponsorship-repository.js';
const PREFIX='/v2/advertising';
const BASE_HEADERS={'cache-control':'no-store','x-content-type-options':'nosniff','referrer-policy':'no-referrer','x-robots-tag':'noindex, nofollow','x-frame-options':'DENY'};
const now=()=>new Date().toISOString();
const equal=(a,b)=>{if(typeof a!=='string'||typeof b!=='string'||a.length!==b.length)return false;let n=0;for(let i=0;i<a.length;i++)n|=a.charCodeAt(i)^b.charCodeAt(i);return n===0;};
function headers(req,env){return {...BASE_HEADERS,...(req.headers.get('origin')===env.ALLOWED_ORIGIN?{'access-control-allow-origin':env.ALLOWED_ORIGIN,'vary':'Origin'}:{})};}
function json(req,env,body,status=200){return new Response(JSON.stringify(body),{status,headers:{...headers(req,env),'content-type':'application/json; charset=utf-8'}});}
function paymentConfigured(env){return env.PAYPAL_ENVIRONMENT==='live'&&env.PAYPAL_CLIENT_ID&&env.PAYPAL_CLIENT_SECRET&&env.PAYPAL_MERCHANT_ID&&env.PAYPAL_WEBHOOK_ID&&env.ALLOWED_ORIGIN==='https://coshuma.com';}
function enabled(env){return env.IMAGE_AD_INTAKE_ENABLED==='true'&&env.ALLOWED_ORIGIN==='https://coshuma.com';}
function write(req,env){if(req.headers.get('origin')!==env.ALLOWED_ORIGIN)throw new AdError('Forbidden',403);}
async function readJson(req,max=2200000){
 if(!req.headers.get('content-type')?.startsWith('application/json'))throw new AdError('JSON is required',415);
 if(Number(req.headers.get('content-length')||0)>max)throw new AdError('Materials exceed the request limit',413);
 const reader=req.body?.getReader();let len=0;const chunks=[];if(reader)while(true){const v=await reader.read();if(v.done)break;len+=v.value.length;if(len>max){await reader.cancel();throw new AdError('Materials exceed the request limit',413);}chunks.push(v.value);}
 const bytes=new Uint8Array(len);let at=0;for(const c of chunks){bytes.set(c,at);at+=c.length;}try{return JSON.parse(new TextDecoder().decode(bytes));}catch{throw new AdError('Invalid JSON',400);}
}
const getApp=(db,id)=>db.prepare('SELECT * FROM ad_sales_applications WHERE id=?').bind(id).first();
const audit=(db,id,action,actor,detail)=>db.prepare('INSERT INTO ad_sales_audit VALUES(?,?,?,?,?,?)').bind(crypto.randomUUID(),id,action,actor,detail,now());
async function ready(db){if(!db)throw new AdError('Application service unavailable',503);await db.batch(['ad_sales_applications','ad_sales_assets','ad_sales_allocations','ad_sales_audit','ad_sales_readiness'].map(t=>db.prepare(`SELECT 1 FROM ${t} LIMIT 1`)));const r=await db.prepare("SELECT count(*) AS n FROM sqlite_master WHERE type='trigger' AND name IN ('ad_sales_terms_immutable','ad_sales_inventory_guard','ad_sales_publication_guard','ad_sales_terminal_stop','ad_sales_no_direct_publication')").first();if(r.n!==5)throw new AdError('Application service unavailable',503);}
async function access(req,db,id){const app=await getApp(db,id),token=req.headers.get('authorization')?.match(/^Bearer ([a-f0-9]{64})$/)?.[1];if(!app||!token||!equal(await sha256(token),app.token_hash))throw new AdError('Use your private application receipt to access this order',401);return app;}
function status(app){const q=JSON.parse(app.quote_json),state=app.state==='scheduled'?(now()>=q.endAt?'ended':now()>=q.startAt?'active':'scheduled'):app.state;return {id:app.id,reference:app.reference,advertiser:app.advertiser,product:app.product,quote:q,state,notes:app.review_notes||'',reviewedAt:app.reviewed_at,paymentVerified:!!app.verified_at&&['scheduled'].includes(app.state),verifiedAt:app.verified_at,createdAt:app.created_at};}
export async function imagePaymentReadiness(env,origin){
 const result=await checkPayPalReadiness(env,origin+'/v1/webhooks/paypal');
 const good=!!(paymentConfigured(env)&&result.providerAuthenticationVerified&&result.webhookUrlVerified&&result.requiredEventsVerified);
 await env.ORDERS.prepare('INSERT INTO ad_sales_readiness VALUES(1,?,?) ON CONFLICT(id) DO UPDATE SET checked_at=excluded.checked_at,result_json=excluded.result_json').bind(now(),JSON.stringify({good,...result})).run();return {good,...result};
}
async function providerReady(env){const r=await env.ORDERS.prepare('SELECT * FROM ad_sales_readiness WHERE id=1').first();return !!(paymentConfigured(env)&&env.IMAGE_AD_CHECKOUT_ENABLED==='true'&&r&&Date.now()-Date.parse(r.checked_at)<86400000&&JSON.parse(r.result_json).good);}
async function available(db,q){const result=[];for(const slot of q.slots){const p=catalog.positions.find(p=>p.id===slot),busy=await db.prepare("SELECT DISTINCT seat FROM ad_sales_allocations WHERE slot=? AND start_at<? AND end_at>? AND (payment_lock=1 OR hold_until>?)").bind(slot,q.endAt,q.startAt,now()).all();const seats=new Set((busy.results||[]).map(x=>x.seat));result.push({slot,capacity:p.capacity,available:p.capacity-seats.size});}return {available:result.every(x=>x.available>0),positions:result};}
async function reserve(db,app){
 const q=JSON.parse(app.quote_json);if(Date.parse(q.startAt)<=Date.now())throw new AdError('The requested start date has passed; submit a new selection',409);
 const exp=new Date(Date.now()+30*60000).toISOString(),statements=[db.prepare('DELETE FROM ad_sales_allocations WHERE application_id=? AND payment_lock=0').bind(app.id)];
 for(const slot of q.slots){const p=catalog.positions.find(p=>p.id===slot);statements.push(db.prepare(`INSERT INTO ad_sales_allocations(application_id,slot,seat,start_at,end_at,hold_until)
 VALUES(?,?,(SELECT seat FROM (SELECT 0 AS seat UNION ALL SELECT 1 UNION ALL SELECT 2) seats WHERE seats.seat<? AND NOT EXISTS(SELECT 1 FROM ad_sales_allocations r WHERE r.slot=? AND r.seat=seats.seat AND r.application_id!=? AND r.start_at<? AND r.end_at>? AND (r.payment_lock=1 OR r.hold_until>?)) ORDER BY seat LIMIT 1),?,?,?)`).bind(app.id,slot,p.capacity,slot,app.id,q.endAt,q.startAt,now(),q.startAt,q.endAt,exp));}
 statements.push(db.prepare("UPDATE ad_sales_applications SET state='awaiting_payment',updated_at=? WHERE id=? AND state IN ('approved','awaiting_payment')").bind(now(),app.id));
 try{await db.batch(statements);}catch{throw new AdError('The complete package is no longer available for these dates. No payment was taken.',409);}return exp;
}
async function stop(db,app,reason,reversed){if(['refunded','cancelled','rejected'].includes(app.state))return;await db.batch([db.prepare('UPDATE ad_sales_applications SET state=?,review_notes=?,updated_at=? WHERE id=?').bind(reversed?'refunded':'payment_review',reason,now(),app.id),audit(db,app.id,'payment_stop','verified-provider',reason)]);}
async function finalize(db,app,env,actor){
 if(['refunded','cancelled','rejected','paused','payment_review'].includes(app.state))throw new AdError('This order is stopped for review',409);
 const order=await getPayPalOrder(env,app.provider_order_id),caps=order.purchase_units?.flatMap(u=>u.payments?.captures||[])||[];
 if(caps.length!==1||!caps[0].id)throw new AdError('A completed payment has not yet been verified',409);
 const cap=await getPayPalCapture(env,caps[0].id),blocked=await new SponsorshipRepository(db).blockingPaymentEvent('live',order.id,cap.id);
 if(blocked||['REFUNDED','PARTIALLY_REFUNDED'].includes(cap.status)){await stop(db,app,'Payment reversed or disputed',true);throw new AdError('This payment cannot activate advertising',409);}
 let evidence;try{evidence=verifyPayment(order,cap,app,env);}catch(e){await stop(db,app,'Provider evidence requires reconciliation',false);throw e;}
 await db.batch([db.prepare('UPDATE ad_sales_allocations SET payment_lock=1 WHERE application_id=?').bind(app.id),db.prepare("UPDATE ad_sales_applications SET capture_id=?,merchant_id=?,verified_at=?,state='scheduled',updated_at=? WHERE id=? AND state IN ('capturing','awaiting_payment','approved','scheduled')").bind(evidence.captureId,evidence.merchant,now(),now(),app.id),audit(db,app.id,'payment_verified',actor,'Order, capture, merchant, currency and immutable gross amount matched')]);return getApp(db,app.id);
}
export async function handleImageAdWebhook(event,env,metadata){
 const db=env.ORDERS;try{await ready(db);}catch{return false;}let apps=[];
 if(metadata.relatedOrderId){const a=await db.prepare('SELECT * FROM ad_sales_applications WHERE provider_order_id=?').bind(metadata.relatedOrderId).first();if(a)apps.push(a);}
 for(const capture of metadata.captureIds||[]){const a=await db.prepare('SELECT * FROM ad_sales_applications WHERE capture_id=?').bind(capture).first();if(a&&!apps.some(x=>x.id===a.id))apps.push(a);}
 for(const app of apps){if(['PAYMENT.CAPTURE.REFUNDED','PAYMENT.CAPTURE.REVERSED'].includes(event.event_type))await stop(db,app,event.event_type,true);else if(event.event_type.startsWith('CUSTOMER.DISPUTE.')||['PAYMENT.CAPTURE.DENIED','PAYMENT.CAPTURE.DECLINED'].includes(event.event_type))await stop(db,app,event.event_type,false);else if(event.event_type==='PAYMENT.CAPTURE.COMPLETED'&&!['refunded','cancelled','rejected','paused','payment_review'].includes(app.state))await finalize(db,app,env,'signed-paypal-webhook');}return apps.length>0;
}
async function owner(req,env){const authEnv={...env,ADMIN_PATH:'/ops',ADMIN_USERNAME:'support@coshuma.com',ADMIN_PASSWORD_SHA256:env.OPS_PASSWORD_SHA256};if(!await authorized(req,authEnv,false))throw new AdError('Owner authentication required',401);if(!['GET','HEAD'].includes(req.method)&&req.headers.get('origin')!==new URL(req.url).origin)throw new AdError('Same-origin owner request required',403);}
async function assetResponse(req,env,asset){return new Response(new Uint8Array(asset.bytes),{headers:{...headers(req,env),'content-type':asset.media_type,'content-security-policy':"default-src 'none'; sandbox",'cross-origin-resource-policy':'cross-origin'}});}
export async function handleImageAdRequest(req,env){
 const u=new URL(req.url),admin=u.pathname.startsWith('/ops/image-ads');if(!u.pathname.startsWith(PREFIX)&&!admin)return null;const db=env.ORDERS;
 try{
  if(req.method==='OPTIONS'){write(req,env);return new Response(null,{status:204,headers:{...headers(req,env),'access-control-allow-methods':'GET,POST,OPTIONS','access-control-allow-headers':'content-type,authorization'}});}
  if(admin)await owner(req,env);await ready(db);
  if(admin){
   const suffix=u.pathname.slice('/ops/image-ads'.length);
   if(req.method==='POST'&&suffix==='/readiness'){await readJson(req,4096);return json(req,env,await imagePaymentReadiness(env,u.origin));}
   if(req.method==='GET'&&['','/applications'].includes(suffix)){const rows=(await db.prepare('SELECT * FROM ad_sales_applications ORDER BY created_at DESC LIMIT 50').all()).results||[];return json(req,env,{applications:rows.map(a=>({...status(a),email:a.email,billingName:a.billing_name,claims:a.claims,creatives:JSON.parse(a.creative_json)}))});}
   const am=/^\/assets\/([a-f0-9-]{36})$/.exec(suffix);if(req.method==='GET'&&am){const a=await db.prepare('SELECT * FROM ad_sales_assets WHERE id=?').bind(am[1]).first();if(!a)throw new AdError('Not found',404);return assetResponse(req,env,a);}
   const m=/^\/applications\/([a-f0-9-]{36})\/(review|pause|reconcile)$/.exec(suffix);if(req.method!=='POST'||!m)throw new AdError('Not found',404);let a=await getApp(db,m[1]);if(!a)throw new AdError('Not found',404);const input=await readJson(req,8192),note=text(input.notes,'Review notes',10,1000);
   if(m[2]==='review'){if(a.state!=='submitted'||!['approve','reject'].includes(input.decision)||input.assetsDecoded!==true)throw new AdError('Review all decoded images and unchanged materials first',409);await db.batch([db.prepare('UPDATE ad_sales_applications SET state=?,review_notes=?,reviewed_at=?,reviewed_by=?,updated_at=? WHERE id=? AND state=\'submitted\'').bind(input.decision==='approve'?'approved':'rejected',note,now(),'owner-ops-session',now(),a.id),audit(db,a.id,'materials_'+input.decision,'owner-ops-session',note)]);}
   if(m[2]==='pause'){if(!['scheduled','capturing','awaiting_payment'].includes(a.state))throw new AdError('Order is not active',409);await stop(db,a,note,false);}
   if(m[2]==='reconcile')await finalize(db,a,env,'owner-reconciliation');return json(req,env,status(await getApp(db,a.id)));
  }
  const path=u.pathname.slice(PREFIX.length);
  if(req.method==='GET'&&path==='/catalog'){
   const cached=await db.prepare('SELECT checked_at FROM ad_sales_readiness WHERE id=1').first();
   if(!cached||Date.now()-Date.parse(cached.checked_at)>3600000)await imagePaymentReadiness(env,u.origin);
   const paymentReady=await providerReady(env);return json(req,env,{...catalog,intakeReady:enabled(env),paymentReady,...(paymentReady?{publicClientId:env.PAYPAL_CLIENT_ID}:{})});
  }
  if(req.method==='GET'&&path==='/availability'){const q=quote(Object.fromEntries(u.searchParams));return json(req,env,{quote:q,...await available(db,q)});}
  if(req.method==='GET'&&path==='/placements'){
   let page=u.searchParams.get('path');if(page==='/compare/index.html')page='/compare/';if(page==='/best/')page='/best/index.html';if(!catalog.positions.some(p=>p.page===page))throw new AdError('Unknown page');
   const rows=(await db.prepare("SELECT a.* FROM ad_sales_applications a WHERE state='scheduled' AND merchant_id=? AND verified_at IS NOT NULL AND json_extract(quote_json,'$.startAt')<=? AND json_extract(quote_json,'$.endAt')>?").bind(env.PAYPAL_MERCHANT_ID||'',now(),now()).all()).results||[];const ads=[];
   for(const a of rows){const q=JSON.parse(a.quote_json);for(const c of JSON.parse(a.creative_json)){const p=catalog.positions.find(p=>p.id===c.slot&&p.page===page);if(p)ads.push({campaignId:a.id,advertiser:a.advertiser,product:a.product,position:p,creative:c,startAt:q.startAt,endAt:q.endAt,label:'Sponsored',imageUrl:u.origin+PREFIX+'/assets/'+c.imageId,logoUrl:u.origin+PREFIX+'/assets/'+c.logoId});}}
   return json(req,env,{ads});
  }
  const asset=/^\/assets\/([a-f0-9-]{36})$/.exec(path);if(req.method==='GET'&&asset){const a=await db.prepare("SELECT s.* FROM ad_sales_assets s JOIN ad_sales_applications a ON a.id=s.application_id WHERE s.id=? AND a.state='scheduled' AND a.merchant_id=? AND a.verified_at IS NOT NULL AND json_extract(a.quote_json,'$.startAt')<=? AND json_extract(a.quote_json,'$.endAt')>?").bind(asset[1],env.PAYPAL_MERCHANT_ID||'',now(),now()).first();if(!a)throw new AdError('Not found',404);return assetResponse(req,env,a);}
  if(req.method==='POST')write(req,env);
  if(req.method==='POST'&&path==='/applications'){
   if(!enabled(env))throw new AdError('Applications are temporarily unavailable',503);
   const gate=new SponsorshipRepository(db);await gate.rateLimit(await sha256(req.headers.get('cf-connecting-ip')||'unknown'),now());
   const cap=await db.prepare("SELECT count(*) AS n FROM ad_sales_applications WHERE state IN ('submitted','approved','awaiting_payment','capturing')").first();if(cap.n>=100)throw new AdError('The review queue is full. Try again later.',503);
   const v=await validateMaterials(await readJson(req)),id=crypto.randomUUID(),secret=Array.from(crypto.getRandomValues(new Uint8Array(32)),x=>x.toString(16).padStart(2,'0')).join(''),reference='COSHUMA-IMG-'+id;
   if(!(await available(db,v.quote)).available)throw new AdError('One or more selected positions are unavailable',409);
   const statements=[db.prepare('INSERT INTO ad_sales_applications(id,reference,token_hash,advertiser,product,email,billing_name,claims,quote_json,creative_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)').bind(id,reference,await sha256(secret),v.advertiser,v.product,v.email,v.billingName,v.claims,JSON.stringify(v.quote),JSON.stringify(v.creatives),now(),now())];
   for(const a of v.assets)statements.push(db.prepare('INSERT INTO ad_sales_assets VALUES(?,?,?,?,?,?,?,?,?)').bind(a.id,id,a.role,a.type,a.width,a.height,a.size,a.digest,a.bytes));
   statements.push(audit(db,id,'application_received','advertiser','Materials and fixed-price selection received; no charge and no reserved inventory'));
   await db.batch(statements);return json(req,env,{...status(await getApp(db,id)),accessToken:secret},201);
  }
  const m=/^\/applications\/([a-f0-9-]{36})(?:\/(order|capture|asset\/([a-f0-9-]{36})))?$/.exec(path);if(!m)throw new AdError('Not found',404);let a=await access(req,db,m[1]);
  if(req.method==='GET'&&!m[2])return json(req,env,{...status(a),paymentReady:await providerReady(env)});
  if(req.method==='GET'&&m[3]){const asset=await db.prepare('SELECT * FROM ad_sales_assets WHERE id=? AND application_id=?').bind(m[3],a.id).first();if(!asset)throw new AdError('Not found',404);return assetResponse(req,env,asset);}
  if(req.method!=='POST'||!['order','capture'].includes(m[2]))throw new AdError('Not found',404);const body=await readJson(req,4096);
  if(!await providerReady(env))throw new AdError('Payment is temporarily unavailable. Your application remains saved.',503);
  if(!a.reviewed_at||!a.reviewed_by||!['approved','awaiting_payment','capturing','scheduled'].includes(a.state))throw new AdError('Payment becomes available after material approval',409);
  if(m[2]==='order'){
   if(a.state==='scheduled')return json(req,env,{...status(a),orderId:a.provider_order_id});if(a.state==='capturing')throw new AdError('Payment is being verified; do not pay again',409);
   const expiry=await reserve(db,a),q=JSON.parse(a.quote_json);
   if(!a.provider_order_id){const result=await createSponsorshipPayPalOrder(env,a.id.replaceAll('-','')+'c',{intent:'CAPTURE',purchase_units:[{reference_id:a.id,custom_id:a.id,invoice_id:a.reference,description:(q.label+' / '+a.product).slice(0,127),payee:{merchant_id:env.PAYPAL_MERCHANT_ID},amount:{currency_code:'USD',value:q.amount}}]});if(!result.id||!['CREATED','APPROVED','PAYER_ACTION_REQUIRED'].includes(result.status))throw new AdError('The payment order was not created',502);await db.prepare('UPDATE ad_sales_applications SET provider_order_id=?,updated_at=? WHERE id=? AND provider_order_id IS NULL').bind(result.id,now(),a.id).run();a=await getApp(db,a.id);if(a.provider_order_id!==result.id)throw new AdError('Payment order could not be linked safely',409);}
   return json(req,env,{orderId:a.provider_order_id,holdUntil:expiry});
  }
  if(!a.provider_order_id||body.orderId!==a.provider_order_id)throw new AdError('Payment order mismatch',409);
  if(a.state==='scheduled')return json(req,env,status(a));
  if(a.state!=='capturing'){
   const q=JSON.parse(a.quote_json),rows=(await db.prepare('SELECT * FROM ad_sales_allocations WHERE application_id=? AND hold_until>?').bind(a.id,now()).all()).results||[];
   if(rows.length!==q.slots.length||Date.parse(q.startAt)<=Date.now())throw new AdError('The payment reservation has expired. No new charge was made.',409);
   await db.batch([db.prepare('UPDATE ad_sales_allocations SET payment_lock=1 WHERE application_id=? AND hold_until>?').bind(a.id,now()),db.prepare("UPDATE ad_sales_applications SET state='capturing',updated_at=? WHERE id=? AND state='awaiting_payment'").bind(now(),a.id)]);
  }
  a=await getApp(db,a.id);if(!['capturing','scheduled'].includes(a.state))throw new AdError('Payment could not be locked safely',409);const order=await getPayPalOrder(env,a.provider_order_id);
  if(order.status!=='COMPLETED')await capturePayPalOrder(env,a.provider_order_id,a.id.replaceAll('-','')+'p');
  a=await finalize(db,a,env,'advertiser-capture');return json(req,env,status(a));
 }catch(e){return json(req,env,{error:e instanceof AdError?e.message:'The service could not verify completion. Do not repeat a payment until its status is checked.'},e instanceof AdError?e.status:503);}
}

export async function maintainImageAds(env,origin='https://globalsaashub-payments.qmfforfhem.workers.dev') {
 await ready(env.ORDERS);await imagePaymentReadiness(env,origin);
 const rows=(await env.ORDERS.prepare("SELECT * FROM ad_sales_applications WHERE state='capturing' AND provider_order_id IS NOT NULL LIMIT 10").all()).results||[];
 for(const app of rows){try{await finalize(env.ORDERS,app,env,'scheduled-read-only-reconciliation');}catch{/* No new capture or automatic approval in reconciliation. */}}
}
