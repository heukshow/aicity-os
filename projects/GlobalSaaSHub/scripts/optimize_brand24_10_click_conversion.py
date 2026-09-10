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

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "brand24.html"
TRACKING_URL = "https://try.brand24.com/8xqrjxybmsbt"
MARKER = 'data-brand24-conversion-v2="2026-09-11"'

text = PAGE.read_text(encoding="utf-8")
if TRACKING_URL not in text:
    raise SystemExit("Refusing Brand24 conversion patch: verified tracking URL missing")

old_hero = ">Start Brand24 Free — No Card →</a>"
new_hero = ">Start 14-Day Pro-Level Trial — No Card →</a>"
if old_hero in text:
    text = text.replace(old_hero, new_hero, 1)
elif new_hero not in text:
    raise SystemExit("Refusing Brand24 conversion patch: hero CTA anchor changed unexpectedly")

if MARKER not in text:
    disclosure = '<p class="text-[11px] text-slate-500 leading-relaxed">Affiliate disclosure: COSHUMA may earn a commission if an eligible purchase is attributed through the verified Brand24 partner link, at no extra cost to you.</p>'
    benefit = '<p data-brand24-conversion-v2="2026-09-11" class="text-xs text-emerald-200 leading-relaxed"><strong class="text-white">Trial value:</strong> Brand24 currently says the 14-day trial is based on Pro, supports up to 10 keywords and 30,000 mentions, and requires no credit card. Use the trial to test real monitoring volume before paying.</p>'
    if disclosure not in text:
        raise SystemExit("Refusing Brand24 conversion patch: affiliate disclosure anchor missing")
    text = text.replace(disclosure, benefit + "\n            " + disclosure, 1)

old_trial = ">Run the 14-day Brand24 test via COSHUMA →</a>"
new_trial = ">Start the 14-Day Pro-Level Brand24 Trial →</a>"
if old_trial in text:
    text = text.replace(old_trial, new_trial, 1)
elif new_trial not in text:
    raise SystemExit("Refusing Brand24 conversion patch: trial CTA anchor changed unexpectedly")

# Revenue safety: never invent a pricing/signup deep link. Keep the exact issued URL.
if text.count(TRACKING_URL) < 2:
    raise SystemExit("Brand24 conversion patch failed: verified tracking coverage unexpectedly low")
if 'data-brand24-conversion-v2="2026-09-11"' not in text:
    raise SystemExit("Brand24 conversion patch failed: benefit marker missing")

PAGE.write_text(text, encoding="utf-8")
print("Brand24 10-click conversion patch applied; verified tracking URL preserved.")
