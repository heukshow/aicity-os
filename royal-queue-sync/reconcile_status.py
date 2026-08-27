#!/usr/bin/env python3
"""Reconcile royal-queue status snapshots from authoritative task JSON files.

This is a GitHub-side fallback for the local bridge/dashboard path. It does not
restart local workers or inspect secrets. It only reads queue JSON committed to
the royal-queue branch and rewrites status/latest.json + status/dashboard.json
with one winning semantic state per UUID.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STATE_DIRS = ("todo", "in_progress", "done", "failed", "waiting_human")
STATUS_DIR = ROOT / "status"
LATEST_PATH = STATUS_DIR / "latest.json"
DASHBOARD_PATH = STATUS_DIR / "dashboard.json"

SEMANTIC_MAP = {
    "todo": "todo",
    "queued": "todo",
    "pending": "todo",
    "in_progress": "in_progress",
    "tracking": "in_progress",
    "waiting_reply": "in_progress",
    "pending_review": "in_progress",
    "escalated": "in_progress",
    "waiting_human": "waiting_human",
    "human_required": "waiting_human",
    "done": "done",
    "completed": "done",
    "approved": "done",
    "approved_active": "done",
    "accepted_active": "done",
    "live_verified": "done",
    "submitted": "done",
    "submitted_pending_review": "done",
    "failed": "failed",
    "rejected": "failed",
    "blocked": "failed",
    "superseded": "superseded",
    "cancelled": "superseded",
    "canceled": "superseded",
}

# Only used when timestamps are equal or absent. A terminal result wins a stale
# duplicate with the same freshness; a genuinely newer human blocker still wins.
TIE_PRECEDENCE = {
    "failed": 50,
    "done": 40,
    "in_progress": 30,
    "waiting_human": 20,
    "todo": 10,
    "superseded": 0,
}


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def find_times(obj: Any, key_hint: str = "") -> list[datetime]:
    times: list[datetime] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            lower = str(key).lower()
            if isinstance(value, str) and any(
                token in lower
                for token in (
                    "updated_at",
                    "completed_at",
                    "checked_at",
                    "submitted_at",
                    "verified_at",
                    "created_at",
                    "timestamp",
                    "time",
                    "date",
                )
            ):
                parsed = parse_time(value)
                if parsed:
                    times.append(parsed)
            elif isinstance(value, (dict, list)):
                times.extend(find_times(value, lower))
    elif isinstance(obj, list):
        for value in obj:
            if isinstance(value, (dict, list)):
                times.extend(find_times(value, key_hint))
    return times


def semantic_status(data: dict[str, Any], folder: str) -> str:
    candidates: list[Any] = [data.get("status")]
    result = data.get("result")
    if isinstance(result, dict):
        candidates.extend(
            [
                result.get("status"),
                result.get("application_status"),
                result.get("state"),
            ]
        )
    payload = data.get("payload")
    if isinstance(payload, dict):
        # Payload status is lower-confidence than top-level/result status.
        candidates.append(payload.get("status"))

    for value in candidates:
        if not isinstance(value, str):
            continue
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in SEMANTIC_MAP:
            return SEMANTIC_MAP[normalized]
        if "reject" in normalized or "declin" in normalized:
            return "failed"
        if "approv" in normalized or "accept" in normalized:
            return "done"
        if "supersed" in normalized:
            return "superseded"
        if "waiting" in normalized and "human" in normalized:
            return "waiting_human"
        if "waiting" in normalized and ("reply" in normalized or "review" in normalized):
            return "in_progress"

    return folder if folder in STATE_DIRS else "todo"


def actor_for(data: dict[str, Any]) -> str:
    actor = data.get("actor") or data.get("assigned_to") or "unknown"
    return str(actor).strip().lower() or "unknown"


def task_title(data: dict[str, Any]) -> str | None:
    value = data.get("title")
    return str(value) if value is not None else None


def record_key(record: dict[str, Any]) -> tuple[float, int]:
    return (record["freshness"].timestamp(), TIE_PRECEDENCE.get(record["status"], -1))


def load_records() -> dict[str, list[dict[str, Any]]]:
    by_id: dict[str, list[dict[str, Any]]] = {}
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    for folder in STATE_DIRS:
        directory = ROOT / folder
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"warning: skip unreadable {path}: {exc}")
                continue
            if not isinstance(data, dict):
                continue
            task_id = str(data.get("id") or path.stem)
            times = find_times(data)
            freshness = max(times) if times else epoch
            record = {
                "id": task_id,
                "actor": actor_for(data),
                "status": semantic_status(data, folder),
                "title": task_title(data),
                "freshness": freshness,
                "source_folder": folder,
                "source_path": str(path.relative_to(ROOT)),
            }
            by_id.setdefault(task_id, []).append(record)
    return by_id


def reconcile() -> list[dict[str, Any]]:
    winners: list[dict[str, Any]] = []
    for task_id, records in load_records().items():
        winner = max(records, key=record_key)
        if winner["status"] == "superseded":
            continue
        winners.append(winner)
    winners.sort(key=record_key, reverse=True)
    return winners


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load_existing(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def build_latest(winners: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    latest = []
    for rec in winners[:100]:
        latest.append(
            {
                "id": rec["id"],
                "actor": rec["actor"],
                "status": rec["status"],
                "updated_at": iso(rec["freshness"]),
            }
        )
    return {"generated_at": now.isoformat(), "latest": latest}


def actor_display(actor: str) -> str:
    return {
        "prince": "Prince",
        "work": "Work",
        "codex": "Work",
        "butler": "Butler",
        "princess": "Princess",
    }.get(actor, actor.title() if actor else "Unknown")


def build_dashboard(winners: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    old = load_existing(DASHBOARD_PATH)
    counts = {state: 0 for state in STATE_DIRS}
    for rec in winners:
        if rec["status"] in counts:
            counts[rec["status"]] += 1

    # Preserve known actor metadata fields, but derive active state from the
    # reconciled queue instead of stale duplicate snapshots.
    old_actors = old.get("actors") if isinstance(old.get("actors"), list) else []
    actor_map: dict[str, dict[str, Any]] = {}
    for item in old_actors:
        if isinstance(item, dict) and item.get("name"):
            actor_map[str(item["name"])] = dict(item)
    for name in ("Prince", "Work", "Butler", "Princess"):
        actor_map.setdefault(name, {"name": name})
        actor_map[name].update({"status": "idle", "task": None, "uuid": None})

    active = [r for r in winners if r["status"] in ("in_progress", "waiting_human")]
    for rec in sorted(active, key=record_key):
        name = actor_display(rec["actor"])
        actor_map.setdefault(name, {"name": name})
        actor_map[name].update(
            {
                "status": rec["status"],
                "last_activity": iso(rec["freshness"]),
                "task": rec["title"],
                "uuid": rec["id"],
            }
        )

    # A GitHub-side reconciler cannot inspect local PIDs. Preserve heartbeat
    # history only as evidence and explicitly mark it stale when old, so an old
    # snapshot can never masquerade as current health.
    processes = []
    old_processes = old.get("processes") if isinstance(old.get("processes"), list) else []
    for proc in old_processes:
        if not isinstance(proc, dict):
            continue
        item = dict(proc)
        heartbeat = parse_time(item.get("heartbeat"))
        if heartbeat:
            age = max(0, int((now - heartbeat).total_seconds()))
            item["heartbeat_age_seconds"] = age
            if age > 300:
                item["alive"] = False
                item["health"] = "stale_remote_observation"
                item["pid"] = None
        else:
            item["alive"] = False
            item["health"] = "unknown_remote_observation"
            item["pid"] = None
        processes.append(item)

    return {
        "generated_at": now.isoformat(),
        "actors": list(actor_map.values()),
        "counts": counts,
        "tracking": old.get("tracking", []),
        "processes": processes,
        "reconciliation": {
            "source": "github_fallback",
            "unique_uuid_count": len(winners),
            "note": "Counts and latest states are deduplicated from committed queue JSON. Local process liveness is not inferred from stale heartbeats.",
        },
    }


def main() -> None:
    now = datetime.now(timezone.utc)
    winners = reconcile()
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_PATH.write_text(
        json.dumps(build_latest(winners, now), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    DASHBOARD_PATH.write_text(
        json.dumps(build_dashboard(winners, now), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"reconciled {len(winners)} unique UUIDs")


if __name__ == "__main__":
    main()
