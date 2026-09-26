import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-09-14T21:10:00+09:00';
const tool = {
  id: 'constant-contact',
  name: 'Constant Contact',
  category: 'email_outreach',
  category_display: 'Email & Outreach',
  description: 'Email and digital marketing platform for small businesses with email, social, automation, events, integrations and a 30-day free trial.',
  affiliate_url: null,
  pricing: 'Lite from $12/month, Standard from $35/month, Premium from $80/month; annual prepay can reduce starting prices by up to 15%',
  key_features: ['Email marketing','Marketing automation','Social marketing','Events and ecommerce tools','300+ integrations'],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=constantcontact.com&sz=128',
  primary_category: 'email_outreach',
  comparison_group: 'email_marketing',
  official_url: 'https://www.constantcontact.com/',
  pricing_source_url: 'https://www.constantcontact.com/pricing',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'monthly or annual prepay depending on plan and contact count',
  evidence_source_type: 'official_pricing_affiliate_and_help_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://www.constantcontact.com/partners/affiliate',
  affiliate_verified: false,
  affiliate_status: 'browser_required_affiliate_application',
  affiliate_source_url: 'https://www.constantcontact.com/partners/affiliate',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official affiliate page says affiliates can earn up to $105 when a referred customer pays for a new account.',
    'Official knowledge base updated 2026-07-15 says the affiliate program is free to join.',
    'Official pricing/help confirms a 30-day free trial with no credit card required.',
    'GitHub search and support@coshuma.com Gmail found no prior Constant Contact application, approval, rejection, issued tracking link, commission or payout record before this cycle.',
    'Exact COSHUMA customer tracking URL is unknown; application, dashboard and generic vendor URLs must not be used as revenue links.'
  ],
  affiliate_next_action: 'Submit the official free affiliate application once through the direct browser when available; stop for CAPTCHA, OTP, legal consent or forced identity verification. After approval, recover only the vendor-issued customer-facing tracking URL before changing public CTA state.'
};

for (const file of ['data/tools.json','data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file,'utf8'));
  const existing = tools.find((x)=>x.id===tool.id);
  if (existing) {
    const progressed = ['submitted', 'approved', 'rejected'].includes(existing.application_state);
    const keep = progressed ? {
      affiliate_status: existing.affiliate_status,
      affiliate_verified: existing.affiliate_verified,
      affiliate_url: existing.affiliate_url,
      affiliate_status_checked_at: existing.affiliate_status_checked_at,
      application_state: existing.application_state,
      affiliate_next_action: existing.affiliate_next_action,
      affiliate_evidence_markers: existing.affiliate_evidence_markers
    } : {};
    Object.assign(existing, tool, keep);
    if (existing.application_state === 'approved') {
      existing.affiliate_url = null;
      existing.affiliate_next_action = 'Await the existing official terms clarification for Sections 10.2 and 16 and the account-specific commission schedule. Do not accept the agreement, infer a tracking URL, change public CTAs or send duplicate outreach. After controlling terms are clarified, request the specific legal-consent decision before recovering and verifying the vendor-issued customer URL.';
      existing.affiliate_evidence_markers = [...new Set([
        ...(existing.affiliate_evidence_markers || []),
        '2026-09-27: Official clarification request sent in Gmail thread 1a0df0917006730e. Agreement remains unaccepted and exact customer tracking URL remains null pending controlling terms.'
      ])];
    }
  } else tools.push(tool);
  tools.sort((a,b)=>String(a.id||'').localeCompare(String(b.id||'')));
  fs.writeFileSync(file,`${JSON.stringify(tools,null,2)}\n`);
}

const queuePath='data/browser_required_queue.json';
const queue=JSON.parse(fs.readFileSync(queuePath,'utf8'));
const existingQueueItem = queue.find((item) => item.tool_id === 'constant-contact' || String(item.id || '').startsWith('constant-contact-'));
if (existingQueueItem?.application_state === 'approved') {
  Object.assign(existingQueueItem, {
    task_key: 'constant-contact-tracking-activation-20260927',
    status: 'approved',
    affiliate_status: 'approved',
    exact_tracking_url: null,
    user_action_required: false,
    blocker: 'awaiting_vendor_terms_clarification',
    reason: 'Approved, but Sections 10.2 and 16 and the account-specific commission schedule remain unresolved in the existing official clarification thread.',
    next_action: 'Await the existing official written clarification. Do not accept terms, infer a customer URL, change public CTAs or send duplicate outreach. After controlling terms are clarified, request the specific legal-consent decision before URL activation.',
    do_not_reapply: true
  });
}
if (!existingQueueItem) {
  queue.push({id:'constant-contact-affiliate-application-2026-09-14',tool_id:'constant-contact',priority:'medium',status:'browser_required_affiliate_application',affiliate_status:'browser_required_affiliate_application',application_state:'not_submitted',cost:0,exact_tracking_url:null,user_action_required:false,blocker:'Interactive affiliate application must be completed in the official browser flow; stop only for CAPTCHA, OTP, legal consent or identity verification.',reason:'Duplicate checks are clear and the public program is free, but no account-specific customer tracking URL exists yet.',next_action:'Submit once through the official affiliate application when direct browser interaction is available; then recover only the vendor-issued customer referral URL.',do_not_reapply:true,verified_at:checkedAt});
}
fs.writeFileSync(queuePath,`${JSON.stringify(queue,null,2)}\n`);

const urls=['https://coshuma.com/tool/constant-contact.html','https://coshuma.com/best/constant-contact-free-trial.html','https://coshuma.com/compare/constant-contact-vs-moosend.html'];
let sitemap=fs.readFileSync('public/sitemap.xml','utf8');
for(const url of urls){if(!sitemap.includes(`<loc>${url}</loc>`))sitemap=sitemap.replace('</urlset>',`  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n</urlset>`);}
fs.writeFileSync('public/sitemap.xml',sitemap);

let llms=fs.readFileSync('public/llms.txt','utf8');
if(!llms.includes('https://coshuma.com/tool/constant-contact.html'))llms+='\n- https://coshuma.com/tool/constant-contact.html — Constant Contact pricing, trial and buyer guide\n- https://coshuma.com/best/constant-contact-free-trial.html — Constant Contact 30-day no-card trial guide\n- https://coshuma.com/compare/constant-contact-vs-moosend.html — Constant Contact vs Moosend email-marketing comparison\n';
fs.writeFileSync('public/llms.txt',llms);

const hubBlock='\n<section data-constant-contact-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-cyan-500/25 bg-cyan-500/5 p-5"><div class="text-xs uppercase tracking-widest text-cyan-300 font-bold">Email marketing</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-cyan-300" href="/best/constant-contact-free-trial.html">Constant Contact 30-day trial</a> · <a class="font-bold text-white hover:text-cyan-300" href="/tool/constant-contact.html">Constant Contact pricing</a> · <a class="font-bold text-white hover:text-cyan-300" href="/compare/constant-contact-vs-moosend.html">Constant Contact vs Moosend</a></p></div></section>\n';
for(const file of ['public/best/index.html','index.html']){let html=fs.readFileSync(file,'utf8');if(!html.includes('data-constant-contact-fastlane="2026-09-14"')){html=html.includes('</main>')?html.replace('</main>',hubBlock+'</main>'):html.replace('</body>',hubBlock+'</body>');fs.writeFileSync(file,html);}}

const moosendPath='public/tool/moosend.html';
if(fs.existsSync(moosendPath)){let html=fs.readFileSync(moosendPath,'utf8');if(!html.includes('/compare/constant-contact-vs-moosend.html')){const related='\n<section data-constant-contact-related="2026-09-14" class="max-w-6xl mx-auto px-5 pb-8"><a href="/compare/constant-contact-vs-moosend.html" class="block rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-5"><div class="text-xs uppercase tracking-wider font-bold text-cyan-300">Related email comparison</div><div class="mt-2 font-extrabold text-white">Constant Contact vs Moosend: 30-day trial paths compared →</div></a></section>\n';html=html.includes('</main>')?html.replace('</main>',related+'</main>'):html.replace('</body>',related+'</body>');fs.writeFileSync(moosendPath,html);}}

console.log('Constant Contact fast-lane state and discoverability ensured');
