#!/usr/bin/env python3
"""Governance-only, evidence-driven CAS update of the current registry.

No release verifier write permission is needed. Only existing registry records
are advanced; unregistered handoffs remain an explicit audit failure.
"""
import argparse
import base64
import copy
import json
import os
from datetime import datetime, timezone
from audit_release_handoff_registry import all_comments, field, github_api

PATH = "projects/GlobalSaaSHub/data/operations_registry.json"
EARLY = {"discovered", "evidence_validated", "assigned_to_team", "in_progress", "implemented_and_merged"}


def reconcile(registry, comments, get_pr, get_run, has_spec):
    updated = copy.deepcopy(registry)
    changed = []
    for row in updated.get("active_queue", []):
        if row.get("completion_gate") != "production_verified" or row.get("lifecycle") in {
            "production_verified", "measured", "rejected_with_evidence"}:
            continue
        ev = row.get("evidence", {})
        if not ev.get("implementation_pr"):
            continue
        pr = get_pr(ev["implementation_pr"])
        if not pr.get("merged") or not pr.get("merge_commit_sha"):
            continue
        merge = pr["merge_commit_sha"]
        if ev.get("merge_commit") and ev["merge_commit"] != merge:
            continue  # conflicting evidence requires an explicit reviewed correction
        old = copy.deepcopy(row)
        ev["merge_commit"] = merge
        row["evidence"] = ev
        if row["lifecycle"] in EARLY:
            row["lifecycle"] = "production_verification_requested"
            row["next_owner"] = "Release & Reliability Team"
            row["completion_gate_satisfied"] = False
            row["blocker"] = None if has_spec(row["record_id"]) else "missing_deterministic_verification_spec"
        for comment in sorted(comments, key=lambda c: c.get("created_at", ""), reverse=True):
            body = comment.get("body", "")
            if (comment.get("user", {}).get("login") != "github-actions[bot]" or
                "RELEASE_VERIFICATION" not in body or
                field(body, "record_id") != row["record_id"] or
                field(body, "merge") != merge or field(body, "result") != "production_verified"):
                continue
            run_id = field(body, "verification_run")
            if not run_id or not run_id.isdigit():
                continue
            run = get_run(run_id)
            if (run.get("name") != "COSHUMA Release Verification" or run.get("head_branch") != "main"
                or run.get("status") != "completed"):
                continue
            # A batch can fail for another task. The exact trusted result for this
            # merge is authoritative; a failed comment is never terminal.
            ev["production_verification_comment_id"] = comment["id"]
            ev["deterministic_verification_run"] = int(run_id)
            row.update(lifecycle="production_verified", next_owner="Operations Governance Team",
                       blocker=None, completion_gate_satisfied=True, completed_at=comment["created_at"],
                       last_evidence_at=comment["created_at"],
                       verification=(f"Deterministic production verification succeeded in run {run_id}; "
                                     f"trusted evidence comment {comment['id']}."))
            break
        if old != row:
            changed.append(row["record_id"])
    if changed:
        updated["updated_at"] = datetime.now(timezone.utc).isoformat()
    return updated, changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    token = os.environ["GITHUB_TOKEN"]
    current = github_api("GET", f"/contents/{PATH}?ref=main", token)
    registry = json.loads(base64.b64decode(current["content"]))
    spec_file = github_api("GET", "/contents/projects/GlobalSaaSHub/data/release_verification_specs.json?ref=main", token)
    specs = json.loads(base64.b64decode(spec_file["content"]))["records"]
    updated, changed = reconcile(registry, all_comments(token),
        lambda n: github_api("GET", f"/pulls/{n}", token),
        lambda n: github_api("GET", f"/actions/runs/{n}", token), lambda key: key in specs)
    print(json.dumps({"changed_records": changed, "mode": "write" if args.write else "check"}))
    if changed and args.write:
        # Contents API SHA provides compare-and-swap: concurrent updates fail 409,
        # never overwrite newer state or force-push a stale local checkout.
        github_api("PUT", f"/contents/{PATH}", token, {
            "message": "ops: reconcile registry from verified release evidence [skip ci]",
            "branch": "main", "sha": current["sha"],
            "content": base64.b64encode((json.dumps(updated, ensure_ascii=False, indent=2) + "\n").encode()).decode(),
        })


if __name__ == "__main__":
    main()
