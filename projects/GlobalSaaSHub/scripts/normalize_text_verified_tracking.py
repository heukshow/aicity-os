"""Keep Text affiliate CTAs on the exact vendor-issued campaign URL.

The Partner App campaign URL is authoritative. Internal CTA attribution belongs in
`data-cta-source`; adding new query parameters to the external partner URL is not
necessary and can make revenue attribution harder to verify.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
EXACT_URL = "https://www.text.com/?a=8IetMhQvR&utm_campaign=pp_text-wins-martech-awards&utm_source=PP"

ANCHOR_RE = re.compile(r"<a\b[^>]*>", re.I)
HREF_RE = re.compile(r'href="([^"]+)"', re.I)

changed_files = []
changed_links = 0
seen = 0

for path in PUBLIC.rglob("*.html"):
    original = path.read_text(encoding="utf-8")

    def normalize(match: re.Match[str]) -> str:
        global changed_links, seen
        anchor = match.group(0)
        if 'data-cta="affiliate"' not in anchor or 'data-tool-id="text"' not in anchor:
            return anchor
        seen += 1
        href_match = HREF_RE.search(anchor)
        if not href_match:
            raise SystemExit(f"Text affiliate CTA missing href: {path}")
        href = href_match.group(1).replace("&amp;", "&")
        if href == EXACT_URL:
            return anchor
        if not href.startswith("https://www.text.com/?a=8IetMhQvR&utm_campaign=pp_text-wins-martech-awards&utm_source=PP"):
            raise SystemExit(f"Unexpected Text affiliate URL in {path}: {href}")
        changed_links += 1
        return anchor[: href_match.start(1)] + EXACT_URL + anchor[href_match.end(1) :]

    updated = ANCHOR_RE.sub(normalize, original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed_files.append(path.relative_to(ROOT).as_posix())

if seen == 0:
    raise SystemExit("No Text affiliate CTAs found; expected at least one")

# Fail closed after normalization so later edits cannot silently publish a
# dashboard, homepage-only, or locally-extended partner URL.
for path in PUBLIC.rglob("*.html"):
    html = path.read_text(encoding="utf-8")
    for anchor in ANCHOR_RE.findall(html):
        if 'data-cta="affiliate"' not in anchor or 'data-tool-id="text"' not in anchor:
            continue
        href_match = HREF_RE.search(anchor)
        href = href_match.group(1).replace("&amp;", "&") if href_match else ""
        if href != EXACT_URL:
            raise SystemExit(f"Text affiliate CTA is not exact vendor route in {path}: {href}")

print(f"normalize_text_verified_tracking: seen={seen} changed_links={changed_links} files_changed={len(changed_files)}")
for item in changed_files:
    print(f" - {item}")
