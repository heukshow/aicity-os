import fs from 'node:fs';
import crypto from 'node:crypto';

const serviceRaw=process.env.GOOGLE_SERVICE_ACCOUNT_JSON||'';
const siteUrl=String(process.env.GSC_SITE_URL||'https://coshuma.com/').trim();
if(!serviceRaw) throw new Error('GOOGLE_SERVICE_ACCOUNT_JSON missing');
const account=JSON.parse(serviceRaw);
const b64=v=>Buffer.from(v).toString('base64url');
async function token(){
  const now=Math.floor(Date.now()/1000);
  const h=b64(JSON.stringify({alg:'RS256',typ:'JWT'}));
  const c=b64(JSON.stringify({iss:account.client_email,scope:'https://www.googleapis.com/auth/webmasters.readonly',aud:'https://oauth2.googleapis.com/token',iat:now,exp:now+3600}));
  const u=`${h}.${c}`; const s=crypto.createSign('RSA-SHA256'); s.update(u); s.end();
  const assertion=`${u}.${s.sign(account.private_key).toString('base64url')}`;
  const r=await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'content-type':'application/x-www-form-urlencoded'},body:new URLSearchParams({grant_type:'urn:ietf:params:oauth:grant-type:jwt-bearer',assertion})});
  if(!r.ok) throw new Error('token '+r.status); return (await r.json()).access_token;
}
async function inspect(access,url){
  const r=await fetch('https://searchconsole.googleapis.com/v1/urlInspection/index:inspect',{method:'POST',headers:{authorization:`Bearer ${access}`,'content-type':'application/json'},body:JSON.stringify({inspectionUrl:url,siteUrl})});
  if(!r.ok) return {url,error:`${r.status} ${(await r.text()).slice(0,180)}`};
  const j=await r.json(); const x=j.inspectionResult?.indexStatusResult||{};
  return {url,verdict:x.verdict||null,coverageState:x.coverageState||null,indexingState:x.indexingState||null,pageFetchState:x.pageFetchState||null,robotsTxtState:x.robotsTxtState||null,lastCrawlTime:x.lastCrawlTime||null,userCanonical:x.userCanonical||null,googleCanonical:x.googleCanonical||null,referringUrls:x.referringUrls||[]};
}
const sitemapText=await (await fetch('https://coshuma.com/sitemap.xml')).text();
const sitemapUrls=[...sitemapText.matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>m[1]);
const historicalRemoved=["https://coshuma.com/tool/jasper-ai.html","https://coshuma.com/tool/make.html","https://coshuma.com/tool/synthflow.html","https://coshuma.com/compare/notion-ai-vs-boldsign.html","https://coshuma.com/compare/quillbot-vs-socialchamp-io.html","https://coshuma.com/compare/bolddesk-vs-boldsign.html","https://coshuma.com/compare/socialchamp-io-vs-kinsta.html","https://coshuma.com/compare/reactin-vs-quillbot.html","https://coshuma.com/compare/reactin-vs-socialchamp-io.html","https://coshuma.com/compare/octo-browser-vs-socialchamp-io.html","https://coshuma.com/compare/decktopus-vs-socialchamp-io.html","https://coshuma.com/compare/kit-vs-convertkit.html","https://coshuma.com/compare/kittl-vs-socialchamp-io.html","https://coshuma.com/compare/make-vs-make-com.html","https://coshuma.com/compare/make-vs-unbounce.html","https://coshuma.com/compare/surfeo-vs-socialchamp-io.html","https://coshuma.com/compare/catalister-vs-socialchamp-io.html","https://coshuma.com/compare/synthflow-vs-elevenlabs.html","https://coshuma.com/compare/synthflow-vs-murf-ai.html","https://coshuma.com/tool/merlin-ai.html"];
const http=[];
for(const url of [...historicalRemoved,...sitemapUrls]){
  try{
    const r=await fetch(url,{redirect:'manual'});
    if(r.status>=400 || historicalRemoved.includes(url)) http.push({url,status:r.status,location:r.headers.get('location')});
  }catch(e){http.push({url,status:'FETCH_ERROR',error:String(e).slice(0,160)});}
}
const access=await token();
const inspected=[];
for(const url of historicalRemoved){
  inspected.push(await inspect(access,url));
}
const badHttp=http.filter(x=>x.status!==200 && x.status!==301 && x.status!==302 && x.status!==307 && x.status!==308);
console.log('COSHUMA_INDEX_AUDIT '+JSON.stringify({checked_at:new Date().toISOString(),sitemap_count:sitemapUrls.length,bad_http:badHttp,historical_http:http.filter(x=>historicalRemoved.includes(x.url)),historical_inspection:inspected}));
