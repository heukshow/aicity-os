"""Keep the public offers hub buyer-facing without changing tracked destinations.

The page is assembled by several older offer-surfacing scripts. Some of those
scripts still emit partner-network, dashboard, attribution and commission
language that is useful internally but not for shoppers. This final pass runs
after those generators and again against ``dist`` so the customer page keeps
pricing/trial/offer facts and the existing outbound URLs while stripping the
internal mechanics.
"""
from __future__ import annotations

from html import unescape
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET_ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "public"
if not TARGET_ROOT.is_absolute():
    TARGET_ROOT = ROOT / TARGET_ROOT
PAGE = TARGET_ROOT / "best" / "verified-software-free-trials-deals.html"

if not PAGE.exists():
    raise SystemExit(f"offers hub not found: {PAGE}")

text = PAGE.read_text(encoding="utf-8")

# Normalize the collection itself around buyer decisions, not affiliate ops.
REPLACEMENTS = {
    "Verified SaaS Free Trials & Partner Offers (2026) | COSHUMA": "SaaS Free Trials & Current Offers (2026) | COSHUMA",
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, UpLead, Jotform, Unbounce, Pictory, Brand24 and Bookyourdata. COSHUMA separates customer-facing tracking links from product claims.": "Compare SaaS free trials, pricing and current offers across popular software tools before you pay. Check current terms, trial lengths and plan details.",
    "Low-risk software tests and verified COSHUMA partner paths, checked against current vendor information before you subscribe.": "Compare low-risk software trials, pricing and current offers before you subscribe.",
    "Verified SaaS Free Trials & Partner Offers": "SaaS Free Trials & Current Offers",
    "Software free trials and partner offers worth testing before you pay": "Software free trials and current offers worth testing before you pay",
    "This page prioritizes low-risk first steps and customer-facing routes COSHUMA has actually verified. A dashboard, onboarding page or generic homepage is never treated as an affiliate link unless the program issued or confirmed it for customer referrals.": "Compare low-risk ways to try each product before paying. Use the vendor links below to start a trial, check pricing or review the current offer details.",
    "No invented discounts": "Current offer terms",
    "Verified customer links": "Direct vendor links",
    "New low-risk routes surfaced September 11": "Updated September 11",
    "Gamma and Time2book now have dedicated buyer guides and verified COSHUMA referral routes. Their free entry points are exposed here so visitors do not need to discover them only through individual tool pages.": "Gamma and Time2book both offer low-risk ways to test the product before paying. Use the options below to start free and compare the available plans.",
    "The first button uses the exact customer-facing Time2book referral route previously verified for COSHUMA.": "",
    "Direct partner confirmation · September 11": "Trial and pricing options · September 11",
    "Exact partner-issued buyer routes": "Compare before you pay",
    "UpLead and Jotform supplied exact customer-facing destinations in partner correspondence. COSHUMA uses those URLs as provided rather than guessing referral parameters.": "Use the options below to start a trial, compare pricing and review each product before choosing a paid plan.",
    "7-day trial route": "7-day trial",
    "Exact pricing route": "Plan comparison",
    "UpLead confirmed COSHUMA's exact tracked 7-day trial destination and a separate tracked pricing destination for the existing affiliate account.": "UpLead currently offers a 7-day trial and a separate pricing page. Use the options below to test the product and compare plans.",
    "Jotform's affiliate team supplied the exact COSHUMA pricing-page affiliate URL below. COSHUMA does not append that partner tag to other Jotform pages without verification.": "Use the pricing link below to compare Jotform plans, or read the COSHUMA guide for features and fit.",
    "Try Pictory via verified link →": "Start Pictory trial →",
    "15-day trial · verified referral": "15-day trial",
    "Open RGE Studio via verified referral →": "Start RGE Studio trial →",
    "Open BoldSign via verified referral →": "Start BoldSign 30-day trial →",
    "Vendor-issued 30-day trial": "30-day trial offer",
    "Teachable's current official affiliate program states 30% recurring commission for the first year on eligible referred subscriptions and a 30-day cookie window. Confirm the 30-day trial wording shown at the destination before completing signup because vendor offers can change.": "The offer linked here is currently described as a 30-day trial. Confirm the trial length and billing terms shown at the destination before completing signup because vendor offers can change.",
    "Open verified Teachable 30-day trial →": "Start Teachable 30-day trial →",
    "Open Krater via COSHUMA →": "Open Krater →",
    "Open Chatbase via verified route →": "Open Chatbase →",
    "Try Gojiberry via verified route →": "Try Gojiberry →",
    "Explore Taskip via COSHUMA →": "Explore Taskip →",
    "Check Omi via verified referral →": "Check Omi →",
    "Verified referral destination: exact Omi customer route issued to COSHUMA.": "",
    "2. Customer-facing route": "2. Buyer fit",
    "The affiliate URL must be specifically issued or otherwise verified as a referral path. Admin and dashboard URLs are excluded.": "Prioritize low-risk ways to test each product before choosing a paid plan.",
    "3. Revenue is separate": "3. Current terms",
    "A valid link is not proof of a signup, sale or commission. COSHUMA reports revenue only when a partner system confirms it.": "Vendor checkout, pricing pages and trial terms control the final price, eligibility and billing conditions.",
}
for old, new in REPLACEMENTS.items():
    text = text.replace(old, new)

# Keep useful buyer facts when an old paragraph combines them with partner ops.
SENTENCE_PATTERNS = (
    # RGE Studio: keep live pricing/trial, remove partner-team commentary.
    r"\s*Beefree's partner team separately highlighted real-time co-editing, commenting/review, brand controls, connectors/HTML export and its AI Assistant as conversion points\.",
    # BoldSign: keep the vendor's 30-day/no-card trial statement.
    r"\s*Its affiliate program currently states 30% commission for the first 12 months on eligible paid referrals, a 90-day cookie window, and no minimum payout threshold\.",
    # Writesonic: the trial statement is buyer-useful; the source label is not.
    r"Writesonic's current first-party affiliate page says",
    # Gojiberry: keep free-trial/cancel-anytime sentence.
    r"\s*Public affiliate terms currently state a 30% recurring commission structure and 30-day cookie; those program terms do not prove a COSHUMA conversion\.",
    # AWeber: keep the automatic-billing warning.
    r"\s*Its Advocate documentation currently describes a 90-day referral cookie and 30%-50% recurring commission tiers for paid referrals; those are program terms, not proof of COSHUMA revenue\.",
    # Taskip: keep the product summary before this sentence.
    r"\s*COSHUMA uses only the exact customer-facing affiliate URL previously issued by the authenticated Taskip partner account\.",
    # Omi: keep public device/subscription facts.
    r"\s*COSHUMA keeps the exact dashboard-issued referral route separate from those product claims\.",
)
for pattern in SENTENCE_PATTERNS:
    if pattern == r"Writesonic's current first-party affiliate page says":
        text = re.sub(pattern, "Writesonic currently says", text, flags=re.I)
    else:
        text = re.sub(pattern, "", text, flags=re.I)

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.I | re.S)

def visible(fragment: str) -> str:
    fragment = SCRIPT_STYLE_RE.sub(" ", fragment)
    return re.sub(r"\s+", " ", unescape(TAG_RE.sub(" ", fragment))).strip()

# Paragraphs/small notes containing monetization mechanics are internal. Removing
# the whole block is safer than leaving a half-sanitized sentence. Product,
# pricing and trial paragraphs are left alone unless they contain these markers.
INTERNAL_MARKERS = (
    "partnerstack",
    "firstpromoter",
    "authenticated ",
    "affiliate dashboard",
    "affiliate account",
    "affiliate portal",
    "affiliate program",
    "affiliate page",
    "affiliate terms",
    "commission",
    "cookie window",
    "referral cookie",
    "approved tracking",
    "approved-tracking",
    "partner account",
    "partner team",
    "partner system",
    "issued to coshuma",
    "confirmed to coshuma",
    "supplied to coshuma",
    "support supplied",
    "support directly confirmed",
    "customer-facing referral url",
    "customer referral route",
    "account-specific customer referral",
    "account referral route",
    "customer campaign url",
    "impact route",
    "lemon squeezy",
    "dub partner",
    "affonso referral",
    "link validation",
    "earned revenue",
    "proof coshuma has earned",
    "proof that coshuma has earned",
)

def internal_block(match: re.Match[str]) -> str:
    body = visible(match.group(0)).lower()
    if any(marker in body for marker in INTERNAL_MARKERS):
        return ""
    # Internal stage accounting is also not buyer copy.
    if "coshuma" in body and any(word in body for word in ("signup", "paid customer", "payout", "revenue")):
        return ""
    return match.group(0)

for tag in ("p", "small"):
    pattern = re.compile(rf"<{tag}\b[^>]*>.*?</{tag}>", re.I | re.S)
    text = pattern.sub(internal_block, text)

# Remove affiliate/partner-program verification links from the customer guide;
# product/pricing/trial links and tracked conversion CTAs stay untouched.
ANCHOR_RE = re.compile(r"<a\b[^>]*>.*?</a>", re.I | re.S)
def clean_anchor(match: re.Match[str]) -> str:
    label = visible(match.group(0)).lower()
    if label.startswith("verify ") and ("affiliate" in label or "partner terms" in label or "commission" in label):
        return ""
    return match.group(0)
text = ANCHOR_RE.sub(clean_anchor, text)

# Remove a leftover Omi list item if a generator wraps it in markup instead of
# plain text; keep the public price/plan bullets.
LI_RE = re.compile(r"<li\b[^>]*>.*?</li>", re.I | re.S)
def clean_li(match: re.Match[str]) -> str:
    body = visible(match.group(0)).lower()
    if "verified referral destination" in body or ("coshuma" in body and "referral" in body):
        return ""
    return match.group(0)
text = LI_RE.sub(clean_li, text)

# Final visible-text guard. URLs, rel=sponsored and data-cta attributes are not
# part of this check and therefore remain byte-for-byte intact.
check = visible(text).lower()
FORBIDDEN = (
    "partnerstack",
    "firstpromoter",
    "authenticated affiliate",
    "affiliate dashboard",
    "affiliate account",
    "affiliate portal",
    "affiliate program",
    "affiliate terms",
    "commission",
    "approved tracking",
    "approved-tracking",
    "partner account",
    "impact route",
    "lemon squeezy",
    "dub partner",
    "affonso referral",
    "link validation",
    "verified referral",
    "via coshuma",
    "revenue is separate",
    "partner system confirms",
)
leaks = [needle for needle in FORBIDDEN if needle in check]
if leaks:
    raise SystemExit("offers hub still exposes internal affiliate/ops copy: " + ", ".join(leaks))

PAGE.write_text(text, encoding="utf-8")
print(f"cleaned customer-facing offers hub: {PAGE}")
