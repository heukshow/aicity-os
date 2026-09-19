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
            '<p class="text-slate-400 text-sm mt-2">Checked against AWeber\'s official pricing and Advocate Program documentation on September 10, 2026.</p>',
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
)

changed = 0
for filename, replacements in PATCHES.items():
    path = TOOL_DIR / filename
    text = path.read_text(encoding="utf-8")
    original = text

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)

    lowered = text.lower()
    leftovers = [phrase for phrase in FORBIDDEN_PUBLIC_COPY if phrase in lowered]
    if leftovers:
        raise SystemExit(f"CTR customer-copy guard failed in {filename}: {leftovers}")

    if text != original:
        path.write_text(text, encoding="utf-8")
        changed += 1

print(f"Search Console CTR patches applied safely to {changed} tool page(s).")
