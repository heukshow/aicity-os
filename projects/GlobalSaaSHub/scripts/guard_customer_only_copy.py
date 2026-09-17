"""Final customer-only public copy pass.

This script intentionally runs last, after affiliate/revenue generators and before
Vite. It keeps exact outbound URLs intact while removing page-level affiliate disclosures,
internal attribution, KPI and workflow language from buyer-facing copy.
"""
from pathlib import Path
import html as html_lib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

# Buyer facts that must survive, rewritten without internal network/ops details.
EXACT = {
    # Unbounce
    "Unbounce Pricing 2026: $29 Starter + 20%/35% Partner Discount | COSHUMA": "Unbounce Pricing 2026: $29 Starter + 20%/35% Discount | COSHUMA",
    "Unbounce Pricing 2026: $29 Starter + 20%/35% Partner Discount": "Unbounce Pricing 2026: $29 Starter + 20%/35% Discount",
    "Unbounce Pricing 2026: Monthly vs Annual + Partner Discount": "Unbounce Pricing 2026: Monthly vs Annual + Discount",
    "COSHUMA's verified 20%/35% customer offer": "the current 20%/35% offer",
    "COSHUMA's verified customer partner offer": "the current discount offer",
    "COSHUMA's verified Unbounce partner offer": "the current Unbounce discount",
    "COSHUMA's verified Unbounce route": "the current Unbounce offer",
    "Unbounce pricing, trial & verified partner discount": "Unbounce pricing, trial & current discount",
    "Start 14-day trial + partner discount →": "Start 14-day trial + discount →",
    "Start Unbounce trial + verified partner offer →": "Start Unbounce trial + discount →",
    "Check the verified Unbounce offer →": "Check the current Unbounce offer →",
    "Try Unbounce through COSHUMA →": "Try Unbounce →",
    "Why the partner route matters": "Before you start",
    "Use the verified link before starting your trial": "Check the trial and discount before you start",
    "What discount does COSHUMA's Unbounce partner link provide?": "What discount is currently available with this Unbounce offer?",
    "Unbounce's partner welcome email for COSHUMA states that the unique referral link gives eligible customers 20% off their first three months or 35% off their first annual subscription. Final eligibility and checkout pricing are controlled by Unbounce.": "The current offer gives eligible customers 20% off their first three months or 35% off their first annual subscription. Final eligibility and checkout pricing are controlled by Unbounce.",
    "Unbounce's partner welcome email for COSHUMA identifies <span class=\"text-white font-semibold\">https://unbounce.partnerlinks.io/5ubjnt8lluqi</span> as the unique customer referral link, confirms the 20% / 35% customer offer, and states that the link uses a 90-day cookie. COSHUMA therefore keeps revenue CTAs on that exact verified route rather than replacing it with a generic homepage or dashboard URL.": "The current offer provides 20% off the first 3 months or 35% off the first annual subscription for eligible customers. Check final eligibility and pricing on Unbounce before purchase because promotions can change.",
    "Attribution is ultimately controlled by Unbounce and PartnerStack. COSHUMA does not claim a referral or commission until the partner system confirms it.": "Final eligibility and checkout pricing are controlled by Unbounce.",
    "Unbounce's official Partner Program FAQ says referral tracking uses a 90-day cookie. If the referral link is clicked again, Unbounce says the 90-day window restarts. COSHUMA therefore uses the verified PartnerStack URL rather than a generic Unbounce homepage link for revenue CTAs.": "The current offer provides 20% off the first three months or 35% off the first annual subscription for eligible customers. Check final eligibility and checkout pricing on Unbounce before purchasing.",
    "Tip: complete the trial signup from the same browser session after using the partner link when practical. Attribution is ultimately controlled by Unbounce and PartnerStack, so COSHUMA does not claim a referral until the partner dashboard confirms it.": "Tip: check the final discount and plan price at checkout because promotions and eligibility can change.",
    "Affiliate disclosure: COSHUMA may earn a commission if you become a paying Unbounce customer through this verified partner link, at no extra cost to you. Unbounce's welcome email to COSHUMA states a minimum 25% commission for the first year and a 90-day tracking cookie.": "",

    # SaneBox
    "Verified SaneBox Partner · referral route verified Sep 16, 2026": "Pricing & trial terms checked Sep 16, 2026",
    "Compare current plans and start through COSHUMA's exact SaneBox-issued referral route.": "Compare current plans, trial terms and the features included at each tier.",
    "Try SaneBox via COSHUMA →": "Try SaneBox →",
    "Open verified SaneBox referral →": "Check the current SaneBox offer →",
    "Start SaneBox via COSHUMA →": "Start SaneBox →",
    "Trial terms: public vs referral": "Trial terms",
    "Standard public page says 7 days; partner email says referred customers start with 14 days": "The public page says 7 days; this offer currently states 14 days for eligible customers",
    "SaneBox's current public pricing page shows a 7-day trial. COSHUMA's SaneBox Partner Program welcome email separately states that referred trial customers start with a 14-day trial, so COSHUMA keeps those two claims distinct.": "SaneBox's current public pricing page shows a 7-day trial. The offer linked from this page currently states a 14-day trial for eligible referred customers, so confirm the trial length shown at the destination before signup.",
    "SaneBox's live public pricing and partner landing pages currently show a 7-day standard trial. Separately, COSHUMA's SaneBox Partner Program welcome email states that referred trial customers start with a 14-day free trial and SaneBox Concierge. Because these first-party sources differ, COSHUMA keeps the distinction visible instead of pretending they are the same offer.": "SaneBox's live public pricing page currently shows a 7-day standard trial, while the offer linked here currently states a 14-day free trial for eligible customers. Confirm the trial length and final terms shown at the destination before signup.",
    "SaneBox is the direct fit when the problem is a crowded personal or work inbox. COSHUMA now has a verified SaneBox-issued referral route, so SaneBox buttons on this page use that exact customer link rather than a generic homepage or PartnerStack dashboard URL.": "SaneBox is a direct fit when the problem is a crowded personal or work inbox. Compare the current plan limits and trial terms before choosing a paid tier.",
    "SaneBox public pricing/help pages rechecked September 16, 2026; Partner Program referral terms are based on the SaneBox welcome email received September 15, 2026. Prices and offers can change, and the vendor checkout is the final source of truth.": "SaneBox public pricing and offer terms were rechecked September 16, 2026. Prices and offers can change, and the vendor checkout is the final source of truth.",

    # Teachable
    "Teachable 30-Day Free Trial 2026: Verified COSHUMA Partner Route & Pricing": "Teachable 30-Day Free Trial 2026: Trial & Pricing Guide",
    "Teachable 30-Day Free Trial 2026: Verified COSHUMA Partner Route": "Teachable 30-Day Free Trial 2026: Trial & Pricing Guide",
    "Teachable trial and pricing guide for 2026: compare the public 7-day trial with COSHUMA's vendor-confirmed 30-day PartnerStack trial route, plus Starter, Builder and Growth pricing before you choose.": "Teachable trial and pricing guide for 2026: compare the public 7-day trial with the 30-day trial offer linked from this page, plus Starter, Builder and Growth pricing before you choose.",
    "A buyer-focused Teachable trial and pricing guide that separates Teachable's public 7-day trial from the 30-day PartnerStack route Teachable supplied directly to COSHUMA.": "A buyer-focused Teachable trial and pricing guide that compares the public 7-day trial with the 30-day trial offer linked from this page.",
    "Does COSHUMA have a 30-day Teachable trial route?": "Is a 30-day Teachable trial offer available from this page?",
    "Yes. A Teachable affiliate manager supplied COSHUMA an exact PartnerStack customer-facing route specifically described as the 30-day Free Trial route. COSHUMA uses that vendor-issued URL rather than constructing or guessing a tracking link.": "Yes. The offer linked from this page is currently described as a 30-day free trial. Confirm the trial length and billing terms shown at the destination before signup.",
    "Teachable 30-day free trial: use the exact route Teachable gave COSHUMA": "Teachable 30-day free trial: compare the longer offer before signup",
    "Open verified 30-day trial route →": "Check the 30-day trial offer →",
    "Start through verified 30-day route →": "Start the 30-day trial →",
    "7-day public trial vs COSHUMA's 30-day partner route": "7-day public trial vs the 30-day offer linked here",
    "COSHUMA PartnerStack": "30-day offer linked here",
    "Exact route supplied by Teachable manager": "Offer shown at destination",
    "Longer tracked evaluation when still offered at destination": "Longer evaluation when still offered at destination",
    "Route": "Option",
    "COSHUMA has not verified a signup, paying customer, commission or revenue event from publication of this page. Those states remain unverified until partner-side evidence exists.": "",

    # Hub cards / collection labels
    "Workflow automation · verified Make partner route": "Workflow automation · current Make offer",
    "14-day free trial, then 20% off the first 3 months or 35% off the first annual subscription through COSHUMA's verified Unbounce route.": "14-day free trial, then 20% off the first 3 months or 35% off the first annual subscription on the current offer.",
    "See what Fireflies includes at $0, compare Pro and Business, then start through COSHUMA's verified customer referral route if the workflow fits.": "See what Fireflies includes at $0, compare Pro and Business, then check the current offer if the workflow fits.",
    "Course platforms · vendor-confirmed partner route": "Course platforms · 30-day trial offer",
    "Compare Teachable's public trial with COSHUMA's vendor-confirmed 30-day PartnerStack route before choosing a paid creator plan.": "Compare Teachable's public trial with the 30-day trial offer linked here before choosing a paid creator plan.",
    "Claap Pricing & Verified Partner Guide": "Claap Pricing & Buyer Guide",
    "Entry pricing, 14-day trials, traffic limits, A/B testing and agency fit—plus COSHUMA's verified Unbounce partner offer.": "Entry pricing, 14-day trials, traffic limits, A/B testing, agency fit and the current Unbounce discount.",

    # Claap / application-state pages
    "Partner feedback + official pricing checked Sep 15, 2026": "Product & pricing checked Sep 15, 2026",
    "Start Claap with verified tracking →": "Try Claap →",
    "Try Claap with verified tracking →": "Try Claap →",
    "Affiliate status: verified. Claap affiliate manager Lamia Karmaly supplied COSHUMA's exact customer-facing PartnerStack URLs directly by email on Sep 9, 2026. The primary Try Claap buttons use the first issued tracking URL; the pricing button remains the official live pricing page until the intended destination of the second issued URL is clarified. Link issuance does not imply a signup, commission, or sale.": "",
    "Affiliate status: Scribe told COSHUMA on September 14, 2026 that it is not accepting new affiliate applications while the program is being restructured. COSHUMA has no approval or issued customer tracking URL, so these buttons remain official non-affiliate links.": "",
    "Affiliate status: Landingi officially confirms a PartnerStack affiliate program, but COSHUMA has not submitted or verified an account-specific customer tracking URL. These buttons intentionally remain official non-affiliate links.": "",
    "Official non-affiliate link. COSHUMA has not verified an account-specific Leadpages PartnerStack customer tracking URL.": "",

    # Other known public leaks
    "Sources & revenue-truth note": "Sources & disclosure",
    "Sources checked: ClickFunnels official pricing page and ClickFunnels support documentation covering the 14-day trial, automatic billing after the trial, and 2026 pricing. COSHUMA independently verified the affiliate URL in the authenticated ClickFunnels Affiliate Center before using it as a revenue CTA.": "Sources checked: ClickFunnels official pricing page and ClickFunnels support documentation covering the 14-day trial, automatic billing after the trial, and 2026 pricing.",
    "Checked September 16, 2026 against ConvertFlow's current pricing, referral documentation and authenticated partner-dashboard evidence plus COSHUMA's existing verified Unbounce PartnerStack route. ConvertFlow enrollment and the account-issued referral URL are verified; no signup, customer, commission or revenue is inferred from link approval alone.": "Checked September 16, 2026 against current ConvertFlow and Unbounce pricing and product information. Vendor pricing and offer terms can change, so confirm the destination before paying.",
}

# These patterns only match human-readable phrases with spaces, not URL hosts or
# query parameters, so outbound attribution URLs remain byte-for-byte intact.
PHRASE_RULES = (
    (re.compile(r"\bverified\s+[A-Za-z0-9 ._-]{1,40}\s+partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+partner\s+(?:route|path|offer|link)s?\b", re.I), "current offer"),
    (re.compile(r"\bvendor-confirmed\s+(?:[0-9]+-day\s+)?partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+customer\s+referral\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+referral\s+(?:route|link)s?\b", re.I), "current offer"),
    (re.compile(r"\bCOSHUMA-verified\s+partner\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bCOSHUMA's\s+verified\s+[A-Za-z0-9 ._/%-]{1,50}\s+(?:partner\s+)?(?:route|offer|link)\b", re.I), "the current offer"),
    (re.compile(r"\bverified\s+CTA\s+status\b", re.I), "current trial and pricing details"),
    (re.compile(r"\bwith\s+verified\s+tracking\b", re.I), ""),
    (re.compile(r"\b(?:Try|Start)\s+([A-Za-z0-9 ._-]+)\s+(?:via|through)\s+COSHUMA\s*→", re.I), r"Try \1 →"),
)

TAG_RE = re.compile(r"<[^>]+>")
JSONLD_RE = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.I | re.S)

INTERNAL_PATTERNS = [re.compile(p, re.I) for p in [
    r"^Affiliate status:", r"COSHUMA affiliate status", r"COSHUMA CTA state",
    r"PartnerStack application", r"authenticated partner[- ]dashboard", r"affiliate manager",
    r"partner welcome email", r"welcome email to COSHUMA", r"account-specific .* tracking URL",
    r"customer-facing .* tracking URL", r"customer-facing .* PartnerStack", r"exact PartnerStack",
    r"verified PartnerStack", r"revenue[- ]truth", r"revenue CTA", r"tracking cookie",
    r"tracking verification", r"partner dashboard confirms", r"link issuance does not",
    r"publication .* not treated as .* revenue", r"COSHUMA has not (?:submitted|verified|received|recovered)",
    r"official non-affiliate link", r"buttons .* remain official non-affiliate",
    r"generic .* dashboard .* revenue", r"first-party reporting verifies it",
    r"authenticated ClickFunnels Affiliate Center",
]]


def visible_text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(TAG_RE.sub(" ", fragment))).strip()


def is_internal(text: str) -> bool:
    text = re.sub(r"\s+", " ", html_lib.unescape(text)).strip()
    return bool(text) and any(p.search(text) for p in INTERNAL_PATTERNS)


def strip_block(match: re.Match[str]) -> str:
    block = match.group(0)
    text = visible_text(block)
    # Keep a short legal disclosure. Detailed commission/cookie/network language
    # is rewritten or removed by the rules above.
    if re.search(r"Affiliate disclosure:.*may earn (?:an affiliate )?commission", text, re.I) and not is_internal(text):
        return block
    return "" if is_internal(text) else block


def sanitize_jsonld(source: str) -> str:
    def rewrite(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(2))
        except Exception:
            return match.group(0)
        changed = False
        def walk(node):
            nonlocal changed
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if not isinstance(node, dict):
                return
            types = node.get("@type")
            types = types if isinstance(types, list) else [types]
            if "FAQPage" in types and isinstance(node.get("mainEntity"), list):
                kept = []
                for item in node["mainEntity"]:
                    q = str(item.get("name", "")) if isinstance(item, dict) else ""
                    aobj = item.get("acceptedAnswer", {}) if isinstance(item, dict) else {}
                    a = str(aobj.get("text", "")) if isinstance(aobj, dict) else ""
                    admin_q = bool(re.search(r"COSHUMA.*(?:affiliate|partner|route|link)|affiliate link|referral link|tracking URL|PartnerStack", q, re.I))
                    if admin_q or is_internal(f"{q} {a}"):
                        changed = True
                        continue
                    kept.append(item)
                node["mainEntity"] = kept
            for value in node.values():
                walk(value)
        walk(data)
        if not changed:
            return match.group(0)
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)
    return JSONLD_RE.sub(rewrite, source)


def clean_html(text: str) -> str:
    for old, new in EXACT.items():
        text = text.replace(old, new)
    # Remove the specific Unbounce cookie FAQ if it survives an upstream generator.
    text = re.sub(r',\s*\{\s*"@type":\s*"Question",\s*"name":\s*"How long does the Unbounce partner cookie last\?".*?\}\s*\}', '', text, flags=re.S)
    # DocsBot's entire affiliate-operations section is not buyer content.
    text = re.sub(r'<section\b[^>]*>\s*<h2\b[^>]*>Verified COSHUMA affiliate terms</h2>.*?</section>', '', text, flags=re.I | re.S)
    for pattern, replacement in PHRASE_RULES:
        text = pattern.sub(replacement, text)
    for tag in ("p", "li", "small", "tr"):
        text = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", strip_block, text, flags=re.I | re.S)
    text = re.sub(r"<div\b[^>]*>(?:(?!<div\b).)*?</div>", strip_block, text, flags=re.I | re.S)
    return sanitize_jsonld(text)


def clean_public_js(text: str) -> str:
    text = text.replace("A fresh Unbounce Affiliate Team message to COSHUMA emphasized lead handoff as a retention use case. That makes integrations a practical buying test: confirm that captured leads can reach the CRM, email or automation stack you already use before choosing a paid plan.", "Integrations are a practical buying test: confirm that captured leads can reach the CRM, email or automation stack you already use before choosing a paid plan.")
    text = text.replace("These are product-fit checks, not promised results. COSHUMA does not claim a conversion lift, signup or commission unless first-party reporting verifies it.", "These are product-fit checks, not promised results. Test the workflow with your own traffic and integrations before choosing a paid plan.")
    text = text.replace("Test Unbounce through the verified partner route →", "Try Unbounce →")
    return text


def clean_llms(text: str) -> str:
    replacements = (
        ("COSHUMA's verified vendor-issued referral route", "the current vendor offer"),
        ("COSHUMA's verified PartnerStack customer referral URL", "the current marked vendor link"),
        ("verified PartnerStack route", "current vendor offer"),
        ("PartnerStack route", "vendor offer"),
        ("verified referral route", "current offer"),
        ("verified partner route", "current offer"),
        ("revenue CTA", "buyer CTA"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> None:
    changed = []
    html_files = [ROOT / "index.html", *PUBLIC.rglob("*.html")]
    for path in html_files:
        before = path.read_text(encoding="utf-8")
        after = clean_html(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())

    js = PUBLIC / "affiliate-attribution.js"
    if js.exists():
        before = js.read_text(encoding="utf-8")
        after = clean_public_js(before)
        if after != before:
            js.write_text(after, encoding="utf-8")
            changed.append(js.relative_to(ROOT).as_posix())

    llms = PUBLIC / "llms.txt"
    if llms.exists():
        before = llms.read_text(encoding="utf-8")
        after = clean_llms(before)
        if after != before:
            llms.write_text(after, encoding="utf-8")
            changed.append(llms.relative_to(ROOT).as_posix())

    print(f"Customer-only copy guard: {len(changed)} files normalized")


if __name__ == "__main__":
    main()
