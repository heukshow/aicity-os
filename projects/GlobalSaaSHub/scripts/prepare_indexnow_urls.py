#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

class CanonicalParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical: str | None = None

    def handle_starttag(self, tag: str, attrs):
        if self.canonical is not None or tag.lower() != "link":
            return
        values = {str(k).lower(): v for k, v in attrs if k}
        rel = str(values.get("rel") or "").lower().split()
        href = values.get("href")
        if "canonical" in rel and href:
            self.canonical = str(href).strip()


def canonical_from_html(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    parser = CanonicalParser()
    try:
        parser.feed(text)
    except Exception:
        return None
    if parser.canonical:
        return parser.canonical
    if path.name == "index.html" and path.parent.name == "dist":
        return "https://coshuma.com/"
    return None
def sitemap_urls(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for node in root.findall("sm:url/sm:loc", ns):
        if node.text:
            urls.append(node.text.strip())
    return urls

def valid_coshuma_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme == "https" and parsed.netloc == "coshuma.com"

def html_files(root: Path) -> dict[str, Path]:
    return {p.relative_to(root).as_posix(): p for p in root.rglob("*.html")}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True)
    parser.add_argument("--previous", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--key-file", required=True)
    args = parser.parse_args()

    current = Path(args.current)
    previous = Path(args.previous)
    output = Path(args.output)
    key_file = args.key_file

    sitemap = sitemap_urls(current / "sitemap.xml")
    sitemap_set = {url for url in sitemap if valid_coshuma_url(url)}
    if not sitemap_set:
        raise SystemExit("IndexNow preparation failed: sitemap has no valid COSHUMA URLs")

    previous_key = previous / key_file
    bootstrap = not previous_key.exists()

    urls: set[str] = set()
    changed_files: list[str] = []
    deleted_files: list[str] = []

    if bootstrap:
        urls.update(sitemap_set)
    else:
        current_html = html_files(current)
        previous_html = html_files(previous)

        for rel, path in current_html.items():
            old = previous_html.get(rel)
            if old is not None and old.read_bytes() == path.read_bytes():
                continue
            canonical = canonical_from_html(path)
            if canonical and canonical in sitemap_set and valid_coshuma_url(canonical):
                urls.add(canonical)
                changed_files.append(rel)

        for rel, path in previous_html.items():
            if rel in current_html:
                continue
            canonical = canonical_from_html(path)
            if canonical and valid_coshuma_url(canonical):
                urls.add(canonical)
                deleted_files.append(rel)

    ordered = sorted(urls)
    if len(ordered) > 10000:
        raise SystemExit(f"IndexNow URL set too large: {len(ordered)} > 10000")

    payload = {
        "schema_version": 1,
        "host": "coshuma.com",
        "bootstrap": bootstrap,
        "url_count": len(ordered),
        "changed_files": changed_files,
        "deleted_files": deleted_files,
        "urlList": ordered,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"bootstrap": bootstrap, "url_count": len(ordered)}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
