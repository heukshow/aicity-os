"""
tests/test_affiliate_integration.py
=====================================
Deterministic integration test for the affiliate_url_verifier + auto_aggregator
new-tool processing path.

NO external HTTP calls. NO Gemini/Tavily API. NO real tools.json modification.
Uses mock HTTP responses and tempfile for isolation.

Tests:
 1. SUCCESS path: fixture tool -> safe_affiliate_result -> normalize -> update -> write JSON -> reload -> all 8 fields present + correct values
 2. FAILURE path: network error -> affiliate_url=None, affiliate_verified=False, rejection_reason non-empty, all 8 fields present
 3. GitHub Actions gate: test exits 0 on pass, 1 on any failure (no continue-on-error)
"""

import sys, os, json, tempfile, unittest
from unittest.mock import patch, MagicMock

# Make scripts/ importable
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from affiliate_url_verifier import safe_affiliate_result
from auto_aggregator import normalize_unverified_candidate

# ── Required metadata fields ───────────────────────────────────────────────────
REQUIRED_AFFILIATE_FIELDS = [
    "affiliate_url",
    "affiliate_verified",
    "affiliate_source_url",
    "affiliate_final_url",
    "affiliate_http_status",
    "affiliate_evidence_markers",
    "affiliate_verified_at",
    "affiliate_rejection_reason",
]

# ── Fixture tool (never matches existing tools.json) ──────────────────────────
FIXTURE_TOOL = {
    "id": "integration-affiliate-tool",
    "name": "Integration Affiliate Tool",
    "category": "workflow_auto",
    "category_display": "Workflow Automation",
    "description": "Test fixture for affiliate integration test.",
    "official_url": "https://integration-test-fixture.invalid/",
    "affiliate_url": "https://integration-test-fixture.invalid/affiliate-program",
    "pricing": "See official pricing",
    "key_features": ["feature1"],
    "rating": None,
    "logo_url": "",
}

# ── HTML with strong compound evidence ────────────────────────────────────────
HTML_STRONG_EVIDENCE = (
    b"<html><head><title>Affiliate Program</title></head>"
    b"<body><h1>Join our Affiliate Program</h1>"
    b"<p>Earn 30% commission rate on every referral. "
    b"Cookie duration: 90 days. Affiliate dashboard available.</p>"
    b"<a href='/apply'>Apply now</a></body></html>"
)


def _mock_resp(html_bytes, status=200, url="https://integration-test-fixture.invalid/affiliate-program"):
    m = MagicMock()
    m.status = status
    m.geturl.return_value = url
    m.read.return_value = html_bytes
    m.__enter__ = lambda s: s
    m.__exit__ = MagicMock(return_value=False)
    return m


def _build_normalized_tool(aff_meta):
    """Simulate the auto_aggregator new-tool processing path."""
    tool = dict(FIXTURE_TOOL)
    official_url = tool["official_url"]
    normalized = normalize_unverified_candidate(tool, official_url, aff_meta["affiliate_url"])
    normalized.update(aff_meta)
    return normalized


def _write_and_reload(normalized_tool, existing_data=None):
    """Write to tempfile JSON, reload and return reloaded record."""
    dataset = list(existing_data or []) + [normalized_tool]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                     delete=False, encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False)
        fname = f.name
    try:
        with open(fname, encoding="utf-8") as f:
            reloaded = json.load(f)
        # Return the fixture tool record from reloaded data
        for t in reloaded:
            if t.get("id") == FIXTURE_TOOL["id"]:
                return t
        raise AssertionError("Fixture tool not found after reload")
    finally:
        os.unlink(fname)


# ── Test 1: SUCCESS path ───────────────────────────────────────────────────────
def test_success_path_all_fields_present_and_correct():
    """
    Happy path: strong affiliate evidence -> accepted -> fields stored -> survives JSON roundtrip.
    """
    aff_url = FIXTURE_TOOL["affiliate_url"]
    mock_resp = _mock_resp(HTML_STRONG_EVIDENCE, url=aff_url)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        aff_meta = safe_affiliate_result(aff_url, tool_name=FIXTURE_TOOL["name"])

    # Step: normalize + merge
    normalized = _build_normalized_tool(aff_meta)

    # Step: write tools.next.json format, reload
    reloaded = _write_and_reload(normalized)

    # Assert: all 8 fields present
    for field in REQUIRED_AFFILIATE_FIELDS:
        assert field in reloaded, f"SUCCESS PATH: missing field '{field}' after JSON reload"

    # Assert: correct values
    assert reloaded["affiliate_verified"] is True, "affiliate_verified must be True"
    assert reloaded["affiliate_url"] == aff_url, "affiliate_url must match"
    assert reloaded["affiliate_source_url"] == aff_url, "affiliate_source_url must match"
    assert reloaded["affiliate_final_url"] == aff_url, "affiliate_final_url must be stored"
    assert reloaded["affiliate_http_status"] == 200, "affiliate_http_status must be 200"
    assert len(reloaded["affiliate_evidence_markers"]) > 0, "affiliate_evidence_markers must not be empty"
    assert reloaded["affiliate_verified_at"], "affiliate_verified_at must be non-empty"
    assert reloaded["affiliate_rejection_reason"] == "", "affiliate_rejection_reason must be empty on success"


# ── Test 2: FAILURE path ──────────────────────────────────────────────────────
def test_failure_path_network_error_all_fields_present():
    """
    Network error path: affiliate_url=None, affiliate_verified=False,
    rejection_reason non-empty, all 8 fields survive JSON roundtrip.
    """
    import urllib.error
    aff_url = FIXTURE_TOOL["affiliate_url"]

    with patch("urllib.request.urlopen",
               side_effect=urllib.error.URLError("connection timed out")):
        aff_meta = safe_affiliate_result(aff_url, tool_name=FIXTURE_TOOL["name"])

    normalized = _build_normalized_tool(aff_meta)
    reloaded = _write_and_reload(normalized)

    # Assert: all 8 fields present
    for field in REQUIRED_AFFILIATE_FIELDS:
        assert field in reloaded, f"FAILURE PATH: missing field '{field}' after JSON reload"

    # Assert: failure values
    assert reloaded["affiliate_url"] is None, "affiliate_url must be None on failure"
    assert reloaded["affiliate_verified"] is False, "affiliate_verified must be False"
    assert reloaded["affiliate_rejection_reason"], "rejection_reason must be non-empty"
    assert reloaded["affiliate_source_url"] == aff_url, "source_url must be preserved even on failure"


# ── Test 3: new_tools_discovered.json format ──────────────────────────────────
def test_new_tools_discovered_json_format():
    """
    Simulates new_tools_discovered.json write (list of new tools only).
    Fields must survive that format too.
    """
    aff_url = FIXTURE_TOOL["affiliate_url"]
    mock_resp = _mock_resp(HTML_STRONG_EVIDENCE, url=aff_url)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        aff_meta = safe_affiliate_result(aff_url, tool_name=FIXTURE_TOOL["name"])

    normalized = _build_normalized_tool(aff_meta)

    # Write only the new tool (new_tools_discovered format)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                     delete=False, encoding="utf-8") as f:
        json.dump([normalized], f, ensure_ascii=False)
        fname = f.name
    try:
        with open(fname, encoding="utf-8") as f:
            reloaded_list = json.load(f)
        assert len(reloaded_list) == 1
        record = reloaded_list[0]
        for field in REQUIRED_AFFILIATE_FIELDS:
            assert field in record, f"new_tools_discovered format: missing field '{field}'"
        assert record["affiliate_verified"] is True
    finally:
        os.unlink(fname)


# ── Runner ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_success_path_all_fields_present_and_correct,
        test_failure_path_network_error_all_fields_present,
        test_new_tools_discovered_json_format,
    ]
    print("=" * 60)
    print("Affiliate Integration Tests (Deterministic / Mock-based)")
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
    if failed:
        print("SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)
