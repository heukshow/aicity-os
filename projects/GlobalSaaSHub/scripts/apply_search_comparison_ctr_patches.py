"""Apply conservative Search Console CTR patches to generated comparison pages.

Runs after build_search_comparisons.mjs so source-backed generators cannot erase
verified buyer-intent metadata changes. Exact-match only: if the generated source
changes unexpectedly, fail instead of guessing.
"""
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
COMPARE_DIR = PROJECT_DIR / "public" / "compare"

PATCHES = {
    "semrush-vs-frase.html": [
        (
            "<title>Semrush vs Frase: SEO Research or Content Workflow? | COSHUMA</title>",
            "<title>Frase vs Semrush 2026: Pricing, SEO Research, Content Optimization & Best Fit | COSHUMA</title>",
        ),
        (
            '<meta name="description" content="Compare Semrush and Frase for keyword research, content production, AI visibility and pricing. Choose by the work you need to complete, with official sources.">',
            '<meta name="description" content="Frase vs Semrush in 2026: compare current pricing, SEO research, content optimization, AI visibility and free-trial options. Frase starts at $49/mo with a 7-day no-card trial; Semrush SEO starts at $139/mo.">',
        ),
        (
            '<meta property="og:title" content="Semrush vs Frase: SEO Research or Content Workflow? | COSHUMA">',
            '<meta property="og:title" content="Frase vs Semrush 2026: Pricing, SEO Research & Content Workflow | COSHUMA">',
        ),
        (
            '<meta property="og:description" content="Compare Semrush and Frase for keyword research, content production, AI visibility and pricing. Choose by the work you need to complete, with official sources.">',
            '<meta property="og:description" content="Compare Frase and Semrush by price, SEO research depth, content workflow, AI visibility and trial options before paying.">',
        ),
        (
            '<p class="muted">Buyer comparison · Official sources checked September 8, 2026</p><h1>Semrush vs Frase: SEO Research or Content Workflow?</h1>',
            '<p class="muted">Buyer comparison · Official sources checked September 9, 2026</p><h1>Frase vs Semrush 2026: Content Workflow or SEO Research?</h1>',
        ),
        (
            '<td>Compare the exact SEO, content and AI toolkit combination, website limits and extra users on the official pricing page.</td><td>Starter lists $49 monthly or $39/month billed yearly, for one seat and one site. Article and audit allowances apply.</td>',
            '<td>SEO starts at $139/month month-to-month or $117.33/month billed annually. Higher SEO + AI Search tiers cost more.</td><td>Starter lists $49/month or $39/month billed yearly, and the current pricing page offers a 7-day free trial with no credit card.</td>',
        ),
        (
            '>Explore Frase →</a>',
            '>Start Frase 7-day free trial →</a>',
        ),
        (
            'href="https://www.semrush.com/" target="_blank" rel="noopener noreferrer">Explore Semrush →</a>',
            'href="https://www.semrush.com/pricing/seo-ai-search/" target="_blank" rel="noopener noreferrer">Check Semrush SEO pricing →</a>',
        ),
    ],
}

changed = 0
for filename, replacements in PATCHES.items():
    path = COMPARE_DIR / filename
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        if new in text:
            continue
        if old not in text:
            raise SystemExit(f"Refusing uncertain comparison CTR patch: {filename}: {old[:90]}")
        text = text.replace(old, new, 1)
    if text != original:
        path.write_text(text, encoding="utf-8")
        changed += 1

print(f"Search comparison CTR patches applied to {changed} page(s).")
