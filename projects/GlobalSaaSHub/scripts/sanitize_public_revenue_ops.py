"""Remove residual internal affiliate/revenue provenance from buyer-facing HTML.

This pass runs after the broader partner-correspondence sanitizer and before Vite.
It intentionally leaves href values and sponsored attribution untouched. Internal
state/evidence remains available in private repository data, but customer pages may
only describe the product/offer itself, not COSHUMA's verification or revenue ops.
"""
from __future__ import annotations

from html import unescape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

TAG = re.compile(r"<[^>]+>")
URL = re.compile(r"https?://[^\s\"'<>]+", re.I)
BLOCK = re.compile(r"<(p|li|tr|small|figcaption|blockquote)\b[^>]*>.*?</\1>", re.I | re.S)
TEXT_NODE = re.compile(r"(?<=>)([^<]+)(?=<)", re.S)

PRIVATE_BLOCK = re.compile(
    r"\baffiliate\s+evidence\b"
    r"|\bCOSHUMA(?:'s)?\s+verified\s+affiliate\s+records\b"
    r"|\bWhat\s+COSHUMA\s+counts\s+as\s+revenue\b"
    r"|\bCOSHUMA\s+tracking\b"
    r"|\b(?:referral|tracking)\s+URL\s+(?:not\s+yet\s+verified|not\s+verified|unknown)\b"
    r"|\b(?:company-mail|account|dashboard)\s+evidence\b[^.]{0,160}\b(?:affiliate|referral|tracking|commission)\b",
    re.I,
)

PRIVATE_REMAINDER = re.compile(
    r"\baffiliate\s+evidence\b"
    r"|\bverified\s+affiliate\s+records\b"
    r"|\bWhat\s+COSHUMA\s+counts\s+as\s+revenue\b"
    r"|\bCOSHUMA\s+tracking\b"
    r"|\b(?:referral|tracking)\s+URL\s+(?:not\s+yet\s+verified|not\s+verified|unknown)\b"
    r"|\baffiliate_evidence_markers\b"
    r"|\baffiliate_status\b"
    r"|\baffiliate_verified\b"
    r"|\brevenue[_ -]?truth\b"
    r"|\bbrowser[_ -]?queue\b",
    re.I,
)

VERIFIED_RECORD_SENTENCE = re.compile(
    r"[^.!?]{0,360}\bCOSHUMA(?:'s)?\s+verified\s+affiliate\s+records\b[^.!?]{0,360}[.!?]?",
    re.I,
)


def visible(fragment: str) -> str:
    return re.sub(r"\s+", " ", unescape(TAG.sub(" ", fragment))).strip()


def clean_block(match: re.Match[str]) -> str:
    return "" if PRIVATE_BLOCK.search(visible(match.group(0))) else match.group(0)


def clean_text_node(match: re.Match[str]) -> str:
    text = match.group(1)
    text = VERIFIED_RECORD_SENTENCE.sub("", text)
    text = re.sub(r"\bverified\s+COSHUMA\s+partner\s+(?:links?|URLs?)\b", "current offer links", text, flags=re.I)
    text = re.sub(r"\bvia\s+(?:a\s+)?verified\s+(?:link|route)\b", "", text, flags=re.I)
    text = re.sub(r"\bthrough\s+(?:a\s+)?verified\s+(?:link|route)\b", "", text, flags=re.I)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text


def clean_html(source: str) -> str:
    cleaned = BLOCK.sub(clean_block, source)
    cleaned = TEXT_NODE.sub(clean_text_node, cleaned)
    cleaned = re.sub(r"<p\b[^>]*>\s*</p>", "", cleaned, flags=re.I)
    cleaned = re.sub(r"<li\b[^>]*>\s*</li>", "", cleaned, flags=re.I)
    return cleaned


def scan_customer_surface(source: str) -> re.Match[str] | None:
    masked = URL.sub("https://PUBLIC-OUTBOUND-URL", source)
    return PRIVATE_REMAINDER.search(visible(masked))


def main() -> None:
    changed: list[str] = []
    for path in sorted(PUBLIC.rglob("*.html")):
        before = path.read_text(encoding="utf-8")
        after = clean_html(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())

    violations: list[str] = []
    for path in sorted(PUBLIC.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        match = scan_customer_surface(text)
        if match:
            masked = URL.sub("https://PUBLIC-OUTBOUND-URL", text)
            plain = visible(masked)
            found = PRIVATE_REMAINDER.search(plain)
            if found:
                snippet = plain[max(0, found.start() - 90):found.end() + 120]
                violations.append(f"{path.relative_to(PUBLIC).as_posix()}: {snippet[:320]}")

    if violations:
        print("ERROR: revenue/tracking operations copy remains in customer-facing HTML")
        for item in violations[:50]:
            print(f" - {item}")
        raise SystemExit(1)

    print(f"PASS: revenue-ops public sanitizer changed={len(changed)} remaining=0")
    for item in changed[:30]:
        print(f" - {item}")
    if len(changed) > 30:
        print(f" - ... and {len(changed) - 30} more")


if __name__ == "__main__":
    main()
