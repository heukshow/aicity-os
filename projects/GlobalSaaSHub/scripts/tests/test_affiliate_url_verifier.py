"""
tests/test_affiliate_url_verifier.py  (v2 - mock-based)
=========================================================
Official repository tests for affiliate_url_verifier.py v2.

All tests use mock HTTP responses - no real external HTTP calls.

Tests cover:
 1. Valid SSL + strong affiliate evidence -> ACCEPTED
 2. SSL certificate error -> REJECTED
 3. /partners path + strong evidence -> ACCEPTED (path alone does NOT block)
 4. /partners path + no evidence -> REJECTED (evidence check, not path check)
 5. Footer-only single word "affiliate" -> REJECTED (weak signal)
 6. commission_rate pattern present -> ACCEPTED
 7. Redirect: final_url stored in metadata
 8. Network error -> affiliate_url=None + rejection_reason stored
 9. safe_affiliate_result() output has all required metadata fields
10. auto_aggregator normalized tool contains all affiliate fields
"""

import sys, os, ssl, unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from affiliate_url_verifier import (
    verify_affiliate_url,
    safe_affiliate_result,
    _find_strong_evidence,
    _has_path_risk_signal,
    STRONG_EVIDENCE_PATTERNS,
)

REQUIRED_META_FIELDS = [
    "affiliate_url",
    "affiliate_verified",
    "affiliate_source_url",
    "affiliate_final_url",
    "affiliate_http_status",
    "affiliate_evidence_markers",
    "affiliate_verified_at",
    "affiliate_rejection_reason",
]

# ── HTML fixtures ──────────────────────────────────────────────────────────────
HTML_STRONG = b"""<html><head><title>Affiliate Program</title></head>
<body><h1>Join our Affiliate Program</h1>
<p>Earn a 30% commission rate on every referral. Cookie duration: 90 days.</p>
<a href="/apply">Apply now</a></body></html>"""

HTML_FOOTER_ONLY = b"""<html><head><title>Home</title></head>
<body><main><h1>Welcome</h1><p>Best SaaS tool.</p></main>
<footer><a href="/privacy">Privacy</a> | <a href="/affiliate">Affiliate</a></footer>
</body></html>"""

HTML_PARTNERS_WITH_EVIDENCE = b"""<html><head><title>Partner Program</title></head>
<body><h1>Join our Affiliate Program</h1>
<p>Payout terms: monthly. Commission rate: 20%. Affiliate dashboard available.</p>
</body></html>"""

HTML_PARTNERS_NO_EVIDENCE = b"""<html><head><title>Partners</title></head>
<body><h1>Business Partners</h1><p>Contact us to become a reseller.</p>
</body></html>"""

HTML_COMMISSION_PATTERN = b"""<html><head><title>Referral</title></head>
<body><h1>Referral Program</h1>
<p>Our referral tracking system ensures you get credit. Cookie duration: 60 days.</p>
</body></html>"""


def _make_mock_response(html_bytes, status=200, url="https://example.com/affiliate"):
    """Create a mock urllib response object."""
    mock = MagicMock()
    mock.status = status
    mock.geturl.return_value = url
    mock.read.return_value = html_bytes
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


# ── Test 1: Valid SSL + strong evidence -> ACCEPTED ────────────────────────────
def test_strong_evidence_accepted():
    mock_resp = _make_mock_response(HTML_STRONG, url="https://example.com/affiliate-program")
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = verify_affiliate_url("https://example.com/affiliate-program")
    assert r["accepted"], "Strong evidence page should be ACCEPTED"
    assert r["http_status"] == 200
    assert len(r["evidence_patterns"]) > 0
    assert r["verified_at"] is not None


# ── Test 2: SSL certificate error -> REJECTED ─────────────────────────────────
def test_ssl_error_rejected():
    with patch("urllib.request.urlopen", side_effect=ssl.SSLError("CERTIFICATE_VERIFY_FAILED")):
        r = verify_affiliate_url("https://self-signed.badssl.com/affiliate")
    assert not r["accepted"], "SSL error should be REJECTED"
    assert "SSL" in r["rejection_reason"]
    assert r["http_status"] is None


# ── Test 3: /partners path + strong evidence -> ACCEPTED ──────────────────────
def test_partners_path_with_strong_evidence_accepted():
    mock_resp = _make_mock_response(
        HTML_PARTNERS_WITH_EVIDENCE, url="https://example.com/partners"
    )
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = verify_affiliate_url("https://example.com/partners")
    assert r["accepted"], "/partners path with strong affiliate evidence should be ACCEPTED"
    assert len(r["evidence_patterns"]) > 0


# ── Test 4: /partners path + no evidence -> REJECTED ─────────────────────────
def test_partners_path_no_evidence_rejected():
    mock_resp = _make_mock_response(
        HTML_PARTNERS_NO_EVIDENCE, url="https://example.com/partners"
    )
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = verify_affiliate_url("https://example.com/partners")
    assert not r["accepted"], "/partners path with no strong evidence should be REJECTED"
    assert r["evidence_patterns"] == []


# ── Test 5: Footer-only single word -> REJECTED ───────────────────────────────
def test_footer_only_affiliate_word_rejected():
    mock_resp = _make_mock_response(HTML_FOOTER_ONLY, url="https://example.com/home")
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = verify_affiliate_url("https://example.com/home")
    assert not r["accepted"], "Footer-only 'affiliate' word should be REJECTED"
    assert r["evidence_patterns"] == []


# ── Test 6: commission/payout/cookie_duration pattern -> ACCEPTED ─────────────
def test_commission_pattern_accepted():
    mock_resp = _make_mock_response(HTML_COMMISSION_PATTERN, url="https://example.com/referral")
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = verify_affiliate_url("https://example.com/referral")
    assert r["accepted"], "cookie_duration + referral_tracking should be ACCEPTED"
    assert len(r["evidence_patterns"]) > 0


# ── Test 7: Redirect - final_url stored ───────────────────────────────────────
def test_redirect_final_url_stored():
    final = "https://example.com/affiliate-program-final"
    mock_resp = _make_mock_response(HTML_STRONG, url=final)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        r = verify_affiliate_url("https://example.com/affiliate-redirect")
    assert r["final_url"] == final, "final_url after redirect should be stored"
    assert r["accepted"]


# ── Test 8: Network error -> None + rejection_reason ─────────────────────────
def test_network_error_returns_full_meta():
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timed out")):
        meta = safe_affiliate_result("https://example.com/affiliate", tool_name="TestTool")
    assert meta["affiliate_url"] is None
    assert meta["affiliate_verified"] is False
    assert meta["affiliate_rejection_reason"], "rejection_reason must be non-empty"
    assert meta["affiliate_source_url"] == "https://example.com/affiliate"
    for field in REQUIRED_META_FIELDS:
        assert field in meta, f"Missing field: {field}"


# ── Test 9: safe_affiliate_result() returns all required metadata fields ──────
def test_safe_affiliate_result_has_all_fields():
    mock_resp = _make_mock_response(HTML_STRONG, url="https://example.com/affiliate")
    with patch("urllib.request.urlopen", return_value=mock_resp):
        meta = safe_affiliate_result("https://example.com/affiliate", tool_name="Tool")
    for field in REQUIRED_META_FIELDS:
        assert field in meta, f"Missing field in result: {field}"
    assert meta["affiliate_verified"] is True
    assert meta["affiliate_url"] == "https://example.com/affiliate"


# ── Test 10: auto_aggregator normalized tool contains all affiliate fields ─────
def test_normalized_tool_contains_all_affiliate_fields():
    """
    Simulate the auto_aggregator merge: normalize_unverified_candidate + update(aff_meta).
    Ensures all affiliate fields survive the merge.
    """
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from auto_aggregator import normalize_unverified_candidate

    stub_tool = {
        "id": "test-tool", "name": "TestTool", "category": "cat", "category_display": "Cat",
        "description": "desc", "official_url": "https://example.com",
        "pricing": "Free", "key_features": [], "rating": None, "logo_url": "",
    }
    mock_resp = _make_mock_response(HTML_STRONG, url="https://example.com/affiliate")
    with patch("urllib.request.urlopen", return_value=mock_resp):
        aff_meta = safe_affiliate_result("https://example.com/affiliate", tool_name="TestTool")

    normalized = normalize_unverified_candidate(stub_tool, "https://example.com", aff_meta["affiliate_url"])
    normalized.update(aff_meta)

    for field in REQUIRED_META_FIELDS:
        assert field in normalized, f"Missing affiliate field in normalized tool: {field}"
    assert normalized["affiliate_verified"] is True


# ── Runner ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_strong_evidence_accepted,
        test_ssl_error_rejected,
        test_partners_path_with_strong_evidence_accepted,
        test_partners_path_no_evidence_rejected,
        test_footer_only_affiliate_word_rejected,
        test_commission_pattern_accepted,
        test_redirect_final_url_stored,
        test_network_error_returns_full_meta,
        test_safe_affiliate_result_has_all_fields,
        test_normalized_tool_contains_all_affiliate_fields,
    ]
    print("=" * 60)
    print("affiliate_url_verifier v2 - Mock-Based Contract Tests")
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
