import crypto from 'node:crypto';
const RealDate=Date;
class FixedDate extends RealDate { constructor(...args){super(...(args.length?args:['2026-09-10T00:30:00Z']));} static now(){return new RealDate('2026-09-10T00:30:00Z').valueOf();} }
globalThis.Date=FixedDate;
process.env.GOOGLE_SERVICE_ACCOUNT_JSON=JSON.stringify({client_email:'fixture@example.invalid',private_key:crypto.generateKeyPairSync('rsa',{modulusLength:2048,privateKeyEncoding:{type:'pkcs8',format:'pem'},publicKeyEncoding:{type:'spki',format:'pem'}}).privateKey});
const row=(dims,values)=>({dimensionValues:dims.map(value=>({value})),metricValues:values.map(value=>({value:String(value)}))});
const data=[['2026-07-02',2],['2026-08-01',3],['2026-09-07',5],['2026-09-10',7]];
const subset=w=>data.filter(([date])=>date>=w.startDate && date<=w.endDate);
const gaReport=b=>{
 const dims=(b.dimensions||[]).map(d=>d.name).join(','),selected=subset(b.dateRanges[0]);
 let rows;
 if(dims==='date') rows=selected.map(([d,v])=>row([d.replaceAll('-','')],b.dimensionFilter?[v]:[v,v*2,v*3]));
 else if(dims==='date,sessionSource')rows=selected.map(([d,v])=>row([d.replaceAll('-',''),'google'],[v]));
 else if(dims==='sessionSource')rows=[row(['google'],[12,24]),row(['direct'],[8,16])];
 else if(dims==='pagePath')rows=[row(['/tool/gohighlevel.html'],[12,8])];
 else if(dims)rows=[];
 else {const sum=selected.reduce((n,x)=>n+x[1],0);rows=[row([],b.dimensionFilter?[sum]:[selected.length,sum*2,sum*3])];}
 return {rows,metadata:{timeZone:'Asia/Seoul'},rowCount:rows.length};
};
globalThis.fetch=async(url,options)=>{
 if(url.includes('oauth2'))return {ok:true,json:async()=>({access_token:'fixture-only'})};
 const b=JSON.parse(options.body),dims=(b.dimensions||[]).map(d=>d.name||d).join(',');
 if(process.env.FIXTURE_FAIL_SOURCE==='1' && dims==='date,sessionSource')return {ok:false,status:429,text:async()=> 'fixture'};
 if(process.env.FIXTURE_FAIL_DAILY==='1' && dims==='date' && !url.includes('searchconsole'))return {ok:false,status:429,text:async()=> 'fixture'};
 let result;
 if(url.includes('searchconsole')){
   if(b.startDate>b.endDate)throw new Error('Invalid window');
   const rows=[{keys:['2026-09-04'],impressions:9,clicks:2},{keys:['2026-09-06'],impressions:6,clicks:1}].filter(r=>r.keys[0]>=b.startDate&&r.keys[0]<=b.endDate);
   result=dims==='date'?{rows}:dims?{rows:[]}:{rows:rows.length?[{impressions:rows.reduce((n,r)=>n+r.impressions,0),clicks:rows.reduce((n,r)=>n+r.clicks,0)}]:[]};
 }else result=url.includes('batchRunReports')?{reports:b.requests.map(gaReport)}:gaReport(b);
 return {ok:true,json:async()=>result};
};
