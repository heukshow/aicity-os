import fs from 'node:fs';

const checkedAt = '2026-09-14T07:31:00+09:00';
const popupsmart = {
  id: 'popupsmart', name: 'Popupsmart', category: 'dev_coding', category_display: 'Coding & Dev Tools',
  description: 'Conversion-focused popup and onsite messaging platform for lead capture, announcements, ecommerce offers, gamification, targeting and campaign analytics.',
  affiliate_url: null,
  pricing: 'Forever-free plan; monthly list prices: Basic $39, Advanced $69, Pro $99, Expert $159; annual billing offers lower effective pricing',
  key_features: ['Popup and onsite campaign builder','Lead-capture forms and ecommerce offers','Audience targeting and trigger rules','Gamification and announcement campaigns','Campaign analytics and integrations'],
  rating: null,
  logo_url: 'https://www.google.com/s2/favicons?domain=popupsmart.com&sz=128',
  primary_category: 'dev_coding', comparison_group: 'conversion_optimization',
  official_url: 'https://popupsmart.com/', pricing_source_url: 'https://popupsmart.com/pricing',
  pricing_verified_at: checkedAt, pricing_verified: true, currency: 'USD', billing_period: 'monthly or annual depending on plan',
  evidence_source_type: 'official_pricing_home_and_affiliate_pages', is_manual_override: true,
  official_verification_status: 'verified', official_verified_at: checkedAt,
  official_evidence_url: 'https://popupsmart.com/affiliate-program', affiliate_verified: false,
  affiliate_status: 'browser_required_account_registration', affiliate_source_url: 'https://popupsmart.com/affiliate-program',
  affiliate_workflow_url: 'https://app.popupsmart.com/', affiliate_status_checked_at: checkedAt, application_state: 'not_submitted',
  affiliate_evidence_markers: [
    'Official Popupsmart affiliate page states no approval is required and a unique referral link is available after registering a Popupsmart account.',
    'Official current affiliate terms advertise 30% recurring commission on eligible paid subscriptions, a 30-day cookie and 50% off for referred customers for their first 3 months.',
    'Official Popupsmart pages advertise a forever-free plan and no credit card required to get started.',
    'Official affiliate calculator currently shows monthly list prices Basic $39, Advanced $69, Pro $99 and Expert $159; annual billing can be lower.',
    'GitHub search found no pre-existing COSHUMA Popupsmart record before this fast-lane cycle.',
    'support@coshuma.com Gmail in:anywhere search found no prior Popupsmart application, approval, rejection, tracking-link, commission or payout message.',
    'Exact account-specific customer tracking URL is unknown; app/dashboard/onboarding/homepage URLs must not be used as customer revenue links.',
    'GitHub issue #482 tracks the free account registration and exact vendor-issued referral-link recovery step.'
  ],
  affiliate_next_action: 'Use the official Popupsmart free registration flow with the COSHUMA company account, avoid duplicate account creation, then recover and validate only the exact vendor-issued customer referral URL. Stop for CAPTCHA, OTP, legal consent, forced identity verification or payment approval.'
};

for (const file of ['data/tools.json','data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file,'utf8'));
  const existing = tools.find((tool) => tool.id === popupsmart.id);
  if (existing) Object.assign(existing,popupsmart); else tools.push(popupsmart);
  fs.writeFileSync(file, `${JSON.stringify(tools,null,2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath,'utf8'));
outreach.updated_at = '2026-09-14'; outreach.programs ||= {};
outreach.programs.popupsmart = {status:'browser_required_account_registration',tracking_url:null,application_state:'not_submitted',account:'support@coshuma.com',official_program_url:'https://popupsmart.com/affiliate-program',workflow_url:'https://app.popupsmart.com/',github_issue:482,checked_at:checkedAt,note:'Official Popupsmart affiliate program is active, free-account entry is available without a credit card, and the vendor says approval is not required. No existing COSHUMA Popupsmart application/account-specific referral URL was found in GitHub or Gmail. Do not use the app URL as a customer CTA.'};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach,null,2)}\n`);

const queuePath='data/browser_required_queue.json';
const queue=JSON.parse(fs.readFileSync(queuePath,'utf8'));
if(!queue.some((item)=>item.tool_id==='popupsmart'||String(item.id||'').startsWith('popupsmart-'))){queue.push({id:'popupsmart-affiliate-2026-09-14',tool_id:'popupsmart',priority:'high',status:'browser_required_account_registration',affiliate_status:'browser_required_account_registration',application_state:'not_submitted',cost:0,exact_tracking_url:null,user_action_required:false,blocker:'Popupsmart issues the unique affiliate link after account registration in its authenticated app; this run has no authenticated Popupsmart UI session.',reason:'Repository and Gmail duplicate checks are clear and the official program needs no approval, but account registration/link issuance has not been completed.',next_action:'Use the official free Popupsmart registration with support@coshuma.com. If no existing account is found, register once and recover the exact vendor-issued customer referral URL. Stop for CAPTCHA, OTP, legal agreement, forced identity verification or payment approval.',do_not_reapply:true,verified_at:checkedAt,github_issue:482});}
fs.writeFileSync(queuePath, `${JSON.stringify(queue,null,2)}\n`);

const urls=['https://coshuma.com/tool/popupsmart.html','https://coshuma.com/best/popupsmart-free-plan-pricing.html'];
const sitemapPath='public/sitemap.xml'; let sitemap=fs.readFileSync(sitemapPath,'utf8');
for(const url of urls){if(!sitemap.includes(`<loc>${url}</loc>`))sitemap=sitemap.replace('</urlset>',`  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n</urlset>`);} fs.writeFileSync(sitemapPath,sitemap);

const llmsPath='public/llms.txt'; let llms=fs.readFileSync(llmsPath,'utf8');
if(!llms.includes('https://coshuma.com/tool/popupsmart.html'))llms+='\n## Popupsmart buyer guides\n\n- https://coshuma.com/tool/popupsmart.html — Popupsmart free plan, pricing and conversion campaign buyer guide\n- https://coshuma.com/best/popupsmart-free-plan-pricing.html — Popupsmart free plan and paid pricing decision guide\n'; fs.writeFileSync(llmsPath,llms);

const hubBlock=`\n<section data-popupsmart-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-fuchsia-500/25 bg-fuchsia-500/5 p-5"><div class="text-xs uppercase tracking-widest text-fuchsia-300 font-bold">Conversion optimization</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-fuchsia-300" href="/best/popupsmart-free-plan-pricing.html">Popupsmart free plan & pricing</a> · <a class="font-bold text-white hover:text-fuchsia-300" href="/tool/popupsmart.html">Popupsmart buyer guide</a></p></div></section>\n`;
for(const file of ['public/best/index.html','index.html']){let html=fs.readFileSync(file,'utf8'); if(!html.includes('data-popupsmart-fastlane="2026-09-14"')){html=html.includes('</main>')?html.replace('</main>',`${hubBlock}</main>`):html.replace('</body>',`${hubBlock}</body>`); fs.writeFileSync(file,html);}}
console.log('Popupsmart fast-lane state, browser queue and discoverability ensured');
