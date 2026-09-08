"""Patch Databox buyer-intent metadata after public copy normalization.

Backed by the live Search Console snapshot (46 impressions / 0 clicks) and the
current official Databox pricing page. Exact-match only; fail rather than guess.
"""
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "public" / "tool" / "databox.html"
text = path.read_text(encoding="utf-8")
original = text

replacements = [
    (
        "<title>Databox Pricing, AI Analytics & Free Trial (2026) | COSHUMA</title>",
        "<title>Databox Review & Pricing 2026: Free Plan, 14-Day Growth Trial & AI Analytics | COSHUMA</title>",
    ),
    (
        '<meta name="description" content="Compare Databox Free, Analyst, Pro and Growth plans, including the 14-day no-card trial, AI Analyst features, and a verified referral link." />',
        '<meta name="description" content="Databox review and pricing for 2026: Free $0, Analyst $64/mo, Pro $159/mo and Growth $399/mo billed annually. Compare AI Analytics and the 14-day Growth trial with no credit card through COSHUMA\'s verified referral link." />',
    ),
    (
        '<meta property="og:title" content="Databox Pricing & AI Analytics Guide (2026) | COSHUMA" />',
        '<meta property="og:title" content="Databox Review & Pricing 2026: Free Plan + 14-Day Growth Trial | COSHUMA" />',
    ),
    (
        '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Databox</h1>',
        '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Databox Review, Pricing & AI Analytics</h1>',
    ),
    (
        '<p class="text-sm text-slate-400 mt-1">Official annual-billing prices checked September 2, 2026. Monthly billing is higher.</p>',
        '<p class="text-sm text-slate-400 mt-1">Official annual-billing prices checked September 9, 2026. Monthly billing is higher.</p>',
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Refusing uncertain Databox CTR patch: {old[:90]}")
    text = text.replace(old, new, 1)

if text != original:
    path.write_text(text, encoding="utf-8")
    print("Databox CTR patch applied.")
else:
    print("Databox CTR patch already applied.")
