"""
tests/test_affiliate_integration.py  (v2 - opener.open mock)
"""
import sys, os, json, tempfile, unittest
from unittest.mock import patch, MagicMock

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from affiliate_url_verifier import safe_affiliate_result
from auto_aggregator import normalize_unverified_candidate

REQUIRED_AFFILIATE_FIELDS = [
    "affiliate_url","affiliate_verified","affiliate_source_url","affiliate_final_url",
    "affiliate_http_status","affiliate_evidence_markers","affiliate_verified_at","affiliate_rejection_reason",
]

FIXTURE_TOOL = {
    "id": "integration-affiliate-tool","name": "Integration Affiliate Tool",
    "category": "workflow_auto","category_display": "Workflow Automation",
    "description": "Test fixture for affiliate integration test.",
    "official_url": "https://integration-test-fixture.invalid/",
    "affiliate_url": "https://integration-test-fixture.invalid/affiliate-program",
    "pricing": "See official pricing","key_features": ["feature1"],"rating": None,"logo_url": "",
}

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


def _opener_mock(resp):
    mock_opener = MagicMock()
    mock_opener.open.return_value = resp
    return mock_opener


def _build_normalized_tool(aff_meta):
    tool = dict(FIXTURE_TOOL)
    normalized = normalize_unverified_candidate(tool, tool["official_url"], aff_meta["affiliate_url"])
    normalized.update(aff_meta)
    return normalized


def _write_and_reload(normalized_tool, existing_data=None):
    dataset = list(existing_data or []) + [normalized_tool]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False)
        fname = f.name
    try:
        with open(fname, encoding="utf-8") as f:
            reloaded = json.load(f)
        for t in reloaded:
            if t.get("id") == FIXTURE_TOOL["id"]:
                return t
        raise AssertionError("Fixture tool not found after reload")
    finally:
        os.unlink(fname)


def test_success_path_all_fields_present_and_correct():
    aff_url = FIXTURE_TOOL["affiliate_url"]
    resp = _mock_resp(HTML_STRONG_EVIDENCE, url=aff_url)
    with patch("affiliate_url_verifier._build_opener", return_value=_opener_mock(resp)):
        aff_meta = safe_affiliate_result(aff_url, tool_name=FIXTURE_TOOL["name"])
    normalized = _build_normalized_tool(aff_meta)
    reloaded = _write_and_reload(normalized)
    for field in REQUIRED_AFFILIATE_FIELDS:
        assert field in reloaded, f"SUCCESS PATH: missing field '{field}' after JSON reload"
    assert reloaded["affiliate_verified"] is True
    assert reloaded["affiliate_url"] == aff_url
    assert reloaded["affiliate_source_url"] == aff_url
    assert reloaded["affiliate_final_url"] == aff_url
    assert reloaded["affiliate_http_status"] == 200
    assert len(reloaded["affiliate_evidence_markers"]) > 0
    assert reloaded["affiliate_verified_at"]
    assert reloaded["affiliate_rejection_reason"] == ""


def test_failure_path_network_error_all_fields_present():
    import urllib.error
    aff_url = FIXTURE_TOOL["affiliate_url"]
    mock_opener = MagicMock()
    mock_opener.open.side_effect = urllib.error.URLError("connection timed out")
    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        aff_meta = safe_affiliate_result(aff_url, tool_name=FIXTURE_TOOL["name"])
    normalized = _build_normalized_tool(aff_meta)
    reloaded = _write_and_reload(normalized)
    for field in REQUIRED_AFFILIATE_FIELDS:
        assert field in reloaded, f"FAILURE PATH: missing field '{field}' after JSON reload"
    assert reloaded["affiliate_url"] is None
    assert reloaded["affiliate_verified"] is False
    assert reloaded["affiliate_rejection_reason"]
    assert reloaded["affiliate_source_url"] == aff_url


def test_new_tools_discovered_json_format():
    aff_url = FIXTURE_TOOL["affiliate_url"]
    resp = _mock_resp(HTML_STRONG_EVIDENCE, url=aff_url)
    with patch("affiliate_url_verifier._build_opener", return_value=_opener_mock(resp)):
        aff_meta = safe_affiliate_result(aff_url, tool_name=FIXTURE_TOOL["name"])
    normalized = _build_normalized_tool(aff_meta)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
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
        except (AssertionError, Exception) as e:
            print("FAIL  " + t.__name__ + ": " + type(e).__name__ + ": " + str(e))
            failed += 1
    print("=" * 60)
    print("Result: " + str(passed) + "/" + str(passed+failed) + " passed")
    sys.exit(1 if failed else 0)
