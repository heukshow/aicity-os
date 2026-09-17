"""Final public-copy guard for customer-only language.

Runs after all revenue/affiliate generators and immediately before Vite build.
It preserves URLs, data attributes and required affiliate disclosures while
removing operational wording customers do not need to see.
"""
from pathlib import Path
import html as html_lib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

EXACT = {
    # Hub copy: explain purchase decisions, not internal monetization mechanics.
    "COSHUMA separates editorial comparisons from partner links and labels monetized CTAs inside each guide.":
        "COSHUMA focuses on pricing, trials, discounts and practical product fit so you can compare options more quickly.",
    "COSHUMA focuses on pricing, free access, buyer fit and verified partner routes without treating clicks as revenue.":
        "COSHUMA focuses on pricing, free access, buyer fit and practical product differences.",
    "A verified partner route is kept separate from editorial product fit, and publication or test clicks are not treated as signups, customers or revenue.":
        "Use the comparison to narrow your shortlist, then confirm current pricing and terms on the vendor's site before purchasing.",

    # Relevance AI: keep product/pricing guidance, hide route verification details.
    "Relevance AI buyer guide for AI agent teams: current product positioning, pricing reality, free entry path, enterprise controls, integrations, and a verified COSHUMA partner link.":
        "Relevance AI buyer guide for AI agent teams: current product positioning, pricing reality, free entry, enterprise controls, integrations and practical product-fit guidance.",
    "Decide whether Relevance AI fits your AI-agent workflow, then use COSHUMA's verified partner route or the official pricing page.":
        "Decide whether Relevance AI fits your AI-agent workflow, then compare the current free-entry and pricing options.",
    "Buyer guide verified against current official product and pricing pages · Sep 6, 2026":
        "Buyer guide based on current official product and pricing information · Sep 6, 2026",
    "Try Relevance AI via COSHUMA →": "Try Relevance AI →",
    "This makes the verified partner route suitable for visitors who want to test the platform before a paid decision.":
        "This makes it practical to test the platform before making a paid decision.",
    "Start with the verified partner route →": "Start free with Relevance AI →",
    "Use the verified COSHUMA partner route for the free-entry path, then confirm current plan availability and checkout terms directly with Relevance AI before upgrading.":
        "Start with the free-entry path, then confirm current plan availability and checkout terms directly with Relevance AI before upgrading.",

    # Unbounce tool: retain buyer-visible discount facts, hide tracking/attribution operations.
    "Unbounce Pricing 2026: $29 Starter + 20%/35% Partner Discount | COSHUMA":
        "Unbounce Pricing 2026: $29 Starter + 20%/35% Discount | COSHUMA",
    "Unbounce Pricing 2026: $29 Starter + 20%/35% Partner Discount":
        "Unbounce Pricing 2026: $29 Starter + 20%/35% Discount",
    "Unbounce pricing starts at $29/month. Compare current plans, the 14-day no-card trial, and COSHUMA's verified offer: 20% off 3 months or 35% off the first annual subscription.":
        "Unbounce pricing starts at $29/month. Compare current plans, the 14-day no-card trial, and the current offer: 20% off 3 months or 35% off the first annual subscription.",
    "Current Unbounce pricing, 14-day trial, plan-fit guidance, and COSHUMA's verified customer partner offer.":
        "Current Unbounce pricing, 14-day trial, plan-fit guidance and the current discount offer.",
    "What discount does COSHUMA's Unbounce partner link provide?":
        "What discount is currently available with this Unbounce offer?",
    "Unbounce's partner welcome email for COSHUMA states that the unique referral link gives eligible customers 20% off their first three months or 35% off their first annual subscription. Final eligibility and checkout pricing are controlled by Unbounce.":
        "The current offer gives eligible customers 20% off their first three months or 35% off their first annual subscription. Final eligibility and checkout pricing are controlled by Unbounce.",
    "Unbounce pricing, trial & verified partner discount": "Unbounce pricing, trial & current discount",
    "Partner offer": "Current discount",
    "Tracking": "Before you buy",
    "90-day cookie": "Check checkout",
    "Confirmed in COSHUMA's Unbounce partner welcome email.": "Discount eligibility and final pricing are controlled by Unbounce.",
    "Start 14-day trial + partner discount →": "Start 14-day trial + discount →",
    "Check the verified Unbounce offer →": "Check the current Unbounce offer →",
    "Why the partner route matters": "Before you start",
    "Use the verified link before starting your trial": "Check the trial and discount before you start",
    "Unbounce's partner welcome email for COSHUMA identifies <span class=\"text-white font-semibold\">https://unbounce.partnerlinks.io/5ubjnt8lluqi</span> as the unique customer referral link, confirms the 20% / 35% customer offer, and states that the link uses a 90-day cookie. COSHUMA therefore keeps revenue CTAs on that exact verified route rather than replacing it with a generic homepage or dashboard URL.":
        "The current offer provides 20% off the first 3 months or 35% off the first annual subscription for eligible customers. Check final eligibility and pricing on Unbounce before purchase because promotions can change.",
    "Attribution is ultimately controlled by Unbounce and PartnerStack. COSHUMA does not claim a referral or commission until the partner system confirms it.":
        "Final eligibility and checkout pricing are controlled by Unbounce.",
    "Partner discount, commission and cookie details were checked against the Unbounce partner welcome email sent to COSHUMA on September 3, 2026.":
        "The current Unbounce discount was checked against vendor-supplied terms on September 3, 2026.",

    # Webflow vs Unbounce: keep the offer, remove PartnerStack/revenue routing details.
    "Webflow vs Unbounce in 2026: compare current pricing, CMS/hosting vs landing-page optimization, A/B testing, AI features, and COSHUMA's verified Unbounce partner offer.":
        "Webflow vs Unbounce in 2026: compare current pricing, CMS/hosting vs landing-page optimization, A/B testing, AI features and the current Unbounce discount.",
    "Does COSHUMA have a verified Unbounce offer?":
        "What Unbounce discount is currently available?",
    "Yes. COSHUMA's verified Unbounce PartnerStack link is documented with a customer offer of 20% off the first three months or 35% off the first annual subscription. Final eligibility and checkout pricing are controlled by Unbounce.":
        "The current Unbounce offer provides 20% off the first three months or 35% off the first annual subscription for eligible customers. Final eligibility and checkout pricing are controlled by Unbounce.",
    "Start Unbounce trial + verified partner offer →": "Start Unbounce trial + discount →",
    "COSHUMA's verified Unbounce partner route documents 20% off the first 3 months or 35% off the first annual subscription. Final eligibility and checkout pricing are controlled by Unbounce.":
        "The current Unbounce offer provides 20% off the first 3 months or 35% off the first annual subscription for eligible customers. Final eligibility and checkout pricing are controlled by Unbounce.",
    "Build a page for an actual traffic source, measure editing speed and conversion workflow, and only keep the paid plan if the CRO features solve a real campaign bottleneck. COSHUMA keeps the revenue CTA on the exact verified PartnerStack customer link rather than a generic homepage.":
        "Build a page for an actual traffic source, measure editing speed and conversion workflow, and only keep the paid plan if the CRO features solve a real campaign bottleneck.",
    "Try Unbounce through COSHUMA →": "Try Unbounce →",

    # Unbounce discount guide: buyers need the discount and current terms, not attribution plumbing.
    "Unbounce's official Partner Program FAQ says referral tracking uses a 90-day cookie. If the referral link is clicked again, Unbounce says the 90-day window restarts. COSHUMA therefore uses the verified PartnerStack URL rather than a generic Unbounce homepage link for revenue CTAs.":
        "The current offer provides 20% off the first three months or 35% off the first annual subscription for eligible customers. Check final eligibility and checkout pricing on Unbounce before purchasing.",
    "Tip: complete the trial signup from the same browser session after using the partner link when practical. Attribution is ultimately controlled by Unbounce and PartnerStack, so COSHUMA does not claim a referral until the partner dashboard confirms it.":
        "Tip: check the final discount and plan price at checkout because promotions and eligibility can change.",

    # Framer vs Unbounce: keep only the minimum disclosure on the comparison page.
    "Affiliate disclosure: COSHUMA may earn a commission if you become a paying Unbounce customer through this verified partner link, at no extra cost to you. Unbounce's welcome email to COSHUMA states a minimum 25% commission for the first year and a 90-day tracking cookie.":
        "Affiliate disclosure: COSHUMA may earn a commission from eligible purchases made through the marked Unbounce link, at no extra cost to you.",

    # ClickFunnels: keep factual sources, remove authenticated affiliate-center operations.
    "Sources checked: ClickFunnels official pricing page and ClickFunnels support documentation covering the 14-day trial, automatic billing after the trial, and 2026 pricing. COSHUMA independently verified the affiliate URL in the authenticated ClickFunnels Affiliate Center before using it as a revenue CTA.":
        "Sources checked: ClickFunnels official pricing page and ClickFunnels support documentation covering the 14-day trial, automatic billing after the trial, and 2026 pricing.",

    # Databox vs Brand24: keep source transparency, remove account-specific affiliate-state mechanics.
    "Databox pricing and feature claims were rechecked against Databox's live pricing page on September 8, 2026. Brand24 prices, annual discounts and trial terms were rechecked against Brand24's live pricing page on September 8, 2026. The customer-facing Databox and Brand24 URLs used above are the account-specific links already marked verified in COSHUMA's affiliate state; generic dashboards or onboarding URLs are not used as revenue CTAs. Vendor pricing can change, so confirm checkout before paying.":
        "Databox pricing and feature claims were rechecked against Databox's live pricing page on September 8, 2026. Brand24 prices, annual discounts and trial terms were rechecked against Brand24's live pricing page on September 8, 2026. Vendor pricing can change, so confirm checkout before paying.",

    # ConvertFlow comparison: source freshness is useful; authenticated affiliate mechanics are not.
    "Checked September 16, 2026 against ConvertFlow's current pricing, referral documentation and authenticated partner-dashboard evidence plus COSHUMA's existing verified Unbounce PartnerStack route. ConvertFlow enrollment and the account-issued referral URL are verified; no signup, customer, commission or revenue is inferred from link approval alone.":
        "Checked September 16, 2026 against current ConvertFlow and Unbounce pricing and product information. Vendor pricing and offer terms can change, so confirm the destination before paying.",

    # Brand24 vs Mention: keep a short legal disclosure, not revenue-truth mechanics.
    "Sources & revenue-truth note": "Sources & disclosure",
    "Affiliate disclosure: the Brand24 buttons use COSHUMA's previously verified PartnerStack customer tracking URL. COSHUMA may earn a commission if an eligible buyer later becomes a paying customer. Mention stays non-affiliate here because no exact COSHUMA customer tracking URL has been verified. Publishing or clicking this page is not treated as a signup, paid customer, commission or revenue event.":
        "Affiliate disclosure: COSHUMA may earn a commission from eligible purchases made through the marked Brand24 links, at no extra cost to you.",

    # SaneBox: preserve the buyer-relevant 7-day/14-day distinction without exposing partner operations.
    "SaneBox pricing starts at $4.54/month on biyearly billing. Compare Snack, Lunch and Dinner, the standard 7-day public trial, and COSHUMA's verified SaneBox referral route.":
        "SaneBox pricing starts at $4.54/month on biyearly billing. Compare Snack, Lunch and Dinner, the standard 7-day public trial and the current longer-trial offer available from this page.",
    "Compare current SaneBox pricing, the standard public trial, and COSHUMA's verified customer referral route.":
        "Compare current SaneBox pricing, the standard public trial and the current longer-trial offer available from this page.",
    "SaneBox's current public pricing page shows a 7-day trial. COSHUMA's SaneBox Partner Program welcome email separately states that referred trial customers start with a 14-day trial, so COSHUMA keeps those two claims distinct.":
        "SaneBox's current public pricing page shows a 7-day trial. The offer linked from this page currently states a 14-day trial for eligible referred customers, so confirm the trial length shown at the destination before signup.",
    "Verified SaneBox Partner · referral route verified Sep 16, 2026":
        "Pricing & trial terms checked Sep 16, 2026",
    "Compare current plans and start through COSHUMA's exact SaneBox-issued referral route.":
        "Compare current plans, trial terms and the features included at each tier.",
    "Try SaneBox via COSHUMA →": "Try SaneBox →",
    "Trial terms: public vs referral": "Trial terms",
    "Standard public page says 7 days; partner email says referred customers start with 14 days":
        "The public page says 7 days; this offer currently states 14 days for eligible customers",
    "SaneBox's live public pricing and partner landing pages currently show a 7-day standard trial. Separately, COSHUMA's SaneBox Partner Program welcome email states that referred trial customers start with a 14-day free trial and SaneBox Concierge. Because these first-party sources differ, COSHUMA keeps the distinction visible instead of pretending they are the same offer.":
        "SaneBox's live public pricing page currently shows a 7-day standard trial, while the offer linked here currently states a 14-day free trial for eligible customers. Confirm the trial length and final terms shown at the destination before signup.",
    "Open verified SaneBox referral →": "Check the current SaneBox offer →",
    "SaneBox is the direct fit when the problem is a crowded personal or work inbox. COSHUMA now has a verified SaneBox-issued referral route, so SaneBox buttons on this page use that exact customer link rather than a generic homepage or PartnerStack dashboard URL.":
        "SaneBox is a direct fit when the problem is a crowded personal or work inbox. Compare the current plan limits and trial terms before choosing a paid tier.",
    "Start SaneBox via COSHUMA →": "Start SaneBox →",
    "SaneBox public pricing/help pages rechecked September 16, 2026; Partner Program referral terms are based on the SaneBox welcome email received September 15, 2026. Prices and offers can change, and the vendor checkout is the final source of truth.":
        "SaneBox public pricing and offer terms were rechecked September 16, 2026. Prices and offers can change, and the vendor checkout is the final source of truth.",

    # Teachable: present the 30-day offer as a buyer option, not an affiliate-network workflow.
    "Teachable 30-Day Free Trial 2026: Verified COSHUMA Partner Route & Pricing":
        "Teachable 30-Day Free Trial 2026: Trial & Pricing Guide",
    "Teachable trial and pricing guide for 2026: compare the public 7-day trial with COSHUMA's vendor-confirmed 30-day PartnerStack trial route, plus Starter, Builder and Growth pricing before you choose.":
        "Teachable trial and pricing guide for 2026: compare the public 7-day trial with the 30-day trial offer linked from this page, plus Starter, Builder and Growth pricing before you choose.",
    "Teachable 30-Day Free Trial 2026: Verified COSHUMA Partner Route":
        "Teachable 30-Day Free Trial 2026: Trial & Pricing Guide",
    "A buyer-focused Teachable trial and pricing guide that separates Teachable's public 7-day trial from the 30-day PartnerStack route Teachable supplied directly to COSHUMA.":
        "A buyer-focused Teachable trial and pricing guide that compares the public 7-day trial with the 30-day trial offer linked from this page.",
    "Does COSHUMA have a 30-day Teachable trial route?":
        "Is a 30-day Teachable trial offer available from this page?",
    "Yes. A Teachable affiliate manager supplied COSHUMA an exact PartnerStack customer-facing route specifically described as the 30-day Free Trial route. COSHUMA uses that vendor-issued URL rather than constructing or guessing a tracking link.":
        "Yes. The offer linked from this page is currently described as a 30-day free trial. Confirm the trial length and billing terms shown at the destination before signup.",
    "Teachable 30-day free trial: use the exact route Teachable gave COSHUMA":
        "Teachable 30-day free trial: compare the longer offer before signup",
    "Teachable's public pricing page currently shows a <strong class=\"text-white\">7-day free trial</strong>. Separately, Teachable affiliate manager Camila Gouveia supplied COSHUMA the exact PartnerStack URL below and described it as COSHUMA's <strong class=\"text-white\">30-day Free Trial</strong> route. That distinction matters: COSHUMA does not manufacture a longer-trial URL by adding parameters to Teachable's website.":
        "Teachable's public pricing page currently shows a <strong class=\"text-white\">7-day free trial</strong>. The offer linked from this page currently states a <strong class=\"text-white\">30-day free trial</strong>. Confirm the trial length and billing terms shown at the destination before signup.",
    "Open verified 30-day trial route →": "Check the 30-day trial offer →",
    "Affiliate disclosure: the first button uses the customer-facing PartnerStack route that Teachable supplied directly to COSHUMA. COSHUMA may earn a commission if an eligible paid customer is attributed through it, at no extra cost to the buyer. Link issuance does not prove a signup, sale or commission.":
        "Affiliate disclosure: COSHUMA may earn a commission from eligible purchases made through the marked Teachable link, at no extra cost to you.",
    "COSHUMA vendor-supplied route": "Offer linked here",
    "You want a vendor-issued tracked route rather than a guessed coupon or URL parameter.":
        "You want enough time to test a representative course workflow before paying.",
    "7-day public trial vs COSHUMA's 30-day partner route":
        "7-day public trial vs the 30-day offer linked here",
    "COSHUMA PartnerStack": "30-day offer linked here",
    "Exact route supplied by Teachable manager": "Offer shown at destination",
    "Longer tracked evaluation when still offered at destination": "Longer evaluation when still offered at destination",
    "Open the exact 30-day PartnerStack route below, confirm the offer shown at the destination, and use the trial to validate your real course or digital-product workflow. For a broader feature breakdown, read COSHUMA's Teachable pricing guide first.":
        "Open the 30-day trial offer below, confirm the terms shown at the destination, and use the trial to validate your real course or digital-product workflow. For a broader feature breakdown, read COSHUMA's Teachable pricing guide first.",
    "Start through verified 30-day route →": "Start the 30-day trial →",
    "Teachable's official pricing page for current plan prices, public 7-day trial, 30-day guarantee and transaction-fee terms; Teachable's direct PartnerStack message to COSHUMA for the exact 30-day Free Trial customer route. Last checked September 15, 2026.":
        "Teachable's official pricing page and current trial offer were checked for plan prices, trial terms, guarantee and transaction-fee details. Last checked September 15, 2026.",
    "COSHUMA has not verified a signup, paying customer, commission or revenue event from publication of this page. Those states remain unverified until partner-side evidence exists.": "",

    # Moosend vs Mailchimp: retain the legal disclosure; remove network/revenue-status commentary.
    "A buyer-focused comparison of Moosend and Mailchimp's current free-entry options, with COSHUMA's verified Moosend partner route.":
        "A buyer-focused comparison of Moosend and Mailchimp's current free-entry options.",
    "COSHUMA uses its verified account-specific partner URL for Moosend. Mailchimp links on this page are official non-affiliate reference links.":
        "COSHUMA may earn a commission from eligible purchases made through the marked Moosend links. Mailchimp links on this page go to the official vendor site.",
    "Verified COSHUMA partner route. COSHUMA may earn a commission on a qualifying purchase.":
        "Affiliate disclosure: COSHUMA may earn a commission from an eligible Moosend purchase, at no extra cost to you.",
    "Official Mailchimp link. COSHUMA has not verified a commission-bearing Mailchimp customer route, so no affiliate URL is invented here.":
        "Official Mailchimp link.",
    "COSHUMA verified revenue route": "Link type",
    "Yes — exact PartnerStack customer URL verified": "Marked COSHUMA link",
    "No verified affiliate route; official links only": "Official vendor link",
    "Why is only Moosend marked as a partner route?": "Why are the links labeled differently?",
    "COSHUMA has an exact, account-specific Moosend PartnerStack customer URL that has been verified. No commission-bearing Mailchimp customer URL has been verified for COSHUMA, so Mailchimp remains official-only on this page.":
        "The Moosend links are marked because COSHUMA may earn a commission from eligible purchases. Mailchimp links on this page go directly to the official vendor site.",
    "Start Moosend free through COSHUMA →": "Start Moosend free →",
    "Affiliate disclosure: COSHUMA may earn a commission from qualifying Moosend purchases through the marked partner links. Mailchimp references are non-affiliate.":
        "Affiliate disclosure: COSHUMA may earn a commission from eligible purchases made through the marked Moosend links, at no extra cost to you.",

    # Claap: preserve the link and disclosure, remove manager/network/status implementation details.
    "Partner feedback + official pricing checked Sep 15, 2026": "Product & pricing checked Sep 15, 2026",
    "Start Claap with verified tracking →": "Try Claap →",
    "Affiliate status: verified. Claap affiliate manager Lamia Karmaly supplied COSHUMA's exact customer-facing PartnerStack URLs directly by email on Sep 9, 2026. The primary Try Claap buttons use the first issued tracking URL; the pricing button remains the official live pricing page until the intended destination of the second issued URL is clarified. Link issuance does not imply a signup, commission, or sale.": "",
    "Affiliate disclosure: COSHUMA may earn a commission if you purchase through a verified Claap affiliate link, at no extra cost to you. This does not affect our editorial assessment.":
        "Affiliate disclosure: COSHUMA may earn a commission from eligible purchases made through the marked Claap link, at no extra cost to you.",
    "this review uses Claap's current official product/security pages plus direct feedback from Claap affiliate manager Lamia Karmaly. COSHUMA does not claim hands-on testing where none was performed. Final plan limits and pricing are controlled by Claap.":
        "this review uses Claap's current official product and security information. COSHUMA does not claim hands-on testing where none was performed. Final plan limits and pricing are controlled by Claap.",
    "Try Claap with verified tracking →": "Try Claap →",

    # Scribe, Landingi, Leadpages: application state belongs in private ops only.
    "Affiliate status: Scribe told COSHUMA on September 14, 2026 that it is not accepting new affiliate applications while the program is being restructured. COSHUMA has no approval or issued customer tracking URL, so these buttons remain official non-affiliate links.": "",
    "Affiliate status: Landingi officially confirms a PartnerStack affiliate program, but COSHUMA has not submitted or verified an account-specific customer tracking URL. These buttons intentionally remain official non-affiliate links.": "",
    "Official non-affiliate link. COSHUMA has not verified an account-specific Leadpages PartnerStack customer tracking URL.": "",
}

GENERIC = (
    (re.compile(r"\bverified\s+partner\s+routes\b", re.I), "current offers"),
    (re.compile(r"\bverified\s+partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+partner\s+paths\b", re.I), "current offers"),
    (re.compile(r"\bverified\s+partner\s+path\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+partner\s+offers\b", re.I), "current offers"),
    (re.compile(r"\bverified\s+partner\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+partner\s+links\b", re.I), "marked links"),
    (re.compile(r"\bverified\s+partner\s+link\b", re.I), "marked link"),
    (re.compile(r"\bverified\s+referral\s+links\b", re.I), "marked links"),
    (re.compile(r"\bverified\s+referral\s+link\b", re.I), "marked link"),
    (re.compile(r"\bverified\s+COSHUMA\s+partner\s+offers?\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+COSHUMA\s+partner\s+links?\b", re.I), "marked link"),
    (re.compile(r"\bverified\s+COSHUMA\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bCOSHUMA-verified\s+partner\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+Unbounce\s+partner\s+offers?\b", re.I), "current Unbounce discount"),
    (re.compile(r"\bverified\s+Unbounce\s+PartnerStack\s+link\b", re.I), "current Unbounce offer"),
    (re.compile(r"\bverified\s+CTA\s+status\b", re.I), "current trial and pricing details"),
    (re.compile(r"\bwith\s+verified\s+tracking\b", re.I), ""),
    (re.compile(r"\bTry\s+([A-Za-z0-9 ._-]+)\s+(?:via|through)\s+COSHUMA\s*→", re.I), r"Try \1 →"),
    (re.compile(r"\bStart\s+([A-Za-z0-9 ._-]+)\s+(?:via|through)\s+COSHUMA\s*→", re.I), r"Start \1 →"),
)

# Attribution plumbing belongs in private ops; buyers only need offer terms.
UNBOUNCE_COOKIE_FAQ = re.compile(
    r',\s*\{\s*"@type":\s*"Question",\s*"name":\s*"How long does the Unbounce partner cookie last\?",\s*'
    r'"acceptedAnswer":\s*\{\s*"@type":\s*"Answer",\s*"text":\s*"Unbounce\'s partner welcome email states that COSHUMA\'s verified referral link uses a 90-day tracking cookie\."\s*\}\s*\}',
    re.S,
)

DOCSBOT_INTERNAL_SECTION = re.compile(
    r'<section\b[^>]*>\s*<h2\b[^>]*>Verified COSHUMA affiliate terms</h2>.*?</section>',
    re.I | re.S,
)
DOCSBOT_INTERNAL_NOTE = re.compile(
    r'<div\b[^>]*>Unique affiliate URL verified from DocsBot\'s partner welcome email to COSHUMA on September 1, 2026\.</div>',
    re.I | re.S,
)

# Any residual block matching these patterns is operational rather than buyer-facing.
INTERNAL_OPS_PATTERNS = [
    re.compile(p, re.I) for p in [
        r"^Affiliate status:",
        r"COSHUMA affiliate status",
        r"COSHUMA CTA state",
        r"PartnerStack application",
        r"authenticated partner[- ]dashboard",
        r"affiliate manager",
        r"partner welcome email",
        r"welcome email to COSHUMA",
        r"account-specific .* tracking URL",
        r"account-specific .* partner URL",
        r"customer tracking URL .* verified",
        r"customer-facing .* tracking URL",
        r"customer-facing .* PartnerStack",
        r"exact PartnerStack",
        r"verified PartnerStack",
        r"revenue[- ]truth",
        r"revenue CTA",
        r"tracking cookie",
        r"tracking verification",
        r"partner dashboard confirms",
        r"link issuance does not",
        r"publication .* not treated as .* revenue",
        r"no .* commission-bearing .* URL .* verified",
        r"COSHUMA has not (?:submitted|verified|received|recovered)",
        r"COSHUMA .* no approval .* tracking URL",
        r"official non-affiliate link",
        r"buttons .* remain official non-affiliate",
        r"generic .* dashboard .* revenue",
        r"exact customer link rather than",
        r"first-party reporting verifies it",
        r"authenticated ClickFunnels Affiliate Center",
    ]
]

TAG_RE = re.compile(r"<[^>]+>")
JSONLD_RE = re.compile(
    r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S,
)


def visible_text(fragment: str) -> str:
    text = TAG_RE.sub(" ", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(text)).strip()


def internal_ops_text(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", html_lib.unescape(text)).strip()
    return bool(normalized) and any(pattern.search(normalized) for pattern in INTERNAL_OPS_PATTERNS)


def strip_block(match: re.Match[str]) -> str:
    block = match.group(0)
    text = visible_text(block)
    # Keep a short legal disclosure after exact/generic normalization.
    if re.search(r"Affiliate disclosure:.*may earn a commission", text, re.I) and not internal_ops_text(text):
        return block
    return "" if internal_ops_text(text) else block


def sanitize_jsonld(html: str) -> str:
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
                original_items = node["mainEntity"]
                kept = []
                for item in original_items:
                    question = str(item.get("name", "")) if isinstance(item, dict) else ""
                    answer_obj = item.get("acceptedAnswer", {}) if isinstance(item, dict) else {}
                    answer = str(answer_obj.get("text", "")) if isinstance(answer_obj, dict) else ""
                    combined = f"{question} {answer}".strip()
                    admin_question = bool(re.search(
                        r"COSHUMA.*(?:affiliate|partner|route|link)|affiliate link|referral link|tracking URL|PartnerStack",
                        question,
                        re.I,
                    ))
                    if admin_question or internal_ops_text(combined):
                        changed = True
                        continue
                    kept.append(item)
                if len(kept) != len(original_items):
                    node["mainEntity"] = kept
            for value in node.values():
                walk(value)

        walk(data)
        if not changed:
            return match.group(0)
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    return JSONLD_RE.sub(rewrite, html)


def strip_internal_ops_html(source: str) -> str:
    updated = source
    for tag in ("p", "li", "small", "tr"):
        updated = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", strip_block, updated, flags=re.I | re.S)
    # Simple leaf divs only; do not eat nested page structure.
    updated = re.sub(r"<div\b[^>]*>(?:(?!<div\b).)*?</div>", strip_block, updated, flags=re.I | re.S)
    return sanitize_jsonld(updated)


BANNED_CUSTOMER_COPY = re.compile(
    r'verified partner route|verified partner path|verified partner offer|verified partner link|'
    r'Verified COSHUMA affiliate terms|unique referral URL|partner welcome email|'
    r'revenue CTA|verified CTA status|without treating clicks as revenue|'
    r'tracking cookie|first-party reporting verifies it|dashboard/login URL|'
    r'account-specific links already marked verified|partner dashboard confirms it|'
    r'exact verified PartnerStack customer link|authenticated ClickFunnels Affiliate Center|'
    r'Affiliate status:|COSHUMA verified revenue route|exact PartnerStack customer URL verified|'
    r'authenticated partner-dashboard|affiliate manager .* supplied COSHUMA|'
    r'COSHUMA has not verified an account-specific',
    re.I,
)


def clean_html(text: str) -> str:
    for old, new in EXACT.items():
        text = text.replace(old, new)
    text = UNBOUNCE_COOKIE_FAQ.sub('', text)
    text = DOCSBOT_INTERNAL_SECTION.sub('', text)
    text = DOCSBOT_INTERNAL_NOTE.sub('', text)
    for pattern, replacement in GENERIC:
        text = pattern.sub(replacement, text)
    text = strip_internal_ops_html(text)
    return text


def clean_public_js(text: str) -> str:
    text = text.replace(
        "return heading && /verified link before starting your trial/i.test(heading.textContent || '');",
        "return heading && /check the trial and discount before you start/i.test(heading.textContent || '');",
    )
    text = text.replace(
        "A fresh Unbounce Affiliate Team message to COSHUMA emphasized lead handoff as a retention use case. That makes integrations a practical buying test: confirm that captured leads can reach the CRM, email or automation stack you already use before choosing a paid plan.",
        "Integrations are a practical buying test: confirm that captured leads can reach the CRM, email or automation stack you already use before choosing a paid plan.",
    )
    text = text.replace(
        "These are product-fit checks, not promised results. COSHUMA does not claim a conversion lift, signup or commission unless first-party reporting verifies it.",
        "These are product-fit checks, not promised results. Test the workflow with your own traffic and integrations before choosing a paid plan.",
    )
    text = text.replace("Test Unbounce through the verified partner route →", "Try Unbounce →")
    return text


def clean_llms(text: str) -> str:
    # llms.txt is public too. Keep guide descriptions useful without exposing ops/network state.
    replacements = (
        ("COSHUMA's verified vendor-issued referral route", "the current vendor offer"),
        ("COSHUMA's verified PartnerStack customer referral URL", "the current marked vendor link"),
        ("verified PartnerStack route", "current vendor offer"),
        ("PartnerStack route", "vendor offer"),
        ("PartnerStack", "partner platform"),
        ("verified referral route", "current offer"),
        ("verified partner route", "current offer"),
        ("revenue CTA", "buyer CTA"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> None:
    changed = []
    html_files = [ROOT / 'index.html', *PUBLIC.rglob('*.html')]
    for path in html_files:
        original = path.read_text(encoding='utf-8')
        updated = clean_html(original)
        if updated != original:
            path.write_text(updated, encoding='utf-8')
            changed.append(path.relative_to(ROOT).as_posix())

    attribution_js = PUBLIC / 'affiliate-attribution.js'
    if attribution_js.exists():
        original = attribution_js.read_text(encoding='utf-8')
        updated = clean_public_js(original)
        if updated != original:
            attribution_js.write_text(updated, encoding='utf-8')
            changed.append(attribution_js.relative_to(ROOT).as_posix())

    llms_path = PUBLIC / 'llms.txt'
    if llms_path.exists():
        original = llms_path.read_text(encoding='utf-8')
        updated = clean_llms(original)
        if updated != original:
            llms_path.write_text(updated, encoding='utf-8')
            changed.append(llms_path.relative_to(ROOT).as_posix())

    violations = []
    for path in html_files:
        text = path.read_text(encoding='utf-8')
        if BANNED_CUSTOMER_COPY.search(text):
            violations.append(path.relative_to(ROOT).as_posix())
    if attribution_js.exists() and re.search(
        r'Affiliate Team message to COSHUMA|first-party reporting verifies it|Test Unbounce through the verified partner route',
        attribution_js.read_text(encoding='utf-8'),
        re.I,
    ):
        violations.append(attribution_js.relative_to(ROOT).as_posix())

    if violations:
        raise RuntimeError('Internal operations copy remains public: ' + ', '.join(sorted(set(violations))))

    print(f'Customer-only copy guard: {len(changed)} files normalized')


if __name__ == '__main__':
    main()
