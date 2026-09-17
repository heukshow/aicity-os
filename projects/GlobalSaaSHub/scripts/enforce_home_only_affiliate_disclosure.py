"""Enforce COSHUMA policy: one general affiliate disclosure on the homepage only."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

BLOCK_PATTERNS = [
    re.compile(
        r'<p\b[^>]*>(?:(?!</p>).)*(?:Affiliate\s+disclosure\s*:|COSHUMA\s+may\s+earn\s+(?:an\s+affiliate\s+)?commission)(?:(?!</p>).)*</p>',
        re.I | re.S,
    ),
    re.compile(
        r'<div\b[^>]*>\s*(?:<strong\b[^>]*>)?\s*Affiliate\s+disclosure\s*:.*?</div>',
        re.I | re.S,
    ),
    re.compile(
        r'<section\b[^>]*>\s*(?:<strong\b[^>]*>)?\s*Affiliate\s+disclosure\s*:.*?</section>',
        re.I | re.S,
    ),
    re.compile(
        r'<aside\b[^>]*>\s*(?:<strong\b[^>]*>)?\s*Affiliate\s+disclosure\s*:.*?</aside>',
        re.I | re.S,
    ),
]
DISCLOSURE_ATTR = re.compile(
    r'\s+data-affiliate-disclosure\s*=\s*["\'][^"\']*["\']', re.I
)
OLD_GLOBAL = re.compile(
    r'<p\b[^>]*\bdata-site-affiliate-disclosure=["\']global["\'][^>]*>.*?</p>',
    re.I | re.S,
)
# Some legacy templates append the disclosure to an otherwise useful text node,
# e.g. "Product sources: ... Affiliate disclosure: ...". Remove only the
# disclosure clause and preserve the useful buyer/source copy before it.
INLINE_DISCLOSURE_TEXT = re.compile(
    r'\s*Affiliate\s+disclosure\s*:\s*[^<]*',
    re.I,
)
INLINE_COMMISSION_TEXT = re.compile(
    r'\s*COSHUMA\s+may\s+earn\s+(?:an\s+affiliate\s+)?commission[^<]*',
    re.I,
)
# Legacy homepage fallback copy used a second, semantically identical disclosure
# sentence in the methodology list. Replace it with a buyer-safety check so the
# homepage has one—and only one—commission disclosure.
HOME_SEMANTIC_DISCLOSURE = re.compile(
    r'<li><strong([^>]*)>Clear disclosure:</strong>\s*some outbound links may earn COSHUMA a commission, without changing the buyer\'s price\.</li>',
    re.I,
)
HOME_INTERNAL_LINK_COPY = re.compile(
    r'<li><strong([^>]*)>Separate link verification:</strong>\s*affiliate destinations are verified independently from editorial pricing sources\.</li>',
    re.I,
)
HOME_NOTICE = (
    '<p data-site-affiliate-disclosure="global" '
    'style="max-width:72rem;margin:0 auto;padding:0 1.5rem 1.5rem;color:#94a3b8;font-size:12px;line-height:1.6">'
    'Affiliate disclosure: COSHUMA may earn a commission from some links, at no extra cost to you. '
    '<a href="/affiliate-disclosure.html" style="text-decoration:underline">Details</a>.'
    '</p>'
)


def strip_notice_blocks(html: str) -> str:
    for pattern in BLOCK_PATTERNS:
        html = pattern.sub('', html)
    html = DISCLOSURE_ATTR.sub('', html)
    html = OLD_GLOBAL.sub('', html)
    html = INLINE_DISCLOSURE_TEXT.sub('', html)
    html = INLINE_COMMISSION_TEXT.sub('', html)
    return html


def normalize_homepage_support_copy(html: str) -> str:
    html = HOME_SEMANTIC_DISCLOSURE.sub(
        r'<li><strong\1>Final-term check:</strong> pricing, eligibility and vendor terms can change, so confirm them before purchasing.</li>',
        html,
    )
    html = HOME_INTERNAL_LINK_COPY.sub(
        r'<li><strong\1>Direct vendor links:</strong> outbound destinations are checked before publication.</li>',
        html,
    )
    return html


def main() -> None:
    if not DIST.exists():
        raise RuntimeError('dist/ missing; run vite build first')

    changed = 0
    checked = 0
    for path in DIST.rglob('*.html'):
        rel = path.relative_to(DIST).as_posix()
        html = path.read_text(encoding='utf-8')
        before = html
        checked += 1

        if rel != 'affiliate-disclosure.html':
            html = strip_notice_blocks(html)

        if rel == 'index.html':
            html = normalize_homepage_support_copy(html)
            if '</body>' not in html:
                raise RuntimeError('Homepage closing body tag missing')
            html = html.replace('</body>', HOME_NOTICE + '\n</body>', 1)
            if html.count('data-site-affiliate-disclosure="global"') != 1:
                raise RuntimeError('Homepage must contain exactly one global affiliate disclosure')
            if html.lower().count('affiliate disclosure:') != 1:
                raise RuntimeError('Homepage must contain exactly one affiliate disclosure notice')
            semantic_commission_mentions = len(re.findall(
                r'(?:COSHUMA\s+may\s+earn\s+(?:an\s+affiliate\s+)?commission|may\s+earn\s+COSHUMA\s+a\s+commission)',
                html,
                re.I,
            ))
            if semantic_commission_mentions != 1:
                raise RuntimeError(
                    f'Homepage must contain exactly one commission disclosure; found {semantic_commission_mentions}'
                )
            if re.search(r'Separate\s+link\s+verification|affiliate\s+destinations\s+are\s+verified\s+independently', html, re.I):
                raise RuntimeError('Homepage contains customer-visible internal link-verification wording')
        elif rel != 'affiliate-disclosure.html':
            if re.search(r'Affiliate\s+disclosure\s*:', html, re.I):
                raise RuntimeError(f'Repeated affiliate disclosure remains in {rel}')
            if re.search(r'COSHUMA\s+may\s+earn\s+(?:an\s+affiliate\s+)?commission', html, re.I):
                raise RuntimeError(f'Repeated commission disclosure remains in {rel}')
            if 'data-affiliate-disclosure=' in html.lower():
                raise RuntimeError(f'Repeated disclosure marker remains in {rel}')

        if html != before:
            path.write_text(html, encoding='utf-8')
            changed += 1

    print(f'Homepage-only affiliate disclosure policy: checked={checked} changed={changed} homepage_notice=1 semantic_commission_notice=1 repeated_page_notices=0')


if __name__ == '__main__':
    main()
