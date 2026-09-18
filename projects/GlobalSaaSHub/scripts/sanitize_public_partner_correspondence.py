"""Remove partner-correspondence and tracking-verification mechanics from public HTML.

Internal evidence stays in data/ops files. Customer pages must not republish, paraphrase,
or reframe facts whose only stated basis is private partner correspondence. Any sentence
or block that cites who emailed COSHUMA, what an affiliate/partner manager said, or email/
message evidence is removed from public output rather than rewritten as customer copy.
Independent facts may appear only through separate public/product-source content. This
pass runs after content injectors and before the public-source fail-closed guard.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

# Targeted removals/strips for currently generated public copy. Private correspondence
# is never converted into a customer-facing factual claim. Only mechanical/internal
# qualifiers may be stripped when the surrounding public CTA remains independently valid.
RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"Taskade's affiliate team told COSHUMA that code\s*(?:<strong\b[^>]*>)?AI(?:</strong>)?\s*(?:provides|gives)\s*(?:<strong\b[^>]*>)?20% off subscriptions(?:</strong>)?\.",
            re.I,
        ),
        "",
    ),
    (
        re.compile(
            r"The (?:message|email) does not explicitly (?:confirm|state) a lifetime duration for (?:the|this shared) AI code",
            re.I,
        ),
        "",
    ),
    (
        re.compile(
            r"the 20% code and combined-savings guidance come from Pictory's affiliate-manager messages to COSHUMA\.\s*"
            r"On September 7, 2026, the affiliate manager separately reconfirmed that COSHUMA's existing affiliate link and COSHUMA20 remain active and that the affiliate link should remain the primary tracking method\.",
            re.I,
        ),
        "",
    ),
    (
        re.compile(
            r"Pictory's affiliate manager separately confirmed to COSHUMA that the verified referral URL and COSHUMA20 remain active and that COSHUMA20 gives 20% off, subject to current checkout eligibility\.",
            re.I,
        ),
        "",
    ),
    (
        re.compile(r"Pictory's affiliate manager confirmed this code gives\s*", re.I),
        "",
    ),
    (
        re.compile(
            r"COSHUMA's affiliate manager confirmed the offers can combine for savings above 52%, subject to checkout eligibility\.",
            re.I,
        ),
        "",
    ),
    (
        re.compile(r"\s*and reconfirmed that COSHUMA's verified referral link and the code remain active\.", re.I),
        ".",
    ),
    (
        re.compile(
            r"Its affiliate manager separately reconfirmed to COSHUMA that the existing affiliate link and promo code\s*"
            r"(<strong\b[^>]*>COSHUMA20</strong>)\s*remain active\.",
            re.I,
        ),
        "",
    ),
    (
        re.compile(
            r"Jotform's Affiliate Team highlighted the wider suite to COSHUMA and has now directly confirmed tracked COSHUMA routes for Sign, Apps, Workflows, Tables and Report Builder in addition to previously verified pricing and AI Agents links\.",
            re.I,
        ),
        "",
    ),
    (
        re.compile(r"<p(?P<attrs>\b[^>]*)>Jotform's Partner Team first highlighted the wider suite to .*?</p>", re.I | re.S),
        "",
    ),
    (
        re.compile(r"with vendor-confirmed COSHUMA partner routes for pricing, AI Agents and five product pages\.", re.I),
        "with current product links for pricing, AI Agents and key product pages.",
    ),
    (
        re.compile(r"using only vendor-confirmed monetized routes\.", re.I),
        "with current product and pricing links.",
    ),
    (
        re.compile(r"Open verified ([^<\n]+?) partner route →", re.I),
        r"Open current \1 offer →",
    ),
    (
        re.compile(r"Official Boards page\s*[—-]\s*tracking unconfirmed\s*→", re.I),
        "Official Boards page →",
    ),
    (
        re.compile(r"Use the vendor-confirmed pricing route to check current limits and billing before upgrading\.", re.I),
        "Use the current pricing page to check current limits and billing before upgrading.",
    ),
    (re.compile(r"How COSHUMA verified this guide", re.I), ""),
    (re.compile(r"vendor-confirmed product links", re.I), "current product links"),
    (re.compile(r"Free educational paths with affiliate attribution", re.I), "Free educational paths"),
    (
        re.compile(
            r"vidIQ's affiliate team supplied these exact article links to COSHUMA on September 6, 2026 and stated that the affiliate parameters are already inserted, so a reader who later signs up can still be credited to COSHUMA\.\s*"
            r"These links go to educational content first rather than directly to checkout\.",
            re.I,
        ),
        "",
    ),
    (
        re.compile(r"The educational deep links were supplied directly by the vidIQ Affiliate Team to COSHUMA on September 6, 2026 with affiliate parameters already inserted\.", re.I),
        "",
    ),
    (
        re.compile(
            r"Pictory official pricing page, COSHUMA's verified affiliate records, and Pictory affiliate-manager email evidence\.\s*No signup, sale, commission or revenue is inferred from publication or link verification\.",
            re.I,
        ),
        "",
    ),
)

# Broad customer-surface normalization. These replacements remove internal routing and
# verification vocabulary while preserving the actual href and sponsored attribution.
MECHANICAL_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bverified\s+COSHUMA\s+affiliate\s+route\b", re.I), "current offer link"),
    (re.compile(r"\bverified\s+affiliate\s+route\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+affiliate\s+link\b", re.I), "current offer link"),
    (re.compile(r"\bverified\s+referral\s+URL\b", re.I), "current offer link"),
    (re.compile(r"\bverified\s+partner\s+URL\b", re.I), "current offer link"),
    (re.compile(r"\bverified\s+partner\s+route\b", re.I), "current offer link"),
    (re.compile(r"\bvendor-confirmed\s+pricing\s+route\b", re.I), "current pricing page"),
    (re.compile(r"\bvendor-confirmed\s+COSHUMA\s+affiliate\s+deep\s+link\b", re.I), "current pricing link"),
    (re.compile(r"\b(?:COSHUMA(?:'s)?\s+)?partner\s+route\b", re.I), "offer link"),
    (re.compile(r"\b(?:COSHUMA(?:'s)?\s+)?affiliate\s+route\b", re.I), "offer link"),
    (re.compile(r"\bprimary\s+tracking\s+route\b", re.I), "offer link"),
    (re.compile(r"\baffiliate\s+tracking\s+verified\s+September\s+16,\s+2026\b", re.I), ""),
    (re.compile(r"\bvia\s+(?:a\s+)?current\s+offer\s+link\b", re.I), ""),
    (re.compile(r"\bvia\s+current\s+offer\b", re.I), ""),
    (re.compile(r"\bvia\s+the\s+current\s+offer\s+link\b", re.I), ""),
    (re.compile(r"\bStart\s+([^<\n]{1,80}?)\s+via\s+current\s+offer\s+link\s*→", re.I), r"Start \1 →"),
    (re.compile(r"\bTry\s+([^<\n]{1,80}?)\s+via\s+current\s+offer\s+link\s*→", re.I), r"Try \1 →"),
    (re.compile(r"\bCheck\s+([^<\n]{1,80}?)\s+via\s+current\s+offer\s+link\s*→", re.I), r"Check \1 →"),
    (re.compile(r"\bOpen\s+([^<\n]{1,80}?)\s+offer\s+link\s*→", re.I), r"Open \1 →"),
    (re.compile(r"\bUse\s+the\s+offer\s+link\b", re.I), "Open the current offer"),
    (re.compile(r"\bPartner\s+code:\b", re.I), "Promo code:"),
    (re.compile(r"\bNon-affiliate\s+route\.?", re.I), "Official product link."),
    (re.compile(r"\bNo\s+(?:Typeform|Stripo)\s+revenue\s+attribution\s+is\s+claimed\s+by\s+COSHUMA\.?", re.I), ""),
    (re.compile(r"\bCOSHUMA\s+does\s+not\s+claim\s+(?:Stripo|Typeform)\s+attribution\s+from\s+this\s+link\.?", re.I), ""),
    (re.compile(r"\bCOSHUMA\s+is\s+not\s+presenting\s+the\s+Landingi\s+button\s+below\s+as\s+an\s+offer\s+link\.?", re.I), ""),
    (re.compile(r"\bCOSHUMA\s+is\s+not\s+treating\s+a\s+HubSpot\s+offer\s+link\s+as\s+verified\s+on\s+this\s+comparison\.?", re.I), "This comparison links to HubSpot's official pricing page."),
    (re.compile(r"\bthrough\s+COSHUMA(?:'s)?\s+current\s+offer\s+link\b", re.I), ""),
)

# Blocks that exist only to explain private routing/evidence are removed completely.
PRIVATE_BLOCKS: tuple[re.Pattern[str], ...] = (
    re.compile(r"<p\b[^>]*>\s*This is the exact GetGenie Pricing-page affiliate route provided directly to COSHUMA\..*?</p>", re.I | re.S),
    re.compile(r"<p\b[^>]*>\s*COSHUMA has an exact, account-specific Moosend.*?</p>", re.I | re.S),
    re.compile(r"<li\b[^>]*>\s*[•·-]?\s*COSHUMA partner route:.*?</li>", re.I | re.S),
    re.compile(r"<li\b[^>]*>\s*COSHUMA already has an exact vendor-issued Unbounce customer partner route\.?\s*</li>", re.I | re.S),
    re.compile(r"<p\b[^>]*>\s*Castmagic's referral URL was separately verified from its FirstPromoter welcome email;.*?</p>", re.I | re.S),
    re.compile(r"<div\b[^>]*>\s*Murf buttons marked as partner links use COSHUMA's verified referral URL\.?\s*</div>", re.I | re.S),
    re.compile(r"<p\b[^>]*>\s*Verified partner URL:.*?</p>", re.I | re.S),
    re.compile(r"<p\b[^>]*>\s*COSHUMA's HighLevel button uses a verified partner URL\..*?</p>", re.I | re.S),
    re.compile(r"<p\b[^>]*>\s*If you decide to use Inkfluence AI, the verified affiliate link below can earn COSHUMA a commission at no extra cost to you\.?\s*</p>", re.I | re.S),
)

CORRESPONDENCE = re.compile(
    r"\b(?:affiliate|partner)[- ]?(?:team|manager)\b[^\n<>]{0,180}\b(?:message|email|reply|told|confirmed|reconfirmed|supplied|highlighted|evidence)\b"
    r"|\b(?:message|email|reply)\b[^\n<>]{0,180}\b(?:affiliate|partner)[- ]?(?:team|manager)\b"
    r"|\b(?:affiliate|partner)[- ]?(?:manager|team)\b[^\n<>]{0,180}\bCOSHUMA\b"
    r"|\bCOSHUMA(?:'s)?\b[^\n<>]{0,120}\b(?:affiliate|partner)[- ]?(?:manager|team)\b",
    re.I,
)

PUBLIC_MECHANICS = re.compile(
    r"\bvendor[- ]confirmed\b"
    r"|\btracking\s+(?:unconfirmed|confirmed|verified|unknown)\b"
    r"|\bHow\s+COSHUMA\s+verified\b"
    r"|\bverified\s+(?:affiliate|partner|referral|tracking)\s+(?:link|route|URL|destination)\b"
    r"|\b(?:affiliate|partner)\s+route\b"
    r"|\baccount-specific\b[^\n<>]{0,100}\b(?:tracking|tracked|affiliate|referral)\b"
    r"|\brevenue\s+attribution\b"
    r"|\baffiliate\s+tracking\b",
    re.I,
)


def main() -> None:
    changed_files = 0
    replacements = 0

    for path in sorted(PUBLIC.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        updated = text
        file_replacements = 0
        for pattern, replacement in RULES + MECHANICAL_RULES:
            updated, count = pattern.subn(replacement, updated)
            file_replacements += count
        for pattern in PRIVATE_BLOCKS:
            updated, count = pattern.subn("", updated)
            file_replacements += count

        # Correspondence-derived copy is deleted, not paraphrased. Clean empty blocks
        # left by targeted removals without touching unrelated customer content.
        updated = re.sub(r"<p\b[^>]*>\s*</p>", "", updated, flags=re.I)
        updated = re.sub(r"<li\b[^>]*>\s*</li>", "", updated, flags=re.I)
        updated = re.sub(r"\s+([.;,:])", r"\1", updated)

        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
            replacements += file_replacements

    remaining: list[str] = []
    for path in sorted(PUBLIC.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        for label, pattern in (("correspondence", CORRESPONDENCE), ("tracking-verification", PUBLIC_MECHANICS)):
            match = pattern.search(text)
            if match:
                snippet = re.sub(r"\s+", " ", text[max(0, match.start()-80):match.end()+100]).strip()
                remaining.append(f"{path.relative_to(PUBLIC).as_posix()}: {label}: {snippet[:280]}")

    if remaining:
        print("ERROR: partner correspondence or tracking-verification mechanics remain in customer-facing public HTML.")
        for item in remaining[:50]:
            print(f" - {item}")
        raise SystemExit(1)

    print(
        f"PASS: public partner/tracking sanitizer changed={changed_files} "
        f"replacements={replacements} remaining=0"
    )


if __name__ == "__main__":
    main()
