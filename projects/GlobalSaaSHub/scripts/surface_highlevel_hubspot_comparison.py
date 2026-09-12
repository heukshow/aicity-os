"""Keep the HighLevel vs HubSpot buyer-intent comparison safely indexed and discoverable.

The page is hand-authored from current official vendor pricing and uses only the
already-verified COSHUMA HighLevel partner route. This guard refuses to publish if
the tracked HighLevel route or official HubSpot pricing destination disappears.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "compare" / "gohighlevel-vs-hubspot.html"
CRM_HUB = ROOT / "public" / "best" / "crm-for-marketing-agencies.html"
SITEMAP = ROOT / "public" / "sitemap.xml"
CANONICAL = "https://coshuma.com/compare/gohighlevel-vs-hubspot.html"
HIGHLEVEL = "https://www.gohighlevel.com/?fp_ref=sangkwon56"
HUBSPOT = "https://www.hubspot.com/pricing/suite"
HUB_MARKER = 'data-revenue-link="highlevel-vs-hubspot"'

HUB_BLOCK = '''\n    <section data-revenue-link="highlevel-vs-hubspot" class="mt-10 rounded-3xl border border-violet-400/25 bg-violet-500/[0.06] p-6 sm:p-8">\n      <div class="text-xs font-black uppercase tracking-[0.18em] text-violet-300">Direct agency comparison</div>\n      <h2 class="mt-2 text-2xl font-black text-white">Already down to HighLevel vs HubSpot?</h2>\n      <p class="mt-3 max-w-3xl text-sm leading-6 text-slate-300">Compare the current free/trial entry, seat economics and HighLevel sub-account model side by side before choosing a CRM stack.</p>\n      <a href="/compare/gohighlevel-vs-hubspot.html" class="mt-5 inline-flex min-h-11 items-center justify-center rounded-xl bg-violet-600 px-5 py-3 text-sm font-black text-white hover:bg-violet-500">Compare HighLevel vs HubSpot →</a>\n    </section>\n'''


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

    if not CRM_HUB.exists():
        raise SystemExit("CRM buyer hub missing; refusing orphan comparison publish")
    hub = CRM_HUB.read_text(encoding="utf-8")
    if HUB_MARKER not in hub:
        if "</main>" not in hub:
            raise SystemExit("CRM buyer hub main closing tag missing; refusing internal-link patch")
        hub = hub.replace("</main>", HUB_BLOCK + "</main>", 1)
        CRM_HUB.write_text(hub, encoding="utf-8")

    print("highlevel-vs-hubspot-revenue-surface-v2")


if __name__ == "__main__":
    main()
