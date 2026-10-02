from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "browser_required_queue.json"
TASK_ID = "manychat-partnerstack-direct-application-20260910"

TASK = {
    "id": TASK_ID,
    "priority": "high",
    "status": "blocked",
    "type": "user_action_required",
    "cost": "0",
    "verified_at": "2026-10-03T07:14:26+09:00",
    "gmail_thread_id": "1a07b34ffaf04027",
    "gmail_message_id": "1a086b6eabaeb524",
    "reason": (
        "The full Manychat PartnerStack support thread and the authenticated direct application form were "
        "reviewed. PartnerStack support agent Digna Rivas supplied the exact form, and the live form requires "
        "unchecked legal acknowledgments covering the Manychat Partner Program Terms, fraud/compliance "
        "verification, commission forfeiture for violations, and paid-search policy. No application was "
        "submitted, and no approval or tracking URL is inferred."
    ),
    "url": "https://dash.partnerstack.com/application?company=manychat&gref=page",
    "next_action": (
        "Wait for the user to review and accept the Manychat Partner Program legal acknowledgments in the "
        "existing PartnerStack application. After that explicit legal consent, continue the same task, verify "
        "there is no duplicate application state, submit once, and record only the actual resulting state."
    ),
    "do_not": [
        "Do not treat the PartnerStack application URL as a customer-facing affiliate, referral, or revenue link.",
        "Do not create another PartnerStack account.",
        "Do not submit a duplicate application if the authenticated dashboard shows submitted, pending, approved, declined, closed, or cooldown status.",
        "Do not guess or construct a Manychat tracking/referral URL before one is actually issued and verified.",
        "Do not complete CAPTCHA, OTP, legal acceptance, identity verification, or any paid step on the user's behalf."
    ],
    "source_evidence": (
        "Gmail thread 1a07b34ffaf04027 / reply 1a086b6eabaeb524 from Digna Rivas "
        "(PartnerStack Support), plus authenticated live readback of the exact PartnerStack application "
        "form at 2026-10-03T07:14:26+09:00."
    ),
}

TERMINAL_OR_PROTECTED = {
    "resolved",
    "approved_tracking",
    "application_submitted",
    "pending",
    "declined",
    "rejected",
    "closed",
    "cooldown",
    "blocked",
}


def main() -> None:
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    if not isinstance(queue, list):
        raise RuntimeError("browser_required_queue.json must remain a JSON array")

    for index, item in enumerate(queue):
        if item.get("id") != TASK_ID:
            continue
        status = str(item.get("status", "")).strip().lower()
        if status in TERMINAL_OR_PROTECTED:
            print(f"Manychat queue task already protected by newer state: {status}; leaving unchanged")
            break
        queue[index] = {**item, **TASK}
        break
    else:
        queue.append(TASK)

    QUEUE_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Manychat direct PartnerStack application blocked on legal consent; no application submitted")

    # Keep the build-time mailbox reconciliation chain current without requiring
    # a duplicate application or a new browser handoff. This helper only records
    # the human Fathom eligibility decision and never submits or purchases anything.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "reconcile_fathom_not_fit_2026_09_10.py")],
        check=True,
    )


if __name__ == "__main__":
    main()
