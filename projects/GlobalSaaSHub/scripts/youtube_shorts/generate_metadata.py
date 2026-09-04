#!/usr/bin/env python3
"""Generate YouTube Shorts title/description/hashtags for one candidate.

Follows the CTA structure the brief and the existing 3 published Shorts both
use: drive to the COSHUMA page first (with utm_source=youtube&utm_medium=shorts
&utm_campaign=<campaign_slug>), not straight to the raw affiliate link. The
direct affiliate URL is only included when include_direct_affiliate_link=True
is passed explicitly (off by default, matching brief section 5).

This intentionally reuses the same query-param names
(utm_source/utm_medium/utm_campaign) that
projects/GlobalSaaSHub/public/affiliate-attribution.js already reads on every
tool/compare/best page, so no changes to that script are needed for Shorts
traffic to show up correctly attributed in GA4.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS_JSON = ROOT / "data" / "tools.json"

BANNED_PHRASES = [
    "guaranteed income", "guaranteed money", "무조건 돈", "100% 수익 보장",
    "get rich", "passive income guaranteed", "risk-free profit",
]


def load_tool(tool_id: str) -> dict:
    tools = json.loads(TOOLS_JSON.read_text(encoding="utf-8"))
    for t in tools:
        if t.get("id") == tool_id:
            return t
    raise KeyError(f"tool id not found in tools.json: {tool_id}")


def build_coshuma_url(source_page: str, campaign_slug: str) -> str:
    return (
        f"https://coshuma.com{source_page}"
        f"?utm_source=youtube&utm_medium=shorts&utm_campaign={campaign_slug}"
    )


def build_title(tool: dict, hook: str | None = None) -> str:
    name = tool["name"]
    if hook:
        title = f"{hook} - {name} #Shorts"
    else:
        title = f"{name}: {tool.get('description', '').split('.')[0]}"[:95]
    return title[:100]


def build_description(
    tool: dict,
    coshuma_url: str,
    hook_line: str,
    affiliate_url: str | None = None,
    include_direct_affiliate_link: bool = False,
    extra_hashtags: list[str] | None = None,
) -> str:
    lines = [hook_line, ""]
    lines.append(f"Full review, features, and current pricing on COSHUMA:\n{coshuma_url}")

    if include_direct_affiliate_link and affiliate_url:
        lines.append("")
        lines.append(f"Start here (verified partner link): {affiliate_url}")
        lines.append("")
        lines.append(
            "Affiliate Disclosure: This video contains an affiliate link. "
            "COSHUMA may earn a commission if you sign up through this link, "
            "at no extra cost to you."
        )

    hashtags = ["#" + re.sub(r"[^A-Za-z0-9]", "", tool["name"])[:24], "#Shorts", "#SaaS"]
    for h in (extra_hashtags or []):
        tag = "#" + re.sub(r"[^A-Za-z0-9]", "", h)
        if tag not in hashtags:
            hashtags.append(tag)

    lines.append("")
    lines.append(" ".join(dict.fromkeys(hashtags)))

    description = "\n".join(lines)
    lowered = description.lower()
    for banned in BANNED_PHRASES:
        if banned.lower() in lowered:
            raise ValueError(f"banned phrase found in generated description: {banned!r}")
    if len(description) > 5000:
        raise ValueError("description exceeds YouTube's 5000-character limit")
    return description


def generate(
    tool_id: str,
    campaign_slug: str,
    hook_line: str,
    hashtags: list[str] | None = None,
    include_direct_affiliate_link: bool = False,
) -> dict:
    tool = load_tool(tool_id)
    source_page = f"/tool/{tool_id}.html"
    coshuma_url = build_coshuma_url(source_page, campaign_slug)
    title = build_title(tool, hook=hook_line.rstrip("."))
    description = build_description(
        tool,
        coshuma_url,
        hook_line,
        affiliate_url=tool.get("affiliate_url"),
        include_direct_affiliate_link=include_direct_affiliate_link,
        extra_hashtags=hashtags,
    )
    return {
        "affiliate_target": tool_id,
        "campaign_slug": campaign_slug,
        "coshuma_url": coshuma_url,
        "title": title,
        "description": description,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool_id")
    parser.add_argument("--campaign-slug", default=None)
    parser.add_argument("--hook", required=True, help="one-line hook, e.g. 'Struggling to grow on YouTube?'")
    parser.add_argument("--hashtag", action="append", default=[])
    parser.add_argument("--include-direct-affiliate-link", action="store_true")
    args = parser.parse_args()

    result = generate(
        args.tool_id,
        args.campaign_slug or args.tool_id,
        args.hook,
        hashtags=args.hashtag,
        include_direct_affiliate_link=args.include_direct_affiliate_link,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
