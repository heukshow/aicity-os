"""Remove legacy buyer-visible Moosend affiliate operations copy before CTR patches.

This does not change the issued referral URL or product claims. It only removes
legacy routing/verification/listing-management language that should not be shown
to customers on the public buyer guide.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "tool" / "moosend.html"
TRACKING_URL = "https://trymoo.moosend.com/6eappdpw04pw"

text = PAGE.read_text(encoding="utf-8")
original = text

replacements = [
    (
        "<title>Moosend Pricing 2026: 30-Day Trial, Plans & Review | COSHUMA</title>",
        "<title>Moosend Review 2026: 30-Day Free Trial, Pricing & Plans | COSHUMA</title>",
    ),
    (
        '<meta name="description" content="Moosend pricing and review for 2026: 30-day no-card trial, Pro, Moosend+ and Enterprise plans, email credits, automation features, and a current offer link." />',
        '<meta name="description" content="Moosend review for 2026: test the 30-day no-card trial, compare Pro, Moosend+ and Enterprise, subscriber-based pricing, automation, landing pages and email credits before paying." />',
    ),
    (
        '<meta property="og:title" content="Moosend Pricing 2026: 30-Day Trial, Plans & Review | COSHUMA" />',
        '<meta property="og:title" content="Moosend Review 2026: 30-Day Free Trial, Pricing & Plans | COSHUMA" />',
    ),
    (
        '<h1 class="text-4xl md:text-5xl font-black tracking-tight mt-3">Moosend pricing & review: test the full workflow before paying</h1>',
        '<h1 class="text-4xl md:text-5xl font-black tracking-tight mt-3">Moosend review 2026: pricing, 30-day trial & who it fits</h1>',
    ),
    (
        "Start Moosend via verified COSHUMA link →",
        "Start the 30-day Moosend trial →",
    ),
    (
        "Exact referral URL verified from Moosend's affiliate welcome email to COSHUMA. Official pricing remains a separate non-affiliate verification destination.",
        "Pricing and trial terms can change; check Moosend's live pricing before purchasing.",
    ),
    (
        "Source check: Moosend official pricing page and current product documentation, verified September 7, 2026. Affiliate URL verification is based on Moosend's direct affiliate welcome email to COSHUMA. Product pricing and terms can change; verify the live vendor checkout before purchasing.",
        "Source check: Moosend official pricing page and current product documentation. Product pricing and terms can change; verify the live vendor checkout before purchasing.",
    ),
    (
        "&copy; 2026 COSHUMA. Global AI & SaaS decision platform.",
        "&copy; 2026 COSHUMA. Independent AI & SaaS buyer guides.",
    ),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)

text, removed = re.subn(
    r'\n\s*<section class="rounded-3xl bg-\[#181a29\]/80 border border-purple-500/30 p-6 space-y-4">(?:(?!</section>).)*?<a href="/#submit"(?:(?!</section>).)*?</section>\n',
    "\n",
    text,
    count=1,
    flags=re.S,
)

if text.count(TRACKING_URL) < 3:
    raise SystemExit("Moosend cleanup failed: verified customer referral CTAs were lost")
if 'rel="sponsored noopener noreferrer"' not in text:
    raise SystemExit("Moosend cleanup failed: sponsored attribution was lost")
if 'data-cta="affiliate"' in text and 'Affiliate disclosure:' not in text and 'data-affiliate-disclosure=' not in text:
    first_cta = text.find('data-cta="affiliate"')
    anchor_start = text.rfind("<a ", 0, first_cta)
    if anchor_start < 0:
        raise SystemExit("Moosend cleanup failed: could not locate first affiliate CTA for disclosure")
    disclosure = '<p data-affiliate-disclosure="page" style="margin:.75rem 0;color:#94a3b8;font-size:12px;line-height:1.6">Affiliate disclosure: COSHUMA may earn a commission from some links on this page, at no extra cost to you.</p> '
    text = text[:anchor_start] + disclosure + text[anchor_start:]

for forbidden in (
    "exact referral url verified",
    "affiliate welcome email to coshuma",
    'href="/#submit"',
):
    if forbidden in text.lower():
        raise SystemExit(f"Moosend cleanup failed: legacy public operations copy remains: {forbidden}")

if text != original:
    PAGE.write_text(text, encoding="utf-8")
    print(f"Moosend customer copy cleaned; legacy listing block removed={bool(removed)}")
else:
    print("Moosend customer copy already clean")