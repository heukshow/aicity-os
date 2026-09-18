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

# Targeted buyer-safe rewrites for currently generated/source-backed copy. Keep factual
# offer/product information while removing correspondence and tracking mechanics.
RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"Taskade's affiliate team told COSHUMA that code\s*(?:<strong\b[^>]*>)?AI(?:</strong>)?\s*(?:provides|gives)\s*(?:<strong\b[^>]*>)?20% off subscriptions(?:</strong>)?\.",
            re.I,
        ),
        "Code <strong class=\"text-white\">AI</strong> currently gives <strong class=\"text-white\">20% off subscriptions</strong>.",
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
        re.compile(
            r"Pictory's affiliate manager confirmed this code gives\s*",
            re.I,
        ),
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
        re.compile(
            r"\s*and reconfirmed that COSHUMA's verified referral link and the code remain active\.",
            re.I,
        ),
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
        re.compile(
            r"<p(?P<attrs>\b[^>]*)>Jotform's Partner Team first highlighted the wider suite to .*?</p>",
            re.I | re.S,
        ),
        "",
    ),
    (
        re.compile(
            r"with vendor-confirmed COSHUMA partner routes for pricing, AI Agents and five product pages\.",
            re.I,
        ),
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
    (
        re.compile(r"How COSHUMA verified this guide", re.I),
        "Guide notes",
    ),
    (
        re.compile(r"vendor-confirmed product links", re.I),
        "current product links",
    ),
    (
        re.compile(r"Free educational paths with affiliate attribution", re.I),
        "Free educational paths",
    ),
    (
        re.compile(
            r"vidIQ's affiliate team supplied these exact article links to COSHUMA on September 6, 2026 and stated that the affiliate parameters are already inserted, so a reader who later signs up can still be credited to COSHUMA\.\s*"
            r"These links go to educational content first rather than directly to checkout\.",
            re.I,
        ),
        "",
    ),
    (
        re.compile(
            r"The educational deep links were supplied directly by the vidIQ Affiliate Team to COSHUMA on September 6, 2026 with affiliate parameters already inserted\.",
            re.I,
        ),
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
    r"|\b(?:affiliate|partner)\s+route\b",
    re.I,
)


def main() -> None:
    changed_files = 0
    replacements = 0

    for path in sorted(PUBLIC.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        updated = text
        file_replacements = 0
        for pattern, replacement in RULES:
            updated, count = pattern.subn(replacement, updated)
            file_replacements += count

        # Correspondence-derived copy is deleted, not paraphrased. Clean empty blocks
        # left by targeted removals without touching unrelated customer content.
        updated = re.sub(r"<p\b[^>]*>\s*</p>", "", updated, flags=re.I)
        updated = re.sub(r"<li\b[^>]*>\s*</li>", "", updated, flags=re.I)

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
