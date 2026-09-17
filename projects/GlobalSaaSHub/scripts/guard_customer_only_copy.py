"""Final public-copy guard for customer-only language.

Runs after all revenue/affiliate generators and immediately before Vite build.
It preserves URLs, data attributes and required affiliate disclosures while
removing operational wording customers do not need to see.
"""
from pathlib import Path
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
    "Start Unbounce trial + verified partner offer →":
        "Start Unbounce trial + discount →",
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

    # ClickFunnels: keep factual sources, remove authenticated affiliate-center operations.
    "Sources checked: ClickFunnels official pricing page and ClickFunnels support documentation covering the 14-day trial, automatic billing after the trial, and 2026 pricing. COSHUMA independently verified the affiliate URL in the authenticated ClickFunnels Affiliate Center before using it as a revenue CTA.":
        "Sources checked: ClickFunnels official pricing page and ClickFunnels support documentation covering the 14-day trial, automatic billing after the trial, and 2026 pricing.",

    # Databox vs Brand24: keep source transparency, remove account-specific affiliate-state mechanics.
    "Databox pricing and feature claims were rechecked against Databox's live pricing page on September 8, 2026. Brand24 prices, annual discounts and trial terms were rechecked against Brand24's live pricing page on September 8, 2026. The customer-facing Databox and Brand24 URLs used above are the account-specific links already marked verified in COSHUMA's affiliate state; generic dashboards or onboarding URLs are not used as revenue CTAs. Vendor pricing can change, so confirm checkout before paying.":
        "Databox pricing and feature claims were rechecked against Databox's live pricing page on September 8, 2026. Brand24 prices, annual discounts and trial terms were rechecked against Brand24's live pricing page on September 8, 2026. Vendor pricing can change, so confirm checkout before paying.",
}

GENERIC = (
    (re.compile(r"\bverified\s+partner\s+routes\b", re.I), "current offers"),
    (re.compile(r"\bverified\s+partner\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+partner\s+paths\b", re.I), "current offers"),
    (re.compile(r"\bverified\s+partner\s+path\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+partner\s+offers\b", re.I), "current offers"),
    (re.compile(r"\bverified\s+partner\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+partner\s+links\b", re.I), "vendor links"),
    (re.compile(r"\bverified\s+partner\s+link\b", re.I), "vendor link"),
    (re.compile(r"\bverified\s+COSHUMA\s+partner\s+offers?\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+COSHUMA\s+partner\s+links?\b", re.I), "vendor link"),
    (re.compile(r"\bverified\s+COSHUMA\s+offer\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+Unbounce\s+partner\s+offers?\b", re.I), "current Unbounce discount"),
    (re.compile(r"\bverified\s+Unbounce\s+PartnerStack\s+link\b", re.I), "current Unbounce offer"),
    (re.compile(r"\bverified\s+CTA\s+status\b", re.I), "current trial and pricing details"),
    (re.compile(r"\bTry\s+([A-Za-z0-9 ._-]+)\s+through\s+COSHUMA\s*→", re.I), r"Try \1 →"),
)

# This FAQ is pure attribution plumbing; customers only need the offer and final terms.
UNBOUNCE_COOKIE_FAQ = re.compile(
    r',\s*\{\s*"@type":\s*"Question",\s*"name":\s*"How long does the Unbounce partner cookie last\?",\s*'
    r'"acceptedAnswer":\s*\{\s*"@type":\s*"Answer",\s*"text":\s*"Unbounce\'s partner welcome email states that COSHUMA\'s verified referral link uses a 90-day tracking cookie\."\s*\}\s*\}',
    re.S,
)

# DocsBot currently exposes commission mechanics, login/dashboard routing and email evidence.
DOCSBOT_INTERNAL_SECTION = re.compile(
    r'<section\b[^>]*>\s*<h2\b[^>]*>Verified COSHUMA affiliate terms</h2>.*?</section>',
    re.I | re.S,
)
DOCSBOT_INTERNAL_NOTE = re.compile(
    r'<div\b[^>]*>Unique affiliate URL verified from DocsBot\'s partner welcome email to COSHUMA on September 1, 2026\.</div>',
    re.I | re.S,
)

BANNED_CUSTOMER_COPY = re.compile(
    r'verified partner route|verified partner path|verified partner offer|verified partner link|'
    r'Verified COSHUMA affiliate terms|unique referral URL|partner welcome email|'
    r'revenue CTA|verified CTA status|without treating clicks as revenue|'
    r'tracking cookie|first-party reporting verifies it|dashboard/login URL|'
    r'account-specific links already marked verified|partner dashboard confirms it|'
    r'exact verified PartnerStack customer link|authenticated ClickFunnels Affiliate Center',
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
    text = text.replace(
        "Test Unbounce through the verified partner route →",
        "Try Unbounce →",
    )
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
