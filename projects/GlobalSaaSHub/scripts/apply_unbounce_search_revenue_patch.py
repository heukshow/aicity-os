"""Improve the highest-impression approved-tracking Unbounce page for pricing intent.

Evidence used:
- Live Search Console snapshot: /tool/unbounce.html had 168 impressions and 0 clicks.
- Admin snapshot query signal: "unbounce" had 82 impressions and 0 clicks.
- Verified customer tracking URL stays unchanged: https://unbounce.partnerlinks.io/5ubjnt8lluqi
- Unbounce official pricing on 2026-09-09: Starter $29 monthly / $22 yearly,
  Build $99 / $74, Experiment $149 / $112, Optimize $249 / $187;
  14-day free trial with no credit card.
- Unbounce partner program: referred customers receive 20% off first 3 months or
  35% off first annual subscription; 90-day tracking cookie.

This patch is intentionally exact-match and idempotent. It does not change the
verified referral URL or infer signups, commission, or revenue.
"""
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "unbounce.html"
html = PAGE.read_text(encoding="utf-8")
original = html

replacements = [
    (
        "<title>Unbounce Review & Pricing 2026: 14-Day Free Trial, $29 Starter + 20%/35% Discount | COSHUMA</title>",
        "<title>Unbounce Pricing 2026: $22/mo Annual, 14-Day Trial + 20%/35% Off | COSHUMA</title>",
    ),
    (
        '<meta name="description" content="Unbounce review and pricing for 2026: Starter $29/mo, 14-day free trial with no credit card, current plan limits, and COSHUMA\'s verified 20%/35% partner discount." />',
        '<meta name="description" content="Unbounce pricing for 2026: Starter $29/mo or $22/mo billed yearly. Compare Build, Experiment and Optimize, the 14-day no-card trial, and COSHUMA\'s verified 20%/35% customer offer." />',
    ),
    (
        '<meta property="og:title" content="Unbounce Review & Pricing 2026: 14-Day Free Trial + Partner Discount" />',
        '<meta property="og:title" content="Unbounce Pricing 2026: $22/mo Annual + 14-Day Trial + Partner Discount" />',
    ),
    (
        '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce Review, Pricing & Verified Partner Discount</h1>',
        '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce Pricing 2026: Monthly vs Annual + Partner Discount</h1>',
    ),
    (
        '<div class="text-2xl font-black text-emerald-400 mt-1">$29/mo</div><div class="text-xs text-slate-500 mt-2">5 pages · up to 500 traffic · 1 user</div>',
        '<div class="text-2xl font-black text-emerald-400 mt-1">$29/mo</div><div class="text-xs text-emerald-300 mt-1">$22/mo billed yearly</div><div class="text-xs text-slate-500 mt-2">5 pages · up to 500 traffic · 1 user</div>',
    ),
    (
        '<div class="text-2xl font-black text-emerald-400 mt-1">$99/mo</div><div class="text-xs text-slate-500 mt-2">Unlimited pages · up to 20k traffic</div>',
        '<div class="text-2xl font-black text-emerald-400 mt-1">$99/mo</div><div class="text-xs text-emerald-300 mt-1">$74/mo billed yearly</div><div class="text-xs text-slate-500 mt-2">Unlimited pages · up to 20k traffic</div>',
    ),
    (
        '<div class="text-2xl font-black text-emerald-400 mt-1">$149/mo</div><div class="text-xs text-slate-500 mt-2">Unlimited A/B testing · up to 30k traffic · 3 users</div>',
        '<div class="text-2xl font-black text-emerald-400 mt-1">$149/mo</div><div class="text-xs text-emerald-300 mt-1">$112/mo billed yearly</div><div class="text-xs text-slate-500 mt-2">Unlimited A/B testing · up to 30k traffic · 3 users</div>',
    ),
    (
        '<div class="text-2xl font-black text-emerald-400 mt-1">$249/mo</div><div class="text-xs text-slate-500 mt-2">Adds deeper AI optimization and Smart Traffic workflows</div>',
        '<div class="text-2xl font-black text-emerald-400 mt-1">$249/mo</div><div class="text-xs text-emerald-300 mt-1">$187/mo billed yearly</div><div class="text-xs text-slate-500 mt-2">Adds deeper AI optimization and Smart Traffic workflows</div>',
    ),
]

changed = 0
for before, after in replacements:
    if before in html:
        html = html.replace(before, after, 1)
        changed += 1

if html != original:
    PAGE.write_text(html, encoding="utf-8")

print(f"apply_unbounce_search_revenue_patch: replacements={changed}")
