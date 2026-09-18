"""Normalize canonical consumer affiliate disclosures in public source before the source boundary check.

This is not a privacy scrubber. Internal affiliate operations are handled by the raw/source
boundary guards. This pass only makes the consumer-disclosure rule deterministic:
- homepage: exactly one global disclosure;
- affiliate CTA pages: exactly one page disclosure immediately before the first affiliate CTA;
- pages without affiliate CTA: no page disclosure;
- the dedicated affiliate-disclosure policy page is preserved.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
POLICY = json.loads((ROOT / "config" / "public_content_policy.json").read_text(encoding="utf-8"))
DISC = POLICY["affiliate_disclosure"]

AFFILIATE_CTA = re.compile(r'<a\\b[^>]*\\bdata-cta\\s*=\\s*["\\']affiliate["\\'][^>]*>', re.I)
PAGE_NOTICE_RE = re.compile(
    r'<p\\b[^>]*\\bdata-affiliate-disclosure\\s*=\\s*["\\'][^"\\']*["\\'][^>]*>.*?</p>',
    re.I | re.S,
)
GLOBAL_NOTICE_RE = re.compile(
    r'<p\\b[^>]*\\bdata-site-affiliate-disclosure\\s*=\\s*["\\']global["\\'][^>]*>.*?</p>',
    re.I | re.S,
)
LEGACY_DISCLOSURE_RE = re.compile(
    r'<p\\b[^>]*>(?:(?!</p>).)*(?:Affiliate\\s+disclosure\\s*:|COSHUMA\\s+may\\s+earn\\s+(?:(?:an\\s+affiliate|a)\\s+)?commission)(?:(?!</p>).)*</p>',
    re.I | re.S,
)

PAGE_NOTICE = (
    '<p data-affiliate-disclosure="page" '
    'style="margin:.75rem 0;color:#94a3b8;font-size:12px;line-height:1.6">'
    + DISC["page_text"] +
    '</p>'
)
HOME_NOTICE = (
    '<p data-site-affiliate-disclosure="global" '
    'style="max-width:72rem;margin:0 auto;padding:0 1.5rem 1.5rem;color:#94a3b8;font-size:12px;line-height:1.6">'
    + DISC["homepage_text"] + ' '
    '<a href="' + DISC["details_path"] + '" style="text-decoration:underline">Details</a>.'
    '</p>'
)

def normalize_page(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    before = path.read_text(encoding="utf-8")
    if rel.endswith("affiliate-disclosure.html"):
        return False

    text = PAGE_NOTICE_RE.sub("", before)
    text = GLOBAL_NOTICE_RE.sub("", text)
    text = LEGACY_DISCLOSURE_RE.sub("", text)

    first = AFFILIATE_CTA.search(text)
    if first:
        text = text[:first.start()] + PAGE_NOTICE + "\\n" + text[first.start():]
        marker_at = text.find('data-affiliate-disclosure="page"')
        cta_at = AFFILIATE_CTA.search(text).start()
        if text.count('data-affiliate-disclosure="page"') != 1 or marker_at > cta_at:
            raise RuntimeError(f"{rel}: failed to normalize affiliate disclosure before first CTA")
    elif 'data-affiliate-disclosure=' in text.lower():
        raise RuntimeError(f"{rel}: disclosure marker remained on a page without affiliate CTA")

    if text != before:
        path.write_text(text, encoding="utf-8")
        return True
    return False

def normalize_home() -> bool:
    path = ROOT / "index.html"
    before = path.read_text(encoding="utf-8")
    text = PAGE_NOTICE_RE.sub("", before)
    text = GLOBAL_NOTICE_RE.sub("", text)
    text = LEGACY_DISCLOSURE_RE.sub("", text)

    first = AFFILIATE_CTA.search(text)
    if first:
        text = text[:first.start()] + HOME_NOTICE + "\\n" + text[first.start():]
    elif "</body>" in text:
        text = text.replace("</body>", HOME_NOTICE + "\\n</body>", 1)
    else:
        raise RuntimeError("index.html: closing body missing for homepage disclosure")

    if text.count('data-site-affiliate-disclosure="global"') != 1:
        raise RuntimeError("index.html: homepage disclosure normalization failed")
    if DISC["homepage_text"] not in text:
        raise RuntimeError("index.html: homepage disclosure text drifted from central policy")

    if text != before:
        path.write_text(text, encoding="utf-8")
        return True
    return False

def main() -> None:
    changed = 1 if normalize_home() else 0
    checked = 1
    for path in PUBLIC.rglob("*.html"):
        checked += 1
        if normalize_page(path):
            changed += 1
    print(f"Source affiliate disclosure normalization: checked={checked} changed={changed} affiliate_disclosure_gaps=0")

if __name__ == "__main__":
    main()
