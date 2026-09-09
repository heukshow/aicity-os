"""Apply conservative CTR-oriented SEO patches backed by live Search Console data.

The 2026-09-08 live snapshot showed substantial impressions but zero search clicks
for Brand24, Moosend, Unbounce, AWeber, Omnisend and Jotform tool pages. Query data
included Brand24 review/pricing variants, "moosend review", "omnisend pricing",
"aweber pricing" and "jotform pricing". Omnisend is now handled by its dedicated,
approval-aware patch so a stale submitted-state exact match cannot overwrite newer
vendor evidence. Keep this script exact-match and idempotent for the remaining pages.
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
