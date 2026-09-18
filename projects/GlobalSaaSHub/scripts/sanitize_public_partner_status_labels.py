"""Remove affiliate verification/status wording from customer-facing public source.

This is intentionally narrow: exact outbound URLs and sponsored attribution remain
unchanged. Only human-readable status/verification phrases are neutralized before
source-boundary checks and the production build.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TEXT_EXTENSIONS = {".html", ".txt", ".xml", ".json", ".js", ".webmanifest"}
URL = re.compile(r"https?://[^\s\"'<>]+", re.I)

RULES = (
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

print(f"Sanitized public affiliate verification/status labels in {changed} file(s); outbound URLs preserved")
