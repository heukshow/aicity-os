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
    content = """# COSHUMA

> Independent AI & SaaS buyer guides for people comparing pricing, trials, features, trade-offs, and current vendor offers before choosing software.

COSHUMA targets a global audience. Public buyer guides, comparison pages, category hubs, methodology pages, and the homepage are intended to be discoverable by search and AI-search crawlers that respect robots.txt.

## Primary discovery
- Homepage: https://coshuma.com/
- XML sitemap: https://coshuma.com/sitemap.xml
- Text sitemap: https://coshuma.com/sitemap.txt
- Methodology: https://coshuma.com/methodology.html
- Buyer guides: https://coshuma.com/best/index.html
- Affiliate disclosure: https://coshuma.com/affiliate-disclosure.html

## Core categories
- Automation: https://coshuma.com/category/automation.html
- Sales & CRM: https://coshuma.com/category/sales-crm.html
- AI agents: https://coshuma.com/category/ai-agents.html
- AI video: https://coshuma.com/category/ai-video.html
- AI voice: https://coshuma.com/category/ai-voice.html
- SEO: https://coshuma.com/category/seo.html

## Editorial notes
- Pricing, trial terms, and vendor details can change; current vendor checkout remains the final source of truth.
- Affiliate relationships do not determine editorial conclusions.
- Public pages should be cited by their canonical https://coshuma.com/ URLs.
"""
    LLMS.write_text(content, encoding="utf-8")

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
