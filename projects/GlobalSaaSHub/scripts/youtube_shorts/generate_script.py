#!/usr/bin/env python3
"""Generate a deterministic, evidence-bounded Shorts script.

Preferred campaigns live in data/youtube_shorts_campaigns.json. If a campaign
brief exists, only those verified beats are used. Otherwise the fallback uses
the tool description and avoids pricing/promo claims entirely.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS_JSON = ROOT / "data" / "tools.json"
CAMPAIGNS_JSON = ROOT / "data" / "youtube_shorts_campaigns.json"

BANNED = (
    "guaranteed income",
    "guaranteed money",
    "risk-free profit",
    "100% 수익 보장",
    "무조건 돈",
)


def load_tool(tool_id: str) -> dict:
    tools = json.loads(TOOLS_JSON.read_text(encoding="utf-8"))
    for tool in tools:
        if tool.get("id") == tool_id:
            return tool
    raise KeyError(f"Unknown tool id: {tool_id}")


def load_campaign(tool_id: str) -> dict | None:
    if not CAMPAIGNS_JSON.exists():
        return None
    data = json.loads(CAMPAIGNS_JSON.read_text(encoding="utf-8"))
    return data.get(tool_id)


def _validate_copy(text: str) -> None:
    lowered = text.lower()
    for phrase in BANNED:
        if phrase.lower() in lowered:
            raise ValueError(f"Banned unverifiable claim: {phrase}")


def generate(tool_id: str) -> dict:
    tool = load_tool(tool_id)
    campaign = load_campaign(tool_id)

    if campaign:
        hook = campaign["hook"].strip()
        beats = [b.strip() for b in campaign.get("beats", []) if b.strip()]
        cta = campaign["cta"].strip()
        campaign_slug = campaign.get("campaign_slug") or tool_id
        source_page = campaign.get("source_page") or f"/tool/{tool_id}.html"
        evidence = campaign.get("evidence")
    else:
        hook = f"Still doing {tool.get('category_display') or 'this work'} the slow way?"
        desc = (tool.get("description") or "").strip()
        beats = [desc] if desc else [f"{tool['name']} is listed in the COSHUMA buyer guide."]
        cta = f"See the full {tool['name']} buyer guide on COSHUMA."
        campaign_slug = tool_id
        source_page = f"/tool/{tool_id}.html"
        evidence = None

    narration = " ".join([hook, *beats, cta])
    _validate_copy(narration)

    cards = [hook, *beats, cta]
    script_hash = hashlib.sha256(narration.encode("utf-8")).hexdigest()
    return {
        "tool_id": tool_id,
        "tool_name": tool["name"],
        "campaign_slug": campaign_slug,
        "source_page": source_page,
        "hook": hook,
        "beats": beats,
        "cta": cta,
        "cards": cards,
        "narration": narration,
        "script_hash": script_hash,
        "hashtags": (campaign or {}).get("hashtags", ["AITools", "SaaS"]),
        "evidence": evidence,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool_id")
    args = parser.parse_args()
    print(json.dumps(generate(args.tool_id), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
