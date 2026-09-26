import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-09-14T20:28:00+09:00';
const sendpulse = {
  id: 'sendpulse',
  name: 'SendPulse',
  category: 'email_outreach',
  category_display: 'Email & Outreach',
  description: 'Marketing platform for email, automation, CRM, chatbots, websites and online courses with a free email plan.',
  affiliate_url: null,
  pricing: 'Email Free $0 for up to 500 subscribers and 15,000 monthly emails; current annual view for 500 subscribers lists Standard $9.60 and Pro $11.52 per month',
  key_features: ['Email marketing','Automation flows','CRM','Chatbots and live chat','Websites and online courses'],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=sendpulse.com&sz=128',
  primary_category: 'email_outreach',
  comparison_group: 'email_marketing',
  official_url: 'https://sendpulse.com/',
  pricing_source_url: 'https://sendpulse.com/pricing',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'free tier; paid price varies by list size and billing term',
  evidence_source_type: 'official_pricing_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://sendpulse.com/partners/affiliates',
  affiliate_verified: false,
  affiliate_status: 'browser_required_phone_captcha',
  affiliate_source_url: 'https://sendpulse.com/partners/affiliates',
  affiliate_workflow_url: 'https://sendpulse.com/partners/affiliates',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official SendPulse pricing page lists Free at up to 500 subscribers and 15,000 monthly emails with no credit card required.',
    'Official affiliate page lists a starting commission of 30% on referral plan payments and 10% on balance top-ups.',
    'The commission rate becomes 40% when referrals spend at least $1,000 in a month, and commissions apply for two years under current published terms.',
    'A unique referral link is issued only after application approval.',
    'The public application asks for a phone number and robot confirmation.',
    'GitHub search and both Gmail accounts, including sent and spam, contained no prior SendPulse application, approval, rejection, tracking-link, commission or payout record before issue #523.',
    'Exact account-specific customer tracking URL is unknown; application, login, dashboard and generic vendor URLs must not be used as affiliate revenue links.'
  ],
  affiliate_next_action: 'When the account owner is available, submit the official application once. Stop for phone verification, CAPTCHA, OTP, legal consent or identity verification. Publish only the vendor-issued customer-facing referral URL after approval.'
};

for (const file of ['data/tools.json','data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file,'utf8'));
  const existing = tools.find((tool) => tool.id === sendpulse.id);
  if (existing?.affiliate_url) throw new Error('Refusing to overwrite existing SendPulse affiliate URL');
  if (existing) Object.assign(existing,sendpulse); else tools.push(sendpulse);
  tools.sort((a,b)=>String(a.id||'').localeCompare(String(b.id||'')));
  fs.writeFileSync(file,`${JSON.stringify(tools,null,2)}\n`);
}

const outreachPath='data/affiliate_outreach_state.json';
const outreach=JSON.parse(fs.readFileSync(outreachPath,'utf8'));
outreach.updated_at='2026-09-14';
outreach.programs||={};
outreach.programs.sendpulse={status:'browser_required_phone_captcha',tracking_url:null,application_state:'not_submitted',account:'support@coshuma.com',official_program_url:'https://sendpulse.com/partners/affiliates',workflow_url:'https://sendpulse.com/partners/affiliates',github_issue:523,checked_at:checkedAt,note:'No prior relationship found. The public application requires phone details and robot confirmation; no customer tracking URL is verified.'};
fs.writeFileSync(outreachPath,`${JSON.stringify(outreach,null,2)}\n`);

const queuePath='data/browser_required_queue.json';
const queue=JSON.parse(fs.readFileSync(queuePath,'utf8'));
if(!queue.some((item)=>item.tool_id==='sendpulse'||String(item.id||'').startsWith('sendpulse-'))){
  queue.push({id:'sendpulse-phone-captcha-2026-09-14',tool_id:'sendpulse',priority:'medium',status:'browser_required_phone_captcha',affiliate_status:'browser_required_phone_captcha',application_state:'not_submitted',cost:0,exact_tracking_url:null,user_action_required:true,blocker:'The official application requests a phone number and robot confirmation.',reason:'Duplicate checks are clear, but the application cannot be completed unattended and no customer tracking URL exists.',next_action:'Account owner submits the official form once; stop for phone verification, CAPTCHA, OTP, legal consent or identity verification. Recover only a vendor-issued customer-facing referral URL.',do_not_reapply:true,verified_at:checkedAt,github_issue:523});
}
fs.writeFileSync(queuePath,`${JSON.stringify(queue,null,2)}\n`);

const urls=['https://coshuma.com/tool/sendpulse.html','https://coshuma.com/best/sendpulse-free-email-plan.html','https://coshuma.com/compare/sendpulse-vs-sender-net.html'];
let sitemap=fs.readFileSync('public/sitemap.xml','utf8');
for(const url of urls){if(!sitemap.includes(`<loc>${url}</loc>`))sitemap=sitemap.replace('</urlset>',`  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n</urlset>`);}
fs.writeFileSync('public/sitemap.xml',sitemap);

let llms=fs.readFileSync('public/llms.txt','utf8');
if(!llms.includes('https://coshuma.com/tool/sendpulse.html'))llms+='\n- https://coshuma.com/tool/sendpulse.html — SendPulse email, automation, CRM and pricing buyer guide\n- https://coshuma.com/best/sendpulse-free-email-plan.html — SendPulse free email-plan limits and upgrade guide\n- https://coshuma.com/compare/sendpulse-vs-sender-net.html — SendPulse vs Sender.net free-plan comparison\n';
fs.writeFileSync('public/llms.txt',llms);

const hubBlock='\n<section data-sendpulse-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-cyan-500/25 bg-cyan-500/5 p-5"><div class="text-xs uppercase tracking-widest text-cyan-300 font-bold">Email & automation</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-cyan-300" href="/best/sendpulse-free-email-plan.html">SendPulse free plan</a> · <a class="font-bold text-white hover:text-cyan-300" href="/tool/sendpulse.html">SendPulse review</a> · <a class="font-bold text-white hover:text-cyan-300" href="/compare/sendpulse-vs-sender-net.html">SendPulse vs Sender.net</a></p></div></section>\n';
for(const file of ['public/best/index.html','index.html']){let html=fs.readFileSync(file,'utf8');if(!html.includes('data-sendpulse-fastlane="2026-09-14"')){html=html.includes('</main>')?html.replace('</main>',hubBlock+'</main>'):html.replace('</body>',hubBlock+'</body>');fs.writeFileSync(file,html);}}

const senderPath='public/tool/sender-net.html';
if(fs.existsSync(senderPath)){let html=fs.readFileSync(senderPath,'utf8');if(!html.includes('/compare/sendpulse-vs-sender-net.html')){const related='\n<section data-sendpulse-related="2026-09-14" class="max-w-6xl mx-auto px-5 pb-8"><a href="/compare/sendpulse-vs-sender-net.html" class="block rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5"><div class="text-xs uppercase tracking-wider font-bold text-cyan-300">Related email comparison</div><div class="mt-2 font-extrabold text-white">SendPulse vs Sender.net: wider marketing stack or larger free contact allowance →</div></a></section>\n';html=html.includes('</main>')?html.replace('</main>',related+'</main>'):html.replace('</body>',related+'</body>');fs.writeFileSync(senderPath,html);}}

console.log('SendPulse fast-lane state, queue and discoverability ensured');
