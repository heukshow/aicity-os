from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
PUBLIC = PROJECT / "public"
COMPARE = PUBLIC / "compare"
SITEMAP = PUBLIC / "sitemap.xml"
SITE = "https://coshuma.com"


def is_noindex(html: str) -> bool:
    for match in re.finditer(r'<meta\s+[^>]*name=["\']robots["\'][^>]*>', html, flags=re.I):
        if re.search(r'content=["\'][^"\']*noindex', match.group(0), flags=re.I):
            return True
    return False


def canonical_url(html: str):
    match = re.search(
        r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\'][^>]*>',
        html,
        flags=re.I,
    )
    if match:
        return match.group(1).strip()
    match = re.search(
        r'<link\s+[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\'][^>]*>',
        html,
        flags=re.I,
    )
    return match.group(1).strip() if match else None


if not SITEMAP.exists():
    raise SystemExit(f"Missing sitemap: {SITEMAP}")
if not COMPARE.exists():
    raise SystemExit(f"Missing compare directory: {COMPARE}")

sitemap = SITEMAP.read_text(encoding="utf-8")
if "</urlset>" not in sitemap:
    raise SystemExit("sitemap.xml is missing </urlset>")

entries = []
eligible_urls = []
for page in sorted(COMPARE.glob("*.html")):
    html = page.read_text(encoding="utf-8")
    if is_noindex(html):
        continue

    expected = f"{SITE}/compare/{page.name}"
    canonical = canonical_url(html)
    if canonical != expected:
        # Do not index aliases, malformed pages, or pages whose canonical points elsewhere.
        continue

    eligible_urls.append(expected)
    if f"<loc>{expected}</loc>" not in sitemap:
        entries.append(
            "  <url>\n"
            f"    <loc>{expected}</loc>\n"
            "    <changefreq>weekly</changefreq>\n"
            "    <priority>0.7</priority>\n"
            "  </url>"
        )

if entries:
    sitemap = sitemap.replace("</urlset>", "\n".join(entries) + "\n</urlset>")
    SITEMAP.write_text(sitemap, encoding="utf-8")

final_sitemap = SITEMAP.read_text(encoding="utf-8")
missing = [url for url in eligible_urls if f"<loc>{url}</loc>" not in final_sitemap]
if missing:
    raise SystemExit("Canonical compare pages missing from sitemap: " + ", ".join(missing))

print(f"Compare sitemap coverage current: {len(eligible_urls)} canonical pages; added {len(entries)} missing URLs.")
