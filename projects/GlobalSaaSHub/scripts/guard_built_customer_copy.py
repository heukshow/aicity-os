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
    "verified partner trial links": "current trial links",
    "Affiliate disclosure: COSHUMA may earn a commission if an eligible paid signup is attributed through this verified customer-facing referral URL, at no extra cost to the buyer.": "Affiliate disclosure: COSHUMA may earn a commission from some links on this page, at no extra cost to you.",
    "COSHUMA may earn a commission if an eligible paid signup is attributed through this current offer link, at no extra cost to the buyer.": "COSHUMA may earn a commission from some links on this page, at no extra cost to you.",
    "COSHUMA does not currently publish a Framer affiliate/revenue link on this page. These buttons go to Framer's official site while Creator Program enrollment is being verified.": "These buttons go to Framer's official site. Verify current pricing and terms with Framer before purchasing.",
}

POST_PATTERNS = (
    (re.compile(r"\bCOSHUMA may earn a commission if an eligible paid signup is attributed through this (?:verified customer-facing referral URL|current offer link), at no extra cost to the buyer\.", re.I), "COSHUMA may earn a commission from some links on this page, at no extra cost to you."),
    (re.compile(r"\bverified\s+COSHUMA\s+partner\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+[A-Za-z0-9 ._-]{1,40}\s+partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+(?:Dub|Impact|PartnerStack|Cello)\s+(?:partner[- ]?)?route\b", re.I), "current offer"),
    (re.compile(r"\bvendor-confirmed\s+(?:[0-9]+-day\s+)?partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bCOSHUMA's\s+verified\s+[A-Za-z0-9 ._/%-]{1,50}\s+(?:partner\s+)?(?:route|offer|link)\b", re.I), "the current offer"),
    (re.compile(r"\bCOSHUMA's\s+[A-Za-z0-9 ._-]{1,40}\s+PartnerStack\s+route\b", re.I), "the current offer"),
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
INTERNAL_VERIFICATION_NOTE = re.compile(
    r'<div\b[^>]*>\s*<strong\b[^>]*>\s*Verification note:\s*</strong>[^<]*(?:verified customer-facing affiliate URLs|previously verified customer-facing affiliate URLs)[^<]*</div>',
    re.I | re.S,
)

# COSHUMA policy: the short general affiliate notice appears once on the homepage.
# Individual tool/compare/best/category pages must not repeat it. The dedicated
# affiliate-disclosure.html policy page remains available for readers who want details.
AFFILIATE_DISCLOSURE_DATA = re.compile(
    r'<p\b[^>]*\bdata-affiliate-disclosure\s*=\s*["\'][^"\']*["\'][^>]*>.*?</p>',
    re.I | re.S,
)
AFFILIATE_DISCLOSURE_ATTR = re.compile(
    r'\s+data-affiliate-disclosure\s*=\s*["\'][^"\']*["\']',
    re.I,
)
AFFILIATE_DISCLOSURE_PARAGRAPH = re.compile(
    r'<p\b[^>]*>(?:(?!</p>).)*(?:Affiliate\s+disclosure\s*:|COSHUMA\s+may\s+earn\s+(?:an\s+affiliate\s+)?commission)(?:(?!</p>).)*</p>',
    re.I | re.S,
)
AFFILIATE_DISCLOSURE_DIV = re.compile(
    r'<div\b[^>]*>\s*(?:<strong\b[^>]*>)?\s*Affiliate\s+disclosure\s*:.*?</div>',
    re.I | re.S,
)
HOME_AFFILIATE_DISCLOSURE = (
    '<p data-site-affiliate-disclosure="global" '
    'style="max-width:72rem;margin:0 auto;padding:0 1.5rem 1.5rem;color:#94a3b8;font-size:12px;line-height:1.6">'
    'Affiliate disclosure: COSHUMA may earn a commission from some links, at no extra cost to you. '
    '<a href="/affiliate-disclosure.html" style="text-decoration:underline">Details</a>.'
    '</p>'
)



PUBLIC_OPS_MARKER = re.compile(
    r"\b(?:PartnerStack|FirstPromoter)\b|"
    r"\b(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Awin|CJ\s+Affiliate)\b"
    r"(?=[^\n<>]{0,80}\b(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)\b)|"
    r"\b(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)\b"
    r"[^\n<>]{0,80}\b(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Awin|CJ\s+Affiliate)\b|"
    r"\b(?:approved_tracking|tracking_pending|pending_review|affiliate_verified|revenue[_ -]?truth|"
    r"browser[_ -]?queue|customer-facing\s+(?:tracking|referral|partner)\s+(?:URL|route|link)|"
    r"exact\s+(?:customer-facing\s+)?tracking\s+URL|verified\s+customer-facing|partner-side\s+evidence|"
    r"partner\s+correspondence|verification\s+evidence|internal\s+verification|"
    r"affiliate\s+application\s+(?:status|pending|submitted)|partner\s+application\s+(?:status|pending|submitted)|"
    r"tracking\s+status|affiliate\s+status)\b|"
    r"\b(?:affiliate|partner|referral|commission)\s+(?:portal|dashboard)\b|"
    r"\b(?:portal|dashboard)\b[^\n<>]{0,50}\b(?:affiliate|partner|referral|commission)\b",
    re.I,
)
HTTP_URL = re.compile(r"https?://[^\s\"'<>]+", re.I)
PUBLIC_TEXT_BLOCK = re.compile(r"<(?P<tag>p|li)\b(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)>", re.I | re.S)
PUBLIC_META = re.compile(r"<meta\b(?P<attrs>[^>]*\bcontent\s*=\s*[\"'])(?P<content>.*?)(?P<quote>[\"'])(?P<tail>[^>]*)>", re.I | re.S)
PUBLIC_JSONLD = re.compile(
    r'(?P<open><script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(?P<body>.*?)(?P<close></script>)',
    re.I | re.S,
)


def _plain(fragment: str) -> str:
    return re.sub(r"<[^>]+>", " ", fragment)


def _mask_urls(text: str) -> str:
    return HTTP_URL.sub("https://PUBLIC-OUTBOUND-URL", text)


def _has_public_ops(text: str) -> bool:
    return bool(PUBLIC_OPS_MARKER.search(_mask_urls(text)))


def _sanitize_text_value(value: str) -> str:
    if not _has_public_ops(value):
        return value
    pieces = re.split(r"(?<=[.!?])\s+", value)
    kept = [piece for piece in pieces if piece.strip() and not _has_public_ops(piece)]
    cleaned = " ".join(kept).strip()
    return cleaned or "Compare current pricing, trial terms, features and product fit before choosing."


def _strip_internal_blocks(text: str) -> str:
    def block_repl(match: re.Match) -> str:
        visible = _plain(match.group("body"))
        return "" if _has_public_ops(visible) else match.group(0)

    text = PUBLIC_TEXT_BLOCK.sub(block_repl, text)

    def meta_repl(match: re.Match) -> str:
        content = match.group("content")
        cleaned = _sanitize_text_value(content)
        return f'<meta{match.group("attrs")}{cleaned}{match.group("quote")}{match.group("tail")}>'

    text = PUBLIC_META.sub(meta_repl, text)

    def clean_json(value):
        if isinstance(value, dict):
            return {k: clean_json(v) for k, v in value.items()}
        if isinstance(value, list):
            return [clean_json(v) for v in value]
        if isinstance(value, str):
            if value.startswith(("http://", "https://")):
                return value
            return _sanitize_text_value(value)
        return value

    def jsonld_repl(match: re.Match) -> str:
        body = match.group("body")
        try:
            parsed = __import__("json").loads(body)
        except Exception:
            return match.group(0)
        cleaned = __import__("json").dumps(clean_json(parsed), ensure_ascii=False, separators=(",", ":"))
        return match.group("open") + cleaned + match.group("close")

    return PUBLIC_JSONLD.sub(jsonld_repl, text)


def final_polish(text: str) -> str:
    for old, new in POST_EXACT.items():
        text = text.replace(old, new)
    for pattern, replacement in POST_PATTERNS:
        text = pattern.sub(replacement, text)
    text = UNBOUNCE_TRACKING_CARD.sub("", text)
    text = AFFILIATE_STATUS_SECTION.sub("", text)
    text = INTERNAL_HTML_COMMENT.sub("", text)
    text = INTERNAL_VERIFICATION_NOTE.sub("", text)
    text = _strip_internal_blocks(text)
    return text


def strip_general_affiliate_disclosures(text: str) -> str:
    text = AFFILIATE_DISCLOSURE_DATA.sub("", text)
    text = AFFILIATE_DISCLOSURE_PARAGRAPH.sub("", text)
    text = AFFILIATE_DISCLOSURE_DIV.sub("", text)
    # Some older buyer sections used this attribute on the entire offer card rather
    # than on a disclosure paragraph. Keep the useful buyer content, drop only the
    # obsolete disclosure marker.
    text = AFFILIATE_DISCLOSURE_ATTR.sub("", text)
    return text


def enforce_disclosure_policy(rel: str, text: str) -> str:
    # Keep the dedicated legal/details page intact; it is not a repeated page notice.
    if rel == "affiliate-disclosure.html":
        return text

    text = strip_general_affiliate_disclosures(text)
    # Remove a previous post-build homepage notice if this function is ever run twice.
    text = re.sub(
        r'<p\b[^>]*\bdata-site-affiliate-disclosure=["\']global["\'][^>]*>.*?</p>',
        '',
        text,
        flags=re.I | re.S,
    )

    if rel == "index.html":
        if "</body>" not in text:
            raise RuntimeError("Homepage closing body tag missing; refusing to place global affiliate disclosure")
        text = text.replace("</body>", HOME_AFFILIATE_DISCLOSURE + "\n</body>", 1)
        if text.count('data-site-affiliate-disclosure="global"') != 1:
            raise RuntimeError("Homepage must contain exactly one global affiliate disclosure")
        if text.lower().count("affiliate disclosure:") != 1:
            raise RuntimeError("Homepage must contain exactly one visible affiliate disclosure notice")
        return text

    if 'data-affiliate-disclosure=' in text.lower():
        raise RuntimeError(f"Repeated affiliate disclosure attribute remains in {rel}")
    if re.search(r"Affiliate\s+disclosure\s*:", text, re.I):
        raise RuntimeError(f"Repeated affiliate disclosure notice remains in {rel}")
    if re.search(r"COSHUMA\s+may\s+earn\s+(?:an\s+affiliate\s+)?commission", text, re.I):
        raise RuntimeError(f"Repeated affiliate commission notice remains in {rel}")
    return text


def main() -> None:
    if not DIST.exists():
        raise RuntimeError("dist/ does not exist; run vite build first")

    changed = []
    for path in DIST.rglob("*.html"):
        before = path.read_text(encoding="utf-8")
        rel = path.relative_to(DIST).as_posix()
        after = enforce_disclosure_policy(rel, final_polish(clean_html(before)))
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(rel)

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

    print(f"Built customer-only copy guard: {len(changed)} files normalized; homepage disclosure=1; repeated page disclosures=0")


if __name__ == "__main__":
    main()
