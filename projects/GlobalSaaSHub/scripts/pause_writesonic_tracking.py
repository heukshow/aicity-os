#!/usr/bin/env python3
"""Fail closed when Writesonic's vendor-reported affiliate tracking is paused."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "data" / "tools.json"
PUBLIC = ROOT / "public"
TOOL_ID = "writesonic"
TRACKING_URL = "https://writesonic.com?fp_ref=sang-kwon-f5452a"
OFFICIAL_URL = "https://writesonic.com/"


def _rewrite_anchor(match: re.Match[str]) -> str:
    tag = match.group(0)
    if TRACKING_URL not in tag:
        return tag

    tag = tag.replace(TRACKING_URL, OFFICIAL_URL)
    tag = re.sub(r'(data-cta\s*=\s*["\'])affiliate(["\'])', r'\1official\2', tag)

    rel_match = re.search(r'rel\s*=\s*(["\'])(.*?)\1', tag)
    if rel_match:
        tokens = [
            token
            for token in rel_match.group(2).split()
            if token.lower() not in {"sponsored", "nofollow"}
        ]
        for required in ("noopener", "noreferrer"):
            if required not in tokens:
                tokens.append(required)
        replacement = f'rel={rel_match.group(1)}{" ".join(tokens)}{rel_match.group(1)}'
        tag = tag[: rel_match.start()] + replacement + tag[rel_match.end() :]
    return tag


data = json.loads(TOOLS.read_text(encoding="utf-8"))
records = data if isinstance(data, list) else data.get("tools", [])
writesonic = next((item for item in records if item.get("id") == TOOL_ID), None)
if writesonic is None:
    raise SystemExit("Writesonic record is missing from data/tools.json")

if not writesonic.get("affiliate_public_cta_paused"):
    print("Writesonic affiliate CTA pause is not active")
    raise SystemExit(0)

if writesonic.get("affiliate_public_cta_pause_reason") != "vendor_reported_tracking_incident":
    raise SystemExit("Writesonic CTA pause is active without the expected vendor incident reason")
if writesonic.get("affiliate_url") != TRACKING_URL:
    raise SystemExit("Writesonic canonical affiliate URL drifted during the tracking pause")
if writesonic.get("affiliate_status") != "approved_tracking":
    raise SystemExit("Writesonic approval state drifted during the temporary tracking pause")

text_replacements = {
    "COSHUMA's verified Writesonic referral link": "Writesonic's official site",
    "Start Writesonic via verified partner link →": "Open Writesonic's official site →",
    "COSHUMA uses the exact customer-facing referral URL already issued for its Writesonic partner account. Writesonic's current first-party affiliate page advertises <strong class=\"text-white\">20% recurring commission for up to 12 months</strong> with a <strong class=\"text-white\">60-day cookie</strong>. Those are affiliate terms, not a guaranteed buyer discount.": "Open Writesonic's official site to evaluate the current trial and product fit. Confirm live pricing, eligibility and trial terms before starting.",
    "The first button preserves the exact Writesonic customer-facing referral URL already verified for COSHUMA. The pricing button is a separate official non-affiliate reference; COSHUMA does not guess a pricing deep link. A click, trial, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.": "The first button opens Writesonic's official homepage. The pricing button is a separate official pricing reference. Check current product and trial terms before choosing a plan.",
}

files_changed = 0
links_paused = 0
for path in sorted(PUBLIC.rglob("*.html")):
    original = path.read_text(encoding="utf-8")
    updated, replaced = re.subn(r"<a\b[^>]*>", _rewrite_anchor, original, flags=re.IGNORECASE)
    links_paused += replaced

    # Catch non-anchor or encoded copies after preserving the canonical URL in data only.
    updated = updated.replace(TRACKING_URL, OFFICIAL_URL)
    for old, new in text_replacements.items():
        updated = updated.replace(old, new)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        files_changed += 1

remaining = []
for path in sorted(PUBLIC.rglob("*")):
    if path.is_file() and path.suffix.lower() in {".html", ".js", ".json", ".xml"}:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if TRACKING_URL in text:
            remaining.append(str(path.relative_to(ROOT)))

if remaining:
    raise SystemExit(
        "Writesonic tracking URL remains in public source while vendor pause is active: "
        + ", ".join(remaining)
    )

print(
    f"Paused Writesonic affiliate CTAs: {links_paused} links across "
    f"{files_changed} public files; canonical verified URL preserved in data."
)
