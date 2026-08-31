"""SEO, English-only, and revenue-link contract for public GlobalSaaSHub pages."""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PUBLIC = PROJECT / "public"
BASE_URL = "https://coshuma.com"
HANGUL = re.compile(r"[\uac00-\ud7a3]")
CANONICAL = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"')
JSON_LD = re.compile(r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>', re.S)


def main():
    errors = []
    pages = [PROJECT / "index.html"] + sorted((PUBLIC / "tool").glob("*.html")) + sorted((PUBLIC / "compare").glob("*.html"))
    expected_urls = {f"{BASE_URL}/"}

    for path in pages:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(PROJECT)
        if HANGUL.search(text):
            errors.append(f"Hangul found in English public page: {relative}")

        match = CANONICAL.search(text)
        if not match:
            errors.append(f"Missing canonical: {relative}")
        else:
            expected_urls.add(match.group(1))

        blocks = JSON_LD.findall(text)
        if not blocks:
            errors.append(f"Missing JSON-LD: {relative}")
        for block in blocks:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"Invalid JSON-LD in {relative}: {exc}")

        if path.parent.name == "compare":
            slugs = path.stem.split("-vs-")
            if len(slugs) != 2 or any(f'href="/tool/{slug}.html"' not in text for slug in slugs):
                errors.append(f"Missing comparison-to-tool internal links: {relative}")

    tools = json.loads((PROJECT / "data" / "tools.json").read_text(encoding="utf-8"))
    for tool in tools:
        if tool.get("affiliate_verified") is not True or tool.get("affiliate_status") != "approved_tracking":
            continue
        affiliate_url = tool.get("affiliate_url")
        if not affiliate_url:
            errors.append(f"Verified affiliate missing URL in tools.json: {tool.get('id')}")
            continue
        page = PUBLIC / "tool" / f"{tool['id']}.html"
        if not page.exists():
            errors.append(f"Verified affiliate missing static tool page: {tool['id']}")
            continue
        text = page.read_text(encoding="utf-8")
        if 'data-cta="affiliate"' not in text or f'href="{affiliate_url}"' not in text:
            errors.append(f"Verified affiliate CTA drift: {tool['id']}")

    root = ET.parse(PUBLIC / "sitemap.xml").getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in root.findall("sm:url/sm:loc", namespace)}
    missing = sorted(expected_urls - sitemap_urls)
    if missing:
        errors.append(f"Canonical URLs missing from sitemap: {len(missing)}")

    robots = (PUBLIC / "robots.txt").read_text(encoding="utf-8")
    if "User-agent: *" not in robots or f"Sitemap: {BASE_URL}/sitemap.xml" not in robots:
        errors.append("robots.txt does not expose the canonical sitemap")

    if errors:
        print(f"PUBLIC SEO INTEGRITY: FAIL ({len(errors)} errors)")
        for error in errors[:50]:
            print(f"- {error}")
        return 1
    print(f"PUBLIC SEO INTEGRITY: PASS ({len(pages)} English pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
