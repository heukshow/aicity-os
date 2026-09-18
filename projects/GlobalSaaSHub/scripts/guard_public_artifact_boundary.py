"""Fail closed if internal affiliate/operations language leaks into public production artifacts.

Internal evidence may remain in repository data/ops files. The final dist/ bundle is a
customer surface and must not expose network names, verification mechanics or state.
Verified outbound URLs are allowed even when the URL itself contains a network domain
or query parameter.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys

TEXT_EXTENSIONS = {".html", ".txt", ".xml", ".json", ".js", ".webmanifest"}

URL = re.compile(r"https?://[^\s\"'<>]+", re.I)

UNIQUE_NETWORK = re.compile(r"\b(?:PartnerStack|FirstPromoter)\b", re.I)
CONTEXTUAL_NETWORK = re.compile(
    r"\b(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Awin|CJ\s+Affiliate)\b"
    r"(?=[^\n<>]{0,80}\b(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)\b)"
    r"|\b(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)\b"
    r"[^\n<>]{0,80}\b(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Awin|CJ\s+Affiliate)\b",
    re.I,
)
INTERNAL_STATE = re.compile(
    r"\b(?:approved_tracking|tracking_pending|pending_review|affiliate_verified|"
    r"revenue[_ -]?truth|browser[_ -]?queue|customer-facing\s+(?:tracking|referral|partner)\s+(?:URL|route|link)|"
    r"exact\s+(?:customer-facing\s+)?tracking\s+URL|verified\s+customer-facing|"
    r"partner-side\s+evidence|partner\s+correspondence|verification\s+evidence|"
    r"internal\s+verification|affiliate\s+application\s+(?:status|pending|submitted)|"
    r"partner\s+application\s+(?:status|pending|submitted)|tracking\s+status|affiliate\s+status)\b",
    re.I,
)
INTERNAL_DASHBOARD = re.compile(
    r"\b(?:affiliate|partner|referral|commission)\s+(?:portal|dashboard)\b"
    r"|\b(?:portal|dashboard)\b[^\n<>]{0,50}\b(?:affiliate|partner|referral|commission)\b",
    re.I,
)
INTERNAL_KEYS = re.compile(
    r"[\"'](?:affiliate_evidence_markers|affiliate_status|affiliate_verified|"
    r"affiliate_status_checked_at|affiliate_status_evidence_url|affiliate_next_action|"
    r"application_state|browser_required_queue|revenue_truth)[\"']\s*:",
    re.I,
)

PATTERNS = {
    "affiliate-network-name": UNIQUE_NETWORK,
    "affiliate-network-context": CONTEXTUAL_NETWORK,
    "internal-affiliate-state": INTERNAL_STATE,
    "internal-affiliate-dashboard": INTERNAL_DASHBOARD,
}


class PublicHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.jsonld = 0
        self.parts: list[str] = []
        self.meta: list[str] = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "script":
            if attr.get("type", "").lower() == "application/ld+json":
                self.jsonld += 1
            else:
                self.hidden += 1
        elif tag == "style":
            self.hidden += 1
        elif tag == "meta":
            self.meta.append(attr.get("content", ""))

    def handle_endtag(self, tag):
        if tag == "script":
            if self.jsonld:
                self.jsonld -= 1
            elif self.hidden:
                self.hidden -= 1
        elif tag == "style" and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden or self.jsonld:
            self.parts.append(data)


def mask_urls(text: str) -> str:
    return URL.sub("https://PUBLIC-OUTBOUND-URL", text)


def scan_text(text: str) -> list[str]:
    text = mask_urls(text)
    violations: list[str] = []
    for label, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            snippet = re.sub(r"\s+", " ", text[max(0, match.start()-70):match.end()+70]).strip()
            violations.append(f"{label}: {snippet[:220]}")
    return violations


def scan_file(path: Path) -> list[str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    if path.suffix.lower() == ".html":
        p = PublicHTML()
        p.feed(raw)
        return scan_text(" ".join(p.parts + p.meta))

    if path.suffix.lower() == ".js":
        # URLs and public product names are fine in JS. Internal source-state keys are not.
        match = INTERNAL_KEYS.search(raw)
        if not match:
            return []
        snippet = re.sub(r"\s+", " ", raw[max(0, match.start()-70):match.end()+70]).strip()
        return [f"internal-data-key: {snippet[:220]}"]

    if path.suffix.lower() == ".json":
        try:
            # Pretty/minified JSON are both scanned as public text after URL masking.
            raw = json.dumps(json.loads(raw), ensure_ascii=False)
        except Exception:
            pass
        key = INTERNAL_KEYS.search(raw)
        out = [f"internal-data-key: {key.group(0)}"] if key else []
        return out + scan_text(raw)

    return scan_text(raw)


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    if not root.exists():
        raise SystemExit(f"Public artifact boundary guard: missing {root}")

    files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_EXTENSIONS]
    if not files:
        raise SystemExit(f"Public artifact boundary guard: no public text artifacts under {root}")

    errors: list[str] = []
    for path in files:
        for violation in scan_file(path):
            errors.append(f"{path.relative_to(root).as_posix()}: {violation}")

    if errors:
        print("ERROR: internal affiliate/operations language reached the public production bundle.")
        print("Internal evidence may remain in data/ops files, but dist/ must stay customer-only.")
        for error in errors[:100]:
            print(f" - {error}")
        if len(errors) > 100:
            print(f" - ... and {len(errors)-100} more")
        raise SystemExit(1)

    print(f"PASS: public artifact boundary clean across {len(files)} text artifacts; network/status/dashboard leaks=0")


if __name__ == "__main__":
    main()
