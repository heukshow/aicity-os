#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "operations_registry.json"
ALLOWED = [
    "discovered","evidence_validated","assigned_to_team","in_progress",
    "implemented_and_merged","production_verification_requested",
    "production_verified","measured","rejected_with_evidence","completed_with_evidence"
]
PRIORITIES = {"critical", "high", "normal", "low"}

def fail(msg):
    raise SystemExit(f"operations-registry: FAIL: {msg}")

data = json.loads(REGISTRY.read_text(encoding="utf-8"))
if data.get("schema_version") != 1:
    fail("schema_version must be 1")
queue = data.get("active_queue")
if not isinstance(queue, list):
    fail("active_queue must be a list")

seen_ids = set()
seen_task_targets = set()
for i, item in enumerate(queue):
    where = f"active_queue[{i}]"
    for field in ("record_id","task_key","target","owner_team","lifecycle","next_owner","priority","evidence","completion_gate","user_action_required"):
        if field not in item:
            fail(f"{where} missing {field}")
    if item["record_id"] in seen_ids:
        fail(f"duplicate record_id {item['record_id']}")
    seen_ids.add(item["record_id"])
    key = (item["task_key"], item["target"])
    if key in seen_task_targets:
        fail(f"duplicate active task/target {key}")
    seen_task_targets.add(key)
    if item["lifecycle"] not in ALLOWED:
        fail(f"{where} invalid lifecycle {item['lifecycle']}")
    if item["priority"] not in PRIORITIES:
        fail(f"{where} invalid priority {item['priority']}")
    if not item["owner_team"].strip() or not item["next_owner"].strip():
        fail(f"{where} owner/next_owner must be non-empty")
    if not isinstance(item["evidence"], dict):
        fail(f"{where} evidence must be an object")
    pv = item["evidence"].get("production_verification_comment_id")
    structured_pv = (
        item.get("completion_gate_satisfied") is True
        and isinstance(item["evidence"].get("site_deploy_run"), int)
        and isinstance(item["evidence"].get("github_pages_run"), int)
        and isinstance(item["evidence"].get("deployment_source_commit"), str)
        and len(item["evidence"]["deployment_source_commit"]) == 40
        and isinstance(item["evidence"].get("gh_pages_commit"), str)
        and len(item["evidence"]["gh_pages_commit"]) == 40
        and isinstance(item["evidence"].get("live_url"), str)
        and item["evidence"]["live_url"].startswith("https://")
        and isinstance(item["evidence"].get("live_verification"), str)
        and bool(item["evidence"]["live_verification"].strip())
    )
    if item["lifecycle"] == "completed_with_evidence":
        proof = item["evidence"]
        if (item["completion_gate"] != "formal_application_submission_evidence_or_rejected_with_evidence"
                or proof.get("application_state") != "submitted"
                or not proof.get("submission_confirmation")
                or not proof.get("submission_evidence_comment_id")
                or not proof.get("form_url", "").startswith("https://")
                or item.get("completion_gate_satisfied") is not True):
            fail(f"{where} completed_with_evidence requires explicit formal-submission proof; never substitutes for production")
    if item["lifecycle"] in ("production_verified","measured") and not (pv or structured_pv):
        fail(f"{where} {item['lifecycle']} requires a verification comment or structured deployment/live evidence")
    if item["lifecycle"] == "measured" and item["completion_gate"] == "production_verified" and not (pv or structured_pv):
        fail(f"{where} measured before production verification")
    if item["user_action_required"] is True and item.get("blocker") not in {
        "captcha","otp","legal_consent","payment","forced_identity_verification"
    }:
        fail(f"{where} user_action_required is only valid for approved user gates")

print(f"operations-registry: PASS records={len(queue)}")
