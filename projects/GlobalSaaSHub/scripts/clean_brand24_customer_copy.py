from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "public" / "tool" / "brand24.html",
    ROOT / "public" / "best" / "brand24-free-trial.html",
]
TRACKING_URL = "https://try.brand24.com/8xqrjxybmsbt"

REPLACEMENTS = {
    "Brand24 review and pricing for 2026: plans start at $249/mo ($199/mo billed annually), with a 14-day free trial and no credit card. Compare limits, AI Visibility, who it fits, and try it through COSHUMA's verified partner link.":
        "Brand24 review and pricing for 2026: plans start at $249/mo ($199/mo billed annually), with a 14-day free trial and no credit card. Compare limits, AI Visibility, buyer fit, and the lowest-risk way to test it before paying.",
    "Brand24 free trial guide for 2026: 14 days, no credit card, Pro-based trial features, 10 keywords, up to 30K mentions, current pricing and a verified COSHUMA partner link.":
        "Brand24 free trial guide for 2026: 14 days, no credit card, Pro-based trial features, 10 keywords, up to 30K mentions, current pricing and buyer-fit guidance before choosing a paid plan.",
}

for page in PAGES:
    if not page.exists():
        raise SystemExit(f"Missing Brand24 buyer page: {page}")
    html = page.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        html = html.replace(old, new)

    # Customer pages should explain the offer, not COSHUMA's internal validation state.
    html = re.sub(
        r'<span\b[^>]*>\s*Verified partner tracking\s*</span>',
        "",
        html,
        flags=re.I,
    )

    for forbidden in (
        "verified partner tracking",
        "verified COSHUMA partner link",
        "COSHUMA's verified partner link",
    ):
        if forbidden.lower() in html.lower():
            raise SystemExit(f"Brand24 customer page still exposes internal partner-validation copy: {forbidden} ({page.name})")

    if TRACKING_URL not in html:
        raise SystemExit(f"Brand24 exact customer-facing tracking URL was lost: {page.name}")
    if 'data-cta="affiliate" data-tool-id="brand24"' not in html:
        raise SystemExit(f"Brand24 affiliate CTA instrumentation was lost: {page.name}")
    if 'rel="sponsored' not in html:
        raise SystemExit(f"Brand24 sponsored attribution was lost: {page.name}")

    page.write_text(html, encoding="utf-8")

print("Brand24 buyer pages normalized; exact tracking and sponsored attribution preserved")
