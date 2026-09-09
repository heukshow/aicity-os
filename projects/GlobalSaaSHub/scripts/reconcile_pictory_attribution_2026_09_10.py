from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHECKED_AT = "2026-09-09T18:53:59+09:00"
TRACKING_URL = "https://pictory.ai?fpr=sangkwon-an23"
ATTRIBUTION_EVIDENCE = "data/pictory-attribution-verification-2026-09-09.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reconcile_tools() -> None:
    markers = [
        "Gmail message 1a080260af602adb from Pictory Affiliate Manager Ashutosh Dhamija confirms full affiliate-dashboard access was restored while payout setup remains pending.",
        "COSHUMA GA4 recorded the 2026-09-06 outbound affiliate_click from /tool/pictory.html to the verified Pictory referral destination.",
        "Gmail message 1a08596f9b30d2a4 from Pictory Affiliate Manager Ashutosh Dhamija explicitly confirms that the same click was recorded on Pictory's side.",
        "End-to-end click attribution is therefore verified for that event. This does not prove a signup, sale, commission, payout, or revenue.",
        ATTRIBUTION_EVIDENCE,
    ]

    for filename in ("tools.json", "tools.next.json"):
        path = DATA / filename
        tools = load_json(path)
        tool = next((item for item in tools if item.get("id") == "pictory"), None)
        if not tool:
            raise RuntimeError(f"pictory missing from {filename}")

        existing_url = tool.get("affiliate_url")
        if existing_url and existing_url.rstrip("/") != TRACKING_URL.rstrip("/"):
            raise RuntimeError(f"Unexpected Pictory affiliate URL in {filename}: {existing_url}")

        tool.update(
            {
                "affiliate_url": TRACKING_URL,
                "affiliate_final_url": TRACKING_URL,
                "affiliate_verified": True,
                "affiliate_status": "approved_tracking",
                "affiliate_verified_at": CHECKED_AT,
                "affiliate_status_checked_at": CHECKED_AT,
                "affiliate_tracking_url_verified": True,
                "affiliate_tracking_attribution_currently_verified": True,
                "affiliate_tracking_attribution_verified_at": CHECKED_AT,
                "affiliate_dashboard_status": "access_restored_payout_setup_pending",
                "payout_status": "setup_pending",
                "affiliate_next_action": (
                    "Keep the exact verified Pictory referral URL as the primary tracking route and display COSHUMA20 alongside it. "
                    "End-to-end click attribution is verified. Do not reapply or reopen the stale OTP task. "
                    "Do not infer signup, sale, commission, payout, or revenue until direct evidence exists."
                ),
                "affiliate_evidence_markers": markers,
            }
        )
        write_json(path, tools)


def reconcile_outreach() -> None:
    path = DATA / "affiliate_outreach_state.json"
    if not path.exists():
        return
    state = load_json(path)
    programs = state.get("programs", {}) if isinstance(state, dict) else {}
    program = programs.get("pictory") if isinstance(programs, dict) else None
    if isinstance(program, dict):
        program.update(
            {
                "status": "approved_tracking",
                "tracking_url": TRACKING_URL,
                "updated_at": CHECKED_AT,
                "payout_status": "setup_pending",
                "tracking_attribution_currently_verified": True,
                "tracking_attribution_verified_at": CHECKED_AT,
                "current_dashboard_status": "access_restored_payout_setup_pending",
                "note": (
                    "Pictory manager confirmed the Sep 6 COSHUMA referral click is recorded on Pictory's side, matching GA4. "
                    "End-to-end click attribution is verified; no signup, sale, commission, payout, or revenue is inferred."
                ),
            }
        )
        write_json(path, state)


def reconcile_queue() -> None:
    path = DATA / "browser_required_queue.json"
    if not path.exists():
        return
    queue = load_json(path)
    if not isinstance(queue, list):
        raise RuntimeError("browser_required_queue.json must be a JSON array")

    changed = False
    for item in queue:
        identity = " ".join(str(item.get(k, "")) for k in ("id", "tool_id", "name", "program", "task")).lower()
        if "pictory" not in identity:
            continue
        status = str(item.get("status", "")).lower()
        reason = str(item.get("reason", "")).lower()
        next_action = str(item.get("next_action", "")).lower()
        if "otp" in status or "otp" in reason or "otp" in next_action:
            item.update(
                {
                    "status": "resolved",
                    "affiliate_status": "approved_tracking",
                    "tracking_url": TRACKING_URL,
                    "resolved_at": CHECKED_AT,
                    "resolution": (
                        "Superseded by newer first-party evidence: Pictory restored dashboard access and later confirmed "
                        "the COSHUMA referral click was recorded partner-side. No OTP follow-up is currently required for attribution verification."
                    ),
                }
            )
            changed = True
    if changed:
        write_json(path, queue)


def main() -> None:
    evidence = DATA / "pictory-attribution-verification-2026-09-09.md"
    if not evidence.exists():
        raise RuntimeError(f"Missing Pictory attribution evidence file: {evidence}")
    text = evidence.read_text(encoding="utf-8")
    for marker in ("1a08596f9b30d2a4", "recorded on Pictory's side", "not** evidence of a signup"):
        if marker not in text:
            raise RuntimeError(f"Pictory attribution evidence missing required marker: {marker}")

    reconcile_tools()
    reconcile_outreach()
    reconcile_queue()
    print("Pictory end-to-end click attribution reconciled; stale OTP state cleared without inferring revenue")


if __name__ == "__main__":
    main()
