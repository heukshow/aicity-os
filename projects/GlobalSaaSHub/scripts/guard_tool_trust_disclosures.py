"""Prevent tool-page trust blocks from overstating affiliate verification.

`affiliate_verified` in the source dataset can mean that an affiliate *state* was
verified (for example, application_submitted). A public disclosure saying an
"affiliate destination" is verified is only valid when we have an exact,
customer-facing URL and the state is approved_tracking.

This script runs late in the production build so earlier page generators cannot
reintroduce an overclaim. It is intentionally idempotent and fails closed.
"""
from pathlib import Path
import json
import re

PROJECT = Path(__file__).resolve().parents[1]
TOOLS_PATH = PROJECT / "data" / "tools.json"
TOOL_DIR = PROJECT / "public" / "tool"

TRUST_RE = re.compile(
    r"<!-- COSHUMA_TRUST_BLOCK -->(.*?)<!-- /COSHUMA_TRUST_BLOCK -->",
    re.S,
)
AFFILIATE_DISCLOSURE_RE = re.compile(
    r'<div><div class="text-\[10px\] uppercase tracking-wider text-slate-500">'
    r'Affiliate disclosure</div><div class="mt-1 text-sm text-slate-300">'
    r'Affiliate destination verified separately from editorial product sources\.'
    r'</div></div>',
    re.S,
)
FALSE_PHRASE = "Affiliate destination verified separately from editorial product sources."


def exact_tracking_verified(tool):
    url = tool.get("affiliate_url") or tool.get("affiliate_final_url")
    return (
        tool.get("affiliate_verified") is True
        and tool.get("affiliate_status") == "approved_tracking"
        and isinstance(url, str)
        and url.strip().startswith(("https://", "http://"))
    )


tools = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
by_id = {item.get("id"): item for item in tools if item.get("id")}
changed = 0
checked = 0

for tool_id, tool in by_id.items():
    page = TOOL_DIR / f"{tool_id}.html"
    if not page.exists():
        continue

    text = page.read_text(encoding="utf-8")
    match = TRUST_RE.search(text)
    if not match:
        continue
    checked += 1

    # Sendcloud now has a handcrafted, source-dated buyer guide. Its generic
    # block is both redundant and misleading while the PartnerStack application
    # remains pending, so remove the generic block completely.
    if tool_id == "sendcloud":
        text = TRUST_RE.sub("", text, count=1)
    elif not exact_tracking_verified(tool):
        body = match.group(1)
        body = AFFILIATE_DISCLOSURE_RE.sub("", body)
        text = text[: match.start(1)] + body + text[match.end(1) :]

    if not exact_tracking_verified(tool) and FALSE_PHRASE in text:
        raise SystemExit(
            f"Refusing production overclaim: {tool_id} is not approved_tracking "
            "with an exact URL but still says its affiliate destination is verified"
        )

    if text != page.read_text(encoding="utf-8"):
        page.write_text(text, encoding="utf-8")
        changed += 1

# Explicit safety assertion for the current pending Sendcloud relationship.
sendcloud = by_id.get("sendcloud")
if sendcloud and sendcloud.get("affiliate_status") != "approved_tracking":
    sendcloud_page = TOOL_DIR / "sendcloud.html"
    if sendcloud_page.exists() and FALSE_PHRASE in sendcloud_page.read_text(encoding="utf-8"):
        raise SystemExit("Sendcloud pending state is still presented as a verified affiliate destination")

print(f"Tool trust disclosure guard checked {checked} page(s); changed {changed} page(s).")
