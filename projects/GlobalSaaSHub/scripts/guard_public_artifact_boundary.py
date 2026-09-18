"""Fail closed if internal affiliate/operations language leaks into public production artifacts.

This guard intentionally scans the final dist/ bundle, not source evidence. Internal
records may retain network names and verification state; public artifacts may not.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

TEXT_EXTENSIONS = {".html", ".txt", ".xml", ".json", ".js", ".css", ".webmanifest"}

# Unique network/vendor-operation tokens that should never be shipped as customer copy.
# "Impact" and "Dub" need context because they are ordinary English words/names.
UNIQUE_NETWORK = re.compile(
    r"\b(?:PartnerStack|FirstPromoter|Tapfiliate|ShareASale|Partnerize|Everflow|Affise)\b",
    re.I,
)
CONTEXTUAL_NETWORK = re.compile(
    r"\b(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Rewardful|Awin|CJ\s+Affiliate)\b"
    r"(?=[^\n<>]{0,80}\b(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)\b)"
    r"|\b(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)\b"
    r"[^\n<>]{0,80}\b(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Rewardful|Awin|CJ\s+Affiliate)\b",
    re.I,
)

INTERNAL_STATE = re.compile(
    r"\b(?:approved_tracking|tracking_pending|pending_review|affiliate_verified|"
    r"revenue[_ -]?truth|browser[_ -]?queue|customer-facing\s+(?:tracking|referral)\s+URL|"
    r"exact\s+tracking\s+URL|verified\s+customer-facing|partner-side\s+evidence|"
    r"partner\s+correspondence|verification\s+evidence|internal\s+verification|"
    r"affiliate\s+application\s+(?:status|pending|submitted)|"
    r"partner\s+application\s+(?:status|pending|submitted)|"
    r"tracking\s+status|affiliate\s+status)\b",
    re.I,
)

INTERNAL_DASHBOARD = re.compile(
    r"\b(?:affiliate|partner|referral|commission|tracking)\s+(?:portal|dashboard)\b"
    r"|\b(?:portal|dashboard)\b[^\n<>]{0,50}\b(?:affiliate|partner|referral|commission|tracking)\b",
    re.I,
)

# The dedicated disclosure page may explain commissions generally, but it still must
# not expose network names, internal status, dashboards, or verification mechanics.
PATTERNS = {
    "affiliate-network-name": UNIQUE_NETWORK,
    "affiliate-network-context": CONTEXTUAL_NETWORK,
    "internal-affiliate-state": INTERNAL_STATE,
    "internal-affiliate-dashboard": INTERNAL_DASHBOARD,
}


def scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    violations: list[str] = []
    for label, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            snippet = re.sub(r"\s+", " ", text[max(0, match.start()-70):match.end()+70]).strip()
            violations.append(f"{label}: {snippet[:220]}")
    return violations


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
        for error in errors[:80]:
            print(f" - {error}")
        if len(errors) > 80:
            print(f" - ... and {len(errors)-80} more")
        raise SystemExit(1)

    print(f"PASS: public artifact boundary clean across {len(files)} text artifacts; network/status/dashboard leaks=0")


if __name__ == "__main__":
    main()
