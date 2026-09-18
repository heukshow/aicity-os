"""One-time migration for legacy affiliate-operations copy in committed public HTML.

The normal production pipeline must fail closed before broad sanitizers. This script is
therefore intentionally *not* part of npm build. It exists only to migrate already
committed legacy customer source into the current private-by-default policy.

Rules:
- never rewrite outbound URLs or sponsored attribution;
- preserve consumer affiliate disclosures;
- remove internal application/account/network/verification provenance;
- neutralize legacy "verified partner/referral link" wording into buyer-facing copy.
"""
from __future__ import annotations

from html import unescape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
TAG_RE = re.compile(r"<[^>]+>")
BLOCK_RE = re.compile(
    r"<(p|li|small|blockquote|figcaption|td|th)\b[^>]*>.*?</\1>",
    re.I | re.S,
)
FAQ_RE = re.compile(
    r'\{"@type":"Question","name":"(?P<name>(?:[^"\\]|\\.)*)",'
    r'"acceptedAnswer":\{"@type":"Answer","text":"(?P<answer>(?:[^"\\]|\\.)*)"\}\}',
    re.I,
)

OPS_BLOCK = re.compile(
    r"\b(?:PartnerStack|FirstPromoter)\b"
    r"|\b(?:affiliate|partner)[- ]?(?:team|manager)\b"
    r"|\b(?:affiliate|partner|referral|tracking)\b[^.\n]{0,260}"
    r"\b(?:application|approval|submitted|pending|dashboard|portal|control panel|authenticated|"
    r"account-specific|verification|verified|evidence|issued|welcome email)\b"
    r"|\b(?:application|approval|submitted|pending|dashboard|portal|control panel|authenticated|"
    r"account-specific|verification|verified|evidence|issued|welcome email)\b[^.\n]{0,260}"
    r"\b(?:affiliate|partner|referral|tracking)\b"
    r"|\bCOSHUMA(?:'s)?\b[^.\n]{0,320}\b(?:affiliate|partner|referral|tracking)\b[^.\n]{0,220}"
    r"\b(?:application|approval|submitted|pending|dashboard|portal|control panel|authenticated|"
    r"account-specific|verification|verified|evidence|issued|not yet|has not)\b"
    r"|\b(?:affiliate|partner|referral|tracking)\b[^.\n]{0,220}"
    r"\b(?:application|approval|submitted|pending|dashboard|portal|control panel|authenticated|"
    r"account-specific|verification|verified|evidence|issued|not yet|has not)\b[^.\n]{0,320}\bCOSHUMA\b",
    re.I,
)

FAQ_OPS = re.compile(
    r"\bCOSHUMA\b.*\b(?:affiliate|partner|referral|tracking|application|dashboard|portal)\b"
    r"|\b(?:affiliate|partner|referral|tracking|application|dashboard|portal)\b.*\bCOSHUMA\b",
    re.I,
)

NON_URL_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\bverified\s+(?:customer-facing\s+)?(?:COSHUMA\s+)?"
            r"(?:affiliate|partner|referral|tracking)\s+"
            r"(?:links?|routes?|URLs?|destinations?|offers?|paths?)\b",
            re.I,
        ),
        "current offer link",
    ),
    (
        re.compile(
            r"\bverified\s+(?:affiliate|partner|referral|tracking)\b",
            re.I,
        ),
        "current offer",
    ),
    (
        re.compile(r"\bcustomer-facing\s+(?:tracking|referral|partner)\s+(?:URL|route|link)\b", re.I),
        "current offer link",
    ),
    (re.compile(r"\baffiliate[ _-]?status\b", re.I), "offer availability"),
    (re.compile(r"\btracking\s+status\b", re.I), "offer availability"),
    (
        re.compile(r"\b(?:affiliate|partner|referral|commission)\s+(?:dashboard|portal)\b", re.I),
        "offer page",
    ),
    (
        re.compile(
            r"\b(?:customer-facing\s+)?affiliate\s+URL\s+through\s+the\s+approved\s+Kittl\s+Impact\s+account\b",
            re.I,
        ),
        "current offer link",
    ),
    (re.compile(r"\bverified\s+link\b", re.I), "current offer link"),
    (re.compile(r"\b(?:affiliate|partner)\s+route\b", re.I), "offer link"),
    (re.compile(r"\baffiliate\s+tracking\b", re.I), "offer link"),
    (re.compile(r"\brevenue[-_ ]?truth\b", re.I), "source-check"),
    (
        re.compile(r"\bofficial\s+or\s+verified\s+partner\s+destination\b", re.I),
        "official product or current offer destination",
    ),
    # Unique network names are operational provenance outside URLs. URL hosts and
    # parameters are split out before this function runs and remain byte-for-byte intact.
    (re.compile(r"\bPartnerStack\b", re.I), "the provider"),
    (re.compile(r"\bFirstPromoter\b", re.I), "the provider"),
)


def plain(fragment: str) -> str:
    return re.sub(r"\s+", " ", unescape(TAG_RE.sub(" ", fragment))).strip()


def neutralize_non_url(text: str) -> str:
    for pattern, replacement in NON_URL_RULES:
        text = pattern.sub(replacement, text)
    return text


def preserving_urls(text: str) -> str:
    parts: list[str] = []
    pos = 0
    for match in URL_RE.finditer(text):
        parts.append(neutralize_non_url(text[pos:match.start()]))
        parts.append(match.group(0))
        pos = match.end()
    parts.append(neutralize_non_url(text[pos:]))
    return "".join(parts)


def remove_internal_blocks(text: str) -> tuple[str, int]:
    removed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal removed
        visible = plain(match.group(0))
        if OPS_BLOCK.search(visible):
            # Consumer disclosure must survive this migration. It states the economic
            # relationship without exposing account/network/application mechanics.
            if re.search(r"affiliate\s+disclosure\s*:", visible, re.I):
                return match.group(0)
            removed += 1
            return ""
        return match.group(0)

    return BLOCK_RE.sub(repl, text), removed


def neutralize_internal_faq(text: str) -> tuple[str, int]:
    changed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        combined = f"{match.group('name')} {match.group('answer')}"
        if not FAQ_OPS.search(combined):
            return match.group(0)
        changed += 1
        return (
            '{"@type":"Question","name":"Where should I confirm the current terms?",'
            '"acceptedAnswer":{"@type":"Answer","text":"Use the vendor link on this page '
            'and confirm current pricing, offers and eligibility at the destination."}}'
        )

    return FAQ_RE.sub(repl, text), changed


def main() -> None:
    changed_files = 0
    removed_blocks = 0
    faq_rewrites = 0

    for path in sorted(PUBLIC.rglob("*.html")):
        before = path.read_text(encoding="utf-8")
        after, faq_count = neutralize_internal_faq(before)
        after, block_count = remove_internal_blocks(after)
        after = preserving_urls(after)

        # Tidy only structural leftovers from deleted private paragraphs/list items.
        after = re.sub(r"<p\b[^>]*>\s*</p>", "", after, flags=re.I)
        after = re.sub(r"<li\b[^>]*>\s*</li>", "", after, flags=re.I)
        after = re.sub(r"\s+([,.;:!?])", r"\1", after)

        if after != before:
            path.write_text(after, encoding="utf-8")
            changed_files += 1
            removed_blocks += block_count
            faq_rewrites += faq_count

    print(
        "legacy public affiliate-ops migration: "
        f"changed_files={changed_files} removed_blocks={removed_blocks} faq_rewrites={faq_rewrites}"
    )


if __name__ == "__main__":
    main()
