"""Sanitize built Vite output after config-time generators have finished."""
from pathlib import Path
import re
from guard_customer_only_copy import clean_html, clean_public_js, clean_llms
from sanitize_public_editorial_copy import clean_llms as clean_editorial_llms

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
    "Verified SaaS Free Trials & Partner Offers": "SaaS Free Trials & Current Offers",
    "Verified SaaS Free Trials &amp; Partner Offers": "SaaS Free Trials &amp; Current Offers",
    "Compare verified SaaS free trials and partner offers across AI, CRM, email, forms, video and sales tools, with pricing context and disclosed referral links.": "Compare SaaS free trials and current offers across AI, CRM, email, forms, video and sales tools, with pricing and plan-fit context.",
    "Compare low-risk SaaS trials and verified COSHUMA partner routes across AI, CRM, email, forms, video and sales tools before you subscribe.": "Compare low-risk SaaS trials and current offers across AI, CRM, email, forms, video and sales tools before you subscribe.",
    "Current Pictory partner offer": "Current Pictory offer",
    "Find the right verified route": "Find the right offer",
    "Search only narrows the verified offers already on this page. Affiliate destinations, vendor terms and revenue evidence are not changed. Filters can be shared with the page URL.": "Search filters the offers and trial options shown on this page. Final pricing and eligibility should be confirmed on the vendor site. Filters can be shared with the page URL.",
    "Search verified software offers": "Search software offers",
    "No verified offer on this page matches that search. Reset the filter to see every route.": "No offer on this page matches that search. Reset the filter to see all options.",
    "verified offers match": "offers match",
    "verified offers available": "offers available",
    "Software free trials and partner offers worth testing before you pay": "Software free trials and current offers worth testing before you pay",
    "current ProProfs affiliate status.": "current ProProfs affiliate program availability.",
    "Editorial information is kept separate from affiliate status.": "",
    "Verified referral route": "Current offer",
    "Verified Referral Route": "Current offer",
    "Verified Referral Link": "current offer",
    "verified referral link": "current offer",
    "Affiliate disclosure: COSHUMA may earn a commission if an eligible paid signup is attributed through this verified customer-facing referral URL, at no extra cost to the buyer.": "Affiliate disclosure: COSHUMA may earn a commission from some links on this page, at no extra cost to you.",
    "COSHUMA does not currently publish a Framer affiliate/revenue link on this page. These buttons go to Framer's official site while Creator Program enrollment is being verified.": "These buttons go to Framer's official site. Verify current pricing and terms with Framer before purchasing.",
}

POST_PATTERNS = (
    (re.compile(r"\bverified\s+COSHUMA\s+partner\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+[A-Za-z0-9 ._-]{1,40}\s+partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+(?:Dub|Impact|PartnerStack|Cello)\s+(?:partner[- ]?)?route\b", re.I), "current offer"),
    (re.compile(r"\bvendor-confirmed\s+(?:[0-9]+-day\s+)?partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bCOSHUMA's\s+verified\s+[A-Za-z0-9 ._/%-]{1,50}\s+(?:partner\s+)?(?:route|offer|link)\b", re.I), "the current offer"),
    (re.compile(r"\bverified\s+(?:customer-facing\s+)?referral\s+(?:route|link)\b", re.I), "current offer"),
    (re.compile(r"\b(?:exact\s+)?verified\s+customer-facing\s+(?:tracking|referral)\s+URL\s*:\s*[^<\n]+", re.I), ""),
    (re.compile(r"\bverified\s+customer-facing\s+(?:tracking|referral)\s+URL\b", re.I), "current offer link"),
    (re.compile(r"\bCOSHUMA[^.<\n]{0,100}(?:affiliate|referral|partner|revenue)[^.<\n]{0,100}(?:being verified|verification pending|pending verification|enrollment is being verified)\.?", re.I), "Verify current terms on the vendor site before purchasing."),
    (re.compile(r"\s+and\s+(?<!data-)(?:affiliate|partner|referral)-status\s+buyer guide\b", re.I), " buyer guide"),
    (re.compile(r"\s+(?:and|with)\s+(?:current\s+)?(?<!data-)(?:affiliate|partner|referral)-status\s+facts\b", re.I), ""),
    (re.compile(r"\bverified\s+(?<!data-)affiliate-status\s+disclosure\b", re.I), "current product details"),
    (re.compile(r"(?<!data-)\b(?:affiliate|partner|referral)-status\s+buyer guide\b", re.I), "buyer guide"),
    (re.compile(r"(?<!data-)\b(?:affiliate|partner|referral)-status\s+facts\b", re.I), "product details"),
    (re.compile(r"(?<!data-)\b(?:affiliate|partner|referral)-status\b", re.I), "program details"),
    (re.compile(r"\bOfficial\s+pricing\s+and\s+affiliate\s+pages\s+checked\b", re.I), "Official pricing sources checked"),
)

UNBOUNCE_TRACKING_CARD = re.compile(
    r'<div class="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-4">\s*'
    r'<div[^>]*>Tracking</div>\s*<div[^>]*>90-day cookie</div>\s*</div>',
    re.I | re.S,
)
AFFILIATE_STATUS_SECTION = re.compile(
    r'<section\b[^>]*>\s*<h2\b[^>]*>\s*(?:Current\s+)?Affiliate status\s*</h2>.*?</section>',
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
    text = AFFILIATE_STATUS_SECTION.sub("", text)
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
        after = clean_editorial_llms(clean_llms(before))
        if after != before:
            llms.write_text(after, encoding="utf-8")
            changed.append(llms.relative_to(DIST).as_posix())

    print(f"Built customer-only copy guard: {len(changed)} files normalized")


if __name__ == "__main__":
    main()
