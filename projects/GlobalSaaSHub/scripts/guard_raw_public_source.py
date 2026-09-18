"""Fail closed when raw customer-facing source contains affiliate operations copy.

This guard intentionally runs after content generators but before customer-copy
sanitizers. Public source must already be safe; cleanup passes are defense in depth,
not permission for generators to emit internal operations language.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TARGETS = [ROOT / "index.html", *PUBLIC.rglob("*")]
TEXT_EXTS = {".html", ".txt", ".xml", ".json", ".js"}

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
FORBIDDEN = [
    ("affiliate manager", re.compile(r"\baffiliate\s+manager\b", re.I)),
    ("verified partner tracking", re.compile(r"\bverified\s+partner\s+tracking\b", re.I)),
    ("verified partner route", re.compile(r"\bverified\s+(?:COSHUMA\s+)?partner\s+(?:route|link|offer)\b", re.I)),
    ("verified tracking", re.compile(r"\bverified\s+tracking\b", re.I)),
    ("customer-facing tracking URL", re.compile(r"\bcustomer-facing\s+(?:tracking|referral|partner)\s+(?:URL|route|link)\b", re.I)),
    ("tracking verification", re.compile(r"\btracking\s+verification\b", re.I)),
    ("affiliate dashboard", re.compile(r"\baffiliate\s+dashboard\b", re.I)),
    ("tracking status", re.compile(r"\btracking\s+status\b", re.I)),
    ("revenue truth", re.compile(r"\brevenue[ _-]?truth\b", re.I)),
    ("browser queue", re.compile(r"\bbrowser[ _-]?queue\b", re.I)),
    ("approved_tracking", re.compile(r"\bapproved_tracking\b", re.I)),
    ("affiliate_verified", re.compile(r"\baffiliate_verified\b", re.I)),
    ("affiliate_evidence_markers", re.compile(r"\baffiliate_evidence_markers\b", re.I)),
    ("network name", re.compile(r"\b(?:PartnerStack|FirstPromoter)\b", re.I)),
]

def masked(text: str) -> str:
    return URL_RE.sub("https://TRACKING-URL", text)

def main() -> None:
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
