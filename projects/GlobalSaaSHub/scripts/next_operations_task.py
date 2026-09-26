#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data" / "operations_registry.json").read_text(encoding="utf-8"))
rank = {"critical": 0, "high": 1, "normal": 2, "low": 3}
terminal = {"production_verified", "measured", "rejected_with_evidence"}
active_items = [x for x in data.get("active_queue", []) if x.get("lifecycle") not in terminal]
unblocked_items = [x for x in active_items if not x.get("blocker")]
items = unblocked_items or active_items
items.sort(key=lambda x: (rank.get(x.get("priority"), 99), x.get("last_evidence_at", ""), x.get("record_id", "")))
if not items:
    print("NO_ACTIVE_TASK")
else:
    x = items[0]
    print(json.dumps({
        "record_id": x["record_id"],
        "task_key": x["task_key"],
        "incident_key": x.get("incident_key"),
        "owner_team": x["owner_team"],
        "lifecycle": x["lifecycle"],
        "next_owner": x["next_owner"],
        "blocker": x.get("blocker"),
        "target": x["target"]
    }, ensure_ascii=False))
