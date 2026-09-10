"""Improve Brand24 click-to-trial conversion after the first verified 10-click milestone.

Vendor/PartnerStack email on 2026-09-11 KST confirmed the COSHUMA referral link
reached its first 10 clicks. It did not report signups, paid customers, commission,
or revenue, so this patch makes no conversion claim.

Brand24's current first-party Help Center says the 14-day trial is based on Pro,
supports up to 10 keywords and 30,000 mentions, and its pricing FAQ says no credit
card is required. This patch moves those concrete trial benefits next to the hero CTA
while preserving the exact already-verified PartnerStack customer URL.
"""
from pathlib import Path
import re

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "brand24.html"
TRACKING_URL = "https://try.brand24.com/8xqrjxybmsbt"
MARKER = 'data-brand24-conversion-v2="2026-09-11"'
BENEFIT = '<p data-brand24-conversion-v2="2026-09-11" class="text-xs text-emerald-200 leading-relaxed"><strong class="text-white">Trial value:</strong> Brand24 currently says the 14-day trial is based on Pro, supports up to 10 keywords and 30,000 mentions, and requires no credit card. Use the trial to test real monitoring volume before paying.</p>'

text = PAGE.read_text(encoding="utf-8")
if TRACKING_URL not in text:
    raise SystemExit("Refusing Brand24 conversion patch: verified tracking URL missing")

# Target CTAs by their stable attribution source instead of brittle full-text anchors.
hero_pattern = re.compile(r'(<a\b[^>]*data-tool-id="brand24"[^>]*data-cta-source="brand24-hero"[^>]*>)(.*?)(</a>)', re.S)
trial_pattern = re.compile(r'(<a\b[^>]*data-tool-id="brand24"[^>]*data-cta-source="brand24-trial-proof"[^>]*>)(.*?)(</a>)', re.S)

hero_match = hero_pattern.search(text)
if hero_match:
    text = hero_pattern.sub(r'\1Start 14-Day Pro-Level Trial — No Card →\3', text, count=1)

trial_match = trial_pattern.search(text)
if trial_match:
    text = trial_pattern.sub(r'\1Start the 14-Day Pro-Level Brand24 Trial →\3', text, count=1)

# Put the concrete trial value immediately beside the primary revenue CTA. If an
# upstream copy pass changes surrounding prose, the stable CTA source still anchors it.
if MARKER not in text:
    hero_match = hero_pattern.search(text)
    if hero_match:
        text = text[:hero_match.end()] + "\n              " + BENEFIT + text[hero_match.end():]

# Revenue safety: never invent a pricing/signup deep link. Keep the exact issued URL.
if TRACKING_URL not in text:
    raise SystemExit("Brand24 conversion patch failed: verified tracking URL was lost")

PAGE.write_text(text, encoding="utf-8")
if MARKER in text:
    print("Brand24 10-click conversion patch applied; trial value surfaced and verified tracking preserved.")
else:
    print("Brand24 verified tracking preserved; stable hero anchor was not present, so no speculative copy insertion was made.")
