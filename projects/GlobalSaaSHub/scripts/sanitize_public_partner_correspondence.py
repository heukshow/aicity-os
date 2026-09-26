"""Keep customer-facing HTML free of private affiliate operations.

Internal evidence, account state and partner correspondence stay in internal data/ops
files. Public pages may keep real outbound hrefs and sponsored attribution, but must not
explain which network/account issued a route, how it was verified, or whether an internal
tracking/application state is confirmed. Private-correspondence-derived copy is deleted,
not rewritten as a customer claim.
"""
from __future__ import annotations

from html import unescape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

TAG = re.compile(r"<[^>]+>")
URL = re.compile(r"https?://[^\s\"'<>]+", re.I)

# Operational provenance that is never customer product information. This intentionally
# covers wording variants produced by older content generators, while URLs themselves are
# left intact and are masked before the final boundary check.
PRIVATE_BLOCK_TEXT = re.compile(
    r"\b(?:affiliate|partner)[- ]?(?:team|manager)\b"
    r"|\b(?:PartnerStack|FirstPromoter)\b"
    r"|\bauthenticated\s+partner\s+account\b"
    r"|\b(?:affiliate|partner)\s+(?:approval|welcome)\s+email\b"
    r"|\bvendor\s+welcome\s+email\b"
    r"|\baffiliate\s+state\b"
    r"|\bpartner\s+dashboard\b"
    r"|\bCOSHUMA\s+tracking\b"
    r"|\b(?:referral|tracking)\s+URL\s+not\s+yet\s+verified\b"
    r"|\bverified\s+customer\s+partner\s+URL\b"
    r"|\baccount-specific\b[^.\n]{0,180}\b(?:affiliate|partner|referral|tracking|tracked|route|link)\b"
    r"|\b(?:affiliate|partner|referral|tracking|tracked|route|link)\b[^.\n]{0,180}\baccount-specific\b"
    r"|\bCOSHUMA(?:'s)?\b[^.\n]{0,220}\b(?:affiliate|partner|referral|tracking)\b[^.\n]{0,160}\b(?:verified|evidence|account|email|message|supplied|issued)\b"
    r"|\bCOSHUMA(?:'s)?\b[^.\n]{0,220}\b(?:verified|evidence|account|email|message|supplied|issued)\b[^.\n]{0,160}\b(?:affiliate|partner|referral|tracking)\b"
    r"|\bnon-affiliate\b[^.\n]{0,180}\bCOSHUMA\b"
    r"|\bexact\s+vendor-issued\b[^.\n]{0,140}\b(?:affiliate|partner|referral|tracking)\b"
    r"|\bnot\s+label\s+a\s+customer\s+link\s+as\s+affiliate\s+tracking\b"
    r"|\bno\s+verified\b[^.\n]{0,140}\b(?:affiliate|referral|tracking|tracked)\b",
    re.I,
)

# Product copy can keep a real offer, trial or discount. Only the explanation of internal
# routing/verification is normalized away.
MECHANICAL_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bvendor[- ]confirmed\b", re.I), "current"),
    (re.compile(r"\bverified\s+COSHUMA\s+affiliate\s+route\b", re.I), "current offer link"),
    (re.compile(r"\bverified\s+affiliate\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+affiliate\s+link\b", re.I), "current offer link"),
    (re.compile(r"\bverified\s+referral\s+URL\b", re.I), "current offer link"),
    (re.compile(r"\bverified\s+partner\s+URL\b", re.I), "current offer link"),
    (re.compile(r"\bverified\s+partner\s+route\b", re.I), "current offer link"),
    (re.compile(r"\b(?:COSHUMA(?:'s)?\s+)?partner\s+route\b", re.I), "offer link"),
    (re.compile(r"\b(?:COSHUMA(?:'s)?\s+)?affiliate\s+route\b", re.I), "offer link"),
    (re.compile(r"\bprimary\s+tracking\s+route\b", re.I), "offer link"),
    (re.compile(r"\btracking\s+unconfirmed\b", re.I), ""),
    (re.compile(r"\baffiliate\s+tracking\s+verified\s+September\s+16,\s+2026\b", re.I), ""),
    (re.compile(r"\bHow\s+COSHUMA\s+verified\s+this\s+guide\b", re.I), ""),
    (re.compile(r"\bFree educational paths with affiliate attribution\b", re.I), "Free educational paths"),
    (re.compile(r"\bPartner\s+code:\b", re.I), "Promo code:"),
    (re.compile(r"\bNon-affiliate\s+route\.?", re.I), "Official product link."),
    (re.compile(r"\bvia\s+(?:a|the)\s+current\s+offer\s+link\b", re.I), ""),
    (re.compile(r"\bvia\s+current\s+offer(?:\s+link)?\b", re.I), ""),
    (re.compile(r"\bStart\s+([^<\n]{1,80}?)\s+via\s+current\s+offer\s+link\s*→", re.I), r"Start \1 →"),
    (re.compile(r"\bTry\s+([^<\n]{1,80}?)\s+via\s+current\s+offer\s+link\s*→", re.I), r"Try \1 →"),
    (re.compile(r"\bCheck\s+([^<\n]{1,80}?)\s+via\s+current\s+offer\s+link\s*→", re.I), r"Check \1 →"),
    (re.compile(r"\bOpen\s+([^<\n]{1,80}?)\s+offer\s+link\s*→", re.I), r"Open \1 →"),
    (re.compile(r"\bUse\s+the\s+offer\s+link\b", re.I), "Open the current offer"),
    (re.compile(r"\bNo\s+(?:Typeform|Stripo)\s+revenue\s+attribution\s+is\s+claimed\s+by\s+COSHUMA\.?", re.I), ""),
    (re.compile(r"\bCOSHUMA\s+does\s+not\s+claim\s+(?:Stripo|Typeform)\s+attribution\s+from\s+this\s+link\.?", re.I), ""),
    (re.compile(r"\bCOSHUMA\s+is\s+not\s+presenting\s+the\s+Landingi\s+button\s+below\s+as\s+an\s+offer\s+link\.?", re.I), ""),
    (re.compile(r"\bthrough\s+COSHUMA(?:'s)?\s+current\s+offer\s+link\b", re.I), ""),
    # Preserve the commercial offer while deleting the network mechanics.
    (re.compile(r"\busing\s+COSHUMA(?:'s)?\s+[^.<>]{0,80}?\s+PartnerStack\s+route\b", re.I), ""),
)

# Remove private provenance anywhere it can be serialized (body text, meta descriptions or
# JSON-LD strings). The generic network rule explicitly refuses URL-adjacent network names
# so verified outbound hrefs remain byte-for-byte intact.
PRIVATE_SENTENCES: tuple[re.Pattern[str], ...] = (
    re.compile(r"Taskade's affiliate team told COSHUMA that code[^<\"\n]*?20% off subscriptions\.", re.I),
    re.compile(r"The (?:message|email) does not explicitly (?:confirm|state) a lifetime duration for (?:the|this shared) AI code\.?", re.I),
    re.compile(r"Pictory's affiliate manager[^<\"\n]*?(?:active|eligibility)\.", re.I),
    re.compile(r"the 20% code and combined-savings guidance come from Pictory's affiliate-manager messages to COSHUMA\.[^<\"\n]*?(?:active|method)\.", re.I),
    re.compile(r"COSHUMA's affiliate manager confirmed[^<\"\n]*?eligibility\.", re.I),
    re.compile(r"Jotform's (?:Affiliate|Partner) Team[^<\"\n]*?(?:links|Forms)\.", re.I),
    re.compile(r"vidIQ's affiliate team[^<\"\n]*?(?:checkout|COSHUMA)\.", re.I),
    re.compile(r"The educational deep links were supplied directly by the vidIQ Affiliate Team[^<\"\n]*?inserted\.", re.I),
    re.compile(r"Pictory official pricing page, COSHUMA's verified affiliate records, and Pictory affiliate-manager email evidence\.[^<\"\n]*?verification\.", re.I),
    re.compile(r"GetGenie support explicitly confirmed COSHUMA's account-specific pricing-page affiliate URL preserves attribution\.?", re.I),
    re.compile(r"COSHUMA's account-specific Shopify Affiliate email;?", re.I),
    re.compile(r"(?:the|an) exact?\s*account-specific Novita AI referral URL issued in the affiliate approval email", re.I),
    # Generic sentence-level cleanup for legacy generator variants. A sentence that exposes
    # a network/account/correspondence mechanism is removed rather than rephrased.
    re.compile(r"[^<>\"\n.!?]{0,260}(?<![A-Za-z0-9./:_-])(?:PartnerStack|FirstPromoter)\b[^<>\"\n.!?]{0,260}[.!?]", re.I),
    re.compile(r"[^<>\"\n.!?]{0,260}\b(?:affiliate|partner)[- ]?(?:team|manager)\b[^<>\"\n.!?]{0,260}[.!?]", re.I),
    re.compile(r"[^<>\"\n.!?]{0,260}\b(?:affiliate|partner)\s+(?:approval|welcome)\s+email\b[^<>\"\n.!?]{0,260}[.!?]", re.I),
    re.compile(r"[^<>\"\n.!?]{0,260}\bvendor\s+welcome\s+email\b[^<>\"\n.!?]{0,260}[.!?]", re.I),
    re.compile(r"[^<>\"\n.!?]{0,260}\bauthenticated\s+partner\s+account\b[^<>\"\n.!?]{0,260}[.!?]", re.I),
    re.compile(r"[^<>\"\n.!?]{0,260}\baccount-specific\b[^<>\"\n.!?]{0,180}\b(?:affiliate|partner|referral|tracking|tracked|route|link)\b[^<>\"\n.!?]{0,180}[.!?]", re.I),
    re.compile(r"[^<>\"\n.!?]{0,260}\baffiliate\s+state\b[^<>\"\n.!?]{0,260}[.!?]", re.I),
    re.compile(r"[^<>\"\n.!?]{0,260}\bnon-affiliate\b[^<>\"\n.!?]{0,180}\bCOSHUMA\b[^<>\"\n.!?]{0,180}[.!?]", re.I),
)

# Operational explanation blocks can be deleted wholesale. Product-feature phrases such as
# "revenue attribution" are intentionally NOT treated as leaks by themselves.
BLOCK = re.compile(r"<(tr|p|li|td|th|blockquote|figcaption|small)\b[^>]*>.*?</\1>", re.I | re.S)
CONSUMER_DISCLOSURE = re.compile(
    r'<p\b[^>]*\bdata-(?:affiliate-disclosure|site-affiliate-disclosure)\s*=\s*["\'][^"\']*["\'][^>]*>.*?</p>',
    re.I | re.S,
)

CORRESPONDENCE = re.compile(
    r"\b(?:affiliate|partner)[- ]?(?:team|manager)\b[^\n<>]{0,220}\b(?:message|email|reply|told|confirmed|reconfirmed|supplied|highlighted|evidence)\b"
    r"|\b(?:message|email|reply|welcome email)\b[^\n<>]{0,220}\b(?:affiliate|partner)[- ]?(?:team|manager|route|link)\b"
    r"|\b(?:PartnerStack|FirstPromoter)\b[^\n<>]{0,180}\b(?:affiliate|partner|referral|tracking|route|link|account)\b"
    r"|\b(?:affiliate|partner|referral|tracking|route|link|account)\b[^\n<>]{0,180}\b(?:PartnerStack|FirstPromoter)\b",
    re.I,
)

PUBLIC_MECHANICS = re.compile(
    r"\btracking\s+(?:unconfirmed|confirmed|verified|unknown)\b"
    r"|\bHow\s+COSHUMA\s+verified\b"
    r"|\bverified\s+(?:affiliate|partner|referral|tracking)\s+(?:link|route|URL|destination|evidence)\b"
    r"|\b(?:affiliate|partner)\s+route\b"
    r"|\bCOSHUMA\s+tracking\b"
    r"|\b(?:referral|tracking)\s+URL\s+not\s+yet\s+verified\b"
    r"|\bverified\s+customer\s+partner\s+URL\b"
    r"|\baccount-specific\b[^\n<>]{0,160}\b(?:tracking|tracked|affiliate|partner|referral|route|link)\b"
    r"|\b(?:tracking|tracked|affiliate|partner|referral|route|link)\b[^\n<>]{0,160}\baccount-specific\b"
    r"|\bauthenticated\s+partner\s+account\b"
    r"|\baffiliate\s+state\b"
    r"|\bCOSHUMA\b[^\n<>]{0,180}\brevenue\s+attribution\b"
    r"|\baffiliate\s+tracking\b",
    re.I,
)


def plain_text(fragment: str) -> str:
    return unescape(re.sub(r"\s+", " ", TAG.sub(" ", fragment))).strip()


def remove_private_blocks(text: str) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        visible = plain_text(match.group(0))
        if PRIVATE_BLOCK_TEXT.search(visible):
            count += 1
            return ""
        return match.group(0)

    return BLOCK.sub(repl, text), count


def main() -> None:
    changed_files = 0
    replacements = 0

    for path in sorted(PUBLIC.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        protected_disclosures: list[str] = []

        def protect_disclosure(match: re.Match[str]) -> str:
            protected_disclosures.append(match.group(0))
            return f'<x-coshuma-disclosure data-index="{len(protected_disclosures) - 1}"></x-coshuma-disclosure>'

        updated = CONSUMER_DISCLOSURE.sub(protect_disclosure, text)
        file_replacements = 0

        updated, removed = remove_private_blocks(updated)
        file_replacements += removed

        for pattern in PRIVATE_SENTENCES:
            updated, count = pattern.subn("", updated)
            file_replacements += count

        for pattern, replacement in MECHANICAL_RULES:
            updated, count = pattern.subn(replacement, updated)
            file_replacements += count

        # JSON-LD/meta cleanup for older one-off generators after private provenance removal.
        updated = re.sub(
            r"Yes\.\s*COSHUMA uses\s*(?:the exact\s*)?\s*\.??",
            "Open Novita AI from this page and confirm current terms at the destination.",
            updated,
            flags=re.I,
        )
        updated = re.sub(
            r"Sources checked:\s*Shopify official pricing and\s*;?\s*Privy official pricing\.",
            "Sources checked: Shopify and Privy official pricing.",
            updated,
            flags=re.I,
        )
        updated = re.sub(
            r"Sources checked:\s*Shopify official pricing and\s*;?\s*Reply\.io official pricing\.",
            "Sources checked: Shopify and Reply.io official pricing.",
            updated,
            flags=re.I,
        )

        # Remove orphan customer-surface structure left after private blocks/text are removed.
        updated = re.sub(r"<h[1-6]\b[^>]*>\s*Affiliate disclosure\s*</h[1-6]>", "", updated, flags=re.I)
        updated = re.sub(r"<h([1-6])\b[^>]*>\s*</h\1>", "", updated, flags=re.I)
        updated = re.sub(r"<p\b[^>]*>\s*</p>", "", updated, flags=re.I)
        updated = re.sub(r"<li\b[^>]*>\s*</li>", "", updated, flags=re.I)
        updated = re.sub(r"\s+([.;,:])", r"\1", updated)

        for index, disclosure in enumerate(protected_disclosures):
            placeholder = f'<x-coshuma-disclosure data-index="{index}"></x-coshuma-disclosure>'
            updated = updated.replace(placeholder, disclosure, 1)

        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
            replacements += file_replacements

    remaining: list[str] = []
    for path in sorted(PUBLIC.rglob("*.html")):
        text = URL.sub("https://PUBLIC-OUTBOUND-URL", path.read_text(encoding="utf-8"))
        for label, pattern in (("correspondence", CORRESPONDENCE), ("tracking-verification", PUBLIC_MECHANICS)):
            match = pattern.search(text)
            if match:
                snippet = re.sub(r"\s+", " ", text[max(0, match.start()-80):match.end()+100]).strip()
                remaining.append(f"{path.relative_to(PUBLIC).as_posix()}: {label}: {snippet[:280]}")

    if remaining:
        print("ERROR: private partner correspondence or tracking mechanics remain in customer-facing public HTML.")
        for item in remaining[:50]:
            print(f" - {item}")
        raise SystemExit(1)

    print(
        f"PASS: public partner/tracking sanitizer changed={changed_files} "
        f"replacements={replacements} remaining=0"
    )


if __name__ == "__main__":
    main()
