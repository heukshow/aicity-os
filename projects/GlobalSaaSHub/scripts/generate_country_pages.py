"""Generate COSHUMA country/region discovery pages and tool country badges.

The country dataset is deliberately source-backed and partial. Unknown tools stay
unknown rather than being guessed. Country ranking means only the number of
COSHUMA-listed tools with verified company-location data.
"""
from __future__ import annotations

from collections import defaultdict
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "data" / "tools.json"
COUNTRY_PATH = ROOT / "data" / "tool_company_countries.json"
PUBLIC = ROOT / "public"
COUNTRIES_DIR = PUBLIC / "countries"
SITEMAP = PUBLIC / "sitemap.xml"
SITE = "https://coshuma.com"
START = "<!-- COSHUMA_COUNTRY_START -->"
END = "<!-- COSHUMA_COUNTRY_END -->"
BLOCK_RE = re.compile(
    re.escape(START) + r".*?" + re.escape(END),
    flags=re.S,
)


def country_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        raise ValueError(f"Cannot make country slug from {name!r}")
    return slug


def safe_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Invalid source URL: {value!r}")
    return value


def flag_img(code: str, css_class: str = "h-4 w-6") -> str:
    asset = PUBLIC / "flags" / f"{code.lower()}.svg"
    if not asset.exists():
        raise ValueError(f"Missing local flag asset for {code}: {asset}")
    return (
        f'<img src="/flags/{escape(code.lower(), quote=True)}.svg" alt="" aria-hidden="true" '
        f'width="24" height="18" loading="lazy" decoding="async" '
        f'class="inline-block shrink-0 rounded-[2px] object-cover {css_class}" />'
    )


def shell(title: str, description: str, canonical: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="index,follow" />
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description, quote=True)}" />
  <link rel="canonical" href="{escape(canonical, quote=True)}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{escape(canonical, quote=True)}" />
  <meta property="og:title" content="{escape(title, quote=True)}" />
  <meta property="og:description" content="{escape(description, quote=True)}" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; background:#08090d; color:#f1f5f9; }}
  </style>
</head>
<body class="min-h-screen bg-[#08090d] text-slate-100">
  <header class="sticky top-0 z-40 border-b border-white/10 bg-[#08090d]/90 backdrop-blur-xl">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
      <a href="/" class="font-black tracking-tight text-white">COSHUMA</a>
      <nav class="flex items-center gap-4 text-xs font-bold text-slate-400">
        <a href="/" class="hover:text-white">All tools</a>
        <a href="/countries/" class="text-cyan-200 hover:text-white">Countries & regions</a>
      </nav>
    </div>
  </header>
  <main class="mx-auto max-w-6xl px-5 py-10 md:py-14">
    {body}
  </main>
  <footer class="border-t border-white/10 py-8">
    <div class="mx-auto max-w-6xl px-5 text-xs leading-5 text-slate-500">
      COSHUMA country/region data describes a source-backed company base or registered company location.
      It does not describe founder nationality, workforce nationality, or where every part of a product was developed.
    </div>
  </footer>
</body>
</html>
"""


tools = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
doc = json.loads(COUNTRY_PATH.read_text(encoding="utf-8"))
records = doc.get("tools", {})
tool_by_id = {tool["id"]: tool for tool in tools}

if not isinstance(records, dict) or not records:
    raise SystemExit("Country dataset is empty")

country_identity = {}
grouped = defaultdict(list)

for tool_id, record in records.items():
    if tool_id not in tool_by_id:
        raise SystemExit(f"Country record points to unknown tool: {tool_id}")
    if not isinstance(record, dict):
        raise SystemExit(f"Invalid country record for {tool_id}")
    code = str(record.get("country_code", "")).strip().upper()
    name = str(record.get("country_name", "")).strip()
    flag = str(record.get("flag", "")).strip()
    basis = str(record.get("basis", "")).strip()
    source_url = safe_url(str(record.get("source_url", "")).strip())
    if not re.fullmatch(r"[A-Z]{2}", code):
        raise SystemExit(f"Invalid ISO-style country code for {tool_id}: {code!r}")
    if not name or not flag or not basis:
        raise SystemExit(f"Incomplete country record for {tool_id}")
    identity = (name, flag)
    if code in country_identity and country_identity[code] != identity:
        raise SystemExit(f"Inconsistent country identity for code {code}")
    country_identity[code] = identity
    record["country_code"] = code
    record["country_name"] = name
    record["flag"] = flag
    record["basis"] = basis
    record["source_url"] = source_url
    record["slug"] = country_slug(name)
    grouped[code].append((tool_by_id[tool_id], record))

# Remove stale generated badges first, then add only source-backed current badges.
tool_dir = PUBLIC / "tool"
for page in tool_dir.glob("*.html"):
    raw = page.read_text(encoding="utf-8")
    cleaned = BLOCK_RE.sub("", raw)
    if cleaned != raw:
        page.write_text(cleaned, encoding="utf-8")

badge_count = 0
skipped_detail_pages = []

for tool_id, record in records.items():
    page = tool_dir / f"{tool_id}.html"
    if not page.exists():
        skipped_detail_pages.append(tool_id)
        continue
    raw = page.read_text(encoding="utf-8")
    h1 = re.search(r"<h1\b[^>]*>.*?</h1>", raw, flags=re.I | re.S)
    if not h1:
        skipped_detail_pages.append(tool_id)
        continue
    badge = (
        f' {START}<div class="mt-3">'
        f'<a data-coshuma-country="{escape(record["country_code"], quote=True)}" '
        f'href="/countries/{escape(record["slug"], quote=True)}.html" '
        f'title="Source-backed company country or region" '
        f'class="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 '
        f'bg-cyan-400/10 px-3 py-1.5 text-xs font-bold text-cyan-200 hover:bg-cyan-400/15">'
        f'{flag_img(record["country_code"], "h-3.5 w-5")}<span>{escape(record["country_name"])} · company base</span>'
        f'</a></div>{END}'
    )
    updated = raw[: h1.end()] + badge + raw[h1.end() :]
    page.write_text(updated, encoding="utf-8")
    badge_count += 1

COUNTRIES_DIR.mkdir(parents=True, exist_ok=True)
for stale in COUNTRIES_DIR.glob("*.html"):
    stale.unlink()

rows = []
for code, items in grouped.items():
    name, flag = country_identity[code]
    rows.append(
        {
            "code": code,
            "name": name,
            "flag": flag,
            "slug": country_slug(name),
            "count": len(items),
            "items": items,
        }
    )
rows.sort(key=lambda x: (-x["count"], x["name"].lower()))

# Standard competition ranking: equal counts share a rank.
last_count = None
last_rank = 0
for idx, row in enumerate(rows, start=1):
    if row["count"] != last_count:
        last_rank = idx
        last_count = row["count"]
    row["rank"] = last_rank

coverage = len(records)
total = len(tools)

ranking_cards = []
for row in rows:
    ranking_cards.append(
        f"""<a href="/countries/{escape(row["slug"], quote=True)}.html"
        class="group grid grid-cols-[3.5rem_1fr_auto] items-center gap-4 rounded-2xl border border-white/10 bg-white/[0.035] p-4 hover:border-cyan-400/30 hover:bg-cyan-400/[0.06]">
          <div class="text-center text-sm font-black text-slate-500">#{row["rank"]}</div>
          <div>
            <div class="flex items-center gap-2 text-lg font-black text-white group-hover:text-cyan-100">{flag_img(row["code"], "h-4 w-6")}<span>{escape(row["name"])}</span></div>
            <div class="mt-1 text-xs text-slate-500">{row["count"]} source-backed COSHUMA tool{"s" if row["count"] != 1 else ""}</div>
          </div>
          <div class="text-sm font-bold text-cyan-300">View →</div>
        </a>"""
    )

index_body = f"""
<section class="max-w-4xl">
  <div class="text-xs font-bold uppercase tracking-[0.18em] text-cyan-300">Country & region explorer</div>
  <h1 class="mt-3 text-4xl font-black tracking-tight text-white md:text-6xl">Explore AI & SaaS by company country/region</h1>
  <p class="mt-5 max-w-3xl text-base leading-7 text-slate-400">
    This ranking counts only COSHUMA-listed tools whose company base or registered company location has a cited public source.
    It is not a world technology ranking, innovation score, or market-share estimate.
  </p>
  <div class="mt-6 inline-flex rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-bold text-slate-300">
    Verified coverage: {coverage} of {total} listed tools · unknown locations are excluded, not guessed
  </div>
</section>
<section class="mt-10 grid gap-3">
  {"".join(ranking_cards)}
</section>
<section class="mt-10 rounded-2xl border border-white/10 bg-white/[0.025] p-5 text-sm leading-6 text-slate-400">
  <strong class="text-white">How to read this ranking:</strong>
  counts reflect COSHUMA's current catalog and verification coverage. A higher count does not mean a country has better technology or a larger total software market.
</section>
"""
(COUNTRIES_DIR / "index.html").write_text(
    shell(
        "AI & SaaS Tools by Country/Region | COSHUMA",
        f"Browse {coverage} COSHUMA-listed AI and SaaS tools with source-backed company country or region data.",
        f"{SITE}/countries/",
        index_body,
    ),
    encoding="utf-8",
)

for row in rows:
    cards = []
    for tool, record in sorted(row["items"], key=lambda pair: pair[0].get("name", "").lower()):
        detail = PUBLIC / "tool" / f'{tool["id"]}.html'
        if detail.exists():
            primary_link = (
                f'<a href="/tool/{escape(tool["id"], quote=True)}.html" '
                f'class="text-lg font-black text-white hover:text-cyan-200">'
                f'{escape(tool.get("name", tool["id"]))}</a>'
            )
            action_link = (
                f'<a href="/tool/{escape(tool["id"], quote=True)}.html" '
                f'class="rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-bold '
                f'text-slate-200 hover:bg-white/[0.08]">Buyer guide →</a>'
            )
        else:
            official = str(tool.get("official_url") or "").strip()
            if official.startswith(("https://", "http://")):
                primary_link = (
                    f'<a href="{escape(official, quote=True)}" target="_blank" rel="noopener noreferrer" '
                    f'class="text-lg font-black text-white hover:text-cyan-200">'
                    f'{escape(tool.get("name", tool["id"]))}</a>'
                )
                action_link = (
                    f'<a href="{escape(official, quote=True)}" target="_blank" rel="noopener noreferrer" '
                    f'class="rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-bold '
                    f'text-slate-200 hover:bg-white/[0.08]">Official site ↗</a>'
                )
            else:
                primary_link = f'<span class="text-lg font-black text-white">{escape(tool.get("name", tool["id"]))}</span>'
                action_link = ""

        cards.append(
            f"""<article class="rounded-2xl border border-white/10 bg-white/[0.035] p-5">
              <div class="flex items-start justify-between gap-4">
                <div>
                  {primary_link}
                  <div class="mt-1 text-xs font-bold uppercase tracking-wider text-violet-300">{escape(tool.get("category_display", "AI & SaaS"))}</div>
                </div>
                {flag_img(row["code"], "h-5 w-7")}
              </div>
              <p class="mt-3 line-clamp-3 text-sm leading-6 text-slate-400">{escape(tool.get("description", ""))}</p>
              <div class="mt-4 flex flex-wrap gap-2">
                {action_link}
                <a href="{escape(record["source_url"], quote=True)}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-cyan-400/20 bg-cyan-400/[0.06] px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/10">Company-location source ↗</a>
              </div>
            </article>"""
        )

    body = f"""
<nav class="text-xs font-bold text-slate-500"><a href="/countries/" class="hover:text-white">Countries & regions</a> / {escape(row["name"])}</nav>
<section class="mt-6 max-w-4xl">
  <div>{flag_img(row["code"], "h-10 w-14")}</div>
  <h1 class="mt-4 text-4xl font-black tracking-tight text-white md:text-6xl">{escape(row["name"])} AI & SaaS tools on COSHUMA</h1>
  <p class="mt-5 text-base leading-7 text-slate-400">
    {row["count"]} COSHUMA-listed tool{"s" if row["count"] != 1 else ""} currently have source-backed company-location data for {escape(row["name"])}.
    This is catalog coverage, not a claim about global market share.
  </p>
</section>
<section class="mt-10 grid gap-4 md:grid-cols-2">
  {"".join(cards)}
</section>
<section class="mt-10 rounded-2xl border border-white/10 bg-white/[0.025] p-5 text-sm leading-6 text-slate-400">
  Country/region labels use a primary company base or registered company location supported by the linked source for each tool.
  Founder nationality and distributed-team locations are intentionally not inferred.
</section>
"""
    (COUNTRIES_DIR / f'{row["slug"]}.html').write_text(
        shell(
            f'{row["name"]} AI & SaaS Tools | COSHUMA',
            f'Browse {row["count"]} COSHUMA-listed AI and SaaS tools with source-backed company-location data for {row["name"]}.',
            f'{SITE}/countries/{row["slug"]}.html',
            body,
        ),
        encoding="utf-8",
    )

sitemap = SITEMAP.read_text(encoding="utf-8")
sitemap_start = "<!-- country-explorer:start -->"
sitemap_end = "<!-- country-explorer:end -->"
sitemap_re = re.compile(re.escape(sitemap_start) + r".*?" + re.escape(sitemap_end), re.S)
sitemap = sitemap_re.sub("", sitemap)
country_urls = [
    f"""  <url>
    <loc>{SITE}/countries/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""
]
for row in rows:
    country_urls.append(
        f"""  <url>
    <loc>{SITE}/countries/{row["slug"]}.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>"""
    )
block = "\n" + sitemap_start + "\n" + "\n".join(country_urls) + "\n" + sitemap_end + "\n"
if "</urlset>" not in sitemap:
    raise SystemExit("sitemap.xml has no closing urlset tag")
sitemap = sitemap.replace("</urlset>", block + "</urlset>")

# This generator runs after the other sitemap-mutating build steps. Normalize the
# final XML before link-integrity checks so an earlier idempotency drift cannot
# leave duplicate <loc> entries and block an otherwise safe release.
url_block_re = re.compile(r"<url>\s*.*?</url>", re.S)
seen_locs: set[str] = set()
duplicate_count = 0
parts: list[str] = []
cursor = 0
for match in url_block_re.finditer(sitemap):
    loc_match = re.search(r"<loc>\s*(.*?)\s*</loc>", match.group(0), re.S)
    if not loc_match:
        continue
    loc = loc_match.group(1).strip()
    if loc in seen_locs:
        parts.append(sitemap[cursor:match.start()])
        cursor = match.end()
        duplicate_count += 1
        continue
    seen_locs.add(loc)
parts.append(sitemap[cursor:])
sitemap = "".join(parts)

SITEMAP.write_text(sitemap, encoding="utf-8")

print(
    f"Generated country explorer: {coverage}/{total} tools, "
    f"{len(rows)} countries/regions, {badge_count} tool-page badges, "
    f"{len(skipped_detail_pages)} mapped tools without badgeable static detail pages"
)
