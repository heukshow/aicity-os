"""Preserve the dedicated advertising application and remove obsolete sales copy.

The 2026-10-04 reopening accepts applications on advertise.html. Legacy inline
sales blocks stay removed, including from the protected homepage. Payment and
placement activation remain dependent on server verification.
"""
from pathlib import Path
from html import escape
import json
import re
import runpy
import subprocess
from prepare_sponsored_inventory import main as prepare_sponsored_inventory

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
APP = ROOT / "src" / "App.jsx"
SPONSORSHIP_PAGES = {"advertise.html", "sponsorship.html"}

TOOL_INQUIRY_RE = re.compile(
    r"\s*<section\b(?:(?!<section\b).)*?(?:"
    r"data-sponsorship-inquiry=[\"']tool[\"']|"
    r"Request\s+a\s+COSHUMA\s+sponsored\s+placement|"
    r"Email\s+a\s+sponsorship\s+request|"
    r"Ask\s+about\s+(?:the\s+\$49\s+standard\s+placement|sponsorship)|"
    r"mailto:support@coshuma\.com[^\"']*(?:sponsor|advertis)"
    r")(?:(?!<section\b).)*?</section>",
    flags=re.I | re.S,
)
SPONSORSHIP_SALES_SCRIPT_RE = re.compile(
    r"\s*<script\b[^>]*src=[\"']/sponsorship-sales\.js[\"'][^>]*></script>",
    flags=re.I | re.S,
)
HOME_ADVERTISE_LINK_RE = re.compile(
    r"\s*<a\b[^>]*href=[\"']/advertise\.html[\"'][^>]*>\s*Advertise\s*</a>",
    flags=re.I | re.S,
)


def strip_page(text: str) -> str:
    text = TOOL_INQUIRY_RE.sub("", text)
    text = SPONSORSHIP_SALES_SCRIPT_RE.sub("", text)
    return text


def remove_home_solicitation() -> bool:
    if not APP.exists():
        return False
    original = APP.read_text(encoding="utf-8")
    updated = HOME_ADVERTISE_LINK_RE.sub("", original)
    updated = re.sub(
        r'\s*<section\s+id="submit"\b[^>]*>.*?</section>',
        "",
        updated,
        flags=re.I | re.S,
    )
    if updated == original:
        return False
    APP.write_text(updated, encoding="utf-8")
    return True


def ensure_advertise_in_sitemap() -> bool:
    sitemap = PUBLIC / "sitemap.xml"
    if not sitemap.exists():
        return False
    original = sitemap.read_text(encoding="utf-8")
    if '<loc>https://coshuma.com/advertise.html</loc>' in original:
        return False
    updated = original.replace('</urlset>', '<url><loc>https://coshuma.com/advertise.html</loc><changefreq>monthly</changefreq></url>\n</urlset>', 1)
    if updated == original:
        return False
    sitemap.write_text(updated, encoding="utf-8")
    return True


def sync_advertise_catalog() -> None:
    """Keep displayed rates and form choices tied to the existing product table."""
    page = PUBLIC / "advertise.html"
    source = json.loads((ROOT / "data/sponsorship-inventory.json").read_text(encoding="utf-8"))
    catalog = [{"slot": slot, "label": item["package_name"],
                "prices": {str(days): f'{item["pricing"][f"{days}_days"]:.2f}' for days in (7, 30, 90)},
                "allowedPages": item["requestable_pages"]}
               for slot, item in source["placements"].items()]
    rows = ''.join('<tr><th scope="row">' + escape(item['label']) + '</th>'
                   + ''.join('<td>$' + f'{float(item["prices"][str(days)]):g}' + '</td>' for days in (7, 30, 90))
                   + '</tr>' for item in catalog)
    prices = '<div class="table-wrap"><table><caption>USD per placement. The agreed period starts when your card goes live, not when you submit or pay.</caption><thead><tr><th scope="col">Placement</th><th scope="col">7 days</th><th scope="col">30 days</th><th scope="col">90 days</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
    payload = json.dumps({"currency": source["currency"], "catalog": catalog}, separators=(',', ':')).replace('<', '\\u003c')
    catalog_script = '<script id="sponsorship-public-catalog" type="application/json">' + payload + '</script>'
    original = page.read_text(encoding="utf-8")
    updated = original
    for marker, value in (("PRICES", prices), ("CATALOG", catalog_script)):
        pattern = r'(<!-- COSHUMA_SPONSORSHIP_' + marker + r'_START -->).*?(<!-- COSHUMA_SPONSORSHIP_' + marker + r'_END -->)'
        updated, count = re.subn(pattern, lambda match: match[1] + '\n        ' + value + '\n        ' + match[2], updated, flags=re.S)
        if count != 1:
            raise RuntimeError(f"Advertising {marker.lower()} marker missing or duplicated")
    if updated != original:
        page.write_text(updated, encoding="utf-8")


def run_fastlane_state_finalizers() -> None:
    for script_name in (
        "ensure_scribe_fastlane.mjs",
        "ensure_landingi_fastlane.mjs",
        "ensure_leadpages_fastlane.mjs",
        "ensure_instapage_fastlane.mjs",
        "ensure_popupsmart_fastlane.mjs",
        "ensure_poptin_fastlane.mjs",
        "ensure_optimonk_fastlane.mjs",
    ):
        subprocess.run(["node", str(ROOT / "scripts" / script_name)], cwd=ROOT, check=True)


def main() -> None:
    for script_name in ("improve_verified_offer_discovery.py",):
        try:
            runpy.run_path(str(ROOT / "scripts" / script_name), run_name="__main__")
        except SystemExit as exc:
            if exc.code not in (None, 0):
                raise

    changed = 0
    scanned = 0
    if PUBLIC.exists():
        for page in PUBLIC.rglob("*.html"):
            scanned += 1
            if page.relative_to(PUBLIC).as_posix() in SPONSORSHIP_PAGES:
                continue
            original = page.read_text(encoding="utf-8")
            updated = strip_page(original)
            if updated != original:
                page.write_text(updated, encoding="utf-8")
                changed += 1

    home_changed = remove_home_solicitation()
    sitemap_changed = ensure_advertise_in_sitemap()
    sync_advertise_catalog()
    prepare_sponsored_inventory()
    run_fastlane_state_finalizers()
    print(
        "normalize_sponsorship_offer: "
        f"scanned={scanned} changed={changed} "
        f"homepage_solicitation_removed={home_changed} "
        f"advertise_sitemap_added={sitemap_changed} "
        "advertising_applications=open; checkout=server_verified_only"
    )


if __name__ == "__main__":
    main()
