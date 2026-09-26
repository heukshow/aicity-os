#!/usr/bin/env python3
"""Preserve evidence-backed lifecycle fields at every producer boundary.

Run legacy producers with this wrapper. Product facts are never restored/changed.
A backwards transition requires a newer explicit direct-evidence override.
"""
import copy
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ["tools.json", "tools.next.json", "affiliate_outreach_state.json", "browser_required_queue.json"]
EXTRA = {"status", "tracking_url", "exact_tracking_url", "application_state", "next_action",
         "do_not_reapply", "checked_at", "verified_at", "evidence", "blocker", "blockers",
         "user_action_required", "reason", "note"}


def protected(key):
    return key.startswith(("affiliate_", "application_")) or key in EXTRA


def rank(row):
    status = row.get("affiliate_status") or row.get("status") or ""
    application = row.get("application_state") or ""
    if status in {"rejected", "no_affiliate_program", "excluded_user_request", "program_inactive",
                  "program_closed_to_new_applicants", "program_unavailable_company_winding_down", "temporarily_closed"}:
        return 4
    if status.startswith("approved_tracking") or (not status and application == "enrolled_tracking_link_verified"):
        return 5
    if status.startswith("approved") or (not status and application == "approved"):
        return 3
    if status in {"application_submitted", "application_pending", "pending"} or (not status and application in {
        "submitted", "submitted_then_declined", "interest_form_submitted"}):
        return 2
    return 0


def timestamp(row):
    for key in ("affiliate_status_checked_at", "checked_at", "affiliate_verified_at", "verified_at"):
        try:
            return datetime.fromisoformat(row.get(key, "").replace("Z", "+00:00")).timestamp()
        except (ValueError, TypeError, AttributeError):
            pass
    return 0


def preserve(old, new):
    """Return merged row and whether an unproven regression was prevented."""
    if not old or rank(old) == 0:
        return new, False
    evidence = new.get("affiliate_lifecycle_override", {})
    direct_override = (isinstance(evidence, dict) and evidence.get("source_type") in {
        "vendor_email", "authenticated_vendor_dashboard"} and evidence.get("source_ref")
        and evidence.get("reason") and timestamp({"checked_at": evidence.get("observed_at")}) > timestamp(old))
    lower = rank(new) < rank(old)
    status_changed = (new.get("affiliate_status") or new.get("status")) != (old.get("affiliate_status") or old.get("status"))
    stale = timestamp(old) > timestamp(new) or (
        status_changed and rank(new) <= rank(old) and timestamp(new) <= timestamp(old))
    lost_url = rank(old) == 5 and any(old.get(k) and new.get(k) != old[k]
        for k in ("affiliate_url", "tracking_url", "exact_tracking_url"))
    # An unchanged status must not hide older timestamps or erase evidence.
    older_field = any(timestamp({"checked_at": old.get(k)}) > timestamp({"checked_at": new.get(k)})
        for k in ("affiliate_status_checked_at", "checked_at", "affiliate_verified_at", "verified_at")
        if old.get(k))
    lost_evidence = any(isinstance(value, list) and value and protected(k) and "evidence" in k
        and any(item not in new.get(k, []) for item in value)
        for k, value in old.items())
    # Rejections cannot be silently revived by a rank-only comparison.
    decision_changed = rank(old) == 4 and (new.get("affiliate_status") or new.get("status")) != (
        old.get("affiliate_status") or old.get("status"))
    if not direct_override and (lower or stale or lost_url or older_field or lost_evidence or decision_changed):
        result = {k: copy.deepcopy(v) for k, v in new.items() if not protected(k)}
        result.update({k: copy.deepcopy(v) for k, v in old.items() if protected(k)})
        return result, result != new
    return new, False


def rows(data, filename):
    if filename == "affiliate_outreach_state.json":
        return data.get("programs", {})
    return {str(row.get("id") or row.get("tool_id")): row for row in data}


def reconcile(before, after, filename):
    old_rows = rows(before, filename)
    new_rows = rows(after, filename)
    count = 0
    for key, old in old_rows.items():
        if key not in new_rows:
            if rank(old):
                if filename == "browser_required_queue.json":
                    # Keep a resolved/evidence-bearing queue row for audit when
                    # legacy cleanup tries to remove it, without blocking build.
                    after.append(copy.deepcopy(old))
                    count += 1
                    continue
                raise ValueError(f"{filename}: producer deleted progressed record {key}")
            continue
        new = new_rows[key]
        kept, changed = preserve(old, new)
        if changed:
            new.clear()
            new.update(kept)
            count += 1
    return after, count


def snapshot():
    return {name: json.loads((ROOT / "data" / name).read_text()) for name in FILES}


def sync_next():
    path = ROOT / "data/tools.next.json"
    canonical = json.loads((ROOT / "data/tools.json").read_text())
    candidate = json.loads(path.read_text())
    candidate, count = reconcile(canonical, candidate, "tools.next.json")
    if count:
        path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n")
    return count


def main():
    if sys.argv[1:2] == ["--merge"]:
        path = Path(sys.argv[2])
        candidate = json.load(sys.stdin)
        previous = json.loads(path.read_text()) if path.exists() else ([] if isinstance(candidate, list) else {})
        merged, _ = reconcile(previous, candidate, path.name)
        print(json.dumps(merged, ensure_ascii=False, indent=2))
        return 0
    if sys.argv[1:] == ["--sync-next"]:
        print(f"affiliate lifecycle: next-source reconciled records={sync_next()}")
        return 0
    if len(sys.argv) < 2:
        raise SystemExit("usage: affiliate_lifecycle_guard.py COMMAND [ARGS...]")
    before = snapshot()
    result = subprocess.run(sys.argv[1:], cwd=ROOT)
    restored = 0
    for name, previous in before.items():
        path = ROOT / "data" / name
        candidate = json.loads(path.read_text())
        merged, count = reconcile(previous, candidate, name)
        if count:
            path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n")
        restored += count
    if restored:
        print(f"affiliate lifecycle: preserved {restored} progressed records after {Path(sys.argv[1]).name}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
