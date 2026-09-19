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
    "<title>Databox Pricing 2026: Free, Analyst $64, Pro $159, Growth $399 | COSHUMA</title>",
    "title",
)
replace_once(
    r'<meta name="description" content="[^"]*"\s*/>',
    '<meta name="description" content="Databox pricing 2026: Free $0, Analyst $64/mo, Pro $159/mo and Growth $399/mo billed annually. Compare data sources, AI credits, users and the 14-day no-card trial." />',
    "meta description",
)
replace_once(
    r'<meta property="og:title" content="[^"]*"\s*/>',
    '<meta property="og:title" content="Databox Pricing 2026: Free, Analyst $64, Pro $159 & Growth $399 | COSHUMA" />',
    "Open Graph title",
)
replace_once(
    r'<meta property="og:description" content="[^"]*"\s*/>',
    '<meta property="og:description" content="Compare Databox Free, Analyst, Pro and Growth by annual price, users, data sources, AI credits, sync frequency and the 14-day no-card trial." />',
    "Open Graph description",
)
replace_once(
    r'<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">.*?</h1>',
    '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Databox Pricing 2026: Free, Analyst, Pro &amp; Growth</h1>',
    "primary heading",
)
replace_once(
    r'<p class="text-sm text-slate-400 mt-1">Official annual-billing prices .*?</p>',
    '<p class="text-sm text-slate-400 mt-1">Official annual-billing prices rechecked September 19, 2026. Databox currently lists Free $0, Analyst $64, Pro $159 and Growth $399 per month on annual billing.</p>',
    "pricing verification date",
)

# Refresh the visible plan cards to the current first-party pricing structure.
current_replacements = {
    '<div class="text-xs font-bold text-purple-300 uppercase tracking-wider">Analyst</div> <div class="text-2xl font-black text-white mt-1">$71/mo</div> <div class="text-xs text-slate-400 mt-2">Billed annually · 1 user · 5 data sources · 150 AI credits/month · hourly max sync.</div>':
        '<div class="text-xs font-bold text-purple-300 uppercase tracking-wider">Analyst</div> <div class="text-2xl font-black text-white mt-1">$64/mo</div> <div class="text-xs text-slate-400 mt-2">Billed annually · 1 user · 5 data sources · 500 AI credits/month · hourly max sync.</div>',
    '<div class="text-xs font-bold text-purple-300 uppercase tracking-wider">Team Core</div> <div class="text-2xl font-black text-white mt-1">$199/mo</div> <div class="text-xs text-slate-400 mt-2">Billed annually · 3 users · 10 data sources · 500 AI credits/month.</div>':
        '<div class="text-xs font-bold text-purple-300 uppercase tracking-wider">Pro</div> <div class="text-2xl font-black text-white mt-1">$159/mo</div> <div class="text-xs text-slate-400 mt-2">Billed annually · unlimited users · 3 included data sources · 1,500 AI credits/month · hourly max sync.</div>',
    '<div class="text-xs font-bold text-purple-300 uppercase tracking-wider">Team Scale</div> <div class="text-2xl font-black text-white mt-1">$319/mo</div> <div class="text-xs text-slate-400 mt-2">Billed annually · 10 users · 30 data sources · 1,000 AI credits/month · sub-accounts.</div>':
        '<div class="text-xs font-bold text-purple-300 uppercase tracking-wider">Growth</div> <div class="text-2xl font-black text-white mt-1">$399/mo</div> <div class="text-xs text-slate-400 mt-2">Billed annually · unlimited users · 3 included data sources · 4,000 AI credits/month · 15-minute sync on supported sources · sub-accounts.</div>',
    '<div class="font-bold text-emerald-300">Agency: starts at $79 with annual billing</div> <div class="text-xs text-slate-300 mt-2">Agency pricing adds client packs as you grow and currently includes unlimited users, bulk actions, custom templates and cross-client reporting. Custom is sales-assisted for larger requirements.</div>':
        '<div class="font-bold text-emerald-300">Custom: tailored pricing for larger requirements</div> <div class="text-xs text-slate-300 mt-2">Custom includes flexible AI credits, unlimited users, white-labeling, advanced security, account setup and priority support. Agency-specific pricing is available on Databox\'s separate agency plans.</div>',
    'These values are from Databox\'s live pricing page on September 9, 2026. SaaS pricing and limits can change, so verify checkout before purchase.':
        'These values were rechecked on Databox\'s official pricing page on September 19, 2026. Pricing and limits can change, so verify the live plan before purchase.'
}
for old, new in current_replacements.items():
    if old in text:
        text = text.replace(old, new, 1)

if text != original:
    path.write_text(text, encoding="utf-8")
    print("Databox CTR patch applied.")
else:
    print("Databox CTR patch already aligned.")
