import { IMAGE_SLOTS, IMAGE_BUNDLES, CATALOG_VERSION } from './ad-commerce-catalog.js';
import { SponsorshipError as AdError, destinationUrl } from './sponsorship-domain.js';
export { AdError };
export function imageQuote(input={}) {
 const slot=IMAGE_SLOTS.find(s=>s.id===input.product);
 const bundle=IMAGE_BUNDLES.find(b=>b.id===input.product), days=Number(input.days);
 if ((!slot&&!bundle)||!Number.isInteger(days)||![7,30,90].includes(days)) throw new AdError('Choose a listed product and period.');
 if (['amount','currency','price'].some(k=>k in input)) throw new AdError('The server determines the total.');
 if (bundle&&days!==30) throw new AdError('Bundles run for 30 days.');
 if (bundle?.choices.length&&!bundle.choices.includes(input.rotation)) throw new AdError('Choose one shared position for P1.');
 const slots=slot?[slot.id]:[...bundle.slots,...(bundle.choices.length?[input.rotation]:[])];
 return {version:CATALOG_VERSION,product:input.product,days,slots,amount:(bundle?.price??slot.prices[days]).toFixed(2),currency:'USD'};
}
export function plain(value,label,min,max) {
 if (typeof value!=='string') throw new AdError(label+' is required.');
 const s=value.trim();
 if(s.length<min||s.length>max||/[\u0000-\u001f\u007f<>]/.test(s)) throw new AdError(label+' has invalid text or length.');
 return s;
}
export function orderInput(input) {
 const quote=imageQuote(input);
 if (input.rightsConfirmed!==true||input.termsVersion!==CATALOG_VERSION) throw new AdError('Confirm current terms, accuracy and usage rights.');
 const company=plain(input.company,'Advertiser',1,120), productName=plain(input.productName,'Product',1,120), email=plain(input.email,'Email',3,254);
 if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new AdError('Enter a valid email.');
 if(!Array.isArray(input.items)||input.items.length!==quote.slots.length) throw new AdError('Provide every selected position.');
 const items=quote.slots.map(slot=>{
  const i=input.items.find(i=>i.slot===slot);if(!i)throw new AdError('Missing position.');
  return {slot,headline:plain(i.headline,'Headline',5,80),description:plain(i.description,'Description',20,240),button:plain(i.button,'Button',2,30),alt:plain(i.alt,'Image description',10,160),url:destinationUrl(i.url)};
 });
 return {quote,company,productName,email,items,claims:plain(input.claims,'Sources and relevance',10,1800)};
}
export const digest=async value=>{
 const bytes=typeof value==='string'?new TextEncoder().encode(value):value;
 return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
};
export const newToken=()=>Array.from(crypto.getRandomValues(new Uint8Array(32)),b=>b.toString(16).padStart(2,'0')).join('');
