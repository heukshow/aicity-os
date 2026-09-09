from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
EVIDENCE_PATH = DATA_DIR / "claap-teachable-tracking-update-2026-09-09.json"

EXPECTED_DEFAULT = "https://partnerstack.teachable.com/ce4muoxdj46j"
EXPECTED_TRIAL = "https://partnerstack.teachable.com/COSHUMA"
EXPECTED_TRIAL_REPLY = "1a087337fdf3bdd1"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_evidence() -> dict:
    evidence = load_json(EVIDENCE_PATH)
    teachable = evidence.get("teachable") or {}
    if teachable.get("status") != "approved_tracking":
        raise RuntimeError("Teachable evidence is not approved_tracking")
    if teachable.get("tracking_url") != EXPECTED_DEFAULT:
        raise RuntimeError("Teachable default tracking URL does not match vendor evidence")
    if teachable.get("tracked_extended_trial_url") != EXPECTED_TRIAL:
        raise RuntimeError("Teachable 30-day trial URL does not match vendor evidence")
    if teachable.get("extended_trial_reply_gmail_message_id") != EXPECTED_TRIAL_REPLY:
        raise RuntimeError("Teachable 30-day trial vendor reply message is missing or changed")
    return teachable


def reconcile_tools(teachable_e: dict) -> None:
    stale_fragments = (
        "Await the vendor-supplied tracked 30-day extended-trial URL",
        "extended-trial landing page still requires an exact tracked vendor-issued URL",
        "requested that exact trial URL",
    )
    for name in ("tools.json", "tools.next.json"):
        path = DATA_DIR / name
        tools = load_json(path)
        tool = next((item for item in tools if item.get("id") == "teachable"), None)
        if not tool:
            raise RuntimeError(f"Teachable missing from {name}")
        if tool.get("affiliate_url") != EXPECTED_DEFAULT or tool.get("affiliate_status") != "approved_tracking" or tool.get("affiliate_verified") is not True:
            raise RuntimeError(f"Teachable authoritative tracking state is not intact in {name}")

        markers = [
            marker
            for marker in (tool.get("affiliate_evidence_markers") or [])
            if not any(fragment.lower() in str(marker).lower() for fragment in stale_fragments)
        ]
        resolved_markers = [
            f"Teachable manager Camila Gouveia supplied COSHUMA's exact unique default PartnerStack URL in Gmail message {teachable_e['tracking_reply_gmail_message_id']}: {EXPECTED_DEFAULT}",
            f"Teachable manager Camila Gouveia separately supplied the exact COSHUMA 30-day Free Trial PartnerStack route in Gmail message {EXPECTED_TRIAL_REPLY}: {EXPECTED_TRIAL}",
            "Use the default route for general Teachable affiliate CTAs and the separately vendor-issued COSHUMA route only for the 30-day Free Trial offer. Do not use the unwrapped partner30 landing page, dashboard/login URLs, or guessed wrappers.",
            "Approval and link issuance do not prove a click, signup, commission, or revenue event.",
        ]
        for marker in resolved_markers:
            if marker not in markers:
                markers.append(marker)

        tool.update(
            {
                "affiliate_trial_tracking_url": EXPECTED_TRIAL,
                "affiliate_trial_tracking_url_verified": True,
                "affiliate_trial_tracking_url_verified_at": teachable_e["extended_trial_received_at_utc"],
                "affiliate_trial_tracking_status_evidence_url": f"gmail:{EXPECTED_TRIAL_REPLY}",
                "affiliate_next_action": "Use the verified default PartnerStack route for general Teachable CTAs and the separately vendor-confirmed COSHUMA route for 30-day Free Trial CTAs. Do not reapply, reopen link recovery, or guess tracking wrappers. Monitor real click/signup/commission evidence separately.",
                "affiliate_evidence_markers": markers,
            }
        )
        write_json(path, tools)


def reconcile_outreach(teachable_e: dict) -> None:
    path = DATA_DIR / "affiliate_outreach_state.json"
    state = load_json(path)
    programs = state.setdefault("programs", {})
    teachable = programs.setdefault("teachable", {})
    if teachable.get("status") != "approved_tracking" or teachable.get("tracking_url") != EXPECTED_DEFAULT:
        raise RuntimeError("Teachable outreach state lost its authoritative approved tracking route")
    teachable.update(
        {
            "status": "approved_tracking",
            "tracking_url": EXPECTED_DEFAULT,
            "trial_tracking_url": EXPECTED_TRIAL,
            "sender": "support@coshuma.com",
            "gmail_message_id": teachable_e["tracking_reply_gmail_message_id"],
            "trial_gmail_message_id": EXPECTED_TRIAL_REPLY,
            "updated_at": teachable_e["extended_trial_received_at_utc"],
            "note": "Resolved: Teachable manager supplied both COSHUMA's default unique PartnerStack tracking URL and the separate exact 30-day Free Trial PartnerStack route. Use only those vendor-issued routes for their intended CTA types; do not reapply or request the trial link again. Actual attribution and revenue remain unverified until observed.",
        }
    )
    write_json(path, state)


def validate() -> None:
    for name in ("tools.json", "tools.next.json"):
        tool = next(item for item in load_json(DATA_DIR / name) if item.get("id") == "teachable")
        if tool.get("affiliate_trial_tracking_url") != EXPECTED_TRIAL:
            raise RuntimeError(f"Teachable trial URL was not persisted in {name}")
        if "Await the vendor-supplied" in tool.get("affiliate_next_action", ""):
            raise RuntimeError(f"Stale Teachable trial pending instruction remains in {name}")
    outreach = load_json(DATA_DIR / "affiliate_outreach_state.json").get("programs", {}).get("teachable", {})
    if outreach.get("trial_tracking_url") != EXPECTED_TRIAL or "remains pending" in outreach.get("note", ""):
        raise RuntimeError("Stale Teachable trial pending outreach state remains")


def main() -> None:
    teachable_e = verify_evidence()
    reconcile_tools(teachable_e)
    reconcile_outreach(teachable_e)
    validate()
    print("Teachable 30-day trial state reconciled as resolved; duplicate link recovery is blocked.")


if __name__ == "__main__":
    main()
