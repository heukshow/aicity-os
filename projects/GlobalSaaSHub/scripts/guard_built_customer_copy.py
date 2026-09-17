"""Sanitize built Vite output after config-time generators have finished."""
from pathlib import Path
import re
from guard_customer_only_copy import clean_html, clean_public_js, clean_llms

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

POST_EXACT = {
    "including pricing, discounts, trials, comparisons and current offer.": "including pricing, discounts, trials, comparisons and current offers.",
    "pricing, free plans, trials, buyer fit and current offer before choosing a product.": "pricing, free plans, trials, buyer fit and current offers before choosing a product.",
    "COSHUMA separates editorial comparisons from partner links and labels monetized CTAs inside each guide.": "COSHUMA focuses on pricing, trials, discounts and practical product fit so you can compare options more quickly.",
    "Compare current free limits, paid entry prices and usage models, then start Make through COSHUMA's current offer only if it fits your workflow.": "Compare current free limits, paid entry prices and usage models, then check the current Make offer only if it fits your workflow.",
    "Checkout-focused guide for the verified COSHUMA partner offer and current Pictory plans.": "Checkout-focused guide for the current Pictory offer and current plans.",
    "COSHUMA focuses on pricing, free access, buyer fit and current offer without treating clicks as revenue.": "COSHUMA focuses on pricing, free access, buyer fit and practical product differences.",
    "Entry pricing, 14-day trials, traffic limits, A/B testing and agency fit—plus COSHUMA's verified Unbounce partner offer.": "Entry pricing, 14-day trials, traffic limits, A/B testing, agency fit and the current Unbounce discount.",
    "A current offer is kept separate from editorial product fit, and publication or test clicks are not treated as signups, customers or revenue.": "Use the comparison to narrow your shortlist, then confirm current pricing and terms on the vendor's site before purchasing.",
    "Unbounce Pricing 2026: Monthly vs Annual + Partner Discount": "Unbounce Pricing 2026: Monthly vs Annual + Discount",
    "Unbounce Pricing 2026: $22/mo Annual + 14-Day Trial + Partner Discount": "Unbounce Pricing 2026: $22/mo Annual + 14-Day Trial + Discount",
    "COSHUMA's verified 20%/35% customer offer": "the current 20%/35% offer",
    ">Partner offer<": ">Current discount<",
}

POST_PATTERNS = (
    (re.compile(r"\bverified\s+COSHUMA\s+partner\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+[A-Za-z0-9 ._-]{1,40}\s+partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bvendor-confirmed\s+(?:[0-9]+-day\s+)?partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bCOSHUMA's\s+verified\s+[A-Za-z0-9 ._/%-]{1,50}\s+(?:partner\s+)?(?:route|offer|link)\b", re.I), "the current offer"),
)

UNBOUNCE_TRACKING_CARD = re.compile(
    r'<div class="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-4">\s*'
    r'<div[^>]*>Tracking</div>\s*<div[^>]*>90-day cookie</div>\s*</div>',
    re.I | re.S,
)
INTERNAL_HTML_COMMENT = re.compile(
    r'<!--(?:(?!-->).)*(?:COSHUMA_[A-Z0-9_]+|affiliate|revenue[_ -]?truth|tracking[_ -]?verification|partnerstack)(?:(?!-->).)*-->',
    re.I | re.S,
)


def final_polish(text: str) -> str:
    for old, new in POST_EXACT.items():
        text = text.replace(old, new)
    for pattern, replacement in POST_PATTERNS:
        text = pattern.sub(replacement, text)
    text = UNBOUNCE_TRACKING_CARD.sub("", text)
    text = INTERNAL_HTML_COMMENT.sub("", text)
    return text


def main() -> None:
    if not DIST.exists():
        raise RuntimeError("dist/ does not exist; run vite build first")

    changed = []
    for path in DIST.rglob("*.html"):
        before = path.read_text(encoding="utf-8")
        after = final_polish(clean_html(before))
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(path.relative_to(DIST).as_posix())

    js = DIST / "affiliate-attribution.js"
    if js.exists():
        before = js.read_text(encoding="utf-8")
        after = clean_public_js(before)
        if after != before:
            js.write_text(after, encoding="utf-8")
            changed.append(js.relative_to(DIST).as_posix())

    llms = DIST / "llms.txt"
    if llms.exists():
        before = llms.read_text(encoding="utf-8")
        after = clean_llms(before)
        if after != before:
            llms.write_text(after, encoding="utf-8")
            changed.append(llms.relative_to(DIST).as_posix())

    print(f"Built customer-only copy guard: {len(changed)} files normalized")


if __name__ == "__main__":
    main()
