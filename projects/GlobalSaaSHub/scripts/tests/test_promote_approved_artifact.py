"""
tests/test_promote_approved_artifact.py
=======================================
Deterministic tests for promote_approved_artifact.py.
NO external API calls. NO real Production execution. NO real Artifact downloads.
Uses mock HTTP responses, tempfile, and in-memory ZIP construction.

Tests:
 1. Valid artifact + correct SHA256 -> success
 2. Wrong SHA256 -> fatal exit
 3. Mismatched approved_head_sha -> fatal exit
 4. tools.next.json missing from ZIP -> fatal exit
 5. Corrupted JSON in tools.next.json -> fatal exit
 6. Empty tools array -> fatal exit
 7. Workflow structure: Production branch has no Tavily/Gemini/auto_aggregator steps
 8. run_summary source_head_sha mismatch -> fatal exit
 9. run_summary dry_run is false -> fatal exit
10. run_summary failure_test is true -> fatal exit
11. run_summary source_run_id mismatch -> fatal exit
12. run_summary artifact_schema_version missing/invalid -> fatal exit
"""

import sys, os, io, json, hashlib, zipfile, tempfile, unittest
from unittest.mock import patch, MagicMock

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

import promote_approved_artifact as paa


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_zip(files: dict) -> bytes:
    """Build in-memory ZIP. files = {name: content_bytes}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data if isinstance(data, bytes) else data.encode("utf-8"))
    return buf.getvalue()


VALID_TOOLS = json.dumps([
    {"id": "test-tool-1", "name": "Test Tool 1", "official_url": "https://example.com/1"},
    {"id": "test-tool-2", "name": "Test Tool 2", "official_url": "https://example.com/2"},
]).encode("utf-8")

GOOD_HEAD_SHA = "abc123def456abc123def456abc123def456abc123"

VALID_SUMMARY = json.dumps({
    "artifact_schema_version": "1.0",
    "source_head_sha": GOOD_HEAD_SHA,
    "source_run_id": "999999",
    "dry_run": True,
    "failure_test": False,
    "status": "ok"
}).encode("utf-8")


def _good_zip(custom_summary=None):
    summary_bytes = custom_summary if custom_summary is not None else VALID_SUMMARY
    return _make_zip({
        "projects/GlobalSaaSHub/data/tools.next.json": VALID_TOOLS,
        "projects/GlobalSaaSHub/data/run_summary.json": summary_bytes,
    })


def _mock_metadata_response(head_sha=GOOD_HEAD_SHA, run_id=999999):
    """Mock GitHub API metadata response."""
    data = json.dumps({
        "id": 888888,
        "name": "pipeline-artifacts-test",
        "workflow_run": {
            "id": run_id,
            "head_sha": head_sha,
            "repository_id": 123456,
        }
    }).encode("utf-8")
    mock = MagicMock()
    mock.read.return_value = data
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def _mock_zip_response(zip_bytes):
    """Mock GitHub API ZIP download response."""
    mock = MagicMock()
    mock.read.return_value = zip_bytes
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


# ── Test 1: Valid artifact + correct SHA256 -> success ───────────────────────
def test_valid_artifact_passes():
    zip_bytes = _good_zip()
    correct_sha = hashlib.sha256(zip_bytes).hexdigest()

    with tempfile.TemporaryDirectory() as tmp:
        meta = {"workflow_run": {"id": 999999, "head_sha": GOOD_HEAD_SHA, "repository_id": 1}}
        paa.verify_head_sha(meta, GOOD_HEAD_SHA)
        paa.verify_artifact_sha256(zip_bytes, correct_sha)
        result = paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, meta)

        assert len(result["tools"]) == 2
        out = os.path.join(tmp, "tools.next.json")
        assert os.path.exists(out), "tools.next.json not written to output_dir"


# ── Test 2: Wrong SHA256 -> fatal ────────────────────────────────────────────
def test_wrong_sha256_causes_fatal():
    zip_bytes = _good_zip()
    wrong_sha = "0" * 64
    try:
        paa.verify_artifact_sha256(zip_bytes, wrong_sha)
        assert False, "Should have called sys.exit(1)"
    except SystemExit as e:
        assert e.code == 1, f"Expected exit 1, got {e.code}"


# ── Test 3: Mismatched head_sha -> fatal ─────────────────────────────────────
def test_mismatched_head_sha_causes_fatal():
    meta = {"workflow_run": {"head_sha": "different_sha_not_matching", "repository_id": 1}}
    try:
        paa.verify_head_sha(meta, GOOD_HEAD_SHA)
        assert False, "Should have called sys.exit(1)"
    except SystemExit as e:
        assert e.code == 1


# ── Test 4: tools.next.json missing from ZIP -> fatal ────────────────────────
def test_missing_tools_next_json_causes_fatal():
    zip_bytes = _make_zip({
        "run_summary.json": VALID_SUMMARY,
    })
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


# ── Test 5: Corrupted JSON -> fatal ──────────────────────────────────────────
def test_corrupted_json_causes_fatal():
    zip_bytes = _make_zip({
        "tools.next.json": b"NOT VALID JSON {{{{",
        "run_summary.json": VALID_SUMMARY,
    })
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


# ── Test 6: Empty tools array -> fatal ───────────────────────────────────────
def test_empty_tools_array_causes_fatal():
    zip_bytes = _make_zip({
        "tools.next.json": b"[]",
        "run_summary.json": VALID_SUMMARY,
    })
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA)
            assert False, "Should have called sys.exit(1)"
        except SystemExit as e:
            assert e.code == 1


# ── Test 7: Workflow structure - Production has no Tavily/Gemini steps ────────
def test_workflow_production_branch_blocks_api_calls():
    workflow_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "..", "..", ".github", "workflows", "daily-deploy.yml"
    )
    workflow_path = os.path.normpath(workflow_path)

    if not os.path.exists(workflow_path):
        print("  SKIP: workflow file not found at " + workflow_path)
        return

    with open(workflow_path, encoding="utf-8") as f:
        content = f.read()

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
                # Look back up to 10 lines for a dry_run==true guard
                context = "\n".join(lines[max(0,i-10):i+1])
                if "dry_run" not in context and "approved_artifact_id" not in context:
                    errors.append(f"Line {i+1}: '{danger}' appears without dry_run guard: {line.strip()[:100]}")

    if errors:
        print("WORKFLOW STRUCTURE ERRORS:")
        for e in errors:
            print("  " + e)
        assert False, "Production branch is not protected from API calls"
    else:
        print("  Workflow structure OK: all API steps have dry_run guards.")


# ── Test 8: run_summary source_head_sha mismatch -> fatal ────────────────────
def test_summary_mismatched_head_sha_causes_fatal():
    bad_summary = json.dumps({
        "artifact_schema_version": "1.0",
        "source_head_sha": "wrong_sha_value_123456",
        "source_run_id": "999999",
        "dry_run": True,
        "failure_test": False,
    }).encode("utf-8")
    zip_bytes = _good_zip(custom_summary=bad_summary)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA)
            assert False, "Should have called sys.exit(1) on head_sha mismatch"
        except SystemExit as e:
            assert e.code == 1


# ── Test 9: run_summary dry_run false -> fatal ────────────────────────────────
def test_summary_dry_run_false_causes_fatal():
    bad_summary = json.dumps({
        "artifact_schema_version": "1.0",
        "source_head_sha": GOOD_HEAD_SHA,
        "source_run_id": "999999",
        "dry_run": False,
        "failure_test": False,
    }).encode("utf-8")
    zip_bytes = _good_zip(custom_summary=bad_summary)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA)
            assert False, "Should have called sys.exit(1) on dry_run=False"
        except SystemExit as e:
            assert e.code == 1


# ── Test 10: run_summary failure_test true -> fatal ───────────────────────────
def test_summary_failure_test_true_causes_fatal():
    bad_summary = json.dumps({
        "artifact_schema_version": "1.0",
        "source_head_sha": GOOD_HEAD_SHA,
        "source_run_id": "999999",
        "dry_run": True,
        "failure_test": True,
    }).encode("utf-8")
    zip_bytes = _good_zip(custom_summary=bad_summary)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA)
            assert False, "Should have called sys.exit(1) on failure_test=True"
        except SystemExit as e:
            assert e.code == 1


# ── Test 11: run_summary source_run_id mismatch -> fatal ──────────────────────
def test_summary_mismatched_run_id_causes_fatal():
    bad_summary = json.dumps({
        "artifact_schema_version": "1.0",
        "source_head_sha": GOOD_HEAD_SHA,
        "source_run_id": "111111",  # mismatches metadata run id 999999
        "dry_run": True,
        "failure_test": False,
    }).encode("utf-8")
    zip_bytes = _good_zip(custom_summary=bad_summary)
    meta = {"workflow_run": {"id": 999999, "head_sha": GOOD_HEAD_SHA}}
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA, meta)
            assert False, "Should have called sys.exit(1) on run_id mismatch"
        except SystemExit as e:
            assert e.code == 1


# ── Test 12: run_summary artifact_schema_version missing/invalid -> fatal ────
def test_summary_schema_version_invalid_causes_fatal():
    bad_summary = json.dumps({
        "artifact_schema_version": "2.0",  # unsupported version
        "source_head_sha": GOOD_HEAD_SHA,
        "source_run_id": "999999",
        "dry_run": True,
        "failure_test": False,
    }).encode("utf-8")
    zip_bytes = _good_zip(custom_summary=bad_summary)
    with tempfile.TemporaryDirectory() as tmp:
        try:
            paa.extract_and_validate_zip(zip_bytes, tmp, GOOD_HEAD_SHA)
            assert False, "Should have called sys.exit(1) on invalid schema version"
        except SystemExit as e:
            assert e.code == 1


# ── Runner ─────────────────────────────────────────────────────────────────────
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
    ]
    print("=" * 60)
    print("promote_approved_artifact Tests (Deterministic)")
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
