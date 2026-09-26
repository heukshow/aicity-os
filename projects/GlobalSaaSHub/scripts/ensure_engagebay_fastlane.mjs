import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-09-14T19:30:00+09:00';
const engagebay = {
  id: 'engagebay',
  name: 'EngageBay',
  category: 'sales_crm',
  category_display: 'Sales & CRM',
  description: 'All-in-one CRM, email marketing, sales and customer-support platform with a permanent free plan for small contact lists.',
  affiliate_url: null,
  pricing: 'All-in-One Free $0 for 250 contacts; annual-billing view currently lists Basic $14.99, Growth $64.99 and Pro $119.99 per user/month',
  key_features: ['CRM and deal management','Email marketing and sequences','Landing pages and forms','Helpdesk and live chat','Permanent free plan'],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=engagebay.com&sz=128',
  primary_category: 'sales_crm',
  comparison_group: 'crm',
  official_url: 'https://www.engagebay.com/',
  pricing_source_url: 'https://www.engagebay.com/pricing/all-in-one',
  pricing_verified_at: checkedAt,
  pricing_verified: true,
  currency: 'USD',
  billing_period: 'free tier; paid price varies by billing term',
  evidence_source_type: 'official_pricing_and_affiliate_pages',
  is_manual_override: true,
  official_verification_status: 'verified',
  official_verified_at: checkedAt,
  official_evidence_url: 'https://www.engagebay.com/affiliate-program',
  affiliate_verified: false,
  affiliate_status: 'browser_required_account_registration',
  affiliate_source_url: 'https://www.engagebay.com/affiliate-program',
  affiliate_workflow_url: 'https://app.engagebay.com/signup?route=referrer/overview',
  affiliate_status_checked_at: checkedAt,
  application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official EngageBay affiliate page advertises 30% recurring commission while a referred paid subscriber remains active.',
    'Official terms state first-click attribution, a 30-day refund-clearance period, commissions approved before the 3rd and payouts before the 5th under current published terms.',
    'Official program page says affiliates do not need to buy EngageBay to promote it.',
    'Exact official signup route creates an EngageBay account before reaching the referrer overview.',
    'GitHub search and both Gmail accounts, including sent and spam, contained no prior EngageBay application, approval, rejection, tracking-link, commission or payout record before issue #520.',
    'Exact account-specific customer tracking URL is unknown; signup, dashboard, onboarding and generic vendor URLs must not be used as affiliate revenue links.',
  ],
  affiliate_next_action: 'When the account owner is available, use the exact official signup route once. Stop for CAPTCHA, OTP, legal consent or identity verification. After enrollment, publish only the vendor-issued customer-facing referral URL.',
};

for (const file of ['data/tools.json','data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file,'utf8'));
  const existing = tools.find((tool) => tool.id === engagebay.id);
  if (existing?.affiliate_url && engagebay.affiliate_url && existing.affiliate_url !== engagebay.affiliate_url) throw new Error('Refusing to overwrite EngageBay affiliate URL');
  if (existing) Object.assign(existing,engagebay); else tools.push(engagebay);
  tools.sort((a,b)=>String(a.id||'').localeCompare(String(b.id||'')));
  fs.writeFileSync(file,`${JSON.stringify(tools,null,2)}\n`);
}

const outreachPath='data/affiliate_outreach_state.json';
const outreach=JSON.parse(fs.readFileSync(outreachPath,'utf8'));
outreach.updated_at='2026-09-14';
outreach.programs||={};
outreach.programs.engagebay={status:'browser_required_account_registration',tracking_url:null,application_state:'not_submitted',account:'support@coshuma.com',official_program_url:'https://www.engagebay.com/affiliate-program',workflow_url:'https://app.engagebay.com/signup?route=referrer/overview',github_issue:520,checked_at:checkedAt,note:'No prior relationship found. Account creation is not completed unattended, and no customer tracking URL is verified.'};
fs.writeFileSync(outreachPath,`${JSON.stringify(outreach,null,2)}\n`);

const queuePath='data/browser_required_queue.json';
const queue=JSON.parse(fs.readFileSync(queuePath,'utf8'));
if(!queue.some((item)=>item.tool_id==='engagebay'||String(item.id||'').startsWith('engagebay-'))){
  queue.push({id:'engagebay-account-registration-2026-09-14',tool_id:'engagebay',priority:'medium',status:'browser_required_account_registration',affiliate_status:'browser_required_account_registration',application_state:'not_submitted',cost:0,exact_tracking_url:null,user_action_required:true,blocker:'The official referral route requires creating an EngageBay account.',reason:'Duplicate checks are clear, but account creation is not completed and no customer tracking URL exists.',next_action:'Account owner uses the official signup route once; stop for CAPTCHA, OTP, legal consent or identity verification. Recover only a vendor-issued customer-facing referral URL.',do_not_reapply:true,verified_at:checkedAt,github_issue:520});
}
fs.writeFileSync(queuePath,`${JSON.stringify(queue,null,2)}\n`);

const urls=['https://coshuma.com/tool/engagebay.html','https://coshuma.com/best/engagebay-free-crm-pricing.html','https://coshuma.com/compare/engagebay-vs-hubspot.html'];
let sitemap=fs.readFileSync('public/sitemap.xml','utf8');
for(const url of urls){if(!sitemap.includes(`<loc>${url}</loc>`))sitemap=sitemap.replace('</urlset>',`  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n</urlset>`);}
fs.writeFileSync('public/sitemap.xml',sitemap);

let llms=fs.readFileSync('public/llms.txt','utf8');
if(!llms.includes('https://coshuma.com/tool/engagebay.html'))llms+='\n- https://coshuma.com/tool/engagebay.html — EngageBay CRM, email, service and pricing buyer guide\n- https://coshuma.com/best/engagebay-free-crm-pricing.html — EngageBay free CRM limits and upgrade guide\n- https://coshuma.com/compare/engagebay-vs-hubspot.html — EngageBay vs HubSpot CRM comparison\n';
fs.writeFileSync('public/llms.txt',llms);

const hubBlock='\n<section data-engagebay-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-emerald-500/25 bg-emerald-500/5 p-5"><div class="text-xs uppercase tracking-widest text-emerald-300 font-bold">All-in-one CRM</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-emerald-300" href="/best/engagebay-free-crm-pricing.html">EngageBay free CRM & pricing</a> · <a class="font-bold text-white hover:text-emerald-300" href="/tool/engagebay.html">EngageBay review</a> · <a class="font-bold text-white hover:text-emerald-300" href="/compare/engagebay-vs-hubspot.html">EngageBay vs HubSpot</a></p></div></section>\n';
for(const file of ['public/best/index.html','index.html']){let html=fs.readFileSync(file,'utf8');if(!html.includes('data-engagebay-fastlane="2026-09-14"')){html=html.includes('</main>')?html.replace('</main>',hubBlock+'</main>'):html.replace('</body>',hubBlock+'</body>');fs.writeFileSync(file,html);}}

const hubspotPath='public/tool/hubspot.html';
if(fs.existsSync(hubspotPath)){let html=fs.readFileSync(hubspotPath,'utf8');if(!html.includes('/compare/engagebay-vs-hubspot.html')){const related='\n<section data-engagebay-related="2026-09-14" class="max-w-6xl mx-auto px-5 pb-8"><a href="/compare/engagebay-vs-hubspot.html" class="block rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5"><div class="text-xs uppercase tracking-wider font-bold text-emerald-300">Related CRM comparison</div><div class="mt-2 font-extrabold text-white">EngageBay vs HubSpot: compact all-in-one suite or broader CRM ecosystem →</div></a></section>\n';html=html.includes('</main>')?html.replace('</main>',related+'</main>'):html.replace('</body>',related+'</body>');fs.writeFileSync(hubspotPath,html);}}

console.log('EngageBay fast-lane state, queue and discoverability ensured');
