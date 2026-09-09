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
    "<title>Databox Pricing 2026: Free, Analyst, Pro & Growth + 14-Day Trial | COSHUMA</title>",
    "title",
)
replace_once(
    r'<meta name="description" content="[^"]*"\s*/>',
    '<meta name="description" content="Databox pricing in 2026: compare Free ($0), Analyst ($64), Pro ($159) and Growth ($399) annual-billing plans, plus the 14-day no-card Growth trial and verified COSHUMA referral link." />',
    "meta description",
)
replace_once(
    r'<meta property="og:title" content="[^"]*"\s*/>',
    '<meta property="og:title" content="Databox Pricing 2026: Plans + 14-Day Trial | COSHUMA" />',
    "Open Graph title",
)
replace_once(
    r'<meta property="og:description" content="[^"]*"\s*/>',
    '<meta property="og:description" content="Compare Databox Free, Analyst, Pro and Growth pricing, AI credits, data-source limits and the current 14-day no-card Growth trial." />',
    "Open Graph description",
)
replace_once(
    r'<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">.*?</h1>',
    '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Databox Pricing &amp; AI Analytics Guide (2026)</h1>',
    "primary heading",
)
replace_once(
    r'<p class="text-sm text-slate-400 mt-1">Official annual-billing prices (?:re)?checked .*? Monthly billing is higher(?:; annual billing currently saves 20%)?\.</p>',
    '<p class="text-sm text-slate-400 mt-1">Official annual-billing prices rechecked September 9, 2026. Monthly billing is higher; annual billing currently saves 20%.</p>',
    "pricing verification date",
)

if text != original:
    path.write_text(text, encoding="utf-8")
    print("Databox CTR patch applied.")
else:
    print("Databox CTR patch already aligned.")
