"""Remove public sponsorship solicitation while COSHUMA advertising is closed.

Runs near the end of the production public-copy pipeline. It removes advertiser
inquiry blocks, advertiser navigation, and sponsorship-sales tracking from public
tool pages and the homepage. Sponsored inventory generation remains in place so
its separately disabled state is preserved; this script does not enable ads,
payments, or sponsorship checkout.
"""
from pathlib import Path
import re
import runpy
import subprocess
from prepare_sponsored_inventory import main as prepare_sponsored_inventory

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
APP = ROOT / "src" / "App.jsx"

TOOL_INQUIRY_RE = re.compile(
    r"\s*<section\b[^>]*data-sponsorship-inquiry=[\"']tool[\"'][^>]*>.*?</section>",
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
    text = re.sub(
        r'\s*<a\b[^>]*href=["\']/advertise\.html["\'][^>]*>.*?</a>',
        "",
        text,
        flags=re.I | re.S,
    )
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


def remove_advertise_from_sitemap() -> bool:
    sitemap = PUBLIC / "sitemap.xml"
    if not sitemap.exists():
        return False
    original = sitemap.read_text(encoding="utf-8")
    updated = re.sub(
        r"\s*<url>\s*<loc>https://coshuma\.com/advertise\.html</loc>.*?</url>",
        "",
        original,
        flags=re.I | re.S,
    )
    if updated == original:
        return False
    sitemap.write_text(updated, encoding="utf-8")
    return True


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
            original = page.read_text(encoding="utf-8")
            updated = strip_page(original)
            if updated != original:
                page.write_text(updated, encoding="utf-8")
                changed += 1

    home_changed = remove_home_solicitation()
    sitemap_changed = remove_advertise_from_sitemap()
    prepare_sponsored_inventory()
    run_fastlane_state_finalizers()
    print(
        "normalize_sponsorship_offer: "
        f"scanned={scanned} changed={changed} "
        f"homepage_solicitation_removed={home_changed} "
        f"advertise_sitemap_removed={sitemap_changed} "
        "advertising_inquiries=closed"
    )


if __name__ == "__main__":
    main()
