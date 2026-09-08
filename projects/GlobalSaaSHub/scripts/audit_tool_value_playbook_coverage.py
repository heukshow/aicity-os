from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "data" / "tools.json"
DATA_DIR = ROOT / "data"
OUT = ROOT / "public" / "ops" / "tool-value-playbook-audit.json"

# A useful tool analysis does not require another tool recommendation.
# Requiring pairs would encourage forced or speculative stacks.
REQUIRED_SECTIONS = ("problems", "monetization")


def valid_url(value: object) -> bool:
    return isinstance(value, str) and value.startswith(("https://", "http://"))


def load_playbooks() -> dict:
    merged: dict = {}
    files = sorted(DATA_DIR.glob("tool_value_playbooks*.json"))
    if not files:
        raise SystemExit("No tool value playbook data files found")
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SystemExit(f"Playbook file must contain an object: {path.name}")
        overlap = sorted(set(merged).intersection(payload))
        if overlap:
            raise SystemExit(f"Duplicate tool value playbook ids in {path.name}: {', '.join(overlap)}")
        merged.update(payload)
    return merged


def recommendation_issues(tool_id: str, entry: dict) -> list[str]:
    issues: list[str] = []
    pairs = entry.get("pairs")
    if pairs is None:
        return issues
    if not isinstance(pairs, list):
        return ["pairs_must_be_a_list_when_present"]
    for index, item in enumerate(pairs):
        if not isinstance(item, dict):
            issues.append(f"pairs[{index}]_must_be_an_object")
            continue
        target = item.get("id")
        why = item.get("why")
        if not isinstance(target, str) or not target.strip():
            issues.append(f"pairs[{index}]_missing_tool_id")
        if target == tool_id:
            issues.append(f"pairs[{index}]_self_recommendation")
        if not isinstance(why, str) or len(why.strip()) < 20:
            issues.append(f"pairs[{index}]_missing_specific_workflow_reason")
    return issues


def main() -> None:
    tools = json.loads(TOOLS.read_text(encoding="utf-8"))
    playbooks = load_playbooks()

    approved = []
    missing = []
    incomplete = []
    recommendation_review = []

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
                "recommendations_optional": True,
            })
            continue

        empty = [section for section in REQUIRED_SECTIONS if not entry.get(section)]
        if empty:
            incomplete.append({
                "id": tool_id,
                "name": tool.get("name"),
                "missing_sections": empty,
            })

        issues = recommendation_issues(tool_id, entry)
        if issues:
            recommendation_review.append({
                "id": tool_id,
                "name": tool.get("name"),
                "issues": issues,
            })

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "Every verified approved customer tracking tool should receive COSHUMA analysis for problems solved and realistic monetization/service ideas. Tool-pair or stack recommendations are optional and must never be invented merely to fill a section.",
        "recommendation_policy": {
            "pairs_are_optional": True,
            "show_only_when": [
                "the second tool performs a distinct complementary workflow role with a clear hand-off or efficiency benefit",
                "or a similar tool is materially better for a specific buyer condition and is presented as an alternative rather than a forced stack",
            ],
            "do_not_claim": [
                "integration or compatibility unless verified",
                "measurable efficiency, revenue or ROI improvement without evidence",
                "that two tools should be used together merely because both have affiliate links",
            ],
            "when_evidence_is_weak": "publish no tool recommendation",
        },
        "approved_tracking_count": len(approved),
        "playbook_count": len(playbooks),
        "approved_with_playbook_count": len([tool_id for tool_id in approved if tool_id in playbooks]),
        "missing_playbook_count": len(missing),
        "incomplete_playbook_count": len(incomplete),
        "recommendation_review_count": len(recommendation_review),
        "missing_playbooks": missing,
        "incomplete_playbooks": incomplete,
        "recommendation_review": recommendation_review,
        "completion_rule": {
            "affiliate_work_complete_only_when": [
                "approved customer-facing tracking URL verified",
                "problems it solves analyzed",
                "ways to make money / sellable deliverables analyzed without income guarantees",
                "public buyer guide updated where a safe target page exists",
            ],
            "tool_recommendation_is_not_required_for_completion": True,
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Value playbook audit: {len(approved)} approved, "
        f"{len(missing)} missing, {len(incomplete)} incomplete, "
        f"{len(recommendation_review)} recommendation reviews"
    )


if __name__ == "__main__":
    main()
