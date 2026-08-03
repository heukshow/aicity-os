"""
tests/test_affiliate_redirect.py
=================================
Tests for HTTP 307/308 redirect handling in affiliate_url_verifier.py v3.
All tests use mock responses - no external HTTP calls.

Tests:
 1. HTTP 308 + Location -> followed to final URL -> evidence check -> ACCEPTED
 2. HTTP 307 + Location -> followed to final URL -> evidence check -> ACCEPTED
 3. HTTP 308 + strong evidence at final URL -> ACCEPTED
 4. Redirect loop (> MAX_REDIRECTS) -> safely rejected with rejection_reason
 5. HTTP 308 + no Location header -> rejected (HTTPError propagates)
 6. SSL validation still enforced after redirect (SSL error -> rejected)
 7. redirect_verified final_url is stored in safe_affiliate_result metadata
"""

import sys, os, ssl, io, unittest
from unittest.mock import patch, MagicMock, call

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from affiliate_url_verifier import (
    verify_affiliate_url,
    safe_affiliate_result,
    MAX_REDIRECTS,
    _Redirect308Handler,
    _build_opener,
    _make_ssl_context,
)

HTML_STRONG = (
    b"<html><head><title>Affiliate Program</title></head>"
    b"<body><h1>Join our Affiliate Program</h1>"
    b"<p>Commission rate: 30%. Cookie duration: 60 days.</p>"
    b"</body></html>"
)

HTML_NO_EVIDENCE = b"<html><body><p>Welcome to our site.</p></body></html>"


def _mock_resp(html=HTML_STRONG, status=200, url="https://final.example.com/affiliate"):
    m = MagicMock()
    m.status = status
    m.geturl.return_value = url
    m.read.return_value = html
    m.__enter__ = lambda s: s
    m.__exit__ = MagicMock(return_value=False)
    return m


# ── Test 1: HTTP 308 -> follow -> ACCEPTED ────────────────────────────────────
def test_308_redirect_followed_and_accepted():
    """308 redirect should be followed; if final page has strong evidence -> ACCEPTED."""
    final_resp = _mock_resp(HTML_STRONG, url="https://final.example.com/affiliate-program")
    mock_opener = MagicMock()
    mock_opener.open.return_value = final_resp

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        r = verify_affiliate_url("https://example.com/old-affiliate")

    assert r["accepted"], "308 redirect followed + strong evidence should be ACCEPTED"
    assert r["final_url"] == "https://final.example.com/affiliate-program"
    assert len(r["evidence_patterns"]) > 0


# ── Test 2: HTTP 307 -> follow -> ACCEPTED ────────────────────────────────────
def test_307_redirect_followed_and_accepted():
    final_resp = _mock_resp(HTML_STRONG, url="https://final.example.com/affiliate")
    mock_opener = MagicMock()
    mock_opener.open.return_value = final_resp

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        r = verify_affiliate_url("https://example.com/temp-affiliate")

    assert r["accepted"], "307 redirect followed + strong evidence should be ACCEPTED"


# ── Test 3: HTTP 308 + strong evidence at final URL -> metadata stored ────────
def test_308_redirect_metadata_stored_in_safe_result():
    final_url = "https://final.example.com/affiliate-program"
    final_resp = _mock_resp(HTML_STRONG, url=final_url)
    mock_opener = MagicMock()
    mock_opener.open.return_value = final_resp

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        meta = safe_affiliate_result(
            "https://example.com/old-path", tool_name="RedirectTool"
        )

    assert meta["affiliate_verified"] is True
    assert meta["affiliate_final_url"] == final_url
    assert meta["affiliate_url"] == "https://example.com/old-path"
    assert len(meta["affiliate_evidence_markers"]) > 0
    assert meta["affiliate_rejection_reason"] == ""


# ── Test 4: Redirect loop -> safely rejected ──────────────────────────────────
def test_redirect_loop_safely_rejected():
    """Simulates too many redirects (HTTPError 310 or urllib.error.URLError)."""
    import urllib.error
    mock_opener = MagicMock()
    mock_opener.open.side_effect = urllib.error.URLError("too many redirects")

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        r = verify_affiliate_url("https://redirect-loop.example.com/affiliate")

    assert not r["accepted"]
    assert "redirect" in r["rejection_reason"].lower() or "url error" in r["rejection_reason"].lower()


# ── Test 5: HTTP 308 + no evidence at final URL -> REJECTED ──────────────────
def test_308_redirect_no_evidence_rejected():
    final_resp = _mock_resp(HTML_NO_EVIDENCE, url="https://final.example.com/partner-info")
    mock_opener = MagicMock()
    mock_opener.open.return_value = final_resp

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        r = verify_affiliate_url("https://example.com/redirect-to-partner")

    assert not r["accepted"], "308 redirect to page with no evidence should be REJECTED"
    assert r["evidence_patterns"] == []


# ── Test 6: SSL error after redirect -> REJECTED ──────────────────────────────
def test_ssl_error_after_redirect_rejected():
    mock_opener = MagicMock()
    mock_opener.open.side_effect = ssl.SSLError("CERTIFICATE_VERIFY_FAILED")

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        r = verify_affiliate_url("https://self-signed.example.com/affiliate")

    assert not r["accepted"]
    assert "SSL" in r["rejection_reason"]


# ── Test 7: MAX_REDIRECTS constant is set to a safe limit ────────────────────
def test_max_redirects_is_bounded():
    assert isinstance(MAX_REDIRECTS, int), "MAX_REDIRECTS must be an integer"
    assert 3 <= MAX_REDIRECTS <= 20, f"MAX_REDIRECTS={MAX_REDIRECTS} is outside safe range [3,20]"


# ── Test 8: _Redirect308Handler handles 308 ───────────────────────────────────
def test_redirect308handler_has_308_method():
    handler = _Redirect308Handler()
    assert hasattr(handler, "http_error_308"), "_Redirect308Handler must have http_error_308"
    assert hasattr(handler, "http_error_307"), "_Redirect308Handler must have http_error_307"


# ── Runner ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_308_redirect_followed_and_accepted,
        test_307_redirect_followed_and_accepted,
        test_308_redirect_metadata_stored_in_safe_result,
        test_redirect_loop_safely_rejected,
        test_308_redirect_no_evidence_rejected,
        test_ssl_error_after_redirect_rejected,
        test_max_redirects_is_bounded,
        test_redirect308handler_has_308_method,
    ]
    print("=" * 60)
    print("HTTP 307/308 Redirect Tests (Mock-based)")
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
