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
        text = text.replace(old, new, 1)

# Remove the old paid listing-management/profile-claim block. The preceding
# copy-normalization pass may rename labels inside it, so match the stable wrapper
# and /#submit action rather than fragile wording.
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
if 'Affiliate disclosure:' not in text:
    raise SystemExit("Moosend cleanup failed: affiliate disclosure was lost")

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