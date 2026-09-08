from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CATEGORY_DIR = PUBLIC / "category"
TOOLS = json.loads((ROOT / "data" / "tools.json").read_text(encoding="utf-8"))

# Category hubs should be ranked by buyer relevance and evidence quality, never by
# whether COSHUMA has an approved affiliate destination. Affiliate status only
# controls outbound routing on the underlying product pages.
CATEGORY_RULES = {
    "automation": {
        "categories": {"workflow_auto"},
        "include_ids": {"make-com", "n8n"},
        "preferred_ids": ["make-com", "n8n"],
    },
    "sales-crm": {"categories": {"sales_crm", "chatbots_support", "email_outreach"}},
    "ai-agents": {"categories": {"ai_agents"}},
    "ai-video": {"categories": {"video_gen"}},
    "ai-voice": {"categories": {"voice_cloning"}},
    "seo": {"categories": {"seo_tools"}},
}


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def date10(value: object) -> str:
    text = str(value or "")
    return text[:10] if len(text) >= 10 else ""


def latest_check(tool: dict) -> str:
    dates = [
        date10(tool.get("pricing_verified_at")),
        date10(tool.get("official_verified_at")),
        date10(tool.get("affiliate_verified_at")),
    ]
    return max((d for d in dates if d), default="")


def host(url: object) -> str:
    try:
        return urlparse(str(url or "")).netloc.replace("www.", "") or "official source"
    except Exception:
        return "official source"


def evidence_score(tool: dict) -> tuple[int, int, str, str]:
    """Buyer-facing evidence quality only; intentionally excludes affiliate fields."""
    return (
        1 if tool.get("pricing_verified") is True else 0,
        1 if tool.get("official_verification_status") == "verified" else 0,
        max(date10(tool.get("pricing_verified_at")), date10(tool.get("official_verified_at"))),
        str(tool.get("name") or "").lower(),
    )


def render_card(tool: dict) -> str:
    features = "".join(
        f'<span class="pill">{esc(feature)}</span>'
        for feature in (tool.get("key_features") or [])[:3]
    )
    sources: list[str] = []
    for key in ("pricing_source_url", "official_evidence_url", "official_url"):
        url = tool.get(key)
        if isinstance(url, str) and url.startswith("http") and url not in sources:
            sources.append(url)
    source_text = ", ".join(host(url) for url in sources[:2]) or "vendor page recorded in COSHUMA data"
    tool_id = esc(tool.get("id"))
    return (
        f'<article class="card" data-category-tool-id="{tool_id}">'
        f'<div class="eyebrow">{esc(tool.get("category_display") or "Software")}</div>'
        f'<h3><a href="/tool/{tool_id}.html">{esc(tool.get("name"))}</a></h3>'
        f'<p>{esc(tool.get("description") or "See the COSHUMA buyer guide for product details.")}</p>'
        f'<div class="meta"><strong>Pricing snapshot:</strong> '
        f'{esc(tool.get("pricing") or "See current vendor pricing")}</div>'
        f'<div class="pills">{features}</div>'
        f'<div class="verify"><strong>Last recorded check:</strong> '
        f'{esc(latest_check(tool) or "Date not recorded")} · '
        f'<strong>Sources checked:</strong> {esc(source_text)}</div>'
        f'<a class="cta" href="/tool/{tool_id}.html">Read buyer guide →</a>'
        f'</article>'
    )


def shortlist(rule: dict) -> list[dict]:
    categories = set(rule.get("categories") or ())
    include_ids = set(rule.get("include_ids") or ())
    candidates = [
        tool
        for tool in TOOLS
        if tool.get("category") in categories or tool.get("id") in include_ids
    ]

    preferred = list(rule.get("preferred_ids") or ())
    preferred_rank = {tool_id: index for index, tool_id in enumerate(preferred)}

    def sort_key(tool: dict) -> tuple:
        tool_id = str(tool.get("id") or "")
        if tool_id in preferred_rank:
            return (1, -preferred_rank[tool_id], *evidence_score(tool))
        return (0, 0, *evidence_score(tool))

    candidates.sort(key=sort_key, reverse=True)
    return candidates[:8]


def refine(slug: str, rule: dict) -> int:
    path = CATEGORY_DIR / f"{slug}.html"
    if not path.exists():
        return 0
    page = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<h2>Tools to compare first</h2>.*?<section class="grid">)(.*?)(</section><h2>Questions buyers ask</h2>)',
        re.S,
    )
    match = pattern.search(page)
    if not match:
        raise SystemExit(f"Category grid not found: {path}")

    cards = "".join(render_card(tool) for tool in shortlist(rule))
    if not cards:
        raise SystemExit(f"No buyer-relevant tools found for category: {slug}")

    updated = page[: match.start(2)] + cards + page[match.end(2) :]
    path.write_text(updated, encoding="utf-8")
    return cards.count('<article class="card"')


def main() -> None:
    results = {slug: refine(slug, rule) for slug, rule in CATEGORY_RULES.items()}
    print(json.dumps({"refined_category_cards": results, "affiliate_neutral_ranking": True}))


if __name__ == "__main__":
    main()
