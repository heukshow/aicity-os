import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-10-07T17:15:00+09:00';
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
  affiliate_status: 'browser_required_legal_program_consent', affiliate_source_url: 'https://popupsmart.com/affiliate-program',
  affiliate_workflow_url: 'https://app.popupsmart.com/', affiliate_status_checked_at: checkedAt, application_state: 'not_submitted',
  affiliate_evidence_markers: [
    "Official Popupsmart affiliate page says registration is available to publishers and advertises 30% recurring commission, a 30-day cookie and 50% off for referred customers for their first three months.",
    "Official Popupsmart help says the unique affiliate link is available only inside the authenticated affiliate section after product-account registration.",
    "Popupsmart Terms of Use, last updated 2025-12-18, state that service use is governed by binding Terms and Privacy Policy; affiliate participation is subject to those Terms and any additional dashboard terms.",
    "The binding terms require a valid account in good standing, allow supplier approval/revocation despite marketing copy saying no approval, and make the supplier dashboard the controlling source for payout details.",
    "No COSHUMA Popupsmart account, legal/program consent, application, approval, exact customer referral URL, referral, paid customer, commission, payout or revenue is verified.",
    "Generic signup, app, dashboard, onboarding and homepage URLs must not be used as affiliate tracking links."
],
  affiliate_next_action: "Hold at legal consent. After the account holder accepts the current Popupsmart Terms of Use, Privacy Policy and any affiliate dashboard terms through the official flow, check for an existing COSHUMA account before registration and recover only the exact issued customer-facing referral URL. Stop for CAPTCHA, OTP, forced identity verification or payment approval."
};

for (const file of ['data/tools.json','data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file,'utf8'));
  const existing = tools.find((tool) => tool.id === popupsmart.id);
  if (existing) Object.assign(existing,popupsmart); else tools.push(popupsmart);
  fs.writeFileSync(file, `${JSON.stringify(tools,null,2)}\n`);
}

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath,'utf8'));
outreach.updated_at = '2026-10-07'; outreach.programs ||= {};
outreach.programs.popupsmart = {status:'browser_required_legal_program_consent',tracking_url:null,application_state:'not_submitted',account:'support@coshuma.com',official_program_url:'https://popupsmart.com/affiliate-program',workflow_url:'https://app.popupsmart.com/',github_issue:482,checked_at:checkedAt,note:'Official terms make account use and affiliate participation subject to binding legal terms, while the unique link is issued only in the authenticated affiliate area. No COSHUMA account, consent, approval or exact tracking URL is verified.'};
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach,null,2)}\n`);

const queuePath='data/browser_required_queue.json';
const queue=JSON.parse(fs.readFileSync(queuePath,'utf8'));
let item=queue.find((entry)=>entry.tool_id==='popupsmart'||String(entry.id||'').startsWith('popupsmart-'));
const patch={tool_id:'popupsmart',priority:'high',status:'browser_required_legal_program_consent',affiliate_status:'browser_required_legal_program_consent',application_state:'not_submitted',cost:0,exact_tracking_url:null,user_action_required:true,blocker:'Popupsmart account use and affiliate participation are subject to binding Terms of Use, Privacy Policy and any additional dashboard terms.',reason:'Official program and help pages confirm account registration and authenticated link issuance; official legal terms control participation and may require supplier approval despite no-approval marketing copy.',next_action:"Hold at legal consent. After the account holder accepts the current Popupsmart Terms of Use, Privacy Policy and any affiliate dashboard terms through the official flow, check for an existing COSHUMA account before registration and recover only the exact issued customer-facing referral URL. Stop for CAPTCHA, OTP, forced identity verification or payment approval.",do_not_reapply:true,verified_at:checkedAt,github_issue:482};
if(item)Object.assign(item,patch);else queue.push({id:'popupsmart-affiliate-2026-09-14',...patch});
fs.writeFileSync(queuePath, `${JSON.stringify(queue,null,2)}\n`);

const urls=['https://coshuma.com/tool/popupsmart.html','https://coshuma.com/best/popupsmart-free-plan-pricing.html'];
const sitemapPath='public/sitemap.xml'; let sitemap=fs.readFileSync(sitemapPath,'utf8');
for(const url of urls){if(!sitemap.includes(`<loc>${url}</loc>`))sitemap=sitemap.replace('</urlset>',`  <url>\n    <loc>${url}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n</urlset>`);} fs.writeFileSync(sitemapPath,sitemap);

const llmsPath='public/llms.txt'; let llms=fs.readFileSync(llmsPath,'utf8');
if(!llms.includes('https://coshuma.com/tool/popupsmart.html'))llms+='\n## Popupsmart buyer guides\n\n- https://coshuma.com/tool/popupsmart.html — Popupsmart free plan, pricing and conversion campaign buyer guide\n- https://coshuma.com/best/popupsmart-free-plan-pricing.html — Popupsmart free plan and paid pricing decision guide\n'; fs.writeFileSync(llmsPath,llms);

const hubBlock=`\n<section data-popupsmart-fastlane="2026-09-14" class="max-w-6xl mx-auto px-6 pb-10"><div class="rounded-2xl border border-fuchsia-500/25 bg-fuchsia-500/5 p-5"><div class="text-xs uppercase tracking-widest text-fuchsia-300 font-bold">Conversion optimization</div><p class="mt-2 text-sm text-slate-300"><a class="font-bold text-white hover:text-fuchsia-300" href="/best/popupsmart-free-plan-pricing.html">Popupsmart free plan & pricing</a> · <a class="font-bold text-white hover:text-fuchsia-300" href="/tool/popupsmart.html">Popupsmart buyer guide</a></p></div></section>\n`;
for(const file of ['public/best/index.html','index.html']){let html=fs.readFileSync(file,'utf8'); if(!html.includes('data-popupsmart-fastlane="2026-09-14"')){html=html.includes('</main>')?html.replace('</main>',`${hubBlock}</main>`):html.replace('</body>',`${hubBlock}</body>`); fs.writeFileSync(file,html);}}
console.log('Popupsmart fast-lane state, browser queue and discoverability ensured');
