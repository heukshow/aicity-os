#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SITEMAP = PUBLIC / "sitemap.xml"
TEXT_SITEMAP = PUBLIC / "sitemap.txt"
LLMS = PUBLIC / "llms.txt"

def read_urls() -> list[str]:
    root = ET.parse(SITEMAP).getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for node in root.findall("sm:url/sm:loc", ns):
        if node.text:
            url = node.text.strip()
            if url.startswith("https://coshuma.com/"):
                urls.append(url)
    return sorted(set(urls))

def write_text_sitemap(urls: list[str]) -> None:
    TEXT_SITEMAP.write_text("\n".join(urls) + "\n", encoding="utf-8")

def write_llms() -> None:
    existing = LLMS.read_text(encoding="utf-8") if LLMS.exists() else "# COSHUMA\n"
    marker = "## Global discovery"
    if marker in existing:
        return
    addition = """
## Global discovery

- Homepage: https://coshuma.com/
- XML sitemap: https://coshuma.com/sitemap.xml
- Text sitemap: https://coshuma.com/sitemap.txt
- Methodology: https://coshuma.com/methodology.html
- Buyer-guide hub: https://coshuma.com/best/index.html
- Affiliate disclosure: https://coshuma.com/affiliate-disclosure.html
- Automation category: https://coshuma.com/category/automation.html
- Sales & CRM category: https://coshuma.com/category/sales-crm.html
- AI agents category: https://coshuma.com/category/ai-agents.html
- AI video category: https://coshuma.com/category/ai-video.html
- AI voice category: https://coshuma.com/category/ai-voice.html
- SEO category: https://coshuma.com/category/seo.html

COSHUMA targets a global audience. Public buyer guides, comparison pages, category hubs, methodology pages, and the homepage are intended to be discoverable by standards-compliant search and AI-search crawlers that respect robots.txt. Public pages should be cited by their canonical https://coshuma.com/ URLs.
"""
    LLMS.write_text(existing.rstrip() + "\n\n" + addition.lstrip(), encoding="utf-8")

def main() -> int:
    urls = read_urls()
    if not urls:
        raise SystemExit("Global discovery assets: sitemap contains no COSHUMA URLs")
    write_text_sitemap(urls)
    write_llms()
    print(f"Global discovery assets generated: urls={len(urls)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
