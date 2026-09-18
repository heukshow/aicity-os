"""Fail closed when committed/generated customer-facing source contains affiliate operations copy.

This guard is intended to run in prebuild before any customer-copy sanitizer and again
inside the build as defense in depth. Public source must already be safe; cleanup passes
are not permission for generators or committed pages to emit internal operations data.
Tracking/referral URLs are masked before scanning, so network hosts or parameters inside
an outbound URL remain allowed while explanatory network/verification copy does not.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
POLICY_PATH = ROOT / "config" / "public_content_policy.json"
TARGETS = [ROOT / "index.html", *PUBLIC.rglob("*")]
TEXT_EXTS = {".html", ".txt", ".xml", ".json", ".js", ".webmanifest"}

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
UNIQUE_NETWORK = re.compile(r"\b(?:PartnerStack|FirstPromoter)\b", re.I)
CONTEXTUAL_NETWORK = re.compile(
    r"\b(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Awin|CJ\s+Affiliate)\b"
    r"(?=[^\n<>]{0,80}\b(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)\b)"
    r"|\b(?:affiliate|partner|referral|tracking|commission|network|dashboard|program)\b"
    r"[^\n<>]{0,80}\b(?:Impact(?:\.com|\s+Radius)?|Dub|Cello|Tolt|Awin|CJ\s+Affiliate)\b",
    re.I,
)
FORBIDDEN = [
    ("affiliate manager", re.compile(r"\baffiliate\s+manager\b", re.I)),
    ("partner manager", re.compile(r"\bpartner\s+manager\b", re.I)),
    ("verified partner tracking", re.compile(r"\bverified\s+partner\s+tracking\b", re.I)),
    ("verified partner route", re.compile(r"\bverified\s+(?:COSHUMA\s+)?partner\s+(?:route|link|offer)\b", re.I)),
    ("verified tracking", re.compile(r"\bverified\s+tracking\b", re.I)),
    ("verified link", re.compile(r"\bverified\s+(?:affiliate|referral|customer-facing\s+)?link\b", re.I)),
    ("customer-facing tracking URL", re.compile(r"\bcustomer-facing\s+(?:tracking|referral|partner)\s+(?:URL|route|link)\b", re.I)),
    ("tracking verification", re.compile(r"\btracking\s+verification\b", re.I)),
    ("affiliate dashboard", re.compile(r"\b(?:affiliate|partner|referral|commission)\s+(?:dashboard|portal)\b", re.I)),
    ("tracking status", re.compile(r"\btracking\s+status\b", re.I)),
    ("affiliate status", re.compile(r"\baffiliate[ _-]?status\b", re.I)),
    ("affiliate verified", re.compile(r"\baffiliate[ _-]?verified\b", re.I)),
    ("affiliate evidence", re.compile(r"\baffiliate[ _-]?evidence(?:[ _-]?markers)?\b", re.I)),
    ("application state", re.compile(r"\bapplication[ _-]?state\b", re.I)),
    ("application status", re.compile(r"\b(?:affiliate|partner|referral|creator)\s+application\s+(?:status|pending|submitted|under\s+review)\b", re.I)),
    ("revenue truth", re.compile(r"\brevenue[ _-]?truth\b", re.I)),
    ("browser queue", re.compile(r"\bbrowser[ _-]?(?:required[ _-]?)?queue\b", re.I)),
    ("approved_tracking", re.compile(r"\bapproved_tracking\b", re.I)),
    ("internal verification", re.compile(r"\b(?:internal\s+verification|verification\s+evidence|partner-side\s+evidence|partner\s+correspondence)\b", re.I)),
    ("network name", UNIQUE_NETWORK),
    ("contextual network name", CONTEXTUAL_NETWORK),
]


def masked(text: str) -> str:
    # The mask itself must stay neutral. A token such as TRACKING-URL can create a
    # false contextual-network match when a legitimate product name (for example
    # Dub) appears nearby in JSON-LD or page copy.
    return URL_RE.sub("https://PUBLIC-OUTBOUND-URL", text)


def validate_policy_alignment() -> None:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    require = policy.get("public_internal_data", {})
    if require.get("default_private") is not True:
        raise SystemExit("RAW PUBLIC SOURCE BOUNDARY FAILED: central policy is no longer private-by-default")
    labels = set(require.get("forbidden_labels", []))
    expected = {
        "affiliate_status", "affiliate_verified", "affiliate_evidence_markers",
        "application state", "revenue truth", "browser queue",
        "PartnerStack", "FirstPromoter", "Impact", "Dub", "Cello", "Tolt", "Awin", "CJ Affiliate",
    }
    missing = sorted(expected - labels)
    if missing:
        raise SystemExit(f"RAW PUBLIC SOURCE BOUNDARY FAILED: central forbidden-label policy drift: missing={missing}")


def main() -> None:
    validate_policy_alignment()
    violations = []
    checked = 0
    for path in TARGETS:
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        checked += 1
        text = masked(path.read_text(encoding="utf-8", errors="replace"))
        for label, pattern in FORBIDDEN:
            match = pattern.search(text)
            if match:
                rel = path.relative_to(ROOT).as_posix()
                line = text.count("\n", 0, match.start()) + 1
                violations.append(f"{rel}:{line}: {label}: {match.group(0)}")
    if violations:
        print("RAW PUBLIC SOURCE BOUNDARY FAILED")
        for item in violations[:100]:
            print(item)
        if len(violations) > 100:
            print(f"... and {len(violations)-100} more")
        raise SystemExit(1)
    print(f"Raw public source boundary: PASS files={checked} internal_ops=0")


if __name__ == "__main__":
    main()
