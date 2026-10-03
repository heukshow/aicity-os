"""Regression checks for the COSHUMA country/region explorer."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
TOOLS_PATH = ROOT / "data" / "tools.json"
COUNTRY_PATH = ROOT / "data" / "tool_company_countries.json"
PUBLIC = ROOT / "public"
COUNTRIES_DIR = PUBLIC / "countries"
SITEMAP = PUBLIC / "sitemap.xml"

tools = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
doc = json.loads(COUNTRY_PATH.read_text(encoding="utf-8"))
records = doc.get("tools", {})
ids = {tool["id"] for tool in tools}

assert records, "country dataset must not be empty"
assert set(records).issubset(ids), "country dataset contains an unknown tool id"

country_names = {}
for tool_id, record in records.items():
    code = record.get("country_code")
    name = record.get("country_name")
    flag = record.get("flag")
    source = record.get("source_url")
    assert isinstance(code, str) and re.fullmatch(r"[A-Z]{2}", code), f"invalid code: {tool_id}"
    assert isinstance(name, str) and name.strip(), f"missing country name: {tool_id}"
    assert isinstance(flag, str) and flag.strip(), f"missing flag: {tool_id}"
    assert isinstance(source, str) and source.startswith(("https://", "http://")), f"invalid source: {tool_id}"
    if code in country_names:
        assert country_names[code] == name, f"inconsistent country name for {code}"
    else:
        country_names[code] = name

index = COUNTRIES_DIR / "index.html"
assert index.exists(), "country index page was not generated"
index_text = index.read_text(encoding="utf-8")
coverage = f"Verified coverage: {len(records)} of {len(tools)} listed tools"
assert coverage in index_text, "country index coverage disclosure is missing"
assert "not a world technology ranking" in index_text, "country ranking scope disclaimer is missing"

for code, name in country_names.items():
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    page = COUNTRIES_DIR / f"{slug}.html"
    assert page.exists(), f"country page missing: {slug}"
    text = page.read_text(encoding="utf-8")
    assert "Company-location source" in text, f"source link label missing: {slug}"

badgeable = 0
for tool_id, record in records.items():
    page = PUBLIC / "tool" / f"{tool_id}.html"
    if not page.exists():
        continue
    badgeable += 1
    text = page.read_text(encoding="utf-8")
    assert f'data-coshuma-country="{record["country_code"]}"' in text, f"country badge missing: {tool_id}"
    slug = re.sub(r"[^a-z0-9]+", "-", record["country_name"].lower()).strip("-")
    assert f'/countries/{slug}.html' in text, f"country link missing: {tool_id}"

sitemap = SITEMAP.read_text(encoding="utf-8")
assert "https://coshuma.com/countries/" in sitemap, "country index missing from sitemap"
for name in country_names.values():
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    assert f"https://coshuma.com/countries/{slug}.html" in sitemap, f"country sitemap URL missing: {slug}"

print(
    f"PASS: country explorer verified for {len(records)}/{len(tools)} tools "
    f"across {len(country_names)} countries/regions; detail badges={badgeable}"
)
