"""Normalize consumer affiliate disclosures in generated public source.

The public source is a customer-facing surface. This pass never removes a required
page disclosure in favor of a homepage-only policy. Instead it keeps one canonical
consumer disclosure before the first affiliate CTA on every affiliate page, keeps
one general homepage disclosure, and removes stray page disclosures only from pages
that do not contain an affiliate CTA. Internal affiliate operations data is handled
by the separate fail-closed source boundary guards.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
POLICY = json.loads((ROOT / "config" / "public_content_policy.json").read_text(encoding="utf-8"))
DISCLOSURE = POLICY["affiliate_disclosure"]

PAGE_AFFILIATE_CTA = re.compile(
    r'<a\b[^>]*\bdata-cta\s*=\s*["\']affiliate["\'][^>]*>',
    re.I,
)
PAGE_MARKED_BLOCK = re.compile(
    r'<p\b[^>]*\bdata-affiliate-disclosure\s*=\s*["\'][^"\']*["\'][^>]*>.*?</p>\s*',
    re.I | re.S,
)
HOME_MARKED_BLOCK = re.compile(
    r'<p\b[^>]*\bdata-site-affiliate-disclosure\s*=\s*["\'][^"\']*["\'][^>]*>.*?</p>\s*',
    re.I | re.S,
)
GENERIC_DISCLOSURE_PARAGRAPH = re.compile(
    r'<p\b[^>]*>(?:(?!</p>).)*Affiliate\s+disclosure\s*:(?:(?!</p>).)*</p>\s*',
    re.I | re.S,
)

PAGE_DISCLOSURE = (
    '<p data-affiliate-disclosure="page" '
    'style="margin:.75rem 0;color:#94a3b8;font-size:12px;line-height:1.6">'
    f'{DISCLOSURE["page_text"]}'
    '</p>\n'
)
HOME_DISCLOSURE = (
    '<p data-site-affiliate-disclosure="global" '
    'style="max-width:72rem;margin:0 auto;padding:0 1.5rem 1.5rem;color:#94a3b8;font-size:12px;line-height:1.6">'
    f'{DISCLOSURE["homepage_text"]} '
    f'<a href="{DISCLOSURE["details_path"]}" style="text-decoration:underline">Details</a>.'
    '</p>\n'
)


def strip_consumer_disclosures(html: str) -> str:
    html = PAGE_MARKED_BLOCK.sub('', html)
    html = HOME_MARKED_BLOCK.sub('', html)
    html = GENERIC_DISCLOSURE_PARAGRAPH.sub('', html)
    return html


def normalize_page(html: str) -> str:
    html = strip_consumer_disclosures(html)
    first_cta = PAGE_AFFILIATE_CTA.search(html)
    if not first_cta:
        return html
    return html[:first_cta.start()] + PAGE_DISCLOSURE + html[first_cta.start():]


def normalize_home(html: str) -> str:
    html = strip_consumer_disclosures(html)
    first_cta = PAGE_AFFILIATE_CTA.search(html)
    if first_cta:
        return html[:first_cta.start()] + HOME_DISCLOSURE + html[first_cta.start():]
    body_end = html.lower().rfind('</body>')
    if body_end >= 0:
        return html[:body_end] + HOME_DISCLOSURE + html[body_end:]
    return html + '\n' + HOME_DISCLOSURE


def validate_page(path: Path, html: str) -> None:
    cta = PAGE_AFFILIATE_CTA.search(html)
    marker = 'data-affiliate-disclosure="page"'
    count = html.count(marker)
    if cta:
        if count != 1:
            raise RuntimeError(f'{path.relative_to(ROOT)}: affiliate CTA page must contain exactly one consumer disclosure')
        if html.find(marker) > cta.start():
            raise RuntimeError(f'{path.relative_to(ROOT)}: consumer disclosure must appear before the first affiliate CTA')
    elif count:
        raise RuntimeError(f'{path.relative_to(ROOT)}: page without affiliate CTA must not contain a page disclosure')


def validate_home(html: str) -> None:
    marker = 'data-site-affiliate-disclosure="global"'
    if html.count(marker) != 1:
        raise RuntimeError('index.html: homepage must contain exactly one general affiliate disclosure')


def main() -> None:
    changed = 0
    affiliate_pages = 0
    checked = 0

    home = ROOT / 'index.html'
    if home.exists():
        before = home.read_text(encoding='utf-8')
        after = normalize_home(before)
        validate_home(after)
        if after != before:
            home.write_text(after, encoding='utf-8')
            changed += 1
        checked += 1

    for path in PUBLIC.rglob('*.html'):
        if path.name == 'affiliate-disclosure.html':
            continue
        checked += 1
        before = path.read_text(encoding='utf-8')
        after = normalize_page(before)
        validate_page(path, after)
        if PAGE_AFFILIATE_CTA.search(after):
            affiliate_pages += 1
        if after != before:
            path.write_text(after, encoding='utf-8')
            changed += 1

    print(
        f'Source affiliate disclosures normalized: checked={checked} '
        f'affiliate_pages={affiliate_pages} changed={changed} missing=0 duplicates=0'
    )


if __name__ == '__main__':
    main()
