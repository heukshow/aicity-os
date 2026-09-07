from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = ROOT / "data" / "tools.json"
PUBLIC = ROOT / "public"
CATEGORY_DIR = PUBLIC / "category"
SITEMAP = PUBLIC / "sitemap.xml"
SITE = "https://coshuma.com"
TODAY = "2026-09-08"

CATEGORY_CONFIG = {
    "automation": {
        "title": "Best Automation Software & AI Workflow Tools in 2026",
        "description": "Compare workflow automation and no-code AI tools by buyer fit, pricing signals, strengths and practical trade-offs before you subscribe.",
        "category_ids": {"workflow_auto", "dev_coding"},
        "intro": "Automation tools should remove repeated work without creating a maintenance problem. Start by deciding whether you need simple task automation, visual multi-step workflows, developer-oriented orchestration or AI-assisted workspace automation.",
        "choose": [
            "Choose visual workflow builders when non-technical teams need to inspect and edit automations themselves.",
            "Choose developer-oriented tools when API control, branching and custom logic matter more than ease of setup.",
            "Check execution limits, premium connectors and usage-based pricing before committing to a workflow that will scale.",
        ],
        "faq": [
            ("What should I compare first in automation software?", "Start with the workflow you need to automate, the apps it must connect to, execution limits and who will maintain it."),
            ("Is the cheapest automation tool always the best value?", "No. Connector coverage, run limits, reliability and maintenance time can matter more than the entry price."),
        ],
    },
    "sales-crm": {
        "title": "Best Sales CRM & Revenue Tools in 2026",
        "description": "Compare CRM, sales automation, outreach and support platforms by buyer fit, workflow, pricing model and trade-offs.",
        "category_ids": {"sales_crm", "chatbots_support", "email_outreach"},
        "intro": "Sales software becomes expensive when the workflow does not match the team. Decide whether you need a focused pipeline, an agency-style all-in-one platform, outbound prospecting, or a broader customer support and retention stack.",
        "choose": [
            "Check whether pricing is per seat, per contact, per conversation or usage based.",
            "Prioritize pipeline clarity when your main job is moving deals forward; prioritize automation breadth when one platform must run multiple customer workflows.",
            "For agencies, verify sub-account economics and client management limits before comparing headline prices.",
        ],
        "faq": [
            ("What makes a CRM a good fit for an agency?", "Multi-client account structure, automation, reporting and predictable scaling costs are usually more important than a long feature list."),
            ("Should I choose an all-in-one sales platform?", "Only when replacing several separate tools reduces enough operational complexity to justify the broader platform and price."),
        ],
    },
    "ai-agents": {
        "title": "Best AI Agent Platforms in 2026",
        "description": "Compare AI agent platforms for business workflows, research, support and automation with clear buyer-fit guidance and source-led product data.",
        "category_ids": {"ai_agents"},
        "intro": "AI agent platforms vary from simple task assistants to systems that can call tools, coordinate workflows and operate across business data. The right choice depends on control, integrations, observability and how much human review you need.",
        "choose": [
            "Check which external tools and data sources the agent can actually access.",
            "Prefer systems with clear run history, permissions and human review when agents can take actions.",
            "Compare usage limits and model costs separately from the platform subscription when possible.",
        ],
        "faq": [
            ("What is the main risk when buying an AI agent platform?", "A polished demo can hide weak integrations, unclear permissions or unpredictable usage costs. Verify the workflow you actually need."),
            ("Do AI agents replace workflow automation tools?", "Sometimes they complement them rather than replace them. Deterministic automations remain useful when a process must behave the same way every time."),
        ],
    },
    "video": {
        "title": "Best AI Video & YouTube Tools in 2026",
        "description": "Compare AI video creation, avatar, repurposing and YouTube growth tools by use case, workflow and practical trade-offs.",
        "category_ids": {"video_gen"},
        "intro": "Video tools solve different jobs: generating scenes, creating avatar videos, turning long content into clips, editing existing footage or improving YouTube discovery. Pick the job first, then compare output quality and workflow cost.",
        "choose": [
            "Separate generation tools from editing, repurposing and channel-optimization tools.",
            "Check export limits, watermark rules, rendering credits and commercial-use terms before choosing a paid plan.",
            "Use free trials to test your own script and footage instead of relying only on vendor demos.",
        ],
        "faq": [
            ("What should I test during an AI video free trial?", "Test a real script, export quality, editing control, render time and whether the result still needs substantial manual cleanup."),
            ("Are YouTube SEO tools the same as AI video generators?", "No. They may appear in the same buying journey, but one optimizes channel discovery while the other creates or edits video content."),
        ],
    },
    "voice": {
        "title": "Best AI Voice & Speech Tools in 2026",
        "description": "Compare AI voice generation, cloning and speech tools by use case, controls, pricing signals and workflow fit.",
        "category_ids": {"voice_cloning"},
        "intro": "Voice AI buyers usually care about naturalness, language coverage, cloning controls, licensing and how quickly the product fits into a production workflow. Test the exact voice use case before committing to a larger plan.",
        "choose": [
            "Check commercial-use and voice-consent requirements before publishing generated speech.",
            "Compare character or minute limits with your real production volume, not just the monthly sticker price.",
            "Test pronunciation, pacing and editing control in the languages you actually plan to use.",
        ],
        "faq": [
            ("What matters most when comparing AI voice tools?", "Output quality matters, but licensing, language support, editing control and usable monthly limits often determine the better purchase."),
            ("Should I pay for voice cloning if I only need narration?", "Not necessarily. A strong stock-voice library may be simpler and cheaper when you do not need a consistent cloned identity."),
        ],
    },
    "seo": {
        "title": "Best SEO & AI Visibility Tools in 2026",
        "description": "Compare SEO, content optimization and AI visibility tools by workflow, data source, buyer fit and practical trade-offs.",
        "category_ids": {"seo_tools"},
        "intro": "SEO software can focus on keyword research, technical auditing, content optimization, competitive intelligence or AI-search visibility. A useful shortlist starts with the decisions you need the data to support.",
        "choose": [
            "Avoid paying for overlapping datasets unless each tool supports a different decision in your workflow.",
            "For content optimization, check whether recommendations are transparent enough to edit rather than simply accept a score.",
            "For AI visibility, verify which engines, prompts and tracking methods are included before treating a visibility score as actionable."),
        ],
        "faq": [
            ("Do I need more than one SEO tool?", "Sometimes. Research, technical auditing, content optimization and AI visibility are different jobs, but overlapping subscriptions should have a clear operational reason."),
            ("Can AI visibility tools replace Search Console?", "No. They answer different questions. Search Console shows Google search performance, while AI visibility tools estimate or monitor presence in AI-generated answers."),
        ],
    },
}

# Fix accidental tuple syntax if this script is edited by hand later.
CATEGORY_CONFIG["seo"]["choose"][2] = "For AI visibility, verify which engines, prompts and tracking methods are included before treating a visibility score as actionable."


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def date_only(value: object) -> str:
    text = str(value or "")
    return text[:10] if len(text) >= 10 else ""


def source_host(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "") or "Official source"
    except Exception:
        return "Official source"


def latest_verified(tool: dict) -> str:
    candidates = [
        date_only(tool.get("pricing_verified_at")),
        date_only(tool.get("official_verified_at")),
        date_only(tool.get("affiliate_verified_at")),
    ]
    return max([x for x in candidates if x], default="")


def tool_score(tool: dict) -> tuple:
    return (
        1 if tool.get("affiliate_status") == "approved_tracking" else 0,
        1 if tool.get("affiliate_verified") is True else 0,
        1 if tool.get("pricing_verified") is True else 0,
        latest_verified(tool),
        str(tool.get("name") or ""),
    )


def render_tool(tool: dict) -> str:
    features = [esc(x) for x in (tool.get("key_features") or [])[:3] if x]
    feature_html = "".join(f'<span class="pill">{x}</span>' for x in features)
    checked = latest_verified(tool)
    source_urls = []
    for key in ("pricing_source_url", "official_evidence_url", "official_url"):
        url = tool.get(key)
        if isinstance(url, str) and url.startswith("http") and url not in source_urls:
            source_urls.append(url)
    source_text = ", ".join(source_host(x) for x in source_urls[:2]) or "vendor page recorded in COSHUMA data"
    pricing = esc(tool.get("pricing") or "See current vendor pricing")
    desc = esc(tool.get("description") or "See the COSHUMA buyer guide for product details and current verification notes.")
    return f"""
    <article class="card">
      <div class="eyebrow">{esc(tool.get('category_display') or 'Software')}</div>
      <h3><a href="/tool/{esc(tool.get('id'))}.html">{esc(tool.get('name'))}</a></h3>
      <p>{desc}</p>
      <div class="meta"><strong>Pricing snapshot:</strong> {pricing}</div>
      <div class="pills">{feature_html}</div>
      <div class="verify"><strong>Last recorded check:</strong> {esc(checked or 'Date not recorded')} · <strong>Sources checked:</strong> {esc(source_text)}</div>
      <a class="cta" href="/tool/{esc(tool.get('id'))}.html">Read buyer guide →</a>
    </article>"""


def page_shell(title: str, description: str, canonical: str, body: str, schema: dict) -> str:
    schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)} | COSHUMA</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{esc(canonical)}" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="COSHUMA" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:url" content="{esc(canonical)}" />
  <script type="application/ld+json">{schema_json}</script>
  <style>
    :root{{--bg:#08090d;--panel:#11131a;--text:#f8fafc;--muted:#94a3b8;--line:rgba(255,255,255,.1);--violet:#c4b5fd;--cyan:#67e8f9}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.65}}
    a{{color:inherit}} .wrap{{max-width:1100px;margin:0 auto;padding:0 20px}} header{{border-bottom:1px solid var(--line);background:#0c0e14}} header .wrap{{display:flex;justify-content:space-between;gap:20px;align-items:center;padding-top:16px;padding-bottom:16px}} .brand{{font-weight:900;text-decoration:none;font-size:20px}}
    main{{padding:48px 0 80px}} .crumb{{color:#64748b;font-size:14px}} .badge{{display:inline-block;margin-top:28px;border:1px solid rgba(52,211,153,.22);background:rgba(52,211,153,.08);color:#a7f3d0;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:800}}
    h1{{font-size:clamp(38px,6vw,64px);line-height:1.05;letter-spacing:-.04em;margin:18px 0}} h2{{font-size:30px;line-height:1.2;margin-top:52px}} h3{{font-size:22px;margin:6px 0 8px}} .lead{{max-width:820px;color:#cbd5e1;font-size:18px}}
    .decision{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:28px}} .decision>div,.card,.faq,.method{{border:1px solid var(--line);background:rgba(255,255,255,.035);border-radius:18px;padding:20px}} .decision strong{{display:block;color:var(--violet);margin-bottom:8px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px;margin-top:18px}} .card p{{color:#cbd5e1;font-size:14px}} .eyebrow{{color:var(--violet);font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.13em}} .meta,.verify{{color:var(--muted);font-size:12px;margin-top:12px}} .pills{{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}} .pill{{border:1px solid var(--line);border-radius:999px;padding:4px 8px;color:#cbd5e1;font-size:11px}} .cta{{display:inline-block;margin-top:16px;color:var(--cyan);font-weight:800;text-decoration:none}}
    ul{{padding-left:22px;color:#cbd5e1}} .faq{{margin-top:12px}} .faq h3{{font-size:17px}} .faq p{{color:#cbd5e1;margin-bottom:0}} .method{{margin-top:42px;color:#cbd5e1}} footer{{border-top:1px solid var(--line);color:#64748b;padding:28px 0;font-size:12px}}
  </style>
</head>
<body>
<header><div class="wrap"><a class="brand" href="/">COSHUMA</a><a href="/methodology.html">Methodology</a></div></header>
<main><div class="wrap">{body}</div></main>
<footer><div class="wrap">COSHUMA · Independent AI & SaaS decision guides · Verify final pricing and terms on the vendor site before purchasing.</div></footer>
</body></html>"""


def render_category(slug: str, cfg: dict, tools: list[dict]) -> str:
    candidates = [t for t in tools if t.get("category") in cfg["category_ids"]]
    candidates.sort(key=tool_score, reverse=True)
    shortlist = candidates[:8]
    cards = "".join(render_tool(t) for t in shortlist)
    decision = "".join(f"<div><strong>{i+1}</strong>{esc(text)}</div>" for i, text in enumerate(cfg["choose"]))
    faq_html = "".join(f'<div class="faq"><h3>{esc(q)}</h3><p>{esc(a)}</p></div>' for q, a in cfg["faq"])
    faq_schema = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in cfg["faq"]]
    canonical = f"{SITE}/category/{slug}.html"
    body = f"""
      <nav class="crumb"><a href="/">Home</a> / Category / {esc(slug.replace('-', ' ').title())}</nav>
      <div class="badge">Buyer guide · updated {TODAY}</div>
      <h1>{esc(cfg['title'])}</h1>
      <p class="lead">{esc(cfg['intro'])}</p>
      <section class="decision">{decision}</section>
      <h2>Tools to compare first</h2>
      <p class="lead">This shortlist is generated from COSHUMA's existing tool records. Verified partner status can affect link routing, but it does not determine editorial fit or imply a sale.</p>
      <section class="grid">{cards}</section>
      <h2>Questions buyers ask</h2>
      {faq_html}
      <section class="method"><strong>How this page is built:</strong> COSHUMA uses recorded product descriptions, pricing verification dates and official-source URLs from its tool dataset. Missing dates are shown as missing rather than guessed. Affiliate destinations are tracked separately from editorial pricing sources. <a href="/methodology.html">Read the full methodology →</a></section>
    """
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "name": cfg["title"], "url": canonical, "dateModified": TODAY, "publisher": {"@type": "Organization", "name": "COSHUMA"}},
            {"@type": "FAQPage", "mainEntity": faq_schema},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Category", "item": f"{SITE}/category/{slug}.html"},
            ]},
        ],
    }
    return page_shell(cfg["title"], cfg["description"], canonical, body, schema)


def render_methodology() -> str:
    title = "COSHUMA Software Review & Verification Methodology"
    description = "How COSHUMA verifies software pricing, public sources, affiliate links, comparisons and update dates without inventing ratings, sales or conversion claims."
    canonical = f"{SITE}/methodology.html"
    body = f"""
      <nav class="crumb"><a href="/">Home</a> / Methodology</nav>
      <div class="badge">Editorial & verification policy · updated {TODAY}</div>
      <h1>{title}</h1>
      <p class="lead">COSHUMA is an independent AI and SaaS buyer-guide site. Our goal is to make software decisions faster while keeping pricing evidence, affiliate tracking and editorial conclusions separate.</p>
      <section class="grid">
        <div class="method"><h2 style="margin-top:0">1. Official-source checks</h2><p>Where a pricing or product claim is marked verified, COSHUMA records an official vendor source and a verification date when available. If the source or date is missing, the site should not invent one.</p></div>
        <div class="method"><h2 style="margin-top:0">2. Buyer-fit comparisons</h2><p>Comparisons focus on use case, pricing model, strengths, limits and who should or should not buy. A longer feature list is not automatically treated as a better product.</p></div>
        <div class="method"><h2 style="margin-top:0">3. Affiliate-link separation</h2><p>Affiliate destinations are verified independently from editorial pricing sources. An approved tracking link can earn COSHUMA a commission, but approval or publication is not evidence of a signup, commission or sale.</p></div>
        <div class="method"><h2 style="margin-top:0">4. Update dates</h2><p>Pages may show pricing, official-source or affiliate verification dates recorded in the dataset. COSHUMA does not backfill a date when no evidence exists.</p></div>
        <div class="method"><h2 style="margin-top:0">5. Ratings and claims</h2><p>COSHUMA does not publish invented review counts, ratings, traffic, conversions or revenue. Third-party ratings should only appear with an identifiable source.</p></div>
        <div class="method"><h2 style="margin-top:0">6. Corrections</h2><p>Software pricing and partner programs change. Final terms should always be checked on the vendor site, and contradictory newer evidence should replace stale records instead of creating duplicate applications or links.</p></div>
      </section>
      <h2>What a strong COSHUMA buyer page should answer</h2>
      <ul><li>Who is this product best for?</li><li>Who should skip it?</li><li>What pricing or trial information is currently recorded?</li><li>What are the practical trade-offs?</li><li>What alternatives should be compared?</li><li>When and where was the information checked?</li></ul>
      <section class="method"><strong>Affiliate disclosure:</strong> Some outbound links may be affiliate links. That can generate commission for COSHUMA without changing the buyer's price. Sponsorship or affiliate status does not guarantee a positive recommendation.</section>
    """
    schema = {"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": canonical, "dateModified": TODAY, "publisher": {"@type": "Organization", "name": "COSHUMA"}}
    return page_shell(title, description, canonical, body, schema)


def ensure_sitemap(urls: list[str]) -> None:
    if not SITEMAP.exists():
        return
    text = SITEMAP.read_text(encoding="utf-8")
    additions = []
    for url in urls:
        if f"<loc>{url}</loc>" in text:
            continue
        additions.append(f"  <url>\n    <loc>{url}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>\n")
    if additions and "</urlset>" in text:
        text = text.replace("</urlset>", "".join(additions) + "</urlset>")
        SITEMAP.write_text(text, encoding="utf-8")


def main() -> None:
    tools = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
    CATEGORY_DIR.mkdir(parents=True, exist_ok=True)
    urls = []
    for slug, cfg in CATEGORY_CONFIG.items():
        out = CATEGORY_DIR / f"{slug}.html"
        out.write_text(render_category(slug, cfg, tools), encoding="utf-8")
        urls.append(f"{SITE}/category/{slug}.html")
    (PUBLIC / "methodology.html").write_text(render_methodology(), encoding="utf-8")
    urls.append(f"{SITE}/methodology.html")
    ensure_sitemap(urls)
    print(json.dumps({"generated_category_pages": len(CATEGORY_CONFIG), "methodology": True, "sitemap_urls": len(urls)}))


if __name__ == "__main__":
    main()
