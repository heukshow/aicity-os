"""Deterministic integrity audit for every generated tool URL."""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

PROJECT = Path(__file__).resolve().parents[2]
PUBLIC = PROJECT / "public"
BASE_URL = "https://coshuma.com"


def select_dataset(source):
    tools = PROJECT / "data" / "tools.json"
    candidate = PROJECT / "data" / "tools.next.json"
    if source == "tools.json":
        return tools
    if source == "tools.next.json":
        return candidate
    # Link integrity audits committed Production unless a candidate is explicitly requested.
    return tools


def fail(errors, message):
    errors.append(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=("auto", "tools.json", "tools.next.json"), default="tools.json")
    args = parser.parse_args()
    dataset = select_dataset(args.source)
    tools = json.loads(dataset.read_text(encoding="utf-8"))
    ids = [tool["id"] for tool in tools]
    errors = []
    if len(ids) != len(set(ids)):
        fail(errors, "tools.json contains duplicate canonical ids")
    expected_paths = {f"/tool/{tool_id}.html" for tool_id in ids}

    app_source = (PROJECT / "src" / "App.jsx").read_text(encoding="utf-8")
    if 'href={`/tool/${tool.id}.html`}' not in app_source:
        fail(errors, "Home cards do not use tools.json id for their href")

    actual_files = {f"/tool/{path.name}" for path in (PUBLIC / "tool").glob("*.html")}
    for path in sorted(expected_paths - actual_files):
        fail(errors, f"Missing detail page: {path}")
    for path in sorted(actual_files - expected_paths):
        fail(errors, f"Unexpected detail page: {path}")

    root = ET.parse(PUBLIC / "sitemap.xml").getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text for node in root.findall("sm:url/sm:loc", namespace)}
    sitemap_tool_paths = {urlparse(url).path for url in sitemap_urls if url and "/tool/" in urlparse(url).path}

    if len(sitemap_tool_paths) != len(actual_files):
        fail(errors, f"Sitemap tool count {len(sitemap_tool_paths)} != detail page count {len(actual_files)}")
    if sitemap_tool_paths != expected_paths:
        fail(errors, "Sitemap tool URLs do not exactly match tools.json ids")

    internal_link_pattern = re.compile(r'href=["\'](/tool/[^"\'#?]+\.html)["\']')
    canonical_pattern = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']')
    for html_file in PUBLIC.rglob("*.html"):
        html = html_file.read_text(encoding="utf-8")
        for link in internal_link_pattern.findall(html):
            if link not in actual_files:
                fail(errors, f"Broken internal link in {html_file.relative_to(PUBLIC)}: {link}")

    for tool_id in ids:
        path = f"/tool/{tool_id}.html"
        html = (PUBLIC / path.removeprefix("/")).read_text(encoding="utf-8")
        canonical = canonical_pattern.search(html)
        expected_url = f"{BASE_URL}{path}"
        if not canonical or canonical.group(1) != expected_url:
            fail(errors, f"Canonical mismatch for {tool_id}: expected {expected_url}")
        if expected_url not in sitemap_urls:
            fail(errors, f"Canonical missing from sitemap: {expected_url}")

    for regression_id in ("notion-ai", "make-com", "copy-ai", "relevance-ai"):
        if regression_id not in ids or f"/tool/{regression_id}.html" not in actual_files:
            fail(errors, f"Regression page missing: {regression_id}")

    relevance = next((tool for tool in tools if tool["id"] == "relevance-ai"), None)
    if not relevance or relevance.get("affiliate_url") is not None or relevance.get("affiliate_verified") is not False:
        fail(errors, "Relevance AI affiliate safety fields changed")
    else:
        relevance_html = (PUBLIC / "tool" / "relevance-ai.html").read_text(encoding="utf-8")
        if "Visit Official Relevance AI Site" not in relevance_html:
            fail(errors, "Relevance AI official-only CTA is missing")
        if relevance.get("official_url") not in relevance_html:
            fail(errors, "Relevance AI official CTA does not use official_url")
        if "Visit Relevance AI" in relevance_html:
            fail(errors, "Relevance AI affiliate CTA must not be rendered")

    taskade = next((tool for tool in tools if tool["id"] == "taskade"), None)
    if not taskade or not taskade.get("affiliate_url") or taskade.get("affiliate_verified") is not True:
        fail(errors, "Taskade verified affiliate fields are missing")
    else:
        taskade_html = (PUBLIC / "tool" / "taskade.html").read_text(encoding="utf-8")
        if taskade.get("affiliate_url") not in taskade_html or "Visit Taskade" not in taskade_html:
            fail(errors, "Taskade affiliate CTA is missing or does not use affiliate_url")
    if errors:
        print(f"LINK INTEGRITY: FAIL ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"LINK INTEGRITY: PASS ({len(ids)}/{len(ids)} tools, {len(actual_files)} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())


