import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED_AT = "2026-09-10T00:53:45+09:00"
GMAIL_MESSAGE_ID = "1a086e0111278d32"
EVIDENCE_FILE = "data/fathom-growth-partner-not-fit-2026-09-10.md"

TOOL_PATCH = {
    "affiliate_url": None,
    "affiliate_verified": True,
    "affiliate_status": "rejected",
    "affiliate_final_url": None,
    "affiliate_verified_at": CHECKED_AT,
    "affiliate_status_checked_at": CHECKED_AT,
    "affiliate_status_evidence_url": f"https://mail.google.com/mail/#all/{GMAIL_MESSAGE_ID}",
    "affiliate_next_action": "Do not reapply to the Fathom Growth Partner Program under the current COSHUMA publisher profile. Revisit only if Fathom changes eligibility or COSHUMA independently becomes an active Fathom user for a genuine operational reason. Do not purchase a plan solely to unlock partner eligibility.",
    "affiliate_evidence_markers": [
        "Human reply from Aby Perez at Fathom says the Growth Partner Program is for active Fathom users such as agencies, consultants, and RevOps practitioners using Fathom with clients.",
        "Fathom explicitly states content and affiliate publishers without an active Fathom account are not a fit at this time.",
        f"Gmail message {GMAIL_MESSAGE_ID} / {EVIDENCE_FILE}",
        "No customer-facing tracking URL was issued. Do not infer clicks, signups, commission, or revenue.",
    ],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reconcile_tools(path: Path):
    tools = load_json(path)
    target = next((item for item in tools if item.get("id") == "fathom"), None)
    if target is None:
        raise RuntimeError(f"Fathom tool record missing in {path}")
    target.update(TOOL_PATCH)
    write_json(path, tools)


def reconcile_outreach(path: Path):
    state = load_json(path)
    programs = state.setdefault("programs", {})
    fathom = programs.setdefault("fathom", {})
    fathom.update({
        "status": "rejected",
        "tracking_url": None,
        "account": "support@coshuma.com",
        "gmail_message_id": GMAIL_MESSAGE_ID,
        "evidence_file": EVIDENCE_FILE,
        "checked_at": CHECKED_AT,
        "note": "Fathom human support confirmed COSHUMA's current content/affiliate publisher profile is not eligible for the Growth Partner Program without being an active Fathom user. Do not reapply or create a paid subscription solely for eligibility.",
    })
    state["updated_at"] = "2026-09-10"
    write_json(path, state)


def reconcile_queue(path: Path):
    queue = load_json(path)
    target = next((item for item in queue if item.get("id") == "fathom-affiliate-batch-20260908-0650"), None)
    if target is None:
        raise RuntimeError("Fathom browser queue record missing")
    target.update({
        "status": "resolved",
        "affiliate_status": "rejected",
        "exact_tracking_url": None,
        "verified_at": CHECKED_AT,
        "reason": "Fathom human support replied that the Growth Partner Program is for active Fathom users working with clients and that content/affiliate publishers without an active Fathom account are not a fit at this time.",
        "next_action": "None under the current COSHUMA profile. Do not reapply. Revisit only if vendor eligibility changes or COSHUMA independently becomes an active Fathom user for a genuine operational reason.",
        "source_evidence": f"Gmail message {GMAIL_MESSAGE_ID}; {EVIDENCE_FILE}",
        "user_action_required": False,
    })
    do_not = target.setdefault("do_not", [])
    for rule in [
        "Do not submit another Fathom Growth Partner application under the current COSHUMA profile.",
        "Do not buy a Fathom subscription solely to unlock partner eligibility.",
        "Do not treat the Fathom homepage, partner page, dashboard, or signup URL as an affiliate/revenue link.",
        "Do not infer clicks, signups, commission, or revenue from this eligibility decision.",
    ]:
        if rule not in do_not:
            do_not.append(rule)
    write_json(path, queue)


def verify():
    tools = load_json(ROOT / "data/tools.json")
    fathom = next(item for item in tools if item.get("id") == "fathom")
    if fathom.get("affiliate_status") != "rejected" or fathom.get("affiliate_url") is not None:
        raise RuntimeError("Fathom rejected state did not reconcile")
    outreach = load_json(ROOT / "data/affiliate_outreach_state.json")
    if outreach.get("programs", {}).get("fathom", {}).get("status") != "rejected":
        raise RuntimeError("Fathom outreach state did not reconcile")
    queue = load_json(ROOT / "data/browser_required_queue.json")
    q = next(item for item in queue if item.get("id") == "fathom-affiliate-batch-20260908-0650")
    if q.get("affiliate_status") != "rejected" or q.get("status") != "resolved":
        raise RuntimeError("Fathom queue state did not reconcile")


if __name__ == "__main__":
    reconcile_tools(ROOT / "data/tools.json")
    reconcile_tools(ROOT / "data/tools.next.json")
    reconcile_outreach(ROOT / "data/affiliate_outreach_state.json")
    reconcile_queue(ROOT / "data/browser_required_queue.json")
    verify()
    print("Fathom partner eligibility reconciled: rejected/current profile not eligible")
