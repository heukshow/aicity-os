"""Keep the HighLevel vs HubSpot buyer-intent comparison safely indexed.

The page is hand-authored from current official vendor pricing and uses only the
already-verified COSHUMA HighLevel partner route. This guard refuses to publish if
the tracked HighLevel route or official HubSpot pricing destination disappears.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "compare" / "gohighlevel-vs-hubspot.html"
SITEMAP = ROOT / "public" / "sitemap.xml"
CANONICAL = "https://coshuma.com/compare/gohighlevel-vs-hubspot.html"
HIGHLEVEL = "https://www.gohighlevel.com/?fp_ref=sangkwon56"
HUBSPOT = "https://www.hubspot.com/pricing/suite"


def main() -> None:
    if not PAGE.exists():
        raise SystemExit("HighLevel vs HubSpot comparison missing; refusing revenue surface")

    html = PAGE.read_text(encoding="utf-8")
    required = (
        CANONICAL,
        HIGHLEVEL,
        HUBSPOT,
        'data-cta="affiliate" data-tool-id="gohighlevel"',
        'data-cta="official" data-tool-id="hubspot"',
        "No signup, paid conversion or revenue is inferred from a click.",
    )
    for token in required:
        if token not in html:
            raise SystemExit(f"HighLevel vs HubSpot safety check failed: {token}")

    if not SITEMAP.exists():
        raise SystemExit("Sitemap missing; refusing unindexed comparison publish")
    sitemap = SITEMAP.read_text(encoding="utf-8")
    if CANONICAL not in sitemap:
        if "</urlset>" not in sitemap:
            raise SystemExit("Sitemap closing tag missing; refusing comparison index patch")
        entry = (
            "  <url>\n"
            f"    <loc>{CANONICAL}</loc>\n"
            "    <changefreq>weekly</changefreq>\n"
            "    <priority>0.82</priority>\n"
            "  </url>\n"
        )
        sitemap = sitemap.replace("</urlset>", entry + "</urlset>", 1)
        SITEMAP.write_text(sitemap, encoding="utf-8")

    print("highlevel-vs-hubspot-revenue-surface-v1")


if __name__ == "__main__":
    main()
