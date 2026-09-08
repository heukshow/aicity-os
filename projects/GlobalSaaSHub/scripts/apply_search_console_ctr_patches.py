"""Apply conservative CTR-oriented SEO patches backed by live Search Console data.

The 2026-09-08 live snapshot showed substantial impressions but zero search clicks
for Brand24, Moosend, Unbounce, AWeber, Omnisend and Jotform tool pages. Query data
included Brand24 review/pricing variants, "moosend review", "omnisend pricing",
"aweber pricing" and "jotform pricing". Keep this script exact-match and idempotent
so it cannot rewrite unrelated pages or invent offers.
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
            '<meta name="description" content="Brand24 review and pricing for 2026: plans start at $249/mo ($199/mo billed annually), with a 14-day free trial and no credit card. Compare limits, AI Visibility, who it fits, and try it through COSHUMA\'s verified partner link." />',
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
            '<meta name="description" content="Moosend pricing and review for 2026: 30-day no-card trial, Pro, Moosend+ and Enterprise plans, email credits, automation features, and a verified COSHUMA affiliate link." />',
            '<meta name="description" content="Moosend review and pricing for 2026: 30-day no-card trial, Pro, Moosend+ and Enterprise plans, email credits, automation features, and COSHUMA\'s verified affiliate link." />',
        ),
        (
            '<meta property="og:title" content="Moosend Pricing 2026: 30-Day Trial, Plans & Review | COSHUMA" />',
            '<meta property="og:title" content="Moosend Review & Pricing 2026: 30-Day Free Trial & Plans | COSHUMA" />',
        ),
    ],
    "unbounce.html": [
        (
            "<title>Unbounce Pricing 2026: $29 Starter + 20%/35% Partner Discount | COSHUMA</title>",
            "<title>Unbounce Review & Pricing 2026: 14-Day Free Trial, $29 Starter + 20%/35% Discount | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Unbounce pricing starts at $29/month. Compare current plans, the 14-day no-card trial, and COSHUMA\'s verified offer: 20% off 3 months or 35% off the first annual subscription." />',
            '<meta name="description" content="Unbounce review and pricing for 2026: Starter $29/mo, 14-day free trial with no credit card, current plan limits, and COSHUMA\'s verified 20%/35% partner discount." />',
        ),
        (
            '<meta property="og:title" content="Unbounce Pricing 2026: $29 Starter + 20%/35% Partner Discount" />',
            '<meta property="og:title" content="Unbounce Review & Pricing 2026: 14-Day Free Trial + Partner Discount" />',
        ),
        (
            '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce pricing, trial & verified partner discount</h1>',
            '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce Review, Pricing & Verified Partner Discount</h1>',
        ),
        (
            '<h2 class="text-3xl font-black text-white mt-1">Unbounce plans checked September 6, 2026</h2>',
            '<h2 class="text-3xl font-black text-white mt-1">Unbounce plans checked September 9, 2026</h2>',
        ),
    ],
    "aweber.html": [
        (
            "<title>AWeber Pricing, 14-Day Trial & Best Fit (2026) | COSHUMA</title>",
            "<title>AWeber Review & Pricing 2026: 14-Day Free Trial, $15 Lite & Best Fit | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="AWeber buyer guide for 2026: compare current Lite and Plus pricing, the 14-day trial, email automation features, best-fit use cases and a verified affiliate link." />',
            '<meta name="description" content="AWeber review and pricing for 2026: Lite starts at $15/mo or $12.49/mo billed annually, Plus from $19.99/mo billed annually, with a 14-day trial and COSHUMA\'s verified affiliate link." />',
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
            '<p class="text-slate-400 text-sm mt-2">Checked against AWeber\'s official pricing and Advocate Program documentation on September 9, 2026.</p>',
        ),
        (
            '<span class="font-extrabold text-lg tracking-tight text-white">GlobalSaaSHub</span>',
            '<span class="font-extrabold text-lg tracking-tight text-white">COSHUMA</span>',
        ),
    ],
    "omnisend.html": [
        (
            "<title>Omnisend Pricing, Features & Review (2026) | GlobalSaaSHub</title>",
            "<title>Omnisend Review & Pricing 2026: Free Plan, $16 Standard & $59 Pro | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="An advanced e-commerce marketing automation platform, integrating email, SMS, and push notifications to drive sales and customer retention.... Discover features, pricing (See official pricing), and official links for Omnisend on GlobalSaaSHub." />',
            '<meta name="description" content="Omnisend review and pricing for 2026: Free up to 250 billable contacts, Standard from $16/mo and Pro from $59/mo. Compare current email/SMS limits, the first-upgrade discount, and a verified Moosend alternative." />',
        ),
        (
            '<meta property="og:title" content="Omnisend Review & Pricing (2026) | GlobalSaaSHub" />',
            '<meta property="og:title" content="Omnisend Review & Pricing 2026: Free, Standard & Pro | COSHUMA" />',
        ),
        (
            '<meta property="og:description" content="An advanced e-commerce marketing automation platform, integrating email, SMS, and push notifications to drive sales and customer retention.... Check rating, pricing, and features." />',
            '<meta property="og:description" content="Compare Omnisend Free, Standard and Pro pricing, current 2026 send/SMS rules, and when a 30-day Moosend trial may be worth comparing." />',
        ),
        (
            '<span class="font-extrabold text-lg tracking-tight text-white">GlobalSaaSHub</span>',
            '<span class="font-extrabold text-lg tracking-tight text-white">COSHUMA</span>',
        ),
        (
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Omnisend</h1>',
            '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Omnisend Review &amp; Pricing 2026</h1>',
        ),
        (
            '<span>Not yet editorially rated</span>',
            '<span>Affiliate application submitted · tracking link not approved yet</span>',
        ),
        (
            "    </style>\n  </head>",
            "    </style>\n    <script defer src=\"/affiliate-attribution.js\"></script>\n  </head>",
        ),
        (
            '        <!-- Alternatives & Direct Competitors Section -->',
            '''        <!-- COSHUMA_OMNISEND_2026_BUYER_DECISION -->\n        <section class="rounded-2xl border border-cyan-500/25 bg-cyan-500/5 p-6 space-y-5">\n          <div>\n            <div class="text-[10px] font-extrabold uppercase tracking-[0.16em] text-cyan-300">2026 buyer decision · verified against Omnisend Help Center</div>\n            <h2 class="mt-2 text-2xl font-black text-white">Start with contact count and channel needs, not the plan name</h2>\n            <p class="mt-2 text-sm leading-relaxed text-slate-300">Omnisend pricing changes with billable contacts. The current Free plan supports up to 250 billable contacts and 500 emails per month. Standard starts at $16/month and includes email credits equal to 12× billable contacts. Pro starts at $59/month with unlimited email; for new paid subscriptions on or after May 4, 2026, SMS is a Pro add-on with volume pricing starting at $0.007 per SMS for US/Canada recipients.</p>\n          </div>\n          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">\n            <div class="rounded-xl border border-white/10 bg-[#0d1018] p-4"><div class="text-xs font-bold text-slate-400">Free</div><div class="mt-1 text-xl font-black text-white">$0</div><p class="mt-2 text-xs leading-5 text-slate-400">Up to 250 billable contacts · 500 emails/month.</p></div>\n            <div class="rounded-xl border border-white/10 bg-[#0d1018] p-4"><div class="text-xs font-bold text-slate-400">Standard</div><div class="mt-1 text-xl font-black text-white">From $16/mo</div><p class="mt-2 text-xs leading-5 text-slate-400">Email-focused plan; monthly email credits scale at 12× billable contacts.</p></div>\n            <div class="rounded-xl border border-white/10 bg-[#0d1018] p-4"><div class="text-xs font-bold text-slate-400">Pro</div><div class="mt-1 text-xl font-black text-white">From $59/mo</div><p class="mt-2 text-xs leading-5 text-slate-400">Unlimited email. Current SMS access for new subscribers requires Pro plus SMS credits.</p></div>\n          </div>\n          <div class="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm leading-relaxed text-slate-300"><strong class="text-white">New-subscriber offer:</strong> Omnisend currently documents 30% off the first three months when a first-time paid subscriber chooses to pay three months upfront: Standard $11.20/month or Pro $41.30/month for that initial three-month period. Verify the live checkout before relying on the offer.</div>\n          <div class="flex flex-col sm:flex-row gap-3">\n            <a data-cta="official" data-tool-id="omnisend" data-cta-source="omnisend_2026_pricing" href="https://www.omnisend.com/pricing/" target="_blank" rel="noopener noreferrer" class="px-5 py-3.5 rounded-xl bg-slate-800 border border-slate-600 text-white font-extrabold text-center">Check current Omnisend pricing →</a>\n            <a data-cta="affiliate" data-tool-id="moosend" data-cta-source="omnisend_verified_alternative" href="https://trymoo.moosend.com/6eappdpw04pw" target="_blank" rel="sponsored noopener noreferrer" class="px-5 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-center">Prefer a 30-day trial? Compare Moosend →</a>\n          </div>\n          <p class="text-[11px] leading-5 text-slate-500">COSHUMA's Omnisend affiliate application is already submitted, but an account-specific Omnisend customer tracking URL is not yet approved or verified, so Omnisend links remain ordinary official links. The Moosend button uses COSHUMA's separately verified customer-facing partner URL; COSHUMA may earn a commission on an eligible Moosend purchase at no extra cost to you.</p>\n        </section>\n\n        <!-- Alternatives & Direct Competitors Section -->''',
        ),
        (
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">See official pricing</div>',
            '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">Free · Standard from $16/mo · Pro from $59/mo</div>',
        ),
        (
            '<a data-cta="official" href="https://www.omnisend.com/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Official Omnisend Site</span><span>→</span></a>',
            '<a data-cta="official" data-tool-id="omnisend" data-cta-source="omnisend_pricing_bottom" href="https://www.omnisend.com/pricing/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>View Official Omnisend Pricing</span><span>→</span></a>',
        ),
    ],
    "jotform.html": [
        (
            "<title>Jotform Pricing 2026: Free, Bronze, Silver, Gold & AI Agents | COSHUMA</title>",
            "<title>Jotform Review & Pricing 2026: Free Plan, $34 Bronze, $39 Silver & AI Agents | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Jotform pricing and buyer guide for 2026: compare the free Starter plan, Bronze, Silver, Gold and Enterprise, plus a verified Jotform AI Agents partner path for customer-support automation." />',
            '<meta name="description" content="Jotform review and pricing for 2026: Starter is free, Bronze $34/mo, Silver $39/mo and Gold $99/mo billed annually. Compare limits and the verified Jotform AI Agents partner path." />',
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
    ],
}

changed = 0
for filename, replacements in PATCHES.items():
    path = TOOL_DIR / filename
    text = path.read_text(encoding="utf-8")
    original = text

    for old, new in replacements:
        if new in text:
            continue
        if old not in text:
            raise SystemExit(f"Refusing uncertain CTR patch: exact source text missing in {filename}: {old[:80]}")
        text = text.replace(old, new, 1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        changed += 1

print(f"Search Console CTR patches applied to {changed} tool page(s).")