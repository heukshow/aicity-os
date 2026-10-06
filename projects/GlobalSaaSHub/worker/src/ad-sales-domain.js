import catalog from '../../data/advertising-sales-catalog.json' with { type:'json' };
export { catalog };
export class AdError extends Error { constructor(message,status=422){super(message);this.status=status;} }
export const sha256=async value=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',typeof value==='string'?new TextEncoder().encode(value):value)),x=>x.toString(16).padStart(2,'0')).join('');
export function text(v,name,min,max){if(typeof v!=='string')throw new AdError(`${name} is required`);v=v.trim();if(v.length<min||v.length>max||/[<>\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(v))throw new AdError(`${name}: use plain text (${min}-${max} characters)`);return v;}
export function https(v){let u;try{u=new URL(v);}catch{throw new AdError('Use a valid HTTPS destination');}if(u.protocol!=='https:'||u.username||u.password||u.href.length>1000||!u.hostname.includes('.')||u.hostname.endsWith('.local')||u.hostname.endsWith('.localhost')||/^\d+(\.\d+){3}$/.test(u.hostname)||u.hostname.includes(':'))throw new AdError('Use a public HTTPS destination without credentials');return u.href;}
export function quote(input,now=new Date()){
 if(!input||typeof input!=='object'||Array.isArray(input))throw new AdError('An order selection is required');
 if(['amount','price','currency','approved','paymentVerified'].some(k=>k in input))throw new AdError('The server sets price and approval');
 const p=catalog.positions.find(x=>x.id===input.productId)||catalog.bundles.find(x=>x.id===input.productId);const days=Number(input.durationDays);
 if(!p||!Number.isInteger(days)||!Object.hasOwn(p.prices,String(days)))throw new AdError('Select a listed product and duration');
 let slots;if(p.fixed){slots=[...p.fixed];if(p.chooseOne.length){if(!p.chooseOne.includes(input.rotation))throw new AdError('P1 requires one listed rotating position');slots.push(input.rotation);}else if(input.rotation)throw new AdError('This package has no optional rotating position');}else{slots=[p.id];if(input.rotation)throw new AdError('Select only one position');}
 const date=input.startDate;if(typeof date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(date))throw new AdError('Choose a start date');
 const start=new Date(date+'T00:00:00.000Z');const today=Date.parse(now.toISOString().slice(0,10)+'T00:00:00Z');
 if(!Number.isFinite(start.getTime())||start.toISOString().slice(0,10)!==date||start.getTime()<today+2*86400000||start.getTime()>today+120*86400000)throw new AdError('Choose a start date 2 to 120 days ahead (UTC)');
 return {version:catalog.version,productId:p.id,label:p.label,durationDays:days,slots,amount:p.prices[days].toFixed(2),currency:'USD',startAt:start.toISOString(),endAt:new Date(start.getTime()+days*86400000).toISOString()};
}
function u32(b,n){return new DataView(b.buffer,b.byteOffset,b.byteLength).getUint32(n,false);}
function ascii(b,a,n){return String.fromCharCode(...b.slice(a,a+n));}
export function imageInfo(b){
 if(!(b instanceof Uint8Array)||b.length<24)throw new AdError('The image file is incomplete');
 if(ascii(b,1,3)==='PNG'&&b[0]===137){
  if(ascii(b,12,4)!=='IHDR'||u32(b,8)!==13)throw new AdError('Invalid PNG header');
  let pos=8,ended=false,alpha=b[25]===4||b[25]===6;
  while(pos+12<=b.length){const n=u32(b,pos),kind=ascii(b,pos+4,4);if(n>b.length-pos-12)throw new AdError('Invalid PNG chunk');if(kind==='acTL')throw new AdError('Animated files are not accepted');if(kind==='tRNS')alpha=true;pos+=n+12;if(kind==='IEND'){ended=true;break;}}
  if(!ended||pos!==b.length)throw new AdError('Invalid PNG structure');return {width:u32(b,16),height:u32(b,20),type:'image/png',alpha};
 }
 if(b[0]===255&&b[1]===216){let i=2;while(i+9<b.length){if(b[i++]!==255)throw new AdError('Invalid JPEG structure');while(b[i]===255)i++;const m=b[i++];if(m===217||m===218)break;if(m===1||(m>=208&&m<=215))continue;const n=(b[i]<<8)|b[i+1];if(n<2||i+n>b.length)throw new AdError('Invalid JPEG segment');if([192,193,194].includes(m)){if(b[b.length-2]!==255||b[b.length-1]!==217)throw new AdError('Incomplete JPEG');return {height:(b[i+3]<<8)|b[i+4],width:(b[i+5]<<8)|b[i+6],type:'image/jpeg',alpha:false};}i+=n;}throw new AdError('Unsupported JPEG');}
 if(ascii(b,0,4)==='RIFF'&&ascii(b,8,4)==='WEBP'){
  const dv=new DataView(b.buffer,b.byteOffset,b.byteLength);if(dv.getUint32(4,true)+8!==b.length)throw new AdError('Invalid WebP length');const kind=ascii(b,12,4);
  if(kind==='VP8X'){if(b[20]&2)throw new AdError('Animated files are not accepted');return {width:1+b[24]+(b[25]<<8)+(b[26]<<16),height:1+b[27]+(b[28]<<8)+(b[29]<<16),type:'image/webp',alpha:!!(b[20]&16)};}
  if(kind==='VP8 '&&b[23]===157&&b[24]===1&&b[25]===42)return {width:(b[26]|b[27]<<8)&16383,height:(b[28]|b[29]<<8)&16383,type:'image/webp',alpha:false};
  if(kind==='VP8L'&&b[20]===47)return {width:1+b[21]+((b[22]&63)<<8),height:1+(b[22]>>6)+(b[23]<<2)+((b[24]&15)<<10),type:'image/webp',alpha:!!(b[24]&16)};
 }
 throw new AdError('Use a static PNG, JPG or WebP image');
}
export async function imageAsset(file,spec,role){
 if(!file||typeof file.base64!=='string'||file.base64.length>Math.ceil(spec.maxBytes/3)*4||!/^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(file.base64))throw new AdError(`${role}: invalid file or file too large`);
 let raw;try{raw=atob(file.base64);}catch{throw new AdError('Invalid image encoding');}const bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));if(bytes.length>spec.maxBytes)throw new AdError(`${role}: file size exceeds the limit`);
 const info=imageInfo(bytes);if(info.width!==spec.width||info.height!==spec.height)throw new AdError(`${role}: required size ${spec.width} x ${spec.height} px`);
 if(role==='logo'&&(info.type!=='image/png'||!info.alpha))throw new AdError('The separate logo must be a transparent PNG');
 return {id:crypto.randomUUID(),role,...info,size:bytes.length,digest:await sha256(bytes),bytes:Array.from(bytes)};
}
export async function validateMaterials(input,now=new Date()){
 const q=quote(input,now);const email=text(input.email,'Contact email',5,254);if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))throw new AdError('Use a valid contact email');
 if(input.rightsConfirmed!==true||input.termsAccepted!==true)throw new AdError('Confirm material rights and the published advertising terms');
 const advertiser=text(input.advertiser,'Advertiser',1,120),product=text(input.product,'Product',1,120),billingName=text(input.billingName,'Billing name',1,120),claims=text(input.claims,'Claims and usage rights evidence',10,2500);
 if(!Array.isArray(input.creatives)||input.creatives.length!==q.slots.length)throw new AdError('Submit one creative per included position');
 const logo=await imageAsset(input.logo,catalog.logo,'logo');const assets=[logo],creatives=[];
 for(const slot of q.slots){const matches=input.creatives.filter(c=>c.slot===slot);if(matches.length!==1)throw new AdError('Every position requires exactly one creative');const c=matches[0],spec=catalog.positions.find(p=>p.id===slot),asset=await imageAsset(c.image,spec,slot);assets.push(asset);creatives.push({slot,imageId:asset.id,logoId:logo.id,title:text(c.title,'Headline',5,80),body:text(c.body,'Description',20,240),button:text(c.button,'Button',2,30),alt:text(c.alt,'Image description',10,160),url:https(c.url)});}
 return {quote:q,advertiser,product,billingName,email,claims,assets,creatives};
}
export function verifyPayment(order,capture,app,env){
 const q=JSON.parse(app.quote_json),u=order?.purchase_units?.[0],cs=u?.payments?.captures;const amount=a=>a?.currency_code==='USD'&&a.value===q.amount;
 if(env.PAYPAL_ENVIRONMENT!=='live'||!env.PAYPAL_MERCHANT_ID||order?.id!==app.provider_order_id||order.status!=='COMPLETED'||order.purchase_units.length!==1||u.custom_id!==app.id||u.invoice_id!==app.reference||u.payee?.merchant_id!==env.PAYPAL_MERCHANT_ID||!amount(u.amount)||!Array.isArray(cs)||cs.length!==1||cs[0].id!==capture?.id||cs[0].status!=='COMPLETED'||!amount(cs[0].amount)||capture.status!=='COMPLETED'||!amount(capture.amount)||capture.payee?.merchant_id!==env.PAYPAL_MERCHANT_ID||capture.supplementary_data?.related_ids?.order_id!==order.id)throw new AdError('The completed payment does not match the order',409);
 return {captureId:capture.id,merchant:env.PAYPAL_MERCHANT_ID};
}
