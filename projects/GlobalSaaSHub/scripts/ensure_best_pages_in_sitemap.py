from pathlib import Path
from html.parser import HTMLParser
from html import escape
from urllib.parse import urlparse
from datetime import datetime
import json
import re
import xml.etree.ElementTree as ET

BASE_URL = "https://coshuma.com"
PROJECT = Path(__file__).resolve().parents[1]
PUBLIC = PROJECT / "public"
SITEMAP = PUBLIC / "sitemap.xml"
BEST_DIR = PUBLIC / "best"
CATEGORY_DIR = PUBLIC / "category"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

ET.register_namespace("", NS)


def valid_http_url(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        return None
    return value


def source_label(url):
    try:
        host = urlparse(url).netloc.lower().removeprefix("www.")
        return host or "Official source"
    except Exception:
        return "Official source"


def parse_date(value):
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d")
        except ValueError:
            return None


def render_methodology_page():
    page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>COSHUMA Methodology | How We Evaluate AI & SaaS Tools</title>
  <meta name="description" content="How COSHUMA checks software pricing, public sources, buyer fit, affiliate links, comparisons, updates and corrections." />
  <link rel="canonical" href="{BASE_URL}/methodology.html" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{BASE_URL}/methodology.html" />
  <meta property="og:title" content="COSHUMA Methodology | How We Evaluate AI & SaaS Tools" />
  <meta property="og:description" content="Our source, pricing, comparison, disclosure and correction standards for AI and SaaS buyer guides." />
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"COSHUMA Methodology","url":"{BASE_URL}/methodology.html","isPartOf":{{"@type":"WebSite","name":"COSHUMA","url":"{BASE_URL}/"}}}}</script>
  <style>body{{margin:0;background:#08090d;color:#e2e8f0;font-family:Inter,Arial,sans-serif}}main{{max-width:900px;margin:auto;padding:48px 20px 80px}}a{{color:#c4b5fd}}.card{{border:1px solid #25293a;background:#101218;border-radius:18px;padding:22px;margin:16px 0}}h1,h2{{color:#fff}}p,li{{line-height:1.75;color:#aeb7c8}}.eyebrow{{color:#a78bfa;font-weight:800;text-transform:uppercase;letter-spacing:.14em;font-size:12px}}</style>
</head>
<body><main>
  <a href="/">← Back to COSHUMA</a>
  <p class="eyebrow">Editorial methodology</p>
  <h1>How COSHUMA evaluates AI & SaaS software</h1>
  <p>COSHUMA is an independent software decision-support site. Our goal is to help buyers compare price, fit, trade-offs and public evidence before they subscribe.</p>
  <section class="card"><h2>1. Official-source pricing checks</h2><p>When a pricing or trial source is available, we prefer the vendor's public pricing, product, help-center or documentation page. Pricing can change, so buyers should verify final terms on the vendor site before purchase.</p></section>
  <section class="card"><h2>2. Buyer-fit comparisons</h2><p>We organize comparisons around practical purchase questions: what the product is for, who it fits, pricing, key capabilities, limitations and relevant alternatives. We do not invent customer counts, review volumes, traffic, conversions or performance claims.</p></section>
  <section class="card"><h2>3. Affiliate links are verified separately</h2><p>Editorial product information and outbound affiliate destinations are treated as separate evidence. A product may have an official source without an affiliate link, or a verified affiliate destination without changing our product description or ranking.</p></section>
  <section class="card"><h2>4. Category and comparison selection</h2><p>Tools are grouped by primary use case. Buyer-guide and comparison links prioritize useful decision paths, especially categories where visitors commonly compare pricing, alternatives or workflow fit.</p></section>
  <section class="card"><h2>5. Updates and rechecks</h2><p>Where our dataset contains a real verification timestamp, tool pages may display a “Last verified” date and the public sources checked. Missing verification data is not replaced with a guessed date.</p></section>
  <section class="card"><h2>6. Affiliate disclosure</h2><p>Some outbound links may earn COSHUMA a commission. A verified affiliate relationship does not guarantee a positive recommendation, does not change the buyer's price, and is not evidence that a sale or commission occurred.</p></section>
  <section class="card"><h2>7. Corrections</h2><p>If a public price, product fact or destination changes, we prefer correcting the affected guide and preserving evidence of the newer source rather than silently fabricating continuity.</p></section>
</main></body></html>'''
    (PUBLIC / "methodology.html").write_text(page, encoding="utf-8")


def render_category_pages(tools):
    CATEGORY_DIR.mkdir(parents=True, exist_ok=True)
    configs = {
        "automation": ("Automation Software", "workflow_auto", "Workflow automation tools for connecting apps, reducing repetitive work and orchestrating business processes.", "/best/index.html"),
        "sales-crm": ("Sales & CRM Software", "sales_crm", "CRM, pipeline, lead-management and sales-enablement software for teams that need a clearer path from prospect to customer.", "/best/crm-for-marketing-agencies.html"),
        "ai-agents": ("AI Agent Platforms", "ai_agents", "AI agent platforms for autonomous tasks, workflows, assistants and multi-step business automation.", "/best/index.html"),
        "ai-video": ("AI Video Software", "video_gen", "AI video generation and editing tools for marketing, training, social content and production workflows.", "/best/ai-video-generators.html"),
        "ai-voice": ("AI Voice Software", "voice_cloning", "AI voice, speech and cloning tools for narration, localization, creative production and voice workflows.", "/best/ai-voice-generators.html"),
        "seo": ("SEO Software", "seo_tools", "SEO software for keyword research, content optimization, visibility monitoring and search-performance workflows.", "/best/index.html"),
    }
    compare_files = sorted((PUBLIC / "compare").glob("*.html")) if (PUBLIC / "compare").exists() else []
    for slug, (title, category_id, intro, best_url) in configs.items():
        matches = [t for t in tools if t.get("category") == category_id]
        matches.sort(key=lambda t: (not bool(t.get("affiliate_verified")), (t.get("name") or "").lower()))
        cards = []
        ids = set()
        for tool in matches[:12]:
            tool_id = tool.get("id")
            if not tool_id:
                continue
            ids.add(tool_id)
            desc = escape((tool.get("description") or "")[:220])
            pricing = escape(tool.get("pricing") or "Pricing on vendor site")
            name = escape(tool.get("name") or tool_id)
            cards.append(f'<article class="card"><h2><a href="/tool/{tool_id}.html">{name}</a></h2><p>{desc}</p><p><strong>Pricing:</strong> {pricing}</p></article>')
        comparison_links = []
        for page in compare_files:
            stem = page.stem
            if any(tool_id in stem for tool_id in ids):
                label = escape(stem.replace("-vs-", " vs ").replace("-", " ").title())
                comparison_links.append(f'<a href="/compare/{page.name}">{label}</a>')
            if len(comparison_links) >= 4:
                break
        comparisons_html = " · ".join(comparison_links) if comparison_links else '<a href="/best/index.html">Browse all buyer guides</a>'
        page = f'''<!doctype html>
<html lang="en"><head>
<meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{escape(title)}: Pricing, Reviews & Comparisons (2026) | COSHUMA</title>
<meta name="description" content="Compare {escape(title.lower())} by pricing, use case, buyer fit and alternatives on COSHUMA." />
<link rel="canonical" href="{BASE_URL}/category/{slug}.html" />
<meta property="og:type" content="website" /><meta property="og:url" content="{BASE_URL}/category/{slug}.html" />
<meta property="og:title" content="{escape(title)}: Pricing, Reviews & Comparisons (2026) | COSHUMA" />
<meta property="og:description" content="{escape(intro)}" />
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"CollectionPage","name":"{escape(title)}","url":"{BASE_URL}/category/{slug}.html","description":"{escape(intro)}"}}</script>
<style>body{{margin:0;background:#08090d;color:#e2e8f0;font-family:Inter,Arial,sans-serif}}main{{max-width:1050px;margin:auto;padding:48px 20px 80px}}a{{color:#c4b5fd}}h1,h2{{color:#fff}}p{{line-height:1.7;color:#aeb7c8}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}.card{{border:1px solid #25293a;background:#101218;border-radius:18px;padding:20px}}.eyebrow{{color:#a78bfa;font-weight:800;text-transform:uppercase;letter-spacing:.14em;font-size:12px}}.hub{{border:1px solid #25293a;border-radius:16px;padding:16px;margin:24px 0;background:#0d0f15}}</style>
</head><body><main>
<a href="/">← Back to COSHUMA</a><p class="eyebrow">Software category guide</p><h1>{escape(title)}</h1><p>{escape(intro)}</p>
<div class="hub"><strong>Buyer guide:</strong> <a href="{best_url}">See the related COSHUMA shortlist</a><br/><strong>Useful comparisons:</strong> {comparisons_html}</div>
<div class="grid">{''.join(cards)}</div>
<p style="margin-top:28px"><a href="/methodology.html">How COSHUMA evaluates software →</a></p>
</main></body></html>'''
        (CATEGORY_DIR / f"{slug}.html").write_text(page, encoding="utf-8")
    return configs


def inject_tool_trust_blocks(tools):
    tool_dir = PUBLIC / "tool"
    if not tool_dir.exists():
        return 0
    injected = 0
    for tool in tools:
        tool_id = tool.get("id")
        if not tool_id:
            continue
        page = tool_dir / f"{tool_id}.html"
        if not page.exists():
            continue
        dates = [parse_date(tool.get(k)) for k in ("official_verified_at", "affiliate_verified_at", "pricing_verified_at", "verified_at")]
        dates = [d for d in dates if d is not None]
        last_verified = max(dates).strftime("%B %-d, %Y") if dates else None
        public_sources = []
        for key in ("pricing_source_url", "official_evidence_url", "official_url"):
            url = valid_http_url(tool.get(key))
            if url and url not in public_sources:
                public_sources.append(url)
        if not last_verified and not public_sources:
            continue
        parts = []
        if last_verified:
            parts.append(f'<div><div class="text-[10px] uppercase tracking-wider text-slate-500">Last verified</div><div class="mt-1 text-sm font-bold text-slate-200">{escape(last_verified)}</div></div>')
        if public_sources:
            links = " · ".join(f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">{escape(source_label(url))}</a>' for url in public_sources[:3])
            parts.append(f'<div><div class="text-[10px] uppercase tracking-wider text-slate-500">Sources checked</div><div class="mt-1 text-sm">{links}</div></div>')
        if tool.get("affiliate_verified") is True:
            parts.append('<div><div class="text-[10px] uppercase tracking-wider text-slate-500">Affiliate disclosure</div><div class="mt-1 text-sm text-slate-300">Affiliate destination verified separately from editorial product sources.</div></div>')
        block = '<!-- COSHUMA_TRUST_BLOCK --><section class="p-5 rounded-2xl bg-[#10131c] border border-[#2b3044] space-y-4"><h2 class="text-lg font-bold text-white">Verification & sources</h2>' + ''.join(parts) + '<p class="text-[11px] leading-5 text-slate-500">Software details and prices can change. Verify final terms on the vendor site before purchasing.</p></section><!-- /COSHUMA_TRUST_BLOCK -->'
        text = page.read_text(encoding="utf-8")
        text = re.sub(r'<!-- COSHUMA_TRUST_BLOCK -->.*?<!-- /COSHUMA_TRUST_BLOCK -->', '', text, flags=re.S)
        anchor = '<!-- Pricing & Action -->'
        if anchor in text:
            text = text.replace(anchor, block + '\n\n        ' + anchor, 1)
        else:
            text = text.replace('</main>', block + '\n</main>', 1)
        page.write_text(text, encoding="utf-8")
        injected += 1
    return injected


# Generate persistent public trust/discovery pages before sitemap scan.
tools = json.loads((PROJECT / "data/tools.json").read_text(encoding="utf-8"))
render_methodology_page()
category_configs = render_category_pages(tools)
trust_count = inject_tool_trust_blocks(tools)

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

# Methodology is a trust page, not a revenue page, but it should be indexable.
add_url(f"{BASE_URL}/methodology.html", "0.6")
for slug in category_configs:
    add_url(f"{BASE_URL}/category/{slug}.html", "0.85")


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


# Scan finished pages, including hand-written pages omitted by generators.
tool_ids = {tool["id"] for tool in tools}
tool_ids.update(json.loads((PROJECT / "data/standalone_tool_pages.json").read_text(encoding="utf-8")))
for directory in ("tool", "compare", "category"):
    for page in sorted((PUBLIC / directory).glob("*.html")):
        if directory == "tool" and page.stem not in tool_ids:
            continue
        url = f"{BASE_URL}/{directory}/{page.name}"
        parsed = IndexablePage(page.read_text(encoding="utf-8"))
        if parsed.canonicals == [url] and not parsed.noindex:
            priority = "0.8" if directory == "tool" else "0.85" if directory == "category" else "0.7"
            add_url(url, priority)

# Root-level buyer-intent landing pages are hand-written and are not emitted by generators.
# Include only pages that contain an affiliate CTA and a matching canonical URL.
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
    f"best={len(best_pages)} categories={len(category_configs)} methodology=1 "
    f"tool_trust_blocks={trust_count} root_revenue={len(root_revenue_pages)} added={len(added)}"
)
for url in added:
    print(f"+ {url}")
