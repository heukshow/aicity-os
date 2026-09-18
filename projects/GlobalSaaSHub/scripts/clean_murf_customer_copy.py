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
}
for old, new in replacements.items():
    html = html.replace(old, new)

# Earlier shared sanitizers may rewrite the section heading before this guard runs.
# Anchor the replacement on the network/evidence sentence itself so the cleanup
# remains stable regardless of those harmless heading changes.
partner_section = re.compile(
    r'<section\b[^>]*>(?:(?!</section>).)*Murf\'s\s+PartnerStack\s+welcome\s+email(?:(?!</section>).)*</section>',
    re.I | re.S,
)
replacement_section = '''<section class="p-7 rounded-3xl bg-[#131520] border border-purple-500/25 space-y-5">
        <div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Buyer note</div>
        <h2 class="text-2xl font-black text-white">Use the free plan to test voice fit before paying for production features</h2>
        <p class="text-sm text-slate-300 leading-relaxed">Start with Murf's free access to check pronunciation, pacing and voice quality. If the result fits your workflow, compare the paid Studio plans for downloads, commercial use and higher production limits before upgrading.</p>
        <p class="text-xs text-slate-400">Murf also has separate dubbing and API pricing surfaces, so confirm the exact product and billing cadence you need before checkout.</p>
      </section>'''
html, section_count = partner_section.subn(replacement_section, html, count=1)

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
if section_count not in (0, 1):
    raise SystemExit("Unexpected Murf partner-section replacement count")

PAGE.write_text(html, encoding="utf-8")
print("Murf customer copy normalized; exact tracking and sponsored attribution preserved")
