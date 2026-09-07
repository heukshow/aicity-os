"""Focused source/dist/live SEO checks and sitemap discovery regression."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[2]
BASE = "https://coshuma.com"
PAGES = ["tool/tagshop-ai.html", "compare/tagshop-ai-vs-tubebuddy.html",
         "compare/tagshop-ai-vs-outlierkit.html", "tool/catalister.html",
         "compare/catalister-vs-kinsta.html", "compare/catalister-vs-quillbot.html"]
source = sys.argv[1] if len(sys.argv) > 1 else "public"

def read(path):
    if source == "live":
        with urlopen(f"{BASE}/{path}", timeout=30) as response:
            assert response.status == 200
            return response.read().decode("utf-8")
    return (PROJECT / source / path).read_text(encoding="utf-8")

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.meta, self.canonical, self.links = {}, [], []
        self.feed(text)
        self.title = re.findall(r"<title>(.*?)</title>", text, re.S)
        self.schemas = [json.loads(s) for s in re.findall(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.S)]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            self.meta.setdefault(a.get("name", a.get("property")), []).append(a.get("content"))
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical.append(a.get("href"))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])

sitemap = ET.fromstring(read("sitemap.xml"))
assert sitemap.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset"
urls = [n.text for n in sitemap.findall("{*}url/{*}loc")]
assert len(urls) == len(set(urls)), "Duplicate sitemap URLs"
assert all(u.startswith(BASE + "/") for u in urls)
robots = RobotFileParser()
robots.parse(read("robots.txt").splitlines())
assert BASE + "/sitemap.xml" in robots.site_maps()
titles, descriptions = set(), set()
parsed = {}
for path in PAGES:
    text = read(path)
    page = parsed[path] = Page(text)
    url = BASE + "/" + path
    assert url in urls, path
    assert robots.can_fetch("Googlebot", url), path
    assert page.canonical == [url], path
    assert len(page.title) == 1 and page.title[0].strip(), path
    assert page.title[0] not in titles, path
    titles.add(page.title[0])
    for key in ("description", "og:title", "og:description", "og:url", "og:type"):
        assert len(page.meta.get(key, [])) == 1 and page.meta[key][0].strip(), (path, key)
    assert page.meta["og:url"] == [url]
    assert page.meta["description"][0] not in descriptions, path
    descriptions.add(page.meta["description"][0])
    assert page.schemas and all(s.get("@context") == "https://schema.org" and s.get("@type") for s in page.schemas)
    for href in page.links:
        if href.startswith(("/tool/", "/compare/")):
            assert (PROJECT / "public" / urlsplit(href).path.lstrip("/")).is_file(), (path, href)
    if path.startswith("compare/"):
        assert "/tool/" + path.split("/")[1].split("-vs-")[0] + ".html" in page.links
    if path == "tool/tagshop-ai.html":
        assert "data-cta=\"affiliate\"" not in text
        assert "UGC-style video ads" in page.meta["description"][0]
        assert "Discover features, pricing (" not in page.meta["description"][0]
        assert not re.search(r"[$€£]\s*\d", page.meta["description"][0])
    print("PASS", source, path)

for path in PAGES[3:]:
    assert any("/" + path in p.links or BASE + "/" + path in p.links
               for other, p in parsed.items() if other != path), ("Missing internal inbound link", path)

if source != "live":
    # Exercise missing pages, canonical aliases, noindex and idempotence in isolation.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir()
        (root / "data").mkdir()
        (root / "data/tools.json").write_text('[{"id":"new"},{"id":"alias"},{"id":"private"}]')
        public = root / "public"
        public.mkdir()
        script = root / "scripts/ensure_best_pages_in_sitemap.py"
        script.write_bytes((PROJECT / "scripts" / script.name).read_bytes())
        (public / "sitemap.xml").write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
        for directory in ("tool", "compare"):
            (public / directory).mkdir()
            for name in ("new", "alias", "private"):
                canonical = f"{BASE}/{directory}/{'new' if name == 'alias' else name}.html"
                meta = '<meta name="robots" content="noindex">' if name == "private" else ""
                (public / directory / f"{name}.html").write_text(f'<link rel="canonical" href="{canonical}">{meta}')
        subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
        before = (public / "sitemap.xml").read_bytes()
        nodes = ET.fromstring(before).findall("{*}url/{*}loc")
        assert {n.text for n in nodes} == {f"{BASE}/{d}/new.html" for d in ("tool", "compare")}
        subprocess.run([sys.executable, str(script)], check=True, capture_output=True)
        assert (public / "sitemap.xml").read_bytes() == before
    print("PASS sitemap discovery, alias/noindex exclusion and idempotence")
print("PASS robots, sitemap XML, self-canonicals, metadata uniqueness, JSON-LD syntax and internal links")
