"""Self-heal generated source HTML before the production bundle is built.

Policy:
- the dedicated affiliate-disclosure policy page is preserved;
- customer tool/compare/best/category/etc. pages must not carry repeated general
  commission notices;
- the homepage source must not carry a second semantic commission notice;
- the final production-bundle guard adds exactly one global homepage notice.

Normal steady state is changed=0 because content generators must not create page-level
affiliate disclosures in the first place. This pass exists only as a last-resort
repair and safety stop for a future regression, not as part of the normal content
production path. It raises if a prohibited notice still remains after repair.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

BLOCK_PATTERNS = [
    re.compile(
        r'<p\b[^>]*>(?:(?!</p>).)*(?:Affiliate\s+disclosure\s*:|COSHUMA\s+may\s+earn\s+(?:(?:an\s+affiliate|a)\s+)?commission|may\s+earn\s+COSHUMA\s+a\s+commission)(?:(?!</p>).)*</p>',
        re.I | re.S,
    ),
    re.compile(
        r'<(?:div|section|aside)\b[^>]*>\s*(?:<strong\b[^>]*>)?\s*Affiliate\s+disclosure\s*:.*?</(?:div|section|aside)>',
        re.I | re.S,
    ),
]
MARKER_RE = re.compile(r'\s+data-affiliate-disclosure\s*=\s*["\'][^"\']*["\']', re.I)
INLINE_DISCLOSURE_RE = re.compile(r'\s*Affiliate\s+disclosure\s*:\s*[^<]*', re.I)
INLINE_COMMISSION_RE = re.compile(
    r'\s*COSHUMA\s+may\s+earn\s+(?:(?:an\s+affiliate|a)\s+)?commission[^<]*', re.I
)
HOME_SEMANTIC_DISCLOSURE = re.compile(
    r'<li><strong([^>]*)>Clear disclosure:</strong>\s*some outbound links may earn COSHUMA a commission, without changing the buyer\'s price\.</li>',
    re.I,
)
HOME_INTERNAL_LINK_COPY = re.compile(
    r'<li><strong([^>]*)>Separate link verification:</strong>\s*affiliate destinations are verified independently from editorial pricing sources\.</li>',
    re.I,
)


def strip_general_notice(html: str) -> str:
    for pattern in BLOCK_PATTERNS:
        html = pattern.sub('', html)
    html = MARKER_RE.sub('', html)
    html = INLINE_DISCLOSURE_RE.sub('', html)
    html = INLINE_COMMISSION_RE.sub('', html)
    return html


def normalize_home(html: str) -> str:
    html = HOME_SEMANTIC_DISCLOSURE.sub(
        r'<li><strong\1>Final-term check:</strong> pricing, eligibility and vendor terms can change, so confirm them before purchasing.</li>',
        html,
    )
    html = HOME_INTERNAL_LINK_COPY.sub(
        r'<li><strong\1>Direct vendor links:</strong> outbound destinations are checked before publication.</li>',
        html,
    )
    return strip_general_notice(html)


def prohibited(html: str) -> bool:
    return bool(
        re.search(r'Affiliate\s+disclosure\s*:', html, re.I)
        or re.search(r'COSHUMA\s+may\s+earn\s+(?:(?:an\s+affiliate|a)\s+)?commission', html, re.I)
        or re.search(r'may\s+earn\s+COSHUMA\s+a\s+commission', html, re.I)
        or 'data-affiliate-disclosure=' in html.lower()
    )


def main() -> None:
    targets = [ROOT / 'index.html', *PUBLIC.rglob('*.html')]
    changed = 0
    checked = 0
    repaired = []

    for path in targets:
        if path.name == 'affiliate-disclosure.html':
            continue
        checked += 1
        before = path.read_text(encoding='utf-8')
        after = normalize_home(before) if path == ROOT / 'index.html' else strip_general_notice(before)
        if after != before:
            path.write_text(after, encoding='utf-8')
            changed += 1
            repaired.append(path.relative_to(ROOT).as_posix())
        if prohibited(after):
            raise RuntimeError(f'Unable to self-heal repeated affiliate disclosure in {path.relative_to(ROOT)}')

    print(
        f'Source affiliate disclosure self-heal: checked={checked} changed={changed} '
        f'remaining_repeated_notices=0'
    )
    if repaired:
        print('Repaired source pages:', ', '.join(repaired[:20]) + (' ...' if len(repaired) > 20 else ''))


if __name__ == '__main__':
    main()
