from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
TRACKING_URL = "https://your.omnisend.com/4aA5k9"
CHECKED_AT = "2026-09-09T17:50:34+09:00"
EVIDENCE = (
    "Omnisend Senior Affiliate Marketing Manager Deimantė Vaitkevičiūtė replied to "
    "support@coshuma.com in Gmail message 1a0855caf8f6dee2: 'Please use this link for tracking: "
    "https://your.omnisend.com/4aA5k9' and confirmed the tracking link is in Impact Assets. "
    "Omnisend's official affiliate documentation states approved affiliates must use the exact link from "
    "Impact Content > Assets; tracking/reporting are handled through Impact with a 60-day attribution window."
)
NEXT_ACTION = (
    "Preserve this exact Omnisend-issued customer tracking URL. Do not reapply and do not substitute the "
    "homepage, pricing page, Impact dashboard, onboarding URL, or email redirect. Track real clicks/signups/"
    "commissions separately; no revenue is inferred from approval or link issuance."
)

if not TRACKING_URL.startswith("https://your.omnisend.com/"):
    raise SystemExit("Refusing non-Omnisend tracking host")

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
# Convert Omnisend buyer CTAs produced by either the base page or the approval-aware patch.
text = re.sub(
    r'<a data-cta="official"(?P<attrs>[^>]*?)href="https://www\.omnisend\.com/(?:pricing/)?"(?P<tail>[^>]*)>',
    lambda m: '<a data-cta="affiliate"' + m.group('attrs') + f'href="{TRACKING_URL}"' +
              re.sub(r'rel="[^"]*"', 'rel="sponsored noopener noreferrer"', m.group('tail')) + '>',
    text,
)
# Base page has a simpler official link without tool metadata.
text = text.replace(
    '<a data-cta="official" href="https://www.omnisend.com/" target="_blank" rel="noopener noreferrer"',
    f'<a data-cta="affiliate" data-tool-id="omnisend" data-cta-source="omnisend_primary" href="{TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer"',
)
text = text.replace("Affiliate approved · exact tracking link pending verification", "Affiliate approved · tracking link verified")
text = text.replace(
    "The approval email did not contain an account-specific customer tracking URL, so Omnisend buttons intentionally remain ordinary official links until the exact Impact-issued URL is copied and verified.",
    "Omnisend's Senior Affiliate Marketing Manager supplied COSHUMA's exact customer tracking URL and confirmed it is the link in Impact Assets. Omnisend buttons now use that verified link; COSHUMA may earn a commission on an eligible purchase at no extra cost to you."
)
if TRACKING_URL not in text:
    raise SystemExit("Omnisend tracking URL was not installed in buyer page")
page.write_text(text, encoding="utf-8")
print("Omnisend approved_tracking state and buyer CTA finalized")
