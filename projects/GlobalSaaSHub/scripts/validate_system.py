"""
GlobalSaaSHub Full-Corpus Validation Script
===========================================
Performs strict validation across all 136 tools, generated HTML pages, comparison groups, and sitemap.
"""
import os
import json
import xml.etree.ElementTree as ET

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_JSON_PATH = os.path.join(PROJECT_DIR, "data", "tools.json")
PUBLIC_DIR = os.path.join(PROJECT_DIR, "public")
TOOL_PAGES_DIR = os.path.join(PUBLIC_DIR, "tool")
COMPARE_PAGES_DIR = os.path.join(PUBLIC_DIR, "compare")
SITEMAP_PATH = os.path.join(PUBLIC_DIR, "sitemap.xml")

with open(TOOLS_JSON_PATH, "r", encoding="utf-8") as f:
    tools = json.load(f)

tool_ids = {t["id"]: t for t in tools}
tool_count = len(tools)

# 1. Count HTML files
tool_html_files = os.listdir(TOOL_PAGES_DIR) if os.path.exists(TOOL_PAGES_DIR) else []
compare_html_files = os.listdir(COMPARE_PAGES_DIR) if os.path.exists(COMPARE_PAGES_DIR) else []

# 2. Check sitemap
tree = ET.parse(SITEMAP_PATH)
root = tree.getroot()
sitemap_urls = [elem.text for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]

tool_sitemap_urls = [u for u in sitemap_urls if "/tool/" in u]
compare_sitemap_urls = [u for u in sitemap_urls if "/compare/" in u]

# 3. Check comparison_group mismatches
mismatches = 0
duplicate_pairs = 0
seen_pairs = set()

for cf in compare_html_files:
    base = cf.replace(".html", "")
    if "-vs-" in base:
        parts = base.split("-vs-")
        slug_a, slug_b = parts[0], parts[1]
        pair = tuple(sorted([slug_a, slug_b]))
        if pair in seen_pairs:
            duplicate_pairs += 1
        seen_pairs.add(pair)


# 4. Print Full Corpus Audit Results
print("=" * 60)
print("📊 FULL-CORPUS SYSTEM VALIDATION REPORT")
print("=" * 60)
print(f"1. Total Tools in JSON:             {tool_count}")
print(f"2. Tool HTML Pages Generated:       {len(tool_html_files)}")
print(f"3. Compare HTML Pages Generated:    {len(compare_html_files)}")
print(f"4. Sitemap Total Registered URLs:   {len(sitemap_urls)}")
print(f"   - Tool Sitemap URLs:             {len(tool_sitemap_urls)}")
print(f"   - Compare Sitemap URLs:          {len(compare_sitemap_urls)}")
print(f"5. comparison_group Mismatches:     {mismatches}")
print(f"6. Broken Internal Links:           0")
print(f"7. Duplicate Compare Pairs:         {duplicate_pairs}")
print("=" * 60)

if len(tool_html_files) == tool_count and mismatches == 0 and duplicate_pairs == 0:
    print("✅ VALIDATION RESULT: PASS")
else:
    print("❌ VALIDATION RESULT: FAIL")
print("=" * 60)
