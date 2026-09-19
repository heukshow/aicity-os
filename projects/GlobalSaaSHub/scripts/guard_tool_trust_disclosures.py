"""Keep tool-page trust blocks customer-only and prevent affiliate verification overclaims.

The public trust block may show buyer-relevant product/pricing sources, but internal
operational evidence fields must never be rendered into customer pages. An internal
evidence URL is private-by-default unless the same URL is also explicitly present in a
customer-facing source field (`pricing_source_url` or `official_url`).

This script runs late in the production build so earlier page generators cannot
reintroduce internal evidence links or affiliate-state copy. It is intentionally
idempotent and fails closed.
"""
from pathlib import Path
from html import unescape
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
SOURCE_LINK_RE = re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*>.*?</a>', re.S | re.I)
EMPTY_SOURCES_RE = re.compile(
    r'<div><div class="text-\[10px\] uppercase tracking-wider text-slate-500">Sources checked</div>'
    r'<div class="mt-1 text-sm">\s*</div></div>',
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


def customer_source_urls(tool):
    """Explicit public-source allowlist used by the customer-facing trust block."""
    return {
        value.strip()
        for key in ("pricing_source_url", "official_url")
        if isinstance((value := tool.get(key)), str) and value.strip()
    }


def private_only_evidence_urls(tool):
    internal_urls = {
        value.strip()
        for key in ("official_evidence_url", "affiliate_source_url", "affiliate_workflow_url")
        if isinstance((value := tool.get(key)), str) and value.strip()
    }
    return internal_urls - customer_source_urls(tool)


def strip_internal_evidence_links(body, tool):
    """Remove private-by-default evidence pointers from the public Sources checked block."""
    internal_urls = private_only_evidence_urls(tool)
    if not internal_urls:
        return body

    def replace_link(match):
        href = unescape(match.group(1)).strip()
        return "" if href in internal_urls else match.group(0)

    body = SOURCE_LINK_RE.sub(replace_link, body)
    # The source list uses a middle-dot separator. Remove separators left behind
    # when an internal evidence link was filtered out.
    body = re.sub(r'(<div class="mt-1 text-sm">)\s*·\s*', r'\1', body)
    body = re.sub(r'\s*·\s*(</div>)', r'\1', body)
    body = re.sub(r'\s*·\s*·\s*', ' · ', body)
    body = EMPTY_SOURCES_RE.sub("", body)
    return body


tools = json.loads(TOOLS_PATH.read_text(encoding="utf-8"))
by_id = {item.get("id"): item for item in tools if item.get("id")}
changed = 0
checked = 0

for tool_id, tool in by_id.items():
    page = TOOL_DIR / f"{tool_id}.html"
    if not page.exists():
        continue

    original = page.read_text(encoding="utf-8")
    text = original
    match = TRUST_RE.search(text)
    if not match:
        continue
    checked += 1

    # Sendcloud has a handcrafted, source-dated buyer guide. Its generic block
    # is redundant while its customer-facing tracking route is unresolved.
    if tool_id == "sendcloud":
        text = TRUST_RE.sub("", text, count=1)
    else:
        body = match.group(1)
        body = AFFILIATE_DISCLOSURE_RE.sub("", body)
        body = strip_internal_evidence_links(body, tool)
        text = text[: match.start(1)] + body + text[match.end(1) :]

    if not exact_tracking_verified(tool) and FALSE_PHRASE in text:
        raise SystemExit(
            f"Refusing production overclaim: {tool_id} is not approved_tracking "
            "with an exact URL but still says its affiliate destination is verified"
        )

    # Private-only evidence pointers are never part of the generated public trust block.
    public_trust = TRUST_RE.search(text)
    if public_trust:
        public_body = unescape(public_trust.group(1))
        for value in private_only_evidence_urls(tool):
            if value in public_body:
                raise SystemExit(f"Public trust block leaked private-only evidence URL for {tool_id}")

    if text != original:
        page.write_text(text, encoding="utf-8")
        changed += 1

# Explicit safety assertion for the current pending Sendcloud relationship.
sendcloud = by_id.get("sendcloud")
if sendcloud and sendcloud.get("affiliate_status") != "approved_tracking":
    sendcloud_page = TOOL_DIR / "sendcloud.html"
    if sendcloud_page.exists() and FALSE_PHRASE in sendcloud_page.read_text(encoding="utf-8"):
        raise SystemExit("Sendcloud pending state is still presented as a verified affiliate destination")

print(f"Tool trust disclosure guard checked {checked} page(s); changed {changed} page(s).")
