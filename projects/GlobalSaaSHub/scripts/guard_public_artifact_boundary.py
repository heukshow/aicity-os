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
CONSUMER_AFFILIATE_DISCLOSURE = re.compile(
    r"\bAffiliate\s+disclosure:\s*COSHUMA\s+may\s+earn\s+"
    r"(?:(?:an\s+affiliate|a)\s+)?commission\b[^.\n<>]*(?:\.)?",
    re.I,
)
INTERNAL_STATE = re.compile(
    r"\b(?:approved_tracking|tracking_pending|pending_review|affiliate_verified|"
    r"revenue[_ -]?truth|browser[_ -]?queue|customer-facing\s+(?:tracking|referral|partner)\s+(?:URL|route|link)|"
    r"exact\s+(?:customer-facing\s+)?tracking\s+URL|verified\s+customer-facing|"
    r"partner-side\s+evidence|partner\s+correspondence|verification\s+evidence|"
    r"internal\s+verification|affiliate\s+application\s+(?:status|pending|submitted)|"
    r"partner\s+application\s+(?:status|pending|submitted)|tracking\s+status|affiliate\s+status|"
    r"review\s+pending|not\s+yet\s+editorially\s+rated|editorial\s+review\s+in\s+progress)\b"
    r"|\baffiliate\s+approved\b[^\n<>]{0,100}\bpending\s+verification\b"
    r"|\b(?:affiliate|partner)[-\s]+program\s+(?:status|facts|terms)\b"
    r"|\bcurrent\s+(?:affiliate|partner)\s+(?:program\s+)?terms\b"
    r"|\bpartner\s+facts\b",
    re.I,
)
INTERNAL_DASHBOARD = re.compile(
    r"\b(?:affiliate|partner|referral|commission)\s+(?:portal|dashboard)\b"
    r"|\b(?:portal|dashboard)\b[^\n<>]{0,50}\b(?:affiliate|partner|referral|commission)\b",
    re.I,
)
INTERNAL_CORRESPONDENCE = re.compile(
    r"\b(?:affiliate|partner)\s+(?:team|manager)\b[^\n<>]{0,120}\b(?:message|email|reply|told|confirmed|supplied|reconfirmed)\b"
    r"|\b(?:message|email|reply)\b[^\n<>]{0,120}\b(?:affiliate|partner)\s+(?:team|manager)\b"
    r"|\bfirst-party\s+reporting\s+(?:verifies|confirms)\b",
    re.I,
)
INTERNAL_VERIFICATION_COPY = re.compile(
    r"\bvendor[- ]confirmed\b"
    r"|\btracking\s+(?:unconfirmed|confirmed|verified|unknown)\b"
    r"|\bHow\s+COSHUMA\s+verified\b"
    r"|\bverified\s+(?:affiliate|partner|referral|tracking)\b"
    r"|\bverified\s+link\b"
    r"|\b(?:affiliate|partner)\s+route\b",
    re.I,
)
INTERNAL_REVENUE_OPS = re.compile(
    r"\bWhat\s+COSHUMA\s+counts\s+as\s+revenue\b"
    r"|\bCOSHUMA\s+tracking\b"
    r"|\b(?:referral|tracking)\s+URL\s+(?:not\s+yet\s+verified|not\s+verified|unknown)\b"
    r"|\baffiliate\s+evidence\b"
    r"|\bverified\s+affiliate\s+records\b"
    r"|\bpublication\s+or\s+test\s+clicks?\s+are\s+not\s+treated\s+as\s+signups?,\s*customers?\s+or\s+revenue\b",
    re.I,
)
INTERNAL_PAYMENT_OPS = re.compile(
    r"\bpayment\s+system\s+update\s+in\s+progress\b"
    r"|\bsponsorship\s+checkout\s+is\s+temporarily\s+unavailable\b"
    r"|\bcheckout\s+is\s+temporarily\s+unavailable\b"
    r"|\bpayments?\s+(?:are\s+)?temporarily\s+paused\b"
    r"|\bpayment\s+handling\s+is\s+being\s+verified\b"
    r"|\b(?:checkout|payment)\s+(?:and\s+)?campaign\s+reporting\s+system\b"
    r"|\bduring\s+maintenance\b",
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
    "internal-affiliate-correspondence": INTERNAL_CORRESPONDENCE,
    "internal-tracking-verification-copy": INTERNAL_VERIFICATION_COPY,
    "internal-revenue-ops": INTERNAL_REVENUE_OPS,
    "internal-payment-ops": INTERNAL_PAYMENT_OPS,
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
    # Consumer-facing affiliate disclosure is intentionally public and required on
    # monetized pages. Mask only that standard disclosure while evaluating contextual
    # network names so product names such as "Dub" do not become false positives merely
    # because the legal disclosure sits next to the CTA. All other leak patterns still
    # scan the original public text unchanged.
    network_text = CONSUMER_AFFILIATE_DISCLOSURE.sub("CONSUMER-DISCLOSURE", text)
    violations: list[str] = []
    for label, pattern in PATTERNS.items():
        source = network_text if label == "affiliate-network-context" else text
        match = pattern.search(source)
        if match:
            snippet = re.sub(r"\s+", " ", source[max(0, match.start()-70):match.end()+70]).strip()
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
        visible = scan_text(" ".join(p.parts + p.meta))
        key = INTERNAL_KEYS.search(mask_urls(raw))
        if key:
            visible.append(f"internal-data-key: {key.group(0)}")
        return visible

    if path.suffix.lower() == ".js":
        # Scan executable public source too. URLs are masked so verified tracking
        # domains/parameters remain allowed while explanatory ops copy fails closed.
        masked = mask_urls(raw)
        out = scan_text(raw)
        key = INTERNAL_KEYS.search(masked)
        if key:
            snippet = re.sub(r"\s+", " ", masked[max(0, key.start()-70):key.end()+70]).strip()
            out.insert(0, f"internal-data-key: {snippet[:220]}")
        return out

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

    print(f"PASS: public artifact boundary clean across {len(files)} text artifacts; network/status/dashboard/correspondence/verification/revenue-ops/payment-ops leaks=0")


if __name__ == "__main__":
    main()
