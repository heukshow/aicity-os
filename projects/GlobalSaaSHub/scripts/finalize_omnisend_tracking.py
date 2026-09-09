from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
TRACKING_URL = "https://your.omnisend.com/4aA5k9"
PRICING_TRACKING_URL = "https://your.omnisend.com/VOKyAj"
CHECKED_AT = "2026-09-09T19:56:33+09:00"
EVIDENCE = (
    "Omnisend Senior Affiliate Marketing Manager Deimantė Vaitkevičiūtė replied to "
    "support@coshuma.com in Gmail message 1a0855caf8f6dee2 with COSHUMA's exact general customer tracking URL "
    "https://your.omnisend.com/4aA5k9. In Gmail message 1a085d0074ddb3a0, replying to COSHUMA's request for a "
    "pricing-destination link, she supplied the exact direct pricing tracking URL https://your.omnisend.com/VOKyAj. "
    "Omnisend's official affiliate documentation states approved affiliates must use the exact links supplied through "
    "Impact Content > Assets; tracking/reporting are handled through Impact with a 60-day attribution window."
)
NEXT_ACTION = (
    "Preserve the vendor-issued general URL as the canonical Omnisend affiliate_url. Use the separate vendor-issued "
    "https://your.omnisend.com/VOKyAj only for pricing-intent Omnisend CTAs. Do not synthesize deep links or substitute "
    "the homepage, Impact dashboard, onboarding URL, or email redirect. Track real clicks/signups/commissions separately; "
    "no revenue is inferred from approval or link issuance."
)

for url in (TRACKING_URL, PRICING_TRACKING_URL):
    if not url.startswith("https://your.omnisend.com/"):
        raise SystemExit("Refusing non-Omnisend tracking host")
if TRACKING_URL == PRICING_TRACKING_URL:
    raise SystemExit("Expected separate Omnisend general and pricing tracking URLs")

for rel in ("data/tools.json", "data/tools.next.json"):
    path = ROOT / rel
    data = json.loads(path.read_text(encoding="utf-8"))
    matches = [t for t in data if t.get("id") == "omnisend"]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one omnisend record in {rel}")
    tool = matches[0]
    tool.update({
        "affiliate_url": TRACKING_URL,
        "affiliate_verified": True,
        "affiliate_status": "approved_tracking",
        "affiliate_final_url": TRACKING_URL,
        "affiliate_verified_at": CHECKED_AT,
        "affiliate_status_checked_at": CHECKED_AT,
        "affiliate_status_evidence_url": "https://www.omnisend.com/affiliates/",
        "affiliate_workflow_url": "https://app.impact.com/",
        "affiliate_next_action": NEXT_ACTION,
    })
    markers = list(tool.get("affiliate_evidence_markers") or [])
    markers = [m for m in markers if "Keep affiliate_url null" not in m and "exact tracking URL" not in m.lower()]
    markers.extend([EVIDENCE, NEXT_ACTION, "data/omnisend-affiliate-approved-2026-09-09.md"])
    tool["affiliate_evidence_markers"] = list(dict.fromkeys(markers))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

queue_path = ROOT / "data/browser_required_queue.json"
queue = json.loads(queue_path.read_text(encoding="utf-8"))
for entry in queue:
    if entry.get("tool_id") == "omnisend" or str(entry.get("id", "")).startswith("omnisend-"):
        entry.update({
            "status": "resolved",
            "affiliate_status": "approved_tracking",
            "exact_tracking_url": TRACKING_URL,
            "blocker": None,
            "browser_required": False,
            "next_action": NEXT_ACTION,
            "do_not_reapply": True,
        })
queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

page = ROOT / "public/tool/omnisend.html"
text = page.read_text(encoding="utf-8")

# Pricing-intent Omnisend CTAs receive the vendor-issued direct pricing tracking URL.
text = re.sub(
    r'<a data-cta="official"(?P<attrs>[^>]*?)href="https://www\.omnisend\.com/pricing/"(?P<tail>[^>]*)>',
    lambda m: '<a data-cta="affiliate"' + m.group('attrs') + f'href="{PRICING_TRACKING_URL}"' +
              re.sub(r'rel="[^"]*"', 'rel="sponsored noopener noreferrer"', m.group('tail')) + '>',
    text,
)
# If an earlier generic sync already monetized a pricing-intent anchor with the general URL,
# upgrade only explicit Omnisend pricing CTA sources to the vendor-issued pricing destination.
text = re.sub(
    rf'(<a\b[^>]*data-cta="affiliate"[^>]*data-tool-id="omnisend"[^>]*data-cta-source="[^"]*pricing[^"]*"[^>]*href="){re.escape(TRACKING_URL)}("[^>]*>)',
    rf'\1{PRICING_TRACKING_URL}\2',
    text,
)

# General Omnisend CTAs keep the canonical vendor-issued general tracking URL.
text = re.sub(
    r'<a data-cta="official"(?P<attrs>[^>]*?)href="https://www\.omnisend\.com/"(?P<tail>[^>]*)>',
    lambda m: '<a data-cta="affiliate"' + m.group('attrs') + f'href="{TRACKING_URL}"' +
              re.sub(r'rel="[^"]*"', 'rel="sponsored noopener noreferrer"', m.group('tail')) + '>',
    text,
)
text = text.replace(
    '<a data-cta="official" href="https://www.omnisend.com/" target="_blank" rel="noopener noreferrer"',
    f'<a data-cta="affiliate" data-tool-id="omnisend" data-cta-source="omnisend_primary" href="{TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer"',
)
text = text.replace("Affiliate approved · exact tracking link pending verification", "Affiliate approved · tracking links verified")
text = text.replace("Affiliate approved · tracking link verified", "Affiliate approved · tracking links verified")
text = text.replace(
    "Omnisend's Senior Affiliate Marketing Manager supplied COSHUMA's exact customer tracking URL and confirmed it is the link in Impact Assets. Omnisend buttons now use that verified link; COSHUMA may earn a commission on an eligible purchase at no extra cost to you.",
    "Omnisend's Senior Affiliate Marketing Manager supplied COSHUMA's exact customer tracking URL and a separate direct pricing tracking URL. Pricing-intent buttons use the vendor-issued pricing destination; COSHUMA may earn a commission on an eligible purchase at no extra cost to you."
)
text = text.replace(
    "The approval email did not contain an account-specific customer tracking URL, so Omnisend buttons intentionally remain ordinary official links until the exact Impact-issued URL is copied and verified.",
    "Omnisend's Senior Affiliate Marketing Manager supplied COSHUMA's exact customer tracking URL and a separate direct pricing tracking URL. Pricing-intent buttons use the vendor-issued pricing destination; COSHUMA may earn a commission on an eligible purchase at no extra cost to you."
)

# This finalizer runs after generic page generation. Normalize the visible trust-block
# verification date here so stale source metadata cannot survive the final production pass.
trust_marker = "<!-- COSHUMA_TRUST_BLOCK -->"
if trust_marker not in text:
    raise SystemExit("Omnisend trust block missing; cannot normalize verification date safely")
prefix, trust_tail = text.split(trust_marker, 1)
trust_tail, trust_date_changes = re.subn(
    r'(<div[^>]*>Last verified</div>\s*<div[^>]*>)(?:September 1, 2026|Sep 1, 2026)(</div>)',
    r'\1September 9, 2026\2',
    trust_tail,
    count=1,
)
text = prefix + trust_marker + trust_tail
if trust_date_changes != 1:
    if not re.search(r'<div[^>]*>Last verified</div>\s*<div[^>]*>September 9, 2026</div>', trust_tail):
        raise SystemExit("Omnisend trust-block verification date was not normalized")
if re.search(r'<div[^>]*>Last verified</div>\s*<div[^>]*>(?:September 1, 2026|Sep 1, 2026)</div>', trust_tail):
    raise SystemExit("Stale Omnisend trust-block verification date survived finalizer")

if TRACKING_URL not in text:
    raise SystemExit("Omnisend general tracking URL was not installed in buyer page")
if PRICING_TRACKING_URL not in text:
    raise SystemExit("Omnisend pricing tracking URL was not installed in buyer page")
page.write_text(text, encoding="utf-8")

# Search-comparison pages are generated before this finalizer. Preserve destination intent:
# pricing links get the dedicated pricing tracker; all other explicit Omnisend decision CTAs
# get the canonical general tracker. Source links and unrelated vendor links remain untouched.
comparison_changes = 0
pricing_comparison_ctas = 0
for compare_page in sorted((ROOT / "public/compare").glob("*.html")):
    compare_text = compare_page.read_text(encoding="utf-8")
    if 'data-tool-id="omnisend"' not in compare_text:
        continue

    def convert_compare_anchor(match):
        tag = match.group(0)
        href_match = re.search(r'href="(https://www\.omnisend\.com/[^"]*)"', tag)
        if not href_match:
            return tag
        destination = href_match.group(1)
        target = PRICING_TRACKING_URL if destination.startswith("https://www.omnisend.com/pricing/") else TRACKING_URL
        tag = re.sub(r'data-cta="(?:official|affiliate)"', 'data-cta="affiliate"', tag, count=1)
        tag = re.sub(r'href="https://www\.omnisend\.com/[^"]*"', f'href="{target}"', tag, count=1)
        if re.search(r'rel="[^"]*"', tag):
            tag = re.sub(r'rel="[^"]*"', 'rel="sponsored noopener noreferrer"', tag, count=1)
        else:
            tag = tag[:-1] + ' rel="sponsored noopener noreferrer">'
        return tag

    updated = re.sub(r'<a\b[^>]*data-tool-id="omnisend"[^>]*>', convert_compare_anchor, compare_text)

    # Generic monetization runs earlier and may have already replaced a validated pricing
    # destination with the canonical general tracker. Restore only anchors whose explicit
    # CTA source is pricing-intent; this URL is vendor-issued, not synthesized.
    def restore_pricing_tracker(match):
        nonlocal_tag = match.group(0)
        return re.sub(
            rf'href="{re.escape(TRACKING_URL)}"',
            f'href="{PRICING_TRACKING_URL}"',
            nonlocal_tag,
            count=1,
        )

    pricing_pattern = re.compile(
        r'<a\b(?=[^>]*data-cta="affiliate")(?=[^>]*data-tool-id="omnisend")(?=[^>]*data-cta-source="[^"]*pricing[^"]*")(?=[^>]*href="https://your\.omnisend\.com/4aA5k9")[^>]*>'
    )
    updated, restored = pricing_pattern.subn(restore_pricing_tracker, updated)
    pricing_comparison_ctas += restored

    if updated != compare_text:
        compare_page.write_text(updated, encoding="utf-8")
        comparison_changes += 1
    if not re.search(
        r'<a\b[^>]*data-cta="affiliate"[^>]*data-tool-id="omnisend"[^>]*href="https://your\.omnisend\.com/[^"]+"',
        updated,
    ):
        raise SystemExit(f"Omnisend comparison CTA was not monetized safely: {compare_page}")

# The known Search Console opportunity page must keep the vendor-issued pricing tracker.
privy_compare = (ROOT / "public/compare/privy-vs-omnisend.html").read_text(encoding="utf-8")
if 'data-cta-source="privy-vs-omnisend-pricing"' not in privy_compare or f'href="{PRICING_TRACKING_URL}"' not in privy_compare:
    raise SystemExit("Privy vs Omnisend pricing CTA lost the vendor-issued pricing tracker")

print(
    "Omnisend approved_tracking state finalized with dedicated pricing tracker; "
    f"comparison_pages_monetized={comparison_changes} pricing_comparison_ctas={pricing_comparison_ctas}"
)
