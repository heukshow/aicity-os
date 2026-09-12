"""Keep Text affiliate CTAs on the exact vendor-issued campaign URL.

The Partner App campaign URL is authoritative. Internal CTA attribution belongs in
`data-cta-source`; adding new query parameters to the external partner URL is not
necessary and can make revenue attribution harder to verify.

Text Support confirmed on 2026-09-12 that the partner program is campaign-based
and there is no deeper campaign than those shown in the partner panel. Therefore
COSHUMA must not present the verified campaign URL as if it were a direct trial
or signup deep link. The trial still exists, but visitors first open the tracked
campaign and then choose Text's Start free trial action on text.com.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
EXACT_URL = "https://www.text.com/?a=8IetMhQvR&utm_campaign=pp_text-wins-martech-awards&utm_source=PP"

ANCHOR_RE = re.compile(r"<a\b[^>]*>", re.I)
HREF_RE = re.compile(r'href="([^"]+)"', re.I)
HERO_CTA_RE = re.compile(
    r'(<a\b[^>]*data-cta-source="text-hero-trial"[^>]*>.*?</a>)',
    re.I | re.S,
)

MISLEADING_LABELS = {
    "Start Text Free for 14 Days — No Card →": "Open Text.com → Start 14-day trial",
    "Test Text Free for 14 Days →": "Open Text.com → Start 14-day trial",
}

ROUTING_NOTE_MARKER = "Text partner routing note — September 12, 2026"
ROUTING_NOTE = (
    '<div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 text-sm text-slate-300 leading-relaxed">'
    '<strong class="text-amber-300">Text partner routing note — September 12, 2026:</strong> '
    'Text Support confirmed that its partner program is campaign-based and that there is no deeper affiliate campaign than the campaigns shown in the partner panel. '
    'This verified COSHUMA link therefore opens the tracked Text.com campaign first; on Text.com, choose <strong>Start free trial</strong> to begin the 14-day trial. '
    'Do not treat this campaign URL as a direct trial-signup deep link.'
    '</div>'
)

changed_files = []
changed_links = 0
changed_copy = 0
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

    # The verified campaign is not a direct trial deeplink. Keep trial intent in
    # the button, but make the required intermediate Text.com step explicit.
    if EXACT_URL in updated:
        for old, new in MISLEADING_LABELS.items():
            occurrences = updated.count(old)
            if occurrences:
                updated = updated.replace(old, new)
                changed_copy += occurrences

    # Add the vendor-confirmed routing rule directly after the primary Text CTA.
    # Other build scripts may rewrite the disclosure copy, so the stable CTA
    # source marker is the resilient insertion point.
    if path.as_posix().endswith("public/tool/text.html") and ROUTING_NOTE_MARKER not in updated:
        if not HERO_CTA_RE.search(updated):
            raise SystemExit("Text hero CTA anchor not found; routing note was not inserted")
        updated = HERO_CTA_RE.sub(r"\1\n          " + ROUTING_NOTE, updated, count=1)
        changed_copy += 1

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

# Guard the primary buyer page against the old misleading direct-trial labels.
text_page = PUBLIC / "tool" / "text.html"
if text_page.exists():
    text_html = text_page.read_text(encoding="utf-8")
    if ROUTING_NOTE_MARKER not in text_html:
        raise SystemExit("Text partner routing note missing after normalization")
    for old in MISLEADING_LABELS:
        if old in text_html:
            raise SystemExit(f"Misleading direct-trial CTA survived normalization: {old}")

print(
    f"normalize_text_verified_tracking: seen={seen} changed_links={changed_links} "
    f"changed_copy={changed_copy} files_changed={len(changed_files)}"
)
for item in changed_files:
    print(f" - {item}")
