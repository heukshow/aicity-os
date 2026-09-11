import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = file => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const truth = read('data/revenue-truth-2026-09-11.json');
const baseline = read('data/revenue-browser-baseline-2026-09-08.json');
const approved = read('data/approved-tracking-2026-09-08.json').items;
const tools = read('data/tools.json').filter(t => t.affiliate_verified && t.affiliate_url && ['approved_tracking','approved','approved_account'].includes(t.affiliate_status));
const alias = { HighLevel:'gohighlevel', 'Text / LiveChat Partner Program':'text', 'Murf AI':'murf-ai' };
const idFor = name => alias[name] || tools.find(t => t.name.toLowerCase() === name.toLowerCase())?.id || name.toLowerCase().replace(/[^a-z0-9]+/g,'-');
const metrics = ['outbound_clicks','signups_referrals','trials','paid_customers','gross_sales_revenue','commission_earned','commission_approved','commission_pending','payout_paid','payout_pending','network_reported_conversions'];
const evidence = [...baseline.records.map(r => ({...r, period:'당시 대시보드 누적', evidence_source:'authenticated-browser-dashboard', evidence_id:baseline.source_file})), ...truth.records].map(r => ({
  tool_id:idFor(r.tool), tool:r.tool, network:r.network, period:r.period,
  checked_at:r.evidence_timestamp, source:r.evidence_source, evidence_id:r.evidence_id,
  currency:r.currency, metrics:Object.fromEntries(metrics.map(k => [k, typeof r[k] === 'number' ? r[k] : null])),
}));
const rows = new Map(tools.map(t => [t.id, {id:t.id,name:t.name,network:null,portal_url:null,inventory_source:'data/tools.json'}]));
for (const e of evidence) {
  if (!rows.has(e.tool_id)) rows.set(e.tool_id,{id:e.tool_id,name:e.tool,network:null,portal_url:null,inventory_source:'data/revenue-truth-2026-09-11.json'});
  rows.get(e.tool_id).network = e.network;
}
// These portals and account groupings are from existing authenticated evidence.
for (const item of approved) {
  const row = rows.get(item.id); if (!row) continue;
  row.portal_url = item.portal_url || null;
  row.network ||= item.platform || (/PartnerStack/.test(item.evidence || '') ? 'PartnerStack' : null);
}
for (const id of ['helpdesk','text']) Object.assign(rows.get(id),{network:'LiveChat Partner Program',account_id:'text-account',portal_url:'https://partners.livechat.com/app/affiliate/campaigns/723911/overview'});
Object.assign(rows.get('kittl'),{network:'Impact',account_id:'impact-account',portal_url:'https://app.impact.com/login.user'});
Object.assign(rows.get('voibe'),{network:'Lemon Squeezy',account_id:'lemonsqueezy-account',portal_url:'https://affiliates.lemonsqueezy.com/programs/voibe'});
Object.assign(rows.get('uplead'),{network:'FirstPromoter',portal_url:read('data/browser_required_queue.d/uplead-revenue-stats-2026-09-11.json').dashboard_login_url});
const fillout = read('data/fillout-tracking-link-recovery-2026-09-10.json');
rows.set('fillout',{id:'fillout',name:'Fillout',network:'Dub',portal_url:null,inventory_source:'data/fillout-tracking-link-recovery-2026-09-10.json'});
// Full membership list observed in the existing PartnerStack account on Sep 11.
// Pending memberships remain visible because the account-wide API covers them too.
const partnerPrograms = {claap:'Claap',descript:'Descript',brand24:'Brand24','really-good-emails':'Really Good Emails / RGE Studio','partnerstack-gravity':'Gravity',teachable:'Teachable',bookyourdata:'Bookyourdata',gamma:'Gamma','murf-ai':'Murf AI',unbounce:'Unbounce',moosend:'Moosend','monday-com':'monday.com',sendcloud:'Sendcloud',airia:'Airia','triple-whale':'Triple Whale',pipedrive:'Pipedrive',bidx:'BidX'};
for(const [id,name] of Object.entries(partnerPrograms)){
  if(!rows.has(id)) rows.set(id,{id,name,inventory_source:'authenticated PartnerStack membership list 2026-09-11'});
  Object.assign(rows.get(id),{network:'PartnerStack',account_id:'partnerstack-account',portal_url:'https://dash.partnerstack.com/home'});
}
for(const [id,url] of Object.entries({gohighlevel:'https://affiliate.gohighlevel.com/login',pictory:'https://pictory.firstpromoter.com/login'})) rows.get(id).portal_url=url;
// Recover exact recorded portal routes; customer tracking links never supply these.
function portals(value,source){
  if(!value || typeof value!=='object') return;
  if(Array.isArray(value)){for(const item of value)portals(item,source);return;}
  const row=rows.get(value.tool_id || value.id);
  const candidate=value.portal_url || value.dashboard_login_url || value.dashboard_url;
  if(row && !row.portal_url && typeof candidate==='string'){
    try {const u=new URL(candidate);if(u.protocol==='https:' && !u.username && !u.password && !u.search && !u.hash){row.portal_url=u.href;row.portal_source=source;}}catch{}
  }
  for(const child of Object.values(value)) if(typeof child==='object')portals(child,source);
}
for(const file of fs.readdirSync(path.join(root,'data')).filter(f=>/affiliate|tracking/.test(f)&&f.endsWith('.json')).sort()){
  try {portals(read('data/'+file),'data/'+file);}catch{}
}
for(const file of fs.readdirSync(path.join(root,'data/browser_required_queue.d')).filter(f=>f.endsWith('.json')).sort()){
  try {portals(read('data/browser_required_queue.d/'+file),'data/browser_required_queue.d/'+file);}catch{}
}
const programs = [...rows.values()].map(r=>({...r,account_id:r.account_id || (r.network==='PartnerStack' ? 'partnerstack-account' : r.id), network:r.network || '개별 제휴 포털', evidence:evidence.filter(e=>e.tool_id===r.id).sort((a,b)=>Date.parse(b.checked_at)-Date.parse(a.checked_at))}));
const output = {scope:'현재 검증된 제휴 경로 + 기존 수익 근거에 등장하는 계정',programs};
fs.writeFileSync(path.join(root,'worker/src/revenue-inventory.json'),JSON.stringify(output,null,2)+'\n');
console.log(`Revenue inventory: ${programs.length} programs / ${new Set(programs.map(p=>p.account_id)).size} account groups`);
