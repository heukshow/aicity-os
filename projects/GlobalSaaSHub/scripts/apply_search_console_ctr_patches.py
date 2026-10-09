"""Apply conservative Search Console CTR patches without exposing affiliate operations.

These rewrites are intentionally idempotent. Historical source strings may already
have been cleaned by earlier customer-copy passes, so a missing historical string is
not a build error. Safety is enforced by the fail-closed public-source/artifact guards.
This script never changes issued tracking URLs or sponsored attribution.
"""
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
TOOL_DIR = PROJECT_DIR / "public" / "tool"

PATCHES = {
    "brand24.html": [
        (
            "<title>Brand24 Pricing 2026: $249/mo, 14-Day Free Trial & AI Visibility | COSHUMA</title>",
            "<title>Brand24 Review & Pricing 2026: 14-Day Free Trial, $249/mo Plans & AI Visibility | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Brand24 pricing starts at $249/mo ($199/mo billed annually). See the 14-day free trial, AI social listening features, $99 AI Visibility add-on, plan limits, and verified COSHUMA partner link." />',
            '<meta name="description" content="Brand24 review and pricing for 2026: plans start at $249/mo ($199/mo billed annually), with a 14-day free trial and no credit card. Compare limits, AI Visibility, who it fits, and test Brand24 before paying." />',
        ),
        (
            '<meta property="og:title" content="Brand24 Pricing 2026: $249/mo + 14-Day Free Trial" />',
            '<meta property="og:title" content="Brand24 Review & Pricing 2026: 14-Day Free Trial + $249/mo Plans" />',
        ),
        (
            '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Brand24 Pricing & Review 2026</h1>',
            '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Brand24 Review & Pricing 2026</h1>',
        ),
        (
            '<section class="rounded-3xl border border-[#262a3d] bg-[#121520] p-6 md:p-8 space-y-4"> <h2 class="text-2xl font-black text-white">Bottom line</h2>',
            '<section id="brand24-14-day-evaluation" class="rounded-3xl border border-emerald-500/20 bg-emerald-500/5 p-6 md:p-8 space-y-5"> <div> <div class="text-xs uppercase tracking-widest text-emerald-300 font-bold">Buyer scorecard · official sources checked October 9, 2026</div> <h2 class="mt-2 text-2xl md:text-3xl font-black text-white">A 14-day signal-quality scorecard before you subscribe</h2> <p class="mt-3 text-sm leading-6 text-slate-300">Brand24 currently offers a 14-day trial based on Pro-plan features, with up to 10 keywords, up to 30,000 mentions and 24-hour trial refreshes. COSHUMA has not completed a hands-on product test; use this scorecard with your own public-source monitoring brief and record what the trial actually returns.</p> </div> <div class="overflow-x-auto rounded-2xl border border-emerald-500/15"> <table class="w-full min-w-[760px] text-left text-sm"> <thead class="bg-[#0d1018] text-slate-300"><tr><th class="p-4">Trial checkpoint</th><th class="p-4">Record</th><th class="p-4">Decision question</th></tr></thead> <tbody class="divide-y divide-[#25293b] text-slate-300"> <tr><td class="p-4 font-bold text-white">Day 1 · Monitoring brief</td><td class="p-4">One brand term, one competitor and one high-value category phrase; write the action each signal could trigger.</td><td class="p-4">Would a relevant result change a response, campaign or customer decision?</td></tr> <tr><td class="p-4 font-bold text-white">Days 2–4 · Relevance sample</td><td class="p-4">Review a fixed sample of mentions. Mark relevant, irrelevant and ambiguous results, plus any exclusions you add.</td><td class="p-4">Can you reduce noise without filtering out results your team needs?</td></tr> <tr><td class="p-4 font-bold text-white">Days 5–7 · Source coverage</td><td class="p-4">List required public sources that appear and any important gaps. Do not treat the trial as proof of complete coverage.</td><td class="p-4">Are the sources you would act on represented often enough for your workflow?</td></tr> <tr><td class="p-4 font-bold text-white">Days 8–10 · Alert workflow</td><td class="p-4">Define one alert, its owner and the response rule. Record whether each alert led to a useful review or action.</td><td class="p-4">Does the alert reduce monitoring work, or create another queue of noise?</td></tr> <tr><td class="p-4 font-bold text-white">Days 11–14 · Handoff and plan fit</td><td class="p-4">Prepare one repeatable summary, note required users and keywords, and match the smallest current plan that covers them.</td><td class="p-4">Can a stakeholder use the output, and does that value justify the recurring price?</td></tr> </tbody> </table> </div> <div class="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm leading-6 text-amber-100"><strong>Keep the sample honest:</strong> Brand24 says new projects may begin with some data from the previous 30 days. Separate those historical results from mentions collected during your 14-day evaluation. The trial also limits X/Twitter and Instagram to 100 mentions per day, so a source cap is not the same as low market activity.</div> <div class="grid grid-cols-1 md:grid-cols-2 gap-3"> <div class="rounded-2xl border border-emerald-500/20 bg-[#0d1018] p-4"><h3 class="font-bold text-emerald-300">Continue after the trial if</h3><p class="mt-2 text-sm leading-6 text-slate-300">The results are relevant enough to drive named actions, required sources are adequately represented, and the smallest suitable plan covers your keywords, users and mention volume.</p></div> <div class="rounded-2xl border border-amber-500/20 bg-[#0d1018] p-4"><h3 class="font-bold text-amber-300">Pause before paying if</h3><p class="mt-2 text-sm leading-6 text-slate-300">Noise remains high, a critical source is missing, nobody owns the alert response, or the recurring price exceeds the value of the decisions the workflow supports.</p></div> </div> <div class="flex flex-wrap gap-3 text-sm font-bold"> <a href="https://brand24.com/prices/" target="_blank" rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">Official pricing →</a> <a href="https://help.brand24.com/en/articles/5336548-which-plan-is-the-trial-based-on-and-how-long-does-it-last" target="_blank" rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">Official trial limits →</a> <a href="https://help.brand24.com/en/articles/5336549-does-brand24-collect-historical-data" target="_blank" rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">Historical-data guidance →</a> </div> </section> <section class="rounded-3xl border border-[#262a3d] bg-[#121520] p-6 md:p-8 space-y-4"> <h2 class="text-2xl font-black text-white">Bottom line</h2>',
        ),
    ],
    "moosend.html": [
        (
            "<title>Moosend Pricing 2026: 30-Day Trial, Plans & Review | COSHUMA</title>",
            "<title>Moosend Review & Pricing 2026: 30-Day Free Trial, Plans & Costs | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Moosend pricing and review for 2026: 30-day no-card trial, Pro, Moosend+ and Enterprise plans, email credits, automation features, and a current offer link." />',
            '<meta name="description" content="Moosend review and pricing for 2026: compare the 30-day no-card trial, Pro, Moosend+ and Enterprise plans, 15% biannual and 20% annual savings, email credits and automation features." />',
        ),
        (
            '<meta name="description" content="Moosend pricing and review for 2026: 30-day no-card trial, Pro, Moosend+ and Enterprise plans, email credits, automation features, and a verified COSHUMA affiliate link." />',
            '<meta name="description" content="Moosend review and pricing for 2026: compare the 30-day no-card trial, Pro, Moosend+ and Enterprise plans, 15% biannual and 20% annual savings, email credits and automation features." />',
        ),
        (
            '<meta name="description" content="Moosend review and pricing for 2026: 30-day no-card trial, Pro, Moosend+ and Enterprise plans, email credits, automation features, and COSHUMA\'s verified affiliate link." />',
            '<meta name="description" content="Moosend review and pricing for 2026: compare the 30-day no-card trial, Pro, Moosend+ and Enterprise plans, 15% biannual and 20% annual savings, email credits and automation features." />',
        ),
        (
            '<meta property="og:title" content="Moosend Pricing 2026: 30-Day Trial, Plans & Review | COSHUMA" />',
            '<meta property="og:title" content="Moosend Review & Pricing 2026: 30-Day Free Trial & Plans | COSHUMA" />',
        ),
        (
            'EMAIL MARKETING · AUTOMATION · VERIFIED SEP 7, 2026',
            'EMAIL MARKETING · AUTOMATION · PRICING CHECKED SEP 18, 2026',
        ),
        (
            'Start Moosend via verified COSHUMA link →',
            'Start the 30-day Moosend trial →',
        ),
        (
            'Try Moosend via verified referral link →',
            'Try Moosend free for 30 days →',
        ),
        (
            "Checked against Moosend's official pricing page on September 7, 2026. Exact subscription price depends on contact count; verify the live selector before checkout.",
            "Checked against Moosend's official pricing page on September 18, 2026. Exact subscription price depends on contact count; verify the live selector before checkout.",
        ),
        (
            "Moosend's affiliate team specifically recommends sending prospects to trial and pricing-oriented destinations instead of relying only on a generic homepage. COSHUMA therefore keeps the exact verified referral URL as the monetized route while linking separately to Moosend's official pricing page for independent price verification.",
            "Use the 30-day no-card trial to build a real campaign and automation, then compare the paid price at your actual contact count. Moosend's official pricing page currently lists 15% savings for biannual billing and 20% for annual billing.",
        ),
        (
            'Official pricing remains a separate non-affiliate verification destination.',
            "Pricing and trial terms can change; check Moosend's live pricing before purchasing.",
        ),
        (
            '<a href="/tool/aweber.html" class="px-5 py-3 rounded-xl bg-[#181a29] border border-[#2a2d42] font-bold text-purple-300 text-center">Compare AWeber →</a>',
            '<a href="/best/moosend-vs-mailchimp-free-trial.html" class="px-5 py-3 rounded-xl bg-[#181a29] border border-[#2a2d42] font-bold text-purple-300 text-center">Moosend vs Mailchimp free trial →</a>',
        ),
    ],
    "unbounce.html": [
        (
            "<title>Unbounce Pricing 2026: $29 Starter + 20%/35% Partner Discount | COSHUMA</title>",
            "<title>Unbounce Review & Pricing 2026: 14-Day Free Trial, $29 Starter + 20%/35% Discount | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Unbounce pricing starts at $29/month. Compare current plans, the 14-day no-card trial, and COSHUMA\'s verified offer: 20% off 3 months or 35% off the first annual subscription." />',
            '<meta name="description" content="Unbounce review and pricing for 2026: Starter $29/mo, 14-day free trial with no credit card, current plan limits, and the current 20%/35% discount offer." />',
        ),
        (
            '<meta name="description" content="Unbounce review and pricing for 2026: Starter $29/mo, 14-day free trial with no credit card, current plan limits, and COSHUMA\'s verified 20%/35% partner discount." />',
            '<meta name="description" content="Unbounce review and pricing for 2026: Starter $29/mo, 14-day free trial with no credit card, current plan limits, and the current 20%/35% discount offer." />',
        ),
        (
            '<meta property="og:title" content="Unbounce Pricing 2026: $29 Starter + 20%/35% Partner Discount" />',
            '<meta property="og:title" content="Unbounce Review & Pricing 2026: 14-Day Free Trial + 20%/35% Discount" />',
        ),
        (
            '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce pricing, trial & verified partner discount</h1>',
            '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce Review, Pricing & Current Discount</h1>',
        ),
        (
            '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce Review, Pricing & Verified Partner Discount</h1>',
            '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce Review, Pricing & Current Discount</h1>',
        ),
        (
            '<h2 class="text-3xl font-black text-white mt-1">Unbounce plans checked September 6, 2026</h2>',
            '<h2 class="text-3xl font-black text-white mt-1">Unbounce plans checked September 9, 2026</h2>',
        ),
    ],
    "cloudways.html": [
        (
            "<title>Cloudways Pricing, Features & Review (2026) | COSHUMA</title>",
            "<title>Cloudways Pricing 2026: Managed Hosting from $11 + 3-Day Free Trial | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Cloudways is a managed cloud hosting platform designed to simplify the deployment and management of web applications for businesses and developers.... Discover features, pricing (See official pricing), and official links for Cloudways on COSHUMA." />',
            '<meta name="description" content="Cloudways pricing 2026: Flexible managed cloud hosting starts at $11/month with pay-as-you-go billing and a 3-day free trial without a credit card. Compare server sizes, bandwidth, backups and Autonomous WordPress plans." />',
        ),
        (
            '<meta property="og:title" content="Cloudways Review & Pricing (2026) | COSHUMA" />',
            '<meta property="og:title" content="Cloudways Pricing 2026: $11 Managed Hosting + 3-Day Trial | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="Cloudways is a managed cloud hosting platform designed to simplify the deployment and management of web applications for businesses and developers.... Check rating, pricing, and features." />',
            '<meta property="og:description" content="Compare Cloudways Flexible and Autonomous hosting, $11 entry pricing, hourly/pay-as-you-go billing, bandwidth, backups and the 3-day no-card trial." />',
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Cloudways</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Cloudways Pricing 2026: Flexible vs Autonomous Hosting</h1>',
        ),
        (
            '<p class="text-slate-300 text-base leading-relaxed">Cloudways is a managed cloud hosting platform designed to simplify the deployment and management of web applications for businesses and developers.</p>',
            '<p class="text-slate-300 text-base leading-relaxed"><strong class="text-white">Quick answer:</strong> Cloudways Flexible currently starts at $11/month on its entry managed cloud server and uses pay-as-you-go billing, including hourly calculation for supported infrastructure. New users can test Flexible for 3 days without a credit card. Compare Autonomous separately if you need hands-free WordPress autoscaling rather than direct server-size control.</p>',
        ),
        (
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">See official pricing</div>',
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">Flexible from $11/mo · 3-day no-card trial</div>',
        ),
        (
            'href="https://www.cloudways.com/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Official Cloudways Site</span><span>→</span></a>',
            'href="https://www.cloudways.com/en/pricing.php" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center border border-purple-500 hover:bg-purple-500 transition-all flex items-center justify-center gap-2"><span>Compare Cloudways pricing &amp; trial</span><span>→</span></a>',
        ),
    ],
    "alidropship.html": [
        (
            "<title>AliDropship Pricing, Features & Review (2026) | COSHUMA</title>",
            "<title>AliDropship Pricing 2026: $89 Plugin vs $39/mo Pro + 14-Day Trial | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="AliDropship offers WordPress and WooCommerce solutions to automate AliExpress dropshipping store management and product fulfillment with ease.... Discover features, pricing (Varies by plan), and official links for AliDropship on COSHUMA." />',
            '<meta name="description" content="AliDropship pricing 2026: the WordPress/WooCommerce plugin is $89 one-time; the turnkey Pro subscription starts at $39/month after a 14-day free trial. Compare ownership, hosting and automation before choosing." />',
        ),
        (
            '<meta property="og:title" content="AliDropship Review & Pricing (2026) | COSHUMA" />',
            '<meta property="og:title" content="AliDropship Pricing 2026: $89 Plugin vs $39/mo Pro | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="AliDropship offers WordPress and WooCommerce solutions to automate AliExpress dropshipping store management and product fulfillment with ease.... Check rating, pricing, and features." />',
            "<meta property=\"og:description\" content=\"Compare AliDropship's $89 one-time plugin with the $39/month turnkey Pro subscription and its 14-day trial before choosing a dropshipping setup.\" />",
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">AliDropship</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">AliDropship Pricing 2026: Plugin vs Pro Subscription</h1>',
        ),
        (
            '<p class="text-slate-300 text-base leading-relaxed">AliDropship offers WordPress and WooCommerce solutions to automate AliExpress dropshipping store management and product fulfillment with ease.</p>',
            '<p class="text-slate-300 text-base leading-relaxed"><strong class="text-white">Quick answer:</strong> choose the $89 one-time AliDropship plugin if you want to run the software on your own WordPress or WooCommerce store with no recurring plugin fee. Choose the turnkey Pro subscription if you want a store built for you: it currently starts with a 14-day free trial, then $39/month for Basic, with higher Advanced and Ultimate tiers available.</p>',
        ),
        (
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">Varies by plan</div>',
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">$89 one-time plugin · Pro from $39/mo after 14-day trial</div>',
        ),
        (
            'href="https://alidropship.com/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Official AliDropship Site</span><span>→</span></a>',
            'href="https://alidropship.com/plugin/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center border border-purple-500 hover:bg-purple-500 transition-all flex items-center justify-center gap-2"><span>Compare the $89 AliDropship plugin</span><span>→</span></a>',
        ),
    ],
    "pickaxe.html": [
        (
            "<title>Pickaxe Pricing, Features & Review (2026) | COSHUMA</title>",
            "<title>Pickaxe Pricing 2026: Free, Gold $37, Pro $147 & AI Agent Monetization | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="A no-code platform to effortlessly build, deploy, and monetize custom AI agents and branded portals, accelerating your AI development.... Discover features, pricing (See official pricing), and official links for Pickaxe on COSHUMA." />',
            '<meta name="description" content="Pickaxe pricing 2026: start free; Gold is $37/mo or $29/mo annually, Pro $147/mo or $116/mo annually, Business from $597/mo. Compare AI credits, workspaces, APIs and agent monetization." />',
        ),
        (
            '<meta property="og:title" content="Pickaxe Review & Pricing (2026) | COSHUMA" />',
            '<meta property="og:title" content="Pickaxe Pricing 2026: Free, Gold $37, Pro $147 | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="A no-code platform to effortlessly build, deploy, and monetize custom AI agents and branded portals, accelerating your AI development.... Check rating, pricing, and features." />',
            '<meta property="og:description" content="Compare Pickaxe Free, Gold, Pro and Business pricing, included AI credits, workspaces, APIs, white-labeling and built-in monetization for AI agents." />',
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Pickaxe</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Pickaxe Pricing 2026: Free, Gold, Pro &amp; Business</h1>',
        ),
        (
            '<p class="text-slate-300 text-base leading-relaxed">A no-code platform to effortlessly build, deploy, and monetize custom AI agents and branded portals, accelerating your AI development.</p>',
            '<p class="text-slate-300 text-base leading-relaxed"><strong class="text-white">Quick answer:</strong> start free to test an AI agent. Gold is currently $37/month or $29/month billed annually and includes $15/month in AI credits, white-labeling and up to 3 workspaces. Pro is $147/month or $116/month annually with $50/month in credits, unlimited workspaces and included API access. Business starts at $597/month with a 6-month minimum.</p>',
        ),
        (
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">See official pricing</div>',
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">Free entry · Gold $37 · Pro $147 · Business from $597</div>',
        ),
        (
            'href="https://pickaxe.ai/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Official Pickaxe Site</span><span>→</span></a>',
            'href="https://pickaxe.co/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center border border-purple-500 hover:bg-purple-500 transition-all flex items-center justify-center gap-2"><span>Compare Pickaxe plans &amp; start free</span><span>→</span></a>',
        ),
    ],
    "sendcloud.html": [
        (
            "<title>Sendcloud Pricing 2026: Free Plan, 14-Day Trial, €28 Lite & Label Fees | COSHUMA</title>",
            "<title>Sendcloud Pricing 2026: Free, Lite €28, Growth €87 + 14-Day Trial | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Sendcloud pricing for 2026: Free up to 20 parcels/month, Lite €28/mo, Growth €87/mo, Premium €175/mo, Pro €639/mo, plus label fees and a 14-day no-card trial. Compare the real cost before choosing a plan." />',
            '<meta name="description" content="Sendcloud pricing 2026: Free for up to 20 parcels/month; Lite €28, Growth €87, Premium €175 and Pro €639 monthly, plus per-label fees. Compare the 14-day no-card trial and total shipping cost." />',
        ),
        (
            '<meta property="og:title" content="Sendcloud Pricing 2026: Plans, Free Trial & Label Fees | COSHUMA" />',
            '<meta property="og:title" content="Sendcloud Pricing 2026: Free, Lite €28, Growth €87 & 14-Day Trial | COSHUMA" />',
        ),
        (
            '<h1 class="text-4xl md:text-5xl font-black tracking-tight mt-3">Sendcloud pricing 2026: plans, trial & label fees</h1>',
            '<h1 class="text-4xl md:text-5xl font-black tracking-tight mt-3">Sendcloud Pricing 2026: Free, Lite, Growth & Label Fees</h1>',
        ),
        (
            '<section class="rounded-3xl border border-[#222538] bg-[#131520] p-7 md:p-9"> <h2 class="text-2xl font-black">Affiliate-program status and link safety</h2> <p class="text-xs text-slate-500 mt-3">Publishing or verifying a tracking route would not by itself prove a signup, sale, commission or payout.</p> </section>',
            '',
        ),
        (
            '<strong class="text-slate-400">Sources checked September 10, 2026:</strong> Sendcloud official pricing page, Sendcloud official Affiliate Program page, and Sendcloud Help Center\'s 2026 regional subscription-pricing update.',
            '<strong class="text-slate-400">Sources checked September 19, 2026:</strong> Sendcloud official pricing page and Sendcloud Help Center pricing documentation.',
        ),
    ],
    "gallabox.html": [
        (
            "<title>Gallabox Pricing, Features & Review (2026) | COSHUMA</title>",
            "<title>Gallabox Pricing 2026: 7-Day Trial, Basic $112, Essential $248 | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="An AI-powered B2B platform specializing in WhatsApp automation for marketing, sales, and customer support for businesses and agencies.... Discover features, pricing (See official pricing), and official links for Gallabox on COSHUMA." />',
            '<meta name="description" content="Gallabox pricing 2026: 7-day no-card trial; annual plans currently show Basic $112/mo, Essential $248/mo and Advanced $474/mo. Compare users, AI credits, WhatsApp automation and AI-agent features." />',
        ),
        (
            '<meta property="og:title" content="Gallabox Review & Pricing (2026) | COSHUMA" />',
            '<meta property="og:title" content="Gallabox Pricing 2026: 7-Day Trial, Basic $112 & Essential $248 | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="An AI-powered B2B platform specializing in WhatsApp automation for marketing, sales, and customer support for businesses and agencies.... Check rating, pricing, and features." />',
            '<meta property="og:description" content="Compare Gallabox Basic, Essential and Advanced pricing, 7-day no-card trial, users, AI credits and WhatsApp/Instagram/web automation before choosing a plan." />',
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Gallabox</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Gallabox Pricing 2026: Basic, Essential &amp; Advanced</h1>',
        ),
        (
            '<p class="text-slate-300 text-base leading-relaxed">An AI-powered B2B platform specializing in WhatsApp automation for marketing, sales, and customer support for businesses and agencies.</p>',
            '<p class="text-slate-300 text-base leading-relaxed"><strong class="text-white">Quick answer:</strong> Gallabox offers a 7-day trial without a credit card. Current annual pricing shows Basic at $112/month for 3 users and 500 AI credits, Essential at $248/month for 6 users and 2,000 AI credits, and Advanced at $474/month for 10 users and 8,000 AI credits. Compare the same WhatsApp automation and AI-agent workflow before paying.</p>',
        ),
        (
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">See official pricing</div>',
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">7-day trial · Basic $112 · Essential $248 · Advanced $474</div>',
        ),
        (
            'href="https://www.gallabox.com/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Official Gallabox Site</span><span>→</span></a>',
            'href="https://gallabox.com/pricing" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center border border-purple-500 hover:bg-purple-500 transition-all flex items-center justify-center gap-2"><span>Compare Gallabox pricing &amp; trial</span><span>→</span></a>',
        ),
    ],
    "semrush.html": [
        (
            "<title>Semrush Pricing, Features & Review (2026) | COSHUMA</title>",
            "<title>Semrush Pricing 2026: Free Plan, SEO $139, AI Search & 7-Day Trials | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="A leading all-in-one platform providing comprehensive SEO and marketing tools for bloggers, agencies, and B2B content creators.... Discover features, pricing (See official pricing), and official links for Semrush on COSHUMA." />',
            '<meta name="description" content="Semrush pricing 2026: start free, SEO is $139/mo or $117.33/mo billed annually, and SEO + AI Search starts at $199/mo. Compare keyword research, Site Audit, rank tracking, AI visibility and trial options." />',
        ),
        (
            '<meta property="og:title" content="Semrush Review & Pricing (2026) | COSHUMA" />',
            '<meta property="og:title" content="Semrush Pricing 2026: Free, SEO $139 & AI Search Plans | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="A leading all-in-one platform providing comprehensive SEO and marketing tools for bloggers, agencies, and B2B content creators.... Check rating, pricing, and features." />',
            '<meta property="og:description" content="Compare Semrush Free, SEO and SEO + AI Search plans, current prices, keyword and competitor research, Site Audit, rank tracking and AI visibility." />',
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Semrush</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Semrush Pricing 2026: Free, SEO &amp; AI Search Plans</h1>',
        ),
        (
            '<p class="text-slate-300 text-base leading-relaxed">A leading all-in-one platform providing comprehensive SEO and marketing tools for bloggers, agencies, and B2B content creators.</p>',
            '<p class="text-slate-300 text-base leading-relaxed"><strong class="text-white">Quick answer:</strong> use Semrush Free to test the platform without a card. The current SEO plan is $139/month or $117.33/month billed annually and covers 5 websites, 500 tracked keywords, keyword/competitor research, Position Tracking, Site Audit and AI-search reporting. SEO + AI Search starts at $199/month for teams that need custom prompt tracking and deeper AI visibility.</p>',
        ),
        (
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">See official pricing</div>',
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">Free entry · SEO $139/mo · SEO + AI Search $199/mo</div>',
        ),
        (
            'href="https://www.semrush.com/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Official Semrush Site</span><span>→</span></a>',
            'href="https://www.semrush.com/pricing/seo-ai-search/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center border border-purple-500 hover:bg-purple-500 transition-all flex items-center justify-center gap-2"><span>Compare Semrush pricing &amp; free options</span><span>→</span></a>',
        ),
    ],
    "aweber.html": [
        (
            "<title>AWeber Review & Pricing 2026: 14-Day Free Trial, $15/month Lite & Best Fit | COSHUMA</title>",
            "<title>AWeber Pricing 2026: Free Plan, 14-Day Trial, Lite $15 & Plus $30 | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="AWeber pricing for up to 500 subscribers: Lite $15 monthly or $150 annually; Plus $30 monthly or $240 annually. Compare features and the 14-day trial." />',
            '<meta name="description" content="AWeber pricing 2026: Free supports up to 500 subscribers and 3,000 emails/month; Lite starts at $15/mo and Plus at $30/mo. Compare the 14-day paid-plan trial, limits and annual pricing." />',
        ),
        (
            '<meta property="og:title" content="AWeber Review & Pricing 2026: 14-Day Trial + $15 Lite" />',
            '<meta property="og:title" content="AWeber Pricing 2026: Free Plan, 14-Day Trial, Lite $15 & Plus $30" />',
        ),
        (
            '<meta property="og:description" content="Compare AWeber\'s current Lite and Plus pricing, 14-day trial, automation capabilities and buyer fit before choosing a plan." />',
            '<meta property="og:description" content="Compare AWeber Free, Lite and Plus: 500-subscriber free access, current paid pricing, 14-day trial terms, automation limits and annual savings." />',
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">AWeber Review, Pricing &amp; Best-Fit Guide</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">AWeber Pricing 2026: Free, Lite &amp; Plus Compared</h1>',
        ),
        (
            '<p class="text-slate-400 text-sm mt-2">Pricing and trial terms rechecked against AWeber official pages on September 19, 2026.</p>',
            '<p class="text-slate-400 text-sm mt-2">Pricing and trial terms rechecked against AWeber official pages on September 19, 2026.</p>',
        ),
        (
            '<p class="text-slate-300 leading-relaxed mt-2">AWeber is a practical fit for creators and small businesses that want email campaigns, automations, landing pages, subscriber management and ecommerce tools in one established platform. For up to 500 subscribers, AWeber\'s official pricing tables list Lite at $15 monthly or $150 annually, and Plus at $30 monthly or $240 annually. Annual totals are charged for the year; a 14-day trial is advertised.</p>',
            '<p class="text-slate-300 leading-relaxed mt-2"><strong class="text-white">Quick answer:</strong> start on AWeber Free if 500 subscribers and 3,000 emails per month cover your workflow. Move to Lite when you need more sending capacity and paid features, or Plus when unlimited lists, landing pages, automations and advanced reporting matter. AWeber also advertises a 14-day trial for paid plans.</p>',
        ),
        (
            '>Compare AWeber plans →</a>',
            '>Start with AWeber Free →</a>',
        ),

        (
            "<title>AWeber Pricing, 14-Day Trial & Best Fit (2026) | COSHUMA</title>",
            "<title>AWeber Review & Pricing 2026: 14-Day Free Trial, $15/month Lite & Best Fit | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="AWeber buyer guide for 2026: compare current Lite and Plus pricing, the 14-day trial, email automation features, best-fit use cases and a verified affiliate link." />',
            '<meta name="description" content="AWeber pricing for up to 500 subscribers: Lite $15 monthly or $150 annually; Plus $30 monthly or $240 annually. Compare features and the 14-day trial." />',
        ),
        (
            '<meta property="og:title" content="AWeber Pricing, 14-Day Trial & Best Fit (2026)" />',
            '<meta property="og:title" content="AWeber Review & Pricing 2026: 14-Day Trial + $15 Lite" />',
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">AWeber Pricing &amp; Best-Fit Guide</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">AWeber Review, Pricing &amp; Best-Fit Guide</h1>',
        ),
        (
            '<p class="text-slate-400 text-sm mt-2">Checked against AWeber\'s official pricing and Advocate Program documentation on September 2, 2026.</p>',
            '<p class="text-slate-400 text-sm mt-2">Checked against AWeber\'s official pricing and Advocate Program documentation on September 10, 2026.</p>',
        ),
        (
            '<span class="font-extrabold text-lg tracking-tight text-white">GlobalSaaSHub</span>',
            '<span class="font-extrabold text-lg tracking-tight text-white">COSHUMA</span>',
        ),
    ],
    "jotform.html": [
        (
            "<title>Jotform Review & Pricing 2026: Free Plan, $34 Bronze, $39 Silver & AI Agents | COSHUMA</title>",
            "<title>Jotform Pricing 2026: Free Plan, Bronze $34, Silver $39, Gold $99 | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Jotform review and pricing for 2026: Starter is free, Bronze $34/mo, Silver $39/mo and Gold $99/mo billed annually. Compare plan limits and AI Agents for customer-support automation." />',
            '<meta name="description" content="Jotform pricing 2026: Starter is free; Bronze $34/mo, Silver $39/mo and Gold $99/mo billed annually. Compare forms, submissions, storage, signed-document limits and when to upgrade." />',
        ),
        (
            '<meta property="og:title" content="Jotform Review & Pricing 2026: Free Plan, Paid Tiers & AI Agents | COSHUMA" />',
            '<meta property="og:title" content="Jotform Pricing 2026: Free Plan, Bronze $34, Silver $39 & Gold $99 | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="Compare Jotform Starter, Bronze, Silver, Gold and Enterprise, then see when Jotform AI Agents is the better fit for 24/7 customer-support automation." />',
            '<meta property="og:description" content="Compare Jotform Free, Bronze, Silver and Gold by price, forms, monthly submissions, storage and signed-document limits before upgrading." />',
        ),
        (
            '<h1 class="text-4xl md:text-5xl font-black text-white tracking-tight">Jotform Review, Pricing & Buyer Guide</h1>',
            '<h1 class="text-4xl md:text-5xl font-black text-white tracking-tight">Jotform Pricing 2026: Free, Bronze, Silver & Gold</h1>',
        ),
        (
            '<p class="text-sm text-slate-400 mt-2">Updated September 9, 2026</p>',
            '<p class="text-sm text-slate-400 mt-2">Pricing rechecked against Jotform official pages on September 19, 2026</p>',
        ),
        (
            '<p class="text-lg leading-relaxed text-slate-300 max-w-4xl">Jotform is strongest when you want one no-code stack for forms, payments, e-signatures and workflow capture. The free Starter plan is enough to validate a use case; paid plans mainly raise limits and remove branding. If your goal is automated customer service rather than form building alone, Jotform AI Agents is the more relevant path.</p>',
            '<p class="text-lg leading-relaxed text-slate-300 max-w-4xl"><strong class="text-white">Quick answer:</strong> use Starter for free if 5 forms and 100 monthly submissions are enough. Bronze raises capacity to 25 forms and 1,000 submissions, Silver to 50 forms and 2,500 submissions, and Gold to 100 forms and 10,000 submissions. Upgrade for real limit pressure, branding removal or HIPAA-enabled features—not just because a paid tier exists.</p>',
        ),

        (
            "<title>Jotform Pricing 2026: Free, Bronze, Silver, Gold & AI Agents | COSHUMA</title>",
            "<title>Jotform Review & Pricing 2026: Free Plan, $34 Bronze, $39 Silver & AI Agents | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Jotform pricing and buyer guide for 2026: compare the free Starter plan, Bronze, Silver, Gold and Enterprise, plus a verified Jotform AI Agents partner path for customer-support automation." />',
            '<meta name="description" content="Jotform review and pricing for 2026: Starter is free, Bronze $34/mo, Silver $39/mo and Gold $99/mo billed annually. Compare plan limits and AI Agents for customer-support automation." />',
        ),
        (
            '<meta name="description" content="Jotform review and pricing for 2026: Starter is free, Bronze $34/mo, Silver $39/mo and Gold $99/mo billed annually. Compare limits and the verified Jotform AI Agents partner path." />',
            '<meta name="description" content="Jotform review and pricing for 2026: Starter is free, Bronze $34/mo, Silver $39/mo and Gold $99/mo billed annually. Compare plan limits and AI Agents for customer-support automation." />',
        ),
        (
            '<meta property="og:title" content="Jotform Pricing 2026: Plans, Limits & AI Agents | COSHUMA" />',
            '<meta property="og:title" content="Jotform Review & Pricing 2026: Free Plan, Paid Tiers & AI Agents | COSHUMA" />',
        ),
        (
            '<h1 class="text-4xl md:text-5xl font-black text-white tracking-tight">Jotform pricing & buyer guide</h1>',
            '<h1 class="text-4xl md:text-5xl font-black text-white tracking-tight">Jotform Review, Pricing & Buyer Guide</h1>',
        ),
        (
            '<p class="text-sm text-slate-400 mt-2">Updated September 7, 2026</p>',
            '<p class="text-sm text-slate-400 mt-2">Updated September 9, 2026</p>',
        ),
        (
            "<title>Jotform Review & Pricing 2026: Free Plan, $34 Bronze, $39 Silver & AI Agents | COSHUMA</title>",
            "<title>Jotform Pricing 2026: Free Plan, Bronze $34, Silver $39, Gold $99 | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Jotform review and pricing for 2026: Starter is free, Bronze $34/mo, Silver $39/mo and Gold $99/mo billed annually. Compare plan limits and AI Agents for customer-support automation." />',
            '<meta name="description" content="Jotform pricing 2026: Starter is free; Bronze $34/mo, Silver $39/mo and Gold $99/mo billed annually. Compare forms, submissions, storage, signed-document limits and when to upgrade." />',
        ),
        (
            '<meta property="og:title" content="Jotform Review & Pricing 2026: Free Plan, Paid Tiers & AI Agents | COSHUMA" />',
            '<meta property="og:title" content="Jotform Pricing 2026: Free Plan, Bronze $34, Silver $39 & Gold $99 | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="Compare Jotform Starter, Bronze, Silver, Gold and Enterprise, then see when Jotform AI Agents is the better fit for 24/7 customer-support automation." />',
            '<meta property="og:description" content="Compare Jotform Free, Bronze, Silver and Gold by price, forms, monthly submissions, storage and signed-document limits before upgrading." />',
        ),
        (
            '<h1 class="text-4xl md:text-5xl font-black text-white tracking-tight">Jotform Review, Pricing & Buyer Guide</h1>',
            '<h1 class="text-4xl md:text-5xl font-black text-white tracking-tight">Jotform Pricing 2026: Free, Bronze, Silver & Gold</h1>',
        ),
        (
            '<p class="text-sm text-slate-400 mt-2">Updated September 9, 2026</p>',
            '<p class="text-sm text-slate-400 mt-2">Pricing rechecked against Jotform official pages on September 19, 2026</p>',
        ),
        (
            '<p class="text-lg leading-relaxed text-slate-300 max-w-4xl">Jotform is strongest when you want one no-code stack for forms, payments, e-signatures and workflow capture. The free Starter plan is enough to validate a use case; paid plans mainly raise limits and remove branding. If your goal is automated customer service rather than form building alone, Jotform AI Agents is the more relevant path.</p>',
            '<p class="text-lg leading-relaxed text-slate-300 max-w-4xl"><strong class="text-white">Quick answer:</strong> use Starter for free if 5 forms and 100 monthly submissions are enough. Bronze raises capacity to 25 forms and 1,000 submissions, Silver to 50 forms and 2,500 submissions, and Gold to 100 forms and 10,000 submissions. Upgrade for real limit pressure, branding removal or HIPAA-enabled features—not just because a paid tier exists.</p>',
        ),
    ],
    "octo-browser.html": [
        (
            "<title>Octo Browser Pricing, Features & Review (2026) | COSHUMA</title>",
            "<title>Octo Browser Pricing 2026: Plans, Features & Review | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Octo Browser is an advanced antidetect browser designed for secure multi-accounting and digital fingerprint management across various online platforms... Discover features, pricing (See official pricing), and official links for Octo Browser on COSHUMA." />',
            '<meta name="description" content="Octo Browser pricing and review for 2026: check current official plans, compare antidetect browser, multi-accounting and digital fingerprint features, and decide if it fits your workflow." />',
        ),
        (
            '<meta property="og:title" content="Octo Browser Review & Pricing (2026) | COSHUMA" />',
            '<meta property="og:title" content="Octo Browser Pricing & Review 2026: Plans and Features | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="Octo Browser is an advanced antidetect browser designed for secure multi-accounting and digital fingerprint management across various online platforms... Check rating, pricing, and features." />',
            '<meta property="og:description" content="Check current Octo Browser pricing, then compare its antidetect browser, multi-accounting and digital fingerprint features before choosing." />',
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Octo Browser</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Octo Browser Pricing &amp; Review 2026</h1>',
        ),
        (
            '<p class="text-slate-300 text-base leading-relaxed">Octo Browser is an advanced antidetect browser designed for secure multi-accounting and digital fingerprint management across various online platforms.</p>',
            '<p class="text-slate-300 text-base leading-relaxed"><strong class="text-white">Quick answer:</strong> Octo Browser is a paid profile-management browser for authorized multi-account workflows. Its official pricing page currently shows Lite at €10/month, Starter from €29, Base from €79, Team from €169 and Advanced from €329. Check the live billing term and limits before checkout; use the product only where your account and platform rules permit it.</p>',
        ),
        (
            '<!-- Pricing & Action --> <div class="p-6 rounded-2xl bg-[#181a29] border border-[#222538] flex flex-col sm:flex-row sm:items-center justify-between gap-4"> <div> <div class="text-xs uppercase font-bold text-slate-400 tracking-wider">Pricing Plan</div> <div class="text-xl font-extrabold text-emerald-400 mt-0.5">See official pricing</div> </div> <a data-cta="official" href="https://octobrowser.net/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Official Octo Browser Site</span><span>→</span></a> </div>',
            '<section id="octo-two-day-evaluation" class="space-y-5 pt-4 border-t border-[#222538]"> <div class="space-y-2"> <div class="text-xs uppercase font-bold tracking-wider text-purple-300">Buyer checklist · official sources checked October 8, 2026</div> <h2 class="text-2xl font-black text-white">A 2-day evaluation checklist before you subscribe</h2> <p class="text-sm leading-relaxed text-slate-300">Octo offers new users a one-time 2-day Starter trial with promo code <strong class="text-white">TRIAL</strong>. COSHUMA has not completed a hands-on product test; this checklist translates Octo\'s current official pricing, download and terms pages into a reproducible buying decision.</p> </div> <ol class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-slate-300"> <li class="p-4 rounded-xl bg-[#181a29] border border-[#222538]"><strong class="text-white">1. Confirm installation fit.</strong> The current download page lists Windows 10 or later, Windows Server 2016 or later, macOS Ventura 13 or later, plus supported Linux distributions including Ubuntu 22.04 or later. Install only on a supported test device.</li> <li class="p-4 rounded-xl bg-[#181a29] border border-[#222538]"><strong class="text-white">2. Match profile capacity.</strong> The official comparison currently lists 3 profiles on Lite, 10 on Starter, 100 on Base, 350 on Team and 1,200 on Advanced. Count the profiles you actually need before choosing a tier.</li> <li class="p-4 rounded-xl bg-[#181a29] border border-[#222538]"><strong class="text-white">3. Test the real workflow safely.</strong> Use non-sensitive test accounts in a workflow you are authorized to run. Check profile creation, organization and recovery without trying to evade a platform\'s rules or access controls.</li> <li class="p-4 rounded-xl bg-[#181a29] border border-[#222538]"><strong class="text-white">4. Check collaboration and API needs.</strong> API access starts at Base on the current comparison table; Lite and Starter do not include it. Team currently includes 3 team members and Advanced 8, so verify seats and request limits before paying.</li> <li class="p-4 rounded-xl bg-[#181a29] border border-[#222538] md:col-span-2"><strong class="text-white">5. Calculate the full commitment.</strong> Compare the live 1-, 3-, 6- and 12-month options. Octo\'s terms state that 1 Octo Token equals €1 for subscription payment and that a downgrade takes effect only after the current subscription expires; remove resources above the lower plan\'s limits first.</li> </ol> <div class="grid grid-cols-1 md:grid-cols-2 gap-3"> <div class="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20"><h3 class="font-bold text-emerald-300">Continue after the trial if</h3><p class="mt-2 text-sm text-slate-300">The supported device works, the chosen tier covers profiles, seats and API usage, and your intended workflow passes your platform-policy review.</p></div> <div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20"><h3 class="font-bold text-amber-300">Pause before paying if</h3><p class="mt-2 text-sm text-slate-300">You need API access on Lite or Starter, expect to downgrade mid-term, cannot confirm the workflow is authorized, or still have unpriced operational dependencies.</p></div> </div> <div class="flex flex-wrap gap-3 text-sm font-bold"> <a href="https://octobrowser.net/pricing/" target="_blank" rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">Official pricing →</a> <a href="https://octobrowser.org/download/" target="_blank" rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">System requirements →</a> <a href="https://octobrowser.net/terms/" target="_blank" rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">Terms of use →</a> </div> </section> <!-- Pricing & Action --> <div class="p-6 rounded-2xl bg-[#181a29] border border-[#222538] flex flex-col sm:flex-row sm:items-center justify-between gap-4"> <div> <div class="text-xs uppercase font-bold text-slate-400 tracking-wider">Current headline monthly prices</div> <div class="text-xl font-extrabold text-emerald-400 mt-0.5">Lite €10 · Starter from €29 · Base from €79</div> <div class="text-xs text-slate-400 mt-1">Team from €169 · Advanced from €329 · verify live billing before checkout</div> </div> <a data-cta="official" href="https://octobrowser.net/pricing/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center border border-purple-500 hover:bg-purple-500 transition-all flex items-center justify-center gap-2"><span>Compare official Octo plans</span><span>→</span></a> </div>',
        ),
    ]
}

FORBIDDEN_PUBLIC_COPY = (
    "verified coshuma",
    "verified partner",
    "verified affiliate",
    "verified referral",
    "affiliate manager",
    "partner manager",
    "customer-facing tracking",
    "tracking verification",
    "affiliate dashboard",
    "partner dashboard",
    "revenue-truth",
    "partner-side evidence",
    "affiliate evidence",
    "monetized route",
    "affiliate team specifically recommends",
    'data-campaign-asset="c07"',
    "c07: evidence-backed decision asset",
)

changed = 0
for filename, replacements in PATCHES.items():
    path = TOOL_DIR / filename
    text = path.read_text(encoding="utf-8")
    original = text

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)

    # The deploy workflow polishes generic customer copy before `npm run build`.
    # On Octo Browser that changes "Pricing Plan" to "Pricing" and shortens the
    # official CTA label, so the historical exact-string replacement above can
    # miss only the checklist while still applying the title and overview edits.
    # Recover from that known producer ordering without matching an arbitrary
    # page block, then fail closed if the decision asset is still absent.
    if filename == "octo-browser.html" and 'id="octo-two-day-evaluation"' not in text:
        anchor = "<!-- Pricing & Action -->"
        cta_end = "<span>→</span></a> </div>"
        start = text.find(anchor)
        end = text.find(cta_end, start) if start != -1 else -1
        if end != -1:
            end += len(cta_end)
            current_pricing = text[start:end]
            expected_fragments = (
                'data-cta="official"',
                'href="https://octobrowser.net/"',
                "See official pricing",
            )
            if all(fragment in current_pricing for fragment in expected_fragments):
                text = text[:start] + PATCHES[filename][-1][1] + text[end:]

    if filename == "brand24.html":
        required = (
            'id="brand24-14-day-evaluation"',
            "A 14-day signal-quality scorecard before you subscribe",
            "COSHUMA has not completed a hands-on product test",
            'href="https://brand24.com/prices/"',
            'href="https://help.brand24.com/en/articles/5336548-which-plan-is-the-trial-based-on-and-how-long-does-it-last"',
            "The trial also limits X/Twitter and Instagram to 100 mentions per day",
        )
        missing = [marker for marker in required if marker not in text]
        if missing:
            raise SystemExit(f"Brand24 buyer-scorecard patch incomplete: {missing}")

    if filename == "octo-browser.html":
        required = (
            'id="octo-two-day-evaluation"',
            "A 2-day evaluation checklist before you subscribe",
            'href="https://octobrowser.net/pricing/"',
            "COSHUMA has not completed a hands-on product test",
        )
        missing = [marker for marker in required if marker not in text]
        if missing:
            raise SystemExit(f"Octo Browser buyer-checklist patch incomplete: {missing}")

    lowered = text.lower()
    leftovers = [phrase for phrase in FORBIDDEN_PUBLIC_COPY if phrase in lowered]
    if leftovers:
        raise SystemExit(f"CTR customer-copy guard failed in {filename}: {leftovers}")

    if text != original:
        path.write_text(text, encoding="utf-8")
        changed += 1

print(f"Search Console CTR patches applied safely to {changed} tool page(s).")
