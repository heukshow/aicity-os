from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "tool" / "murf-ai.html"
TRACKING_URL = "https://get.murf.ai/fqac0vixj0qs"

if not PAGE.exists():
    raise SystemExit(f"Missing Murf buyer page: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

replacements = {
    "Murf AI pricing guide for 2026: compare the $0 Free plan, Creator from $19/month billed annually, Business from $66/month, 200+ voices, and a verified COSHUMA partner link.":
        "Murf AI pricing guide for 2026: compare the $0 Free plan, Creator from $19/month billed annually, Business from $66/month, 200+ voices, and practical buyer considerations.",
    ">Verified partner link<": ">200+ voices<",
    ">Try Murf AI via Verified Partner Link →<": ">Try Murf AI →<",
    ">Open Murf through COSHUMA →<": ">Open Murf →<",
    "Pictory is a separate verified partner path for turning scripts and content into videos.":
        "Pictory is built for turning scripts and existing content into videos when you need more than voiceover generation.",
    "Affiliate rate, duration, attribution window and discount policy come from Murf's official affiliate program page; COSHUMA's exact referral URL comes from Murf's PartnerStack welcome email.":
        "Plan and product details can change, so confirm the current Murf pricing and product pages before checkout.",
}
for old, new in replacements.items():
    html = html.replace(old, new)

# Shared sanitizers can rewrite apostrophes and nearby text. Replace the whole
# customer-visible evidence paragraph if the internal network phrase survives.
internal_evidence_paragraph = re.compile(
    r'<p\b[^>]*>(?:(?!</p>).)*PartnerStack\s+welcome\s+email(?:(?!</p>).)*</p>',
    re.I | re.S,
)
html = internal_evidence_paragraph.sub(
    '<p class="text-sm text-slate-300 leading-relaxed">Start with Murf\'s free access to check pronunciation, pacing and voice quality. If the result fits your workflow, compare paid Studio plans for downloads, commercial use and higher production limits before upgrading.</p>',
    html,
    count=1,
)
html = re.sub(
    r"COSHUMA['’]s\s+Murf\s+link[^<]*",
    "Use the free plan to test voice fit before paying for production features",
    html,
    count=1,
    flags=re.I,
)
html = re.sub(r">\s*Partner transparency\s*<", ">Buyer note<", html, count=1, flags=re.I)
html = re.sub(
    r'<p\b[^>]*>(?:(?!</p>).)*The commission is paid by Murf;(?:(?!</p>).)*</p>',
    '<p class="text-xs text-slate-400">Murf also has separate dubbing and API pricing surfaces, so confirm the exact product and billing cadence you need before checkout.</p>',
    html,
    count=1,
    flags=re.I | re.S,
)
# Last-resort source-note cleanup: remove any remaining sentence that discloses
# the internal partner-email evidence while leaving official product sourcing.
html = re.sub(
    r"Affiliate rate, duration, attribution window and discount policy[^<]*PartnerStack\s+welcome\s+email\.",
    "Plan and product details can change, so confirm the current Murf pricing and product pages before checkout.",
    html,
    flags=re.I | re.S,
)

for forbidden in (
    "PartnerStack welcome email",
    "approved personal referral route",
    "Partner transparency",
    "verified COSHUMA partner link",
    "Verified partner link",
    "separate verified partner path",
):
    if forbidden.lower() in html.lower():
        raise SystemExit(f"Murf customer page still exposes internal partner copy: {forbidden}")

if TRACKING_URL not in html:
    raise SystemExit("Murf exact customer-facing tracking URL was lost")
if 'data-cta="affiliate" data-tool-id="murf-ai"' not in html:
    raise SystemExit("Murf affiliate CTA instrumentation was lost")
if 'rel="sponsored' not in html:
    raise SystemExit("Murf sponsored attribution was lost")

PAGE.write_text(html, encoding="utf-8")
print("Murf customer copy normalized; exact tracking and sponsored attribution preserved")
