import fs from 'node:fs';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {approvedTracking} from './approved_tracking_evidence.mjs';
const files=['data/tools.json','data/tools.next.json'];
const originals=files.map(f=>fs.readFileSync(f,'utf8'));
function check(){for(const f of files){const tools=JSON.parse(fs.readFileSync(f,'utf8'));for(const [id,e] of approvedTracking){const t=tools.find(t=>t.id===id);assert.equal(t?.affiliate_url,e.exact_tracking_url,id);assert.equal(t.affiliate_status,'approved_tracking',id);assert.equal(t.affiliate_verified,true,id);assert.ok(t.affiliate_verified_at,id);assert.ok(t.affiliate_evidence_markers?.length,id);}}}
check();
try {for(let n=0;n<2;n++){execFileSync(process.execPath,['scripts/sync_verified_affiliates.mjs']);execFileSync(process.execPath,['scripts/sync_latest_affiliate_states.mjs']);check();for(let j=0;j<files.length;j++){const before=JSON.parse(originals[j]);const after=JSON.parse(fs.readFileSync(files[j],'utf8'));for(const id of approvedTracking.keys()) assert.deepEqual(after.find(t=>t.id===id),before.find(t=>t.id===id),`sync must preserve ${id}`);}}}finally{files.forEach((f,j)=>fs.writeFileSync(f,originals[j]));}
const outreach=JSON.parse(fs.readFileSync('data/affiliate_outreach_state.json','utf8')).programs;
const queue=JSON.parse(fs.readFileSync('data/browser_required_queue.json','utf8'));
const dir=process.argv[2]||'dist';
const decode=s=>s.replaceAll('&amp;','&');
for(const [id,e] of approvedTracking){assert.equal(outreach[id].status,'approved_tracking');assert.equal(outreach[id].tracking_url,e.exact_tracking_url);assert.ok(queue.some(q=>q.affiliate_status==='approved_tracking'&&q.exact_tracking_url===e.exact_tracking_url));
 const toolPage=fs.readFileSync(`${dir}/tool/${id}.html`,'utf8');
 const pages=[['tool/'+id+'.html',toolPage],...fs.readdirSync(`${dir}/compare`).filter(f=>f.endsWith('.html')).map(f=>['compare/'+f,fs.readFileSync(`${dir}/compare/${f}`,'utf8')]).filter(([f,s])=>s.includes(`data-tool-id="${id}"`)||s.includes(e.exact_tracking_url))];
 let count=0;
 for(const [file,s] of pages){const anchors=[...s.matchAll(/<a\b[^>]*>/g)].map(m=>m[0]).filter(a=>(a.includes(`data-tool-id="${id}"`)&&a.includes('data-cta="affiliate"'))||decode(a).includes(`href="${e.exact_tracking_url}"`));assert.ok(anchors.length,`${id}: no CTA on ${file}`);for(const a of anchors){assert.ok(decode(a).includes(`href="${e.exact_tracking_url}"`),`${file}: wrong link`);assert.ok(a.includes('data-cta="affiliate"'),file);assert.ok(a.includes('data-cta-source='),file);assert.ok(a.includes('sponsored'),file);count++;}assert.ok(s.includes('/affiliate-attribution.js'),file);assert.ok(/affiliate disclosure/i.test(s),file);}
 console.log(`${id}: ${count} attributed CTAs across ${pages.length} pages`);
}
console.log('PASS: authoritative exact URLs, state/evidence/queue, repeated deployment sync preservation, and built CTAs.');


