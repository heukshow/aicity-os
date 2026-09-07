from pathlib import Path
from html.parser import HTMLParser
import json
import xml.etree.ElementTree as ET

BASE_URL = "https://coshuma.com"
PROJECT = Path(__file__).resolve().parents[1]
PUBLIC = PROJECT / "public"
SITEMAP = PUBLIC / "sitemap.xml"
BEST_DIR = PUBLIC / "best"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

ET.register_namespace("", NS)

tree = ET.parse(SITEMAP)
root = tree.getroot()
existing = {
    node.text.strip()
    for node in root.findall(f"{{{NS}}}url/{{{NS}}}loc")
    if node.text and node.text.strip()
}

added = []


def add_url(url: str, priority: str = "0.9") -> None:
    if url in existing:
        return
    url_node = ET.SubElement(root, f"{{{NS}}}url")
    ET.SubElement(url_node, f"{{{NS}}}loc").text = url
    ET.SubElement(url_node, f"{{{NS}}}changefreq").text = "weekly"
    ET.SubElement(url_node, f"{{{NS}}}priority").text = priority
    existing.add(url)
    added.append(url)


best_pages = sorted(BEST_DIR.glob("*.html"))
for page in best_pages:
    add_url(f"{BASE_URL}/best/{page.name}", "0.9")


class IndexablePage(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.canonicals = []
        self.noindex = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonicals.append(attrs.get("href"))
        if tag == "meta" and attrs.get("name", "").lower() in ("robots", "googlebot"):
            self.noindex |= "noindex" in attrs.get("content", "").lower()


# Scan the finished pages, including hand-written pages omitted by generators.
# Only index self-canonical pages; aliases and explicitly noindexed pages stay out.
tool_ids = {tool["id"] for tool in json.loads((PROJECT / "data/tools.json").read_text(encoding="utf-8"))}
tool_ids.update(json.loads((PROJECT / "data/standalone_tool_pages.json").read_text(encoding="utf-8")))
for directory in ("tool", "compare"):
    for page in sorted((PUBLIC / directory).glob("*.html")):
        if directory == "tool" and page.stem not in tool_ids:
            continue  # Do not promote orphaned detail pages outside the catalog.
        url = f"{BASE_URL}/{directory}/{page.name}"
        parsed = IndexablePage(page.read_text(encoding="utf-8"))
        if parsed.canonicals == [url] and not parsed.noindex:
            add_url(url, "0.8" if directory == "tool" else "0.7")

# Root-level buyer-intent landing pages are hand-written and are not emitted by
# generate_seo_pages.py. Include only pages that contain an affiliate CTA and a
# matching canonical URL so legal/policy pages do not enter the revenue sitemap.
root_revenue_pages = []
for page in sorted(PUBLIC.glob("*.html")):
    text = page.read_text(encoding="utf-8")
    canonical = f"{BASE_URL}/{page.name}"
    if 'data-cta="affiliate"' not in text or canonical not in text:
        continue
    root_revenue_pages.append(page)
    add_url(canonical, "0.9")

ET.indent(tree, space="  ")
tree.write(SITEMAP, encoding="utf-8", xml_declaration=True)
print(
    "Sitemap buyer hubs: "
    f"best={len(best_pages)} root_revenue={len(root_revenue_pages)} added={len(added)}"
)
for url in added:
    print(f"+ {url}")
