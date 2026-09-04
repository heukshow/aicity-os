#!/usr/bin/env python3
"""Select the next COSHUMA revenue page to turn into a YouTube Short.

Priority order (highest first), matching the brief's revenue-first ranking:
  1. tools.json entries with affiliate_verified == true AND a real tracking
     affiliate_url (not just the bare official homepage)
  2. among those, tools that are already featured on a /best/ Money Hub page
  3. then tools that appear in a /compare/ page
  4. then plain /tool/ pages
  5. affiliate_status values that imply an active, already-approved program
     (approved_tracking / approved_account / approved_link_verified) rank
     above application_submitted / pending statuses, which rank above
     everything else.

Never re-selects a (affiliate_target, campaign_slug) pair already present in
the manifest with status in {rendered, ready, uploaded} — see
data/youtube_shorts_manifest.json's duplicate_prevention_rule.

Usage:
    python3 select_content.py                 # print the top candidate as JSON
    python3 select_content.py --top 5          # print the top 5 candidates
    python3 select_content.py --exclude gohighlevel,vidiq
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # projects/GlobalSaaSHub
DATA_DIR = ROOT / "data"
PUBLIC_DIR = ROOT / "public"
TOOLS_JSON = DATA_DIR / "tools.json"
MANIFEST_JSON = DATA_DIR / "youtube_shorts_manifest.json"

APPROVED_STATUSES = {"approved_tracking", "approved_account", "approved_link_verified"}
PENDING_STATUSES = {"application_submitted", "email_verification_pending", "approved_account_pending"}

GENERIC_HOMEPAGE_MARKERS = ("://www.", "://")  # used only as a fallback shape check


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_generic_homepage_url(affiliate_url: str, official_url: str) -> bool:
    """True if affiliate_url is really just the plain homepage (no tracking)."""
    if not affiliate_url:
        return True
    if official_url and affiliate_url.rstrip("/") == official_url.rstrip("/"):
        return True
    # No query string and no obvious referral path segment => treat as generic.
    has_query = "?" in affiliate_url
    has_ref_path = re.search(r"/(ref|via|fp_ref|coshuma|partner)(?:[/=]|$)", affiliate_url, re.I)
    return not (has_query or has_ref_path)


def find_pages_referencing(tool_id: str, html_dir: Path) -> list[str]:
    """Return relative paths of pages under html_dir whose content links to
    /tool/{tool_id}.html — used to detect /best/ and /compare/ coverage."""
    hits = []
    if not html_dir.exists():
        return hits
    needle = f"/tool/{tool_id}.html"
    for html_file in html_dir.glob("*.html"):
        try:
            text = html_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if needle in text or tool_id in html_file.stem.split("-vs-"):
            hits.append(str(html_file.relative_to(ROOT)))
    return hits


def load_manifest_blocklist(manifest: dict) -> set[tuple[str, str]]:
    blocked = set()
    for entry in manifest.get("entries", []):
        if entry.get("status") in {"rendered", "ready", "uploaded"}:
            blocked.add((entry.get("affiliate_target"), entry.get("campaign_slug")))
    return blocked


def score_candidate(tool: dict, best_hits: list[str], compare_hits: list[str]) -> tuple:
    """Sort key: higher status_rank/hub_rank first, ties broken alphabetically
    by tool id (ascending) so the ordering is stable and not an accidental
    side effect of sorting the whole tuple in reverse."""
    status = tool.get("affiliate_status")
    status_rank = 2 if status in APPROVED_STATUSES else (1 if status in PENDING_STATUSES else 0)
    hub_rank = 2 if best_hits else (1 if compare_hits else 0)
    return (-status_rank, -hub_rank, tool.get("id", ""))


def build_candidates(exclude_ids: set[str] | None = None) -> list[dict]:
    exclude_ids = exclude_ids or set()
    tools = _load_json(TOOLS_JSON)
    manifest = _load_json(MANIFEST_JSON) if MANIFEST_JSON.exists() else {"entries": []}
    blocklist = load_manifest_blocklist(manifest)

    best_dir = PUBLIC_DIR / "best"
    compare_dir = PUBLIC_DIR / "compare"

    candidates = []
    for tool in tools:
        tool_id = tool.get("id")
        if not tool_id or tool_id in exclude_ids:
            continue
        if not tool.get("affiliate_verified"):
            continue
        affiliate_url = tool.get("affiliate_url") or ""
        official_url = tool.get("official_url") or ""
        if is_generic_homepage_url(affiliate_url, official_url):
            continue  # explicit rule: never use a generic homepage URL as the CTA target

        default_campaign_slug = tool_id
        if (tool_id, default_campaign_slug) in blocklist:
            continue  # already covered by an uploaded/ready Short under this campaign slug

        best_hits = find_pages_referencing(tool_id, best_dir)
        compare_hits = find_pages_referencing(tool_id, compare_dir)
        tool_page = PUBLIC_DIR / "tool" / f"{tool_id}.html"

        candidates.append({
            "affiliate_target": tool_id,
            "name": tool.get("name"),
            "affiliate_status": tool.get("affiliate_status"),
            "affiliate_url": affiliate_url,
            "source_page": f"/tool/{tool_id}.html" if tool_page.exists() else None,
            "best_hub_pages": best_hits,
            "compare_pages": compare_hits,
            "campaign_slug": default_campaign_slug,
            "coshuma_url": f"https://coshuma.com/tool/{tool_id}.html"
                           f"?utm_source=youtube&utm_medium=shorts&utm_campaign={default_campaign_slug}",
            "_score": score_candidate(tool, best_hits, compare_hits),
        })

    candidates.sort(key=lambda c: c["_score"])
    for c in candidates:
        del c["_score"]
    return candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top", type=int, default=1, help="number of candidates to print")
    parser.add_argument("--exclude", default="", help="comma-separated tool ids to skip")
    args = parser.parse_args()

    exclude_ids = {t.strip() for t in args.exclude.split(",") if t.strip()}
    candidates = build_candidates(exclude_ids)
    print(json.dumps(candidates[: args.top], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
