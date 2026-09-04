#!/usr/bin/env python3
"""Orchestrator: pick the next candidate, generate metadata, and queue the
render+upload step for a human-in-the-loop agent.

This script intentionally stops BEFORE any video is generated or uploaded.
Repository code currently contains no YouTube Data API OAuth upload wiring.
GitHub Actions secret values are not readable through this integration, so
YOUTUBE_* secret presence must be treated as unknown until verified by a
compatible authenticated environment.

What this script DOES do, safely, with no external calls:
  1. Select the next candidate via select_content.build_candidates()
  2. Generate a template-based hook line + title + description + UTM'd
     COSHUMA URL via generate_metadata.generate()
  3. Append a 'topic_selected' entry to the manifest and a matching
     browser_required_queue.json task for render/upload follow-up.

Usage:
    python3 prepare_next_short.py             # writes manifest + queue entry
    python3 prepare_next_short.py --dry-run   # prints what it would write
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import select_content  # noqa: E402
import generate_metadata  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_JSON = ROOT / "data" / "youtube_shorts_manifest.json"
QUEUE_JSON = ROOT / "data" / "browser_required_queue.json"

HOOK_TEMPLATES = {
    "chatbots_support": "Tired of juggling five tools to run your {category}?",
    "video_editing": "Struggling to edit videos fast enough? This AI tool changes that.",
    "writing": "Staring at a blank page? This AI tool writes the first draft for you.",
    "seo": "Guessing why your content isn't ranking? This AI tool tells you exactly what to fix.",
}
DEFAULT_HOOK = "Still doing {category} the slow way? Here's the AI shortcut."


def build_hook(tool_name: str, category_display: str, category: str) -> str:
    template = HOOK_TEMPLATES.get(category, DEFAULT_HOOK)
    return template.format(category=category_display or category, tool=tool_name)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare_next(dry_run: bool = False) -> dict | None:
    candidates = select_content.build_candidates()
    if not candidates:
        print("No eligible candidates (all affiliate_verified tools already covered, or none pass filters).")
        return None

    top = candidates[0]
    tools = load_json(ROOT / "data" / "tools.json")
    tool = next(t for t in tools if t["id"] == top["affiliate_target"])

    hook = build_hook(tool["name"], tool.get("category_display"), tool.get("category"))
    meta = generate_metadata.generate(
        tool["id"],
        top["campaign_slug"],
        hook,
        hashtags=["AITools", "SaaS"],
    )

    queue_entry = {
        "id": f"coshuma-short-render-{tool['id']}",
        "priority": "medium",
        "status": "browser_required",
        "cost": "0",
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "reason": (
            f"Next Shorts candidate selected by prepare_next_short.py: '{tool['name']}' "
            f"(affiliate_status={tool.get('affiliate_status')}, "
            f"best_hub_pages={top['best_hub_pages']}, compare_pages={top['compare_pages']}). "
            "Rendering still requires a verified creative asset or a generated visual. "
            "Repository code does not yet contain unattended YouTube API upload wiring."
        ),
        "next_action": (
            f"Find an official, reuse-permitted media asset for {tool['name']} when available, "
            "or use a clearly licensed/generated visual. Render a 9:16 1080x1920 Short (30-45s) "
            "with COSHUMA intro/outro cards and safe-area captions. Run quality_gate.py before "
            f"upload. Use this UTM-tagged metadata for campaign_slug={top['campaign_slug']}:\n"
            f"TITLE: {meta['title']}\nDESCRIPTION:\n{meta['description']}"
        ),
        "do_not": [
            "Do not use a generic homepage URL as the CTA — use the coshuma_url below.",
            "Do not fabricate pricing, discount codes, or reuse permission.",
            "Do not upload before quality_gate.py passes.",
            "Do not re-render this same tool if a ready/uploaded manifest entry already covers the campaign.",
        ],
        "coshuma_url": meta["coshuma_url"],
        "affiliate_target": tool["id"],
        "campaign_slug": top["campaign_slug"],
    }

    manifest_entry = {
        "content_slug": top["campaign_slug"],
        "source_page": top["source_page"],
        "affiliate_target": tool["id"],
        "affiliate_url": tool.get("affiliate_url"),
        "campaign_slug": top["campaign_slug"],
        "coshuma_url": meta["coshuma_url"],
        "youtube_video_id": None,
        "title": meta["title"],
        "video_file_name": None,
        "video_sha256": None,
        "video_duration_seconds": None,
        "resolution": None,
        "script_hash": None,
        "published_at": None,
        "status": "topic_selected",
        "ga4": {"source": "youtube", "medium": "shorts", "campaign": top["campaign_slug"]},
        "provenance": "auto-selected by prepare_next_short.py; not yet rendered or uploaded.",
        "notes": "See matching entry in browser_required_queue.json for the render+upload task.",
    }

    if dry_run:
        print(json.dumps({"queue_entry": queue_entry, "manifest_entry": manifest_entry}, indent=2, ensure_ascii=False))
        return manifest_entry

    manifest = load_json(MANIFEST_JSON)
    manifest["entries"].append(manifest_entry)
    save_json(MANIFEST_JSON, manifest)

    queue = load_json(QUEUE_JSON)
    if not any(e.get("id") == queue_entry["id"] for e in queue):
        queue.append(queue_entry)
        save_json(QUEUE_JSON, queue)

    print(f"Queued next Short candidate: {tool['name']} ({top['campaign_slug']})")
    return manifest_entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    prepare_next(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
