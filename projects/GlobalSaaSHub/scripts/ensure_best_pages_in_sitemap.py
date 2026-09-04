from pathlib import Path
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
for page in sorted(BEST_DIR.glob("*.html")):
    url = f"{BASE_URL}/best/{page.name}"
    if url in existing:
        continue
    url_node = ET.SubElement(root, f"{{{NS}}}url")
    ET.SubElement(url_node, f"{{{NS}}}loc").text = url
    ET.SubElement(url_node, f"{{{NS}}}changefreq").text = "weekly"
    ET.SubElement(url_node, f"{{{NS}}}priority").text = "0.9"
    added.append(url)

ET.indent(tree, space="  ")
tree.write(SITEMAP, encoding="utf-8", xml_declaration=True)
print(f"Sitemap buyer hubs: {len(list(BEST_DIR.glob('*.html')))} total, {len(added)} added")
for url in added:
    print(f"+ {url}")
