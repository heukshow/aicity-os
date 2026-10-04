"""Reject known English-copy regressions, not a general grammar or AI detector.

This read-only check protects reviewed wording through the real production build.
It never rewrites prices, product claims, URLs, disclosures or measurement data.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
GLOBAL_PATTERNS = (
    r"\bFree-plan signals\b",
    r"\bPaid-plan direction\b",
    r"\bnext rep or manager touch\b",
    r"\blive checkout is final\b",
    r"\bOne-month Advanced Listening trial is available\b",
    r"\bStart with high-intent categories buyers frequently compare\b",
    r"\bCOSHUMA is currently verifying its partner referral route\b",
)
SCOPED_PATTERNS = {
    "tool/agorapulse.html": (r"\bannual-billing view\b", r"\bAnnual view\b"),
}
REVIEWED_MARKERS = {
    "index.html": "Choose a category to find software guides and side-by-side comparisons.",
    "tool/agorapulse.html": "Eligible Agorapulse customers can try Advanced Listening for one month",
    "compare/brand24-vs-agorapulse.html": "Check Agorapulse's official pricing page for plan details and trial terms.",
    "best/claap-sales-follow-up-ai.html": "Useful follow-up starts with an accurate record of the sales call.",
    "compare/gamma-vs-canva.html": "What the free plan includes",
    "tool/descript.html": "Confirm the current price and plan details at checkout.",
}

class ReaderText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        a = dict(attrs)
        if tag == "meta" and (a.get("name") == "description" or a.get("property") in ("og:title", "og:description")):
            self.parts.append(a.get("content", ""))
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
    def handle_data(self, value):
        if not self.hidden:
            self.parts.append(value)

def reader_text(html: str) -> str:
    parser = ReaderText()
    parser.feed(html)
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()

def violations(html: str, relative_path: str = "") -> list[str]:
    text = reader_text(html)
    patterns = GLOBAL_PATTERNS + SCOPED_PATTERNS.get(relative_path, ())
    return [m.group(0) for pattern in patterns for m in re.finditer(pattern, text, re.I)]

def audit(root: Path, source: bool = False) -> tuple[int, list[str]]:
    public = root / "public" if source else root
    paths = sorted(public.rglob("*.html")) if public.exists() else []
    if source and (root / "index.html").is_file():
        paths.append(root / "index.html")
    errors: list[str] = []
    by_name: dict[str, str] = {}
    if not paths:
        errors.append(f"No HTML files found under {public}")
    for path in paths:
        rel = "index.html" if source and path == root / "index.html" else path.relative_to(public).as_posix()
        html = path.read_text(encoding="utf-8")
        by_name[rel] = reader_text(html)
        errors.extend(f"{rel}: {item}" for item in violations(html, rel))
    for rel, expected in REVIEWED_MARKERS.items():
        if rel not in by_name:
            errors.append(f"Missing reviewed page: {rel}")
        elif expected not in by_name[rel]:
            errors.append(f"{rel}: reviewed copy was lost or changed; review the source and producer together")
    return len(paths), errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path)
    parser.add_argument("--source", action="store_true")
    args = parser.parse_args()
    root = args.root or (PROJECT if args.source else PROJECT / "dist")
    count, errors = audit(root, source=args.source)
    if errors:
        print("ENGLISH COPY REGRESSION CHECK FAILED\n" + "\n".join(errors))
        return 1
    print(f"PASS: known English-copy regressions absent in {count} HTML files; {len(REVIEWED_MARKERS)} reviewed page markers retained. Not a full editorial certification.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
