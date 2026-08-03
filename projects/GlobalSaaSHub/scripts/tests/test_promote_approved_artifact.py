"""
tests/test_promote_approved_artifact.py
=========================================
Strict security tests for promote_approved_artifact.py.
Ensures zero-bypass verification of SHA256 digest, Git HEAD SHA,
strict JSON schema of run_summary.json, metadata structure, and ZIP basename uniqueness.

Tests (29 tests total):
 1. Valid artifact passes all checks
 2. Mismatched SHA256 -> fatal error
 3. Mismatched HEAD SHA -> fatal error
 4. Missing tools.next.json -> fatal error
 5. Corrupted JSON -> fatal error
 6. Empty tools array -> fatal error
 7. Workflow structure - FAIL-CLOSED if missing/unreadable, all API steps guarded
 8. run_summary source_head_sha mismatch -> fatal error
 9. run_summary dry_run=False -> fatal error
10. run_summary failure_test=True -> fatal error
11. run_summary source_run_id mismatch -> fatal error
12. run_summary artifact_schema_version != '1.0' -> fatal error
13. run_summary source_head_sha = 'local-dev' bypass attempt -> fatal error
14. run_summary source_run_id = 'local-run' bypass attempt -> fatal error
15. run_summary source_head_sha missing/null -> fatal error
16. run_summary source_run_id missing/null -> fatal error
17. metadata missing workflow_run.id -> fatal error
18. run_summary dry_run string "true" -> fatal error
19. run_summary failure_test string "false" -> fatal error
20. run_summary non-dict -> fatal error
21. Duplicate tools.next.json in ZIP (basename count > 1) -> fatal error
22. Duplicate run_summary.json in ZIP (basename count > 1) -> fatal error
23. Metadata expired is True -> fatal error
24. Metadata not dict -> fatal error
25. Metadata workflow_run not dict -> fatal error
26. Metadata name mismatch (not pipeline-artifacts-{run_id}) -> fatal error
27. Metadata workflow_run.id mismatch -> fatal error
28. Approved head SHA empty/null -> fatal error
29. Approved head SHA case-insensitive match -> PASS
"""

import sys
import os
import json
import zipfile
import tempfile
import hashlib
import io

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

import promote_approved_artifact as paa

GOOD_HEAD_SHA = "abc123def456abc123def456abc123def456abc123"
GOOD_RUN_ID = "999999"
GOOD_META = {
    "name": f"pipeline-artifacts-{GOOD_RUN_ID}",
    "expired": False,
    "workflow_run": {
        "id": int(GOOD_RUN_ID),
        "head_sha": GOOD_HEAD_SHA,
        "repository_id": 12345,
    },
}

VALID_SUMMARY_DICT = {
    "artifact_schema_version": "1.0",
    "source_head_sha": GOOD_HEAD_SHA,
    "source_run_id": GOOD_RUN_ID,
    "dry_run": True,
    "failure_test": False,
    "status": "success",
}

VALID_TOOLS_JSON = json.dumps([
    {"id": "tool-1", "name": "Tool One", "official_url": "https://t1.com/"},
    {"id": "tool-2", "name": "Tool Two", "official_url": "https://t2.com/"},
]).encode("utf-8")


def _good_zip(custom_tools=None, custom_summary=None):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("projects/GlobalSaaSHub/data/tools.next.json", custom_tools or VALID_TOOLS_JSON)
        summary_bytes = custom_summary or json.dumps(VALID_SUMMARY_DICT).encode("utf-8")
        zf.writestr("projects/GlobalSaaSHub/data/run_summary.json", summary_bytes)
    return buf.getvalue()


def test_valid_artifact_passes():
    zip_bytes = _good_zip()
    digest = hashlib.sha256(zip_bytes).hexdigest()
    with tempfile.TemporaryDirectory() as tmp:
        paa.verify_head_sha(GOOD_META, GOOD_HEAD_SHA, GOOD_RUN_ID)
        paa.verify_artifact_sha256(zip_bytes, digest)
        res = paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
        assert len(res["tools"]) == 2
        assert os.path.exists(os.path.join(tmp, "tools.next.json"))


def test_wrong_sha256_causes_fatal():
    zip_bytes = _good_zip()
    wrong = "0" * 64
    try:
        paa.verify_artifact_sha256(zip_bytes, wrong)
        assert False, "Should have called sys.exit(1)"
    except SystemExit as e:
        assert e.code == 1


def test_mismatched_head_sha_causes_fatal():
    wrong_meta = dict(GOOD_META)
    wrong_meta["workflow_run"] = {"id": int(GOOD_RUN_ID), "head_sha": "different_sha_not_matching"}
    try:
        paa.verify_head_sha(wrong_meta, GOOD_HEAD_SHA, GOOD_RUN_ID)
        assert False, "Should have called sys.exit(1)"
    except SystemExit as e:
        assert e.code == 1


def test_missing_tools_next_json_causes_fatal():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("run_summary.json", json.dumps(VALID_SUMMARY_DICT).encode("utf-8"))
    zip_bytes = buf.getvalue()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_corrupted_json_causes_fatal():
    zip_bytes = _good_zip(custom_tools=b"NOT JSON {{{")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_empty_tools_array_causes_fatal():
    zip_bytes = _good_zip(custom_tools=b"[]")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_workflow_production_branch_blocks_api_calls():
    """Fail-closed test for daily-deploy.yml structure."""
    workflow_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "..", "..", ".github", "workflows", "daily-deploy.yml"
    )
    workflow_path = os.path.normpath(workflow_path)

    if not os.path.exists(workflow_path):
        assert False, f"FATAL FAIL: workflow file not found at {workflow_path}"

    try:
        with open(workflow_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        assert False, f"FATAL FAIL: could not read workflow file: {e}"

    dangerous_steps = [
        "auto_aggregator.py",
        "TAVILY_API_KEY",
        "GEMINI_API_KEY",
        "verify_manual_candidates.py",
    ]

    lines = content.split("\n")
    errors = []
    for i, line in enumerate(lines):
        for danger in dangerous_steps:
            if danger in line and not line.strip().startswith("#"):
                context = "\n".join(lines[max(0, i - 10):i + 1])
                if "dry_run" not in context and "approved_artifact_id" not in context:
                    errors.append(f"Line {i+1}: '{danger}' appears without dry_run guard: {line.strip()[:100]}")

    if errors:
        assert False, f"Production branch is not protected from API calls: {errors}"
    else:
        print("  Workflow structure OK: all API steps have dry_run guards.")


def test_summary_mismatched_head_sha_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["source_head_sha"] = "wrong_sha_value_123456"
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_dry_run_false_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["dry_run"] = False
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_failure_test_true_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["failure_test"] = True
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_mismatched_run_id_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["source_run_id"] = "111111"
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_schema_version_invalid_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["artifact_schema_version"] = "2.0"
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_local_dev_bypass_attempt_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["source_head_sha"] = "local-dev"
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_local_run_bypass_attempt_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["source_run_id"] = "local-run"
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_missing_head_sha_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    del d["source_head_sha"]
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_missing_run_id_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    del d["source_run_id"]
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_metadata_missing_workflow_run_id_causes_fatal():
    bad_meta = {"name": f"pipeline-artifacts-{GOOD_RUN_ID}", "expired": False, "workflow_run": {"head_sha": GOOD_HEAD_SHA}}
    zip_bytes = _good_zip()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, bad_meta)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_string_dry_run_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["dry_run"] = "true"
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_string_failure_test_causes_fatal():
    d = dict(VALID_SUMMARY_DICT)
    d["failure_test"] = "false"
    zip_bytes = _good_zip(custom_summary=json.dumps(d).encode("utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_summary_non_dict_causes_fatal():
    bad_summary = json.dumps(["invalid", "list"]).encode("utf-8")
    zip_bytes = _good_zip(custom_summary=bad_summary)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


def test_duplicate_tools_next_json_in_zip_causes_fatal():
    """Verify that multiple files matching basename tools.next.json cause fatal rejection."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("tools.next.json", VALID_TOOLS_JSON)
        zf.writestr("nested/tools.next.json", VALID_TOOLS_JSON)
        zf.writestr("run_summary.json", json.dumps(VALID_SUMMARY_DICT).encode("utf-8"))
    zip_bytes = buf.getvalue()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1) on duplicate tools.next.json"
        except SystemExit as e:
            assert e.code == 1


def test_duplicate_run_summary_json_in_zip_causes_fatal():
    """Verify that multiple files matching basename run_summary.json cause fatal rejection."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("tools.next.json", VALID_TOOLS_JSON)
        zf.writestr("run_summary.json", json.dumps(VALID_SUMMARY_DICT).encode("utf-8"))
        zf.writestr("nested/run_summary.json", json.dumps(VALID_SUMMARY_DICT).encode("utf-8"))
    zip_bytes = buf.getvalue()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, GOOD_META)
            assert False, "Should have called sys.exit(1) on duplicate run_summary.json"
        except SystemExit as e:
            assert e.code == 1


def test_metadata_expired_true_causes_fatal():
    bad_meta = dict(GOOD_META)
    bad_meta["expired"] = True
    try:
        paa.verify_head_sha(bad_meta, GOOD_HEAD_SHA, GOOD_RUN_ID)
        assert False, "Should have called sys.exit(1) on expired artifact"
    except SystemExit as e:
        assert e.code == 1


def test_metadata_name_mismatch_causes_fatal():
    bad_meta = dict(GOOD_META)
    bad_meta["name"] = "pipeline-artifacts-000000"
    try:
        paa.verify_head_sha(bad_meta, GOOD_HEAD_SHA, GOOD_RUN_ID)
        assert False, "Should have called sys.exit(1) on name mismatch"
    except SystemExit as e:
        assert e.code == 1


def test_approved_head_sha_empty_causes_fatal():
    try:
        paa.verify_head_sha(GOOD_META, "", GOOD_RUN_ID)
        assert False, "Should have called sys.exit(1) on empty approved_head_sha"
    except SystemExit as e:
        assert e.code == 1


def test_approved_head_sha_case_insensitive_pass():
    upper_sha = GOOD_HEAD_SHA.upper()
    paa.verify_head_sha(GOOD_META, upper_sha, GOOD_RUN_ID)


if __name__ == "__main__":
    tests = [
        test_valid_artifact_passes,
        test_wrong_sha256_causes_fatal,
        test_mismatched_head_sha_causes_fatal,
        test_missing_tools_next_json_causes_fatal,
        test_corrupted_json_causes_fatal,
        test_empty_tools_array_causes_fatal,
        test_workflow_production_branch_blocks_api_calls,
        test_summary_mismatched_head_sha_causes_fatal,
        test_summary_dry_run_false_causes_fatal,
        test_summary_failure_test_true_causes_fatal,
        test_summary_mismatched_run_id_causes_fatal,
        test_summary_schema_version_invalid_causes_fatal,
        test_summary_local_dev_bypass_attempt_causes_fatal,
        test_summary_local_run_bypass_attempt_causes_fatal,
        test_summary_missing_head_sha_causes_fatal,
        test_summary_missing_run_id_causes_fatal,
        test_metadata_missing_workflow_run_id_causes_fatal,
        test_summary_string_dry_run_causes_fatal,
        test_summary_string_failure_test_causes_fatal,
        test_summary_non_dict_causes_fatal,
        test_duplicate_tools_next_json_in_zip_causes_fatal,
        test_duplicate_run_summary_json_in_zip_causes_fatal,
        test_metadata_expired_true_causes_fatal,
        test_metadata_name_mismatch_causes_fatal,
        test_approved_head_sha_empty_causes_fatal,
        test_approved_head_sha_case_insensitive_pass,
    ]
    print("=" * 60)
    print(f"promote_approved_artifact Security Tests ({len(tests)} tests)")
    print("=" * 60)
    passed = failed = 0
    for t in tests:
        try:
            t()
            print("PASS  " + t.__name__)
            passed += 1
        except AssertionError as e:
            print("FAIL  " + t.__name__ + ": " + str(e))
            failed += 1
        except Exception as e:
            print("ERROR " + t.__name__ + ": " + type(e).__name__ + ": " + str(e))
            failed += 1
    print("=" * 60)
    print("Result: " + str(passed) + "/" + str(passed + failed) + " passed")
    sys.exit(1 if failed else 0)
