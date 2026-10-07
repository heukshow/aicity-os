// Isolated unit tests. No network, credentials, transactions or production database.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { IMAGE_SLOTS, IMAGE_BUNDLES, CATALOG_VERSION } from '../src/ad-commerce-catalog.js';
import { imageQuote, orderInput, digest, newToken } from '../src/ad-commerce-domain.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';
const expected={
 'tool-primary':[19,49,129], 'buyer-intent-top':[39,99,269],
 'compare-decision-premium':[59,149,399], 'buyer-hub-fixed':[24,59,159],
 'comparison-hub-fixed':[24,59,159], 'tool-rotation':[16,39,105],
 'guide-rotation':[16,39,105], 'compare-rotation':[16,39,105]
};
for(const slot of IMAGE_SLOTS)for(const [i,days] of [7,30,90].entries()){
 test(`server quote ${slot.code} / ${days} days`,()=>{
  const q=imageQuote({product:slot.id,days});
  assert.equal(q.amount,expected[slot.id][i].toFixed(2));
  assert.equal(q.currency,'USD');assert.equal(q.version,CATALOG_VERSION);
  assert.deepEqual(q.slots,[slot.id]);
 });
}
for(const bundle of IMAGE_BUNDLES)for(const rotation of bundle.choices.length?bundle.choices:[undefined]){
 test(`bundle ${bundle.id} / ${rotation||'fixed'}`,()=>{
  const q=imageQuote({product:bundle.id,days:30,rotation});
  assert.equal(q.amount,bundle.price.toFixed(2));assert.equal(q.slots.length,2);
  assert.equal(new Set(q.slots).size,2);
  assert.equal(new Set(q.slots.map(id=>IMAGE_SLOTS.find(s=>s.id===id).path)).size,2);
 });
}
test('every exact placement and file limit is defined',()=>{
 assert.equal(IMAGE_SLOTS.length,8);assert.equal(IMAGE_BUNDLES.length,3);
 assert.equal(IMAGE_SLOTS.filter(s=>s.mode==='fixed').length,5);
 for(const s of IMAGE_SLOTS){assert.equal(s.capacity,s.mode==='fixed'?1:3);assert.deepEqual(AD_ASSET_SPECS[s.id],{width:s.width,height:s.height,maxBytes:s.maxBytes});}
 assert.deepEqual(AD_ASSET_SPECS.logo,{width:400,height:400,maxBytes:100000});
});
test('client prices and unsupported combinations are rejected',()=>{
 for(const key of ['amount','currency','price'])assert.throws(()=>imageQuote({product:'tool-primary',days:30,[key]:'0.01'}));
 for(const days of [0,-1,1,180,7.5,'NaN'])assert.throws(()=>imageQuote({product:'tool-primary',days}));
 for(const product of ['homepage','unknown','P4'])assert.throws(()=>imageQuote({product,days:30}));
 assert.throws(()=>imageQuote({product:'P1',days:30}));
 assert.throws(()=>imageQuote({product:'P1',days:30,rotation:'tool-primary'}));
 assert.throws(()=>imageQuote({product:'P2',days:7}));
});
function input(){return {product:'tool-primary',days:30,termsVersion:CATALOG_VERSION,rightsConfirmed:true,
 company:'LOCAL TEST ONLY',productName:'Test software',email:'test@example.com',claims:'Local fixture, not an advertiser submission.',
 items:[{slot:'tool-primary',headline:'Local fixture title',description:'This fixture is only for an isolated unit test.',button:'View product',alt:'Local test image description',url:'https://example.com/product'}]};}
test('complete material fields validate without external requests',()=>{
 const x=orderInput(input());assert.equal(x.quote.amount,'49.00');assert.equal(x.items.length,1);
});
test('unconfirmed rights, changed terms and incomplete materials are rejected',()=>{
 for(const patch of [{rightsConfirmed:false},{termsVersion:'old'},{email:'not an email'},{items:[]},{claims:''}])assert.throws(()=>orderInput({...input(),...patch}));
 const x=input();x.items[0].headline='<script>';assert.throws(()=>orderInput(x));
});
test('unsafe destinations are rejected',()=>{
 for(const url of ['http://example.com/','javascript:alert(1)','https://127.0.0.1/','https://localhost/','https://user:pass@example.com/']){
  const x=input();x.items[0].url=url;assert.throws(()=>orderInput(x));
 }
});
test('order access token and digest have expected encodings',async()=>{
 const a=newToken(),b=newToken();assert.match(a,/^[a-f0-9]{64}$/);assert.notEqual(a,b);
 const hash=await digest(a);assert.match(hash,/^[a-f0-9]{64}$/);assert.notEqual(a,hash);
});


test('canonical repository removes legacy header-only image acceptance and ambiguous store API', async () => {
 const api = await import('../src/ad-commerce-store.js');
 assert.equal(typeof api.AdStore, 'function');
 assert.equal(Object.hasOwn(api, 'validateAdFile'), false);
 assert.equal(Object.hasOwn(api, 'AdCommerceStore'), false);
});

test('public advertising documents omit runtime, permission and protected-route internals', () => {
 const reports = [
  '../../docs/2026-10-ad-commerce-foundation.md',
  '../../docs/2026-10-ad-commerce-sandbox-integration.md',
  '../README.public-sandbox-test.md',
 ].map(path => readFileSync(new URL(path, import.meta.url), 'utf8'));
 const forbidden = [
  /`[A-Za-z0-9_]+\.(?:write_file|execute|click)`/,
  /앱 권한.{0,200}\bAllow\b/is,
  /전역 기본값.{0,200}\bAllow\b/is,
  /보안 상태.{0,200}도구 요청/is,
  /도구 관측.{0,400}(?:차단|재시도)/is,
  /(?:원래 PC|local-overlay|증거 폴더)/i,
  /\/sandbox\/[a-z]+\/\*/i,
  /<[a-z-]+>\.workers\.dev/i,
 ];
 for (const report of reports) {
  for (const pattern of forbidden) assert.doesNotMatch(report, pattern);
 }
});
