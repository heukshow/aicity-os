import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const tools=JSON.parse(fs.readFileSync(path.join(root,'data/tools.json'),'utf8'));
const configs=[{id:'omi-ai',best:['People who want searchable conversation notes','Teams reviewing spoken tasks and follow-ups'],not:['Workplaces that prohibit recording','Buyers who need verified hands-on accuracy benchmarks'],why:['Search memories instead of replaying entire conversations','Review generated tasks before acting','Share summaries for a clearer handoff'],alternatives:[['fireflies-ai','Fireflies.ai'],['fathom','Fathom']],source:'https://www.omi.me/pages/product'}];
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
for(const c of configs){
 const t=tools.find(x=>x.id===c.id);
 if(t?.affiliate_verified!==true||t.affiliate_status!=='approved_tracking')throw Error('Unverified route: '+c.id);
 for(const u of [t.affiliate_url,t.official_url,c.source])if(new URL(u).protocol!=='https:')throw Error('Unsafe URL');
 const p=path.join(root,'public/tool',c.id+'.html');
 let html=fs.readFileSync(p,'utf8');
 const list=items=>'<ul class="list-disc pl-5 space-y-1">'+items.map(x=>`<li>${esc(x)}</li>`).join('')+'</ul>';
 const box=`<!-- buyer-box:start -->
<section data-buyer-decision-box="${c.id}" class="rounded-2xl border border-purple-400/40 bg-slate-900 p-6 my-6 space-y-4" aria-label="Buyer decision box">
<h2 class="text-2xl font-bold">Is ${esc(t.name)} right for you?</h2>
<div class="grid md:grid-cols-2 gap-5"><div><h3 class="font-bold">Best for</h3>${list(c.best)}</div><div><h3 class="font-bold">Not ideal for</h3>${list(c.not)}</div></div>
<h3 class="font-bold">Why consider it?</h3>${list(c.why)}
<dl><dt class="font-bold">Pricing</dt><dd>Check current pricing.</dd><dt class="font-bold">Free plan</dt><dd>A free Basic plan is available; check current limits.</dd><dt class="font-bold">Free trial</dt><dd>Not confirmed; check current pricing and trial terms.</dd></dl>
<p>Paid pricing differs across official pages; check checkout before buying. Review recording permissions and your workplace policy first.</p>
<p class="text-sm text-slate-400">Official-source check: 2026-09-07. <a data-cta-source="buyer-box-source" href="${esc(c.source)}" target="_blank" rel="noopener noreferrer" class="underline">Features and pricing source</a>. Editorial fit guidance, not a hands-on performance test.</p>
<p data-affiliate-disclosure="buyer-box" class="text-sm text-slate-300">COSHUMA may earn a commission on qualifying purchases through this partner link, at no extra cost to you.</p>
<div class="flex flex-wrap gap-3"><a data-cta="affiliate" data-cta-source="buyer-box-primary" data-tool-id="${c.id}" href="${esc(t.affiliate_url)}" target="_blank" rel="sponsored noopener noreferrer" class="rounded-xl bg-purple-600 px-5 py-3 font-bold">Explore ${esc(t.name)} →</a><a data-cta="official" data-cta-source="buyer-box-official" href="${esc(t.official_url)}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-slate-500 px-5 py-3">Official website</a></div>
<p>Compare alternatives: ${c.alternatives.map(([id,name])=>`<a data-cta-source="buyer-box-alternative" class="underline" href="/tool/${id}.html">${name}</a>`).join(' · ')}</p>
</section>
<!-- buyer-box:end -->`;
 html=html.includes('<!-- buyer-box:start -->')?html.replace(/<!-- buyer-box:start -->[\s\S]*?<!-- buyer-box:end -->/,box):html.replace('<!-- Description -->',box+'\n<!-- Description -->');
 if(!html.includes(box))throw Error('Buyer box insertion failed: '+c.id);
 if(!html.includes('/affiliate-attribution.js'))html=html.replace('</head>','<script defer src="/affiliate-attribution.js"></script>\n</head>');
 html=html.replace(/<a\b(?=[^>]*data-cta=)(?![^>]*data-cta-source=)/g,'<a data-cta-source="tool-existing"');
 fs.writeFileSync(p,html);
}
