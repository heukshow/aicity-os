"""Remove affiliate verification/status wording from customer-facing public source.

This is intentionally narrow: exact outbound URLs and sponsored attribution remain
unchanged. Only human-readable status/verification phrases are neutralized before
source-boundary checks and the production build.
"""
from pathlib import Path
import re

from self_heal_source_affiliate_disclosures import normalize_home, normalize_page

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TEXT_EXTENSIONS = {".html", ".txt", ".xml", ".json", ".js", ".webmanifest"}
URL = re.compile(r"https?://[^\s\"'<>]+", re.I)

RULES = (
    (re.compile(r"\bAffiliate Facts\b"), "Product Details"),
    (re.compile(r"\bPartner Facts\b"), "Product Details"),
    (
        re.compile(
            r"\b(?:verified\s+)?(?:current\s+)?(?:public\s+)?"
            r"(?:affiliate|partner)[-\s]+program\s+(?:status|facts|terms)\b",
            re.I,
        ),
        "current product details",
    ),
    (re.compile(r"\baffiliate\s+offer\s+facts\b", re.I), "product and offer details"),
    (re.compile(r"\bcurrent\s+(?:public\s+)?(?:affiliate|partner)\s+(?:program\s+)?terms\b", re.I), "current product details"),
    (re.compile(r"\b(?:affiliate|partner)\s+facts\b", re.I), "product details"),
    (
        re.compile(
            r"\bverified\s+customer-facing\s+(?:COSHUMA\s+)?"
            r"(?:affiliate|partner|referral|tracking)\s+(?:links?|routes?|URLs?|destinations?)\b",
            re.I,
        ),
        "current offer link",
    ),
    (
        re.compile(
            r"\baffiliate\s+link\s+verified(?:\s+[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})?",
            re.I,
        ),
        "current offer link",
    ),
    (re.compile(r"\bvia\s+verified\s+COSHUMA\s+link\b", re.I), "through COSHUMA"),
    (re.compile(r"\bverified\s+revenue\s+alternative\b", re.I), "relevant alternative"),
    (re.compile(r"\bverified\s+monetization\s+path\b", re.I), "available option"),
    (re.compile(r"\bverified\s+customer-facing\b", re.I), "current"),
    (re.compile(r"\bverified\s+partner\s+(?:links?|routes?|URLs?|offers?)\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+(?:affiliate|referral|tracking)\s+(?:links?|routes?|URLs?|destinations?)\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+partner\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+(?:affiliate|referral|tracking)\b", re.I), "current offer"),
    (re.compile(r"\bverified\s+link\b", re.I), "current offer"),
)


def clean_non_url(text: str) -> str:
    for pattern, replacement in RULES:
        text = pattern.sub(replacement, text)
    return text


def clean_preserving_urls(text: str) -> str:
    parts = []
    pos = 0
    for match in URL.finditer(text):
        parts.append(clean_non_url(text[pos:match.start()]))
        parts.append(match.group(0))
        pos = match.end()
    parts.append(clean_non_url(text[pos:]))
    return "".join(parts)


changed = 0
for path in PUBLIC.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
        continue
    try:
        before = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    after = clean_preserving_urls(before)
    if after != before:
        path.write_text(after, encoding="utf-8")
        changed += 1

disclosures_changed = 1 if normalize_home() else 0
for path in PUBLIC.rglob("*.html"):
    if normalize_page(path):
        disclosures_changed += 1

print(
    f"Sanitized public affiliate verification/status labels in {changed} file(s); "
    f"outbound URLs preserved; disclosures normalized in {disclosures_changed} file(s)"
)
