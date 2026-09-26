#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data" / "operations_registry.json"
ISSUE_NUMBER = 292
CUTOVER = datetime(2026, 9, 24, 9, 45, 0, tzinfo=timezone.utc)
HANDOFF_MARKERS = (
    "RELEASE HANDOFF",
    "AFFILIATE_RELEASE_HANDOFF",
    "HANDOFF — Release & Reliability Team",
    "HANDOFF - Release & Reliability Team",
)


def github_api(method, path, token, payload=None):
    repo = os.environ.get("GITHUB_REPOSITORY", "heukshow/aicity-os")
    url = f"https://api.github.com/repos/{repo}{path}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "COSHUMA-Control-Plane-Handoff-Audit/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None


def all_comments(token):
    rows = []
    page = 1
    while True:
        chunk = github_api("GET", f"/issues/{ISSUE_NUMBER}/comments?per_page=100&page={page}", token)
        if not chunk:
            break
        rows.extend(chunk)
        page += 1
    return rows


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def field(body, name):
    m = re.search(rf"(?mi)^\s*(?:-\s*)?{re.escape(name)}\s*:\s*`?([^`\n]+)`?\s*$", body)
    return m.group(1).strip() if m else None


def main():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    records = registry.get("active_queue", [])
    token = os.environ.get("GITHUB_TOKEN", "")
    comments = all_comments(token)

    known = set()
    for row in records:
        evidence = row.get("evidence", {})
        known.add((row.get("task_key"), evidence.get("merge_commit")))

    drift = []
    for row in comments:
        created = parse_time(row.get("created_at", "1970-01-01T00:00:00Z"))
        if created < CUTOVER:
            continue
        body = row.get("body", "")
        if not any(marker in body for marker in HANDOFF_MARKERS):
            continue
        task_key = field(body, "task_key") or field(body, "source_task")
        merge = field(body, "merge_commit") or field(body, "merged_fix")
        if merge and "/" in merge:
            merge = merge.split("/")[-1].strip()
        if not task_key:
            continue
        if (task_key, merge) in known or (not merge and any(task == task_key for task, _ in known)):
            continue
        drift.append((row, task_key, merge))

    if not drift:
        print(f"release-handoff-registry audit PASS comments={len(comments)}")
        return 0

    row, task_key, merge = drift[0]
    marker = f"handoff_comment_id: `{row['id']}`"
    already = any(marker in c.get("body", "") and "CONTROL_PLANE_DRIFT" in c.get("body", "") for c in comments)
    if token and not already:
        body = "\n".join([
            "### CONTROL_PLANE_DRIFT — release handoff missing from registry",
            f"- task_key: `{task_key}`",
            f"- merge_commit: `{merge}`",
            f"- handoff_comment_id: `{row['id']}`",
            "- impact: deterministic Release verifier cannot consume this valid handoff because the canonical operations registry has no matching record.",
            "- next_owner: Operations Governance Team — synchronize the handoff into operations_registry.json and release_verification_specs.json before retrying Release verification.",
            "- rule: issue #292 remains evidence/audit only; this comment does not create or advance lifecycle state.",
        ])
        github_api("POST", f"/issues/{ISSUE_NUMBER}/comments", token, {"body": body})

    print(f"release-handoff-registry audit FAIL task={task_key} merge={merge} comment={row['id']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
