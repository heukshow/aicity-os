"""Strict semantic immutability audit for GlobalSaaSHub tool datasets."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

VOLATILE_FIELDS = frozenset({"affiliate_verified_at", "pricing_verified_at"})


class AuditError(ValueError):
    pass


def _canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _index_tools(tools, label):
    if not isinstance(tools, list):
        raise AuditError(f"{label} must be a JSON array")
    ids = []
    for index, tool in enumerate(tools):
        if not isinstance(tool, dict): raise AuditError(f"{label}[{index}] must be a JSON object")
        tool_id = tool.get("id")
        if not isinstance(tool_id, str) or not tool_id: raise AuditError(f"{label}[{index}].id must be a non-empty string")
        ids.append(tool_id)
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates: raise AuditError(f"{label} contains duplicate ID(s): {duplicates}")
    return {tool["id"]: tool for tool in tools}


def _strip_volatile(value):
    if isinstance(value, dict): return {key: _strip_volatile(child) for key, child in value.items() if key not in VOLATILE_FIELDS}
    if isinstance(value, list): return [_strip_volatile(child) for child in value]
    return value


def _semantic_form(tools, label):
    indexed = _index_tools(tools, label)
    return [_strip_volatile(indexed[tool_id]) for tool_id in sorted(indexed)]


def _diff(before, after, path=""):
    if type(before) is not type(after): return [path or "$"]
    if isinstance(before, dict):
        diffs = []
        for key in sorted(set(before) | set(after)):
            child_path = f"{path}.{key}" if path else key
            diffs.extend([child_path] if key not in before or key not in after else _diff(before[key], after[key], child_path))
        return diffs
    if isinstance(before, list):
        if len(before) != len(after): return [f"{path}.length"]
        return [item for index, pair in enumerate(zip(before, after)) for item in _diff(pair[0], pair[1], f"{path}[{index}]")]
    return [] if before == after else [path or "$"]


def audit_datasets(before_tools, after_tools, before_raw=None, after_raw=None):
    before_index, after_index = _index_tools(before_tools, "before"), _index_tools(after_tools, "after")
    before_ids, after_ids = set(before_index), set(after_index)
    added, deleted = sorted(after_ids - before_ids), sorted(before_ids - after_ids)
    volatile_changes, forbidden_paths = Counter(), []
    for tool_id in sorted(before_ids & after_ids):
        left, right = before_index[tool_id], after_index[tool_id]
        for field in sorted(VOLATILE_FIELDS):
            if (field in left) != (field in right):
                volatile_changes[field] += 1
            elif field in left:
                volatile_changes[field] += len(_diff(left[field], right[field], f"{tool_id}.{field}"))
        forbidden_paths.extend(_diff(_strip_volatile(left), _strip_volatile(right), tool_id))
    forbidden_paths.extend(f"added:{item}" for item in added); forbidden_paths.extend(f"deleted:{item}" for item in deleted)
    before_semantic, after_semantic = _canonical_bytes(_semantic_form(before_tools, "before")), _canonical_bytes(_semantic_form(after_tools, "after"))
    before_raw = before_raw if before_raw is not None else _canonical_bytes(before_tools); after_raw = after_raw if after_raw is not None else _canonical_bytes(after_tools)
    return {"audit_schema_version": "1.0", "status": "PASS" if not forbidden_paths else "FAIL", "raw_sha256_before": _sha256(before_raw), "raw_sha256_after": _sha256(after_raw), "semantic_sha256_before": _sha256(before_semantic), "semantic_sha256_after": _sha256(after_semantic), "ignored_volatile_fields": sorted(VOLATILE_FIELDS), "volatile_only_diff_count": sum(volatile_changes.values()), "volatile_diff_counts_by_field": dict(sorted(volatile_changes.items())), "forbidden_diff_count": len(forbidden_paths), "forbidden_diff_paths": forbidden_paths, "added_tool_ids": added, "deleted_tool_ids": deleted, "tool_count_before": len(before_tools), "tool_count_after": len(after_tools)}


def audit_files(before_path, after_path):
    before_raw, after_raw = Path(before_path).read_bytes(), Path(after_path).read_bytes()
    try: before_tools, after_tools = json.loads(before_raw.decode("utf-8")), json.loads(after_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise AuditError(f"invalid UTF-8 JSON: {exc}") from exc
    return audit_datasets(before_tools, after_tools, before_raw, after_raw)


def validate_manifest(expected, actual):
    if not isinstance(actual, dict) or actual != expected: raise AuditError("semantic audit manifest does not match recomputed dataset audit")
    if actual.get("status") != "PASS": raise AuditError("semantic audit manifest status is not PASS")


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--before", required=True); parser.add_argument("--after", required=True); parser.add_argument("--manifest", required=True); args = parser.parse_args()
    try: manifest = audit_files(args.before, args.after)
    except (OSError, AuditError) as exc: print(f"[semantic-audit] FATAL: {exc}", file=sys.stderr); return 1
    Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[semantic-audit] volatile allowlist: {manifest['ignored_volatile_fields']}")
    for kind in ("raw", "semantic"):
        print(f"[semantic-audit] {kind} SHA before: {manifest[kind + '_sha256_before']}"); print(f"[semantic-audit] {kind} SHA after:  {manifest[kind + '_sha256_after']}")
    if manifest["raw_sha256_before"] != manifest["raw_sha256_after"]: print("[semantic-audit] WARNING: raw file SHA changed")
    print(f"[semantic-audit] volatile changes: {manifest['volatile_diff_counts_by_field']} (total={manifest['volatile_only_diff_count']})"); print(f"[semantic-audit] forbidden diffs: {manifest['forbidden_diff_count']}"); print(f"[semantic-audit] RESULT: {manifest['status']}")
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__": sys.exit(main())
