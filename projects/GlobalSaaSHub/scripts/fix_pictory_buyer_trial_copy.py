from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "tool" / "pictory.html"

STALE = (
    "Free-plan and trial availability are not confirmed here. "
    "Check the current vendor pricing page for eligibility, limits and billing terms before checkout."
)
VERIFIED = (
    "COSHUMA has not verified a permanent free plan. "
    "Pictory's official pricing page currently advertises a 14-day free trial; "
    "verify current eligibility, limits and billing terms before starting."
)
AFFILIATE_URL = "https://pictory.ai?fpr=sangkwon-an23"

html = PAGE.read_text(encoding="utf-8")

if 'data-buyer-decision-box="pictory"' not in html:
    raise SystemExit("Pictory buyer decision box is missing; refusing to patch an unknown build shape.")
if AFFILIATE_URL not in html:
    raise SystemExit("Verified Pictory affiliate URL is missing; refusing to alter monetization state.")
if "COSHUMA20" not in html:
    raise SystemExit("Verified Pictory partner code is missing; refusing to alter the buyer page.")

if STALE in html:
    html = html.replace(STALE, VERIFIED, 1)
elif VERIFIED not in html:
    raise SystemExit("Expected Pictory trial copy was not found; refusing a blind replacement.")

PAGE.write_text(html, encoding="utf-8")
print("Pictory buyer box aligned with verified 14-day trial evidence.")
