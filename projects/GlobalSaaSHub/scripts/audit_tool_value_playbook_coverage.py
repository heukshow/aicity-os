from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "data" / "tools.json"
PLAYBOOKS = ROOT / "data" / "tool_value_playbooks.json"
OUT = ROOT / "public" / "ops" / "tool-value-playbook-audit.json"

REQUIRED_SECTIONS = ("problems", "monetization", "pairs")


def valid_url(value: object) -> bool:
    return isinstance(value, str) and value.startswith(("https://", "http://"))


def main() -> None:
    tools = json.loads(TOOLS.read_text(encoding="utf-8"))
    playbooks = json.loads(PLAYBOOKS.read_text(encoding="utf-8"))

    approved = []
    missing = []
    incomplete = []

    for tool in tools:
        if not (
            tool.get("affiliate_status") == "approved_tracking"
            and tool.get("affiliate_verified") is True
            and valid_url(tool.get("affiliate_url"))
        ):
            continue

        tool_id = tool.get("id")
        approved.append(tool_id)
        entry = playbooks.get(tool_id)
        if not entry:
            missing.append({
                "id": tool_id,
                "name": tool.get("name"),
                "reason": "approved_tracking_without_value_playbook",
                "required": list(REQUIRED_SECTIONS),
            })
            continue

        empty = [section for section in REQUIRED_SECTIONS if not entry.get(section)]
        if empty:
            incomplete.append({
                "id": tool_id,
                "name": tool.get("name"),
                "missing_sections": empty,
            })

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "Every verified approved customer tracking tool should receive COSHUMA analysis for problems solved, realistic monetization/service ideas, and complementary tool stacks. Missing analysis must not be mistaken for completed affiliate onboarding.",
        "approved_tracking_count": len(approved),
        "playbook_count": len(playbooks),
        "approved_with_playbook_count": len([tool_id for tool_id in approved if tool_id in playbooks]),
        "missing_playbook_count": len(missing),
        "incomplete_playbook_count": len(incomplete),
        "missing_playbooks": missing,
        "incomplete_playbooks": incomplete,
        "completion_rule": {
            "affiliate_work_complete_only_when": [
                "approved customer-facing tracking URL verified",
                "problems it solves analyzed",
                "ways to make money / sellable deliverables analyzed without income guarantees",
                "complementary tool stack analyzed",
                "public buyer guide updated where a safe target page exists",
            ]
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Value playbook audit: {len(approved)} approved, "
        f"{len(missing)} missing, {len(incomplete)} incomplete"
    )


if __name__ == "__main__":
    main()
