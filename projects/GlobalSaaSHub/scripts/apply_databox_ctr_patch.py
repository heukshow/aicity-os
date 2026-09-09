"""Keep Databox buyer-intent metadata aligned with live Search Console intent.

Backed by the live Search Console snapshot (46 impressions / 0 clicks) and the
current official Databox pricing page. The patch is scoped to the known Databox
page and remains idempotent across prior COSHUMA copy-normalization passes.
"""
from pathlib import Path
import re

path = Path(__file__).resolve().parents[1] / "public" / "tool" / "databox.html"
text = path.read_text(encoding="utf-8")
original = text

canonical = '<link rel="canonical" href="https://coshuma.com/tool/databox.html" />'
if canonical not in text:
    raise SystemExit("Refusing Databox CTR patch: canonical page identity missing")


def replace_once(pattern: str, replacement: str, label: str) -> None:
    global text
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"Refusing Databox CTR patch: could not uniquely update {label}")
    text = updated

replace_once(
    r"<title>[^<]*</title>",
    "<title>Databox Pricing 2026: Free, Analyst, Team & Agency + 14-Day Trial | COSHUMA</title>",
    "title",
)
replace_once(
    r'<meta name="description" content="[^"]*"\s*/>',
    '<meta name="description" content="Databox pricing in 2026: Free $0, Analyst $71/mo annually, Team Core $199, Team Scale $319, Agency from $79, plus a 14-day no-card trial through COSHUMA\'s verified referral link." />',
    "meta description",
)
replace_once(
    r'<meta property="og:title" content="[^"]*"\s*/>',
    '<meta property="og:title" content="Databox Pricing 2026: Free, Analyst, Team & Agency | COSHUMA" />',
    "Open Graph title",
)
replace_once(
    r'<meta property="og:description" content="[^"]*"\s*/>',
    '<meta property="og:description" content="Compare current Databox Free, Analyst, Team Core, Team Scale and Agency pricing, AI credits and the 14-day no-card trial." />',
    "Open Graph description",
)
replace_once(
    r'<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">.*?</h1>',
    '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Databox Pricing &amp; AI Analytics Guide (2026)</h1>',
    "primary heading",
)
replace_once(
    r'<p class="text-sm text-slate-400 mt-1">Official annual-billing prices (?:re)?checked .*? Monthly billing is higher(?:; annual billing currently saves 20%)?\.</p>',
    '<p class="text-sm text-slate-400 mt-1">Official annual-billing prices rechecked September 9, 2026. Annual billing currently saves 20%.</p>',
    "pricing verification date",
)

if text != original:
    path.write_text(text, encoding="utf-8")
    print("Databox CTR patch applied.")
else:
    print("Databox CTR patch already aligned.")
