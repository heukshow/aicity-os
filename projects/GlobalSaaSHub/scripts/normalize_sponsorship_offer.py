"""Normalize COSHUMA paid sponsorship copy and route inquiries to the ad landing page.

Runs at the very end of the production public-copy pipeline so hand-authored and
generated tool pages cannot keep stale wording that says payment does not buy a
placement. It also keeps the advertiser offer discoverable from the homepage even
when direct checkout is disabled. It does not alter editorial rankings, affiliate
URLs, or payment state.
"""
from pathlib import Path
import re
from prepare_sponsored_inventory import main as prepare_sponsored_inventory

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TOOL_DIR = PUBLIC / "tool"
APP = ROOT / "src" / "App.jsx"

SPONSORSHIP_COPY = (
    "Sponsored placement starts at USD 49. Approved sponsorships receive a clearly "
    "labeled promotional placement in designated high-visibility areas. Premium "
    "positions are priced separately based on placement and availability. Sponsorship "
    "does not change independent editorial ratings or organic rankings."
)

LEGACY_COPY_PATTERNS = [
    r"A one-time sponsored placement is USD 49\.\s*Sponsorship is reviewed separately from editorial coverage;\s*payment does not guarantee acceptance, ranking,? or an editorial rating\.",
    r"A one-time sponsored placement is USD 49\.\s*Approved sponsorships receive a clearly labeled promotional placement in designated high-visibility areas\.\s*Sponsorship does not change independent editorial ratings or organic rankings\.",
    r"Sponsorship is reviewed separately from editorial coverage\.\s*Payment does not guarantee acceptance, ranking,? or an editorial rating\.",
]

OPTIONS_LINK = (
    '<a data-cta="sponsorship-options" href="/advertise.html" '
    'class="inline-flex items-center justify-center px-5 py-3 rounded-xl border border-violet-500/30 '
    'bg-violet-500/5 text-violet-200 text-xs font-extrabold hover:bg-violet-500/10 transition-all">'
    'See sponsorship options →</a>'
)

HOME_ADVERTISE_LINK = (
    '            <a href="/advertise.html" className="rounded-full border border-violet-400/30 '
    'bg-violet-500/10 px-4 py-2 text-xs font-bold text-violet-200 hover:bg-violet-500/20 sm:text-sm">\n'
    '              Advertise\n'
    '            </a>\n'
)


def normalize_copy(text: str) -> str:
    for pattern in LEGACY_COPY_PATTERNS:
        text = re.sub(pattern, SPONSORSHIP_COPY, text, flags=re.I)
    return text


def normalize_section(section: str) -> str:
    section = normalize_copy(section)
    if '/advertise.html' in section:
        return section

    mailto = re.search(r'<a\b[^>]*href="mailto:support@coshuma\.com[^>]*>', section, flags=re.I)
    if mailto:
        return section[:mailto.start()] + OPTIONS_LINK + "\n        " + section[mailto.start():]

    first_paragraph_end = section.find("</p>")
    if first_paragraph_end >= 0:
        first_paragraph_end += len("</p>")
        return section[:first_paragraph_end] + "\n        " + OPTIONS_LINK + section[first_paragraph_end:]
    return section


def normalize_page(text: str) -> str:
    text = normalize_copy(text)
    pattern = re.compile(
        r'<section\b[^>]*data-sponsorship-inquiry="tool"[^>]*>.*?</section>',
        flags=re.I | re.S,
    )
    return pattern.sub(lambda m: normalize_section(m.group(0)), text)


def ensure_home_advertise_link() -> bool:
    if not APP.exists():
        return False
    text = APP.read_text(encoding="utf-8")
    if 'href="/advertise.html"' in text:
        return False

    anchor = '            {paymentConfig.checkoutEnabled && (\n'
    if anchor not in text:
        raise SystemExit("Could not find the homepage sponsorship navigation anchor")

    updated = text.replace(anchor, HOME_ADVERTISE_LINK + anchor, 1)
    APP.write_text(updated, encoding="utf-8")
    return True


def ensure_sitemap() -> None:
    sitemap = PUBLIC / "sitemap.xml"
    if not sitemap.exists():
        return
    text = sitemap.read_text(encoding="utf-8")
    url = "https://coshuma.com/advertise.html"
    if url not in text and "</urlset>" in text:
        text = text.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>")
        sitemap.write_text(text, encoding="utf-8")


def main() -> None:
    changed = 0
    scanned = 0
    if TOOL_DIR.exists():
        for page in TOOL_DIR.glob("*.html"):
            scanned += 1
            original = page.read_text(encoding="utf-8")
            updated = normalize_page(original)
            if updated != original:
                page.write_text(updated, encoding="utf-8")
                changed += 1
    home_changed = ensure_home_advertise_link()
    ensure_sitemap()
    prepare_sponsored_inventory()
    print(f"normalize_sponsorship_offer: scanned={scanned} changed={changed} homepage_link_added={home_changed}")


if __name__ == "__main__":
    main()
