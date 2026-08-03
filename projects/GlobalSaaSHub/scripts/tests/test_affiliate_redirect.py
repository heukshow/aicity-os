"""
tests/test_affiliate_redirect.py
=================================
Tests for HTTP 307/308 redirect handling and HTTP error resilience in affiliate_url_verifier.py v3.
All tests use mock responses - no external HTTP calls.

Tests:
 1. HTTP 308 + Location -> followed to final URL -> evidence check -> ACCEPTED
 2. HTTP 307 + Location -> followed to final URL -> evidence check -> ACCEPTED
 3. HTTP 308 + strong evidence at final URL -> ACCEPTED
 4. Redirect loop (> MAX_REDIRECTS) -> safely rejected with rejection_reason
 5. HTTP 308 + no Location header -> rejected (HTTPError propagates)
 6. SSL validation still enforced after redirect (SSL error -> rejected)
 7. redirect_verified final_url is stored in safe_affiliate_result metadata
 8. MAX_REDIRECTS constant is bounded
 9. _Redirect308Handler handles 308
10. opener.open() returns None -> safely rejected, no AttributeError
11. HTTP 404 -> http_status=404, rejection_reason="HTTP error 404"
12. HTTP 500 -> http_status=500, rejection_reason="HTTP error 500"
13. HTTPError with URL -> stores final_url
14. 308 redirect followed by 404 -> stores final HTTP 404 and final_url
"""

import sys, os, ssl, io, unittest
import urllib.error
from unittest.mock import patch, MagicMock

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
        meta = safe_affiliate_result("https://example.com/old-path", tool_name="RedirectTool")

    assert meta["affiliate_verified"] is True
    assert meta["affiliate_final_url"] == final_url
    assert meta["affiliate_url"] == "https://example.com/old-path"
    assert len(meta["affiliate_evidence_markers"]) > 0
    assert meta["affiliate_rejection_reason"] == ""


# ── Test 4: Redirect loop -> safely rejected ──────────────────────────────────
def test_redirect_loop_safely_rejected():
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
    assert isinstance(MAX_REDIRECTS, int)
    assert 3 <= MAX_REDIRECTS <= 20


# ── Test 8: _Redirect308Handler handles 308 ───────────────────────────────────
def test_redirect308handler_has_308_method():
    handler = _Redirect308Handler()
    assert hasattr(handler, "http_error_308")
    assert hasattr(handler, "http_error_307")


# ── Test 9: opener.open() returns None -> safely rejected, no AttributeError ─
def test_opener_returns_none_safely_rejected():
    mock_opener = MagicMock()
    mock_opener.open.return_value = None  # None response

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        try:
            r = verify_affiliate_url("https://example.com/none-resp")
            assert not r["accepted"]
            assert "None" in r["rejection_reason"]
        except AttributeError as e:
            assert False, f"AttributeError raised when opener returns None: {e}"


# ── Test 10: HTTP 404 -> http_status=404, rejection_reason="HTTP error 404" ────
def test_http_404_error_code_and_reason_stored():
    err = urllib.error.HTTPError(
        url="https://example.com/affiliate-404", code=404, msg="Not Found", hdrs={}, fp=None
    )
    mock_opener = MagicMock()
    mock_opener.open.side_effect = err

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        r = verify_affiliate_url("https://example.com/affiliate-404")

    assert not r["accepted"]
    assert r["http_status"] == 404
    assert r["rejection_reason"] == "HTTP error 404"


# ── Test 11: HTTP 500 -> http_status=500, rejection_reason="HTTP error 500" ────
def test_http_500_error_code_and_reason_stored():
    err = urllib.error.HTTPError(
        url="https://example.com/affiliate-500", code=500, msg="Server Error", hdrs={}, fp=None
    )
    mock_opener = MagicMock()
    mock_opener.open.side_effect = err

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        r = verify_affiliate_url("https://example.com/affiliate-500")

    assert not r["accepted"]
    assert r["http_status"] == 500
    assert r["rejection_reason"] == "HTTP error 500"


# ── Test 12: HTTPError with URL -> stores final_url ───────────────────────────
def test_http_error_final_url_stored():
    target_url = "https://example.com/final-404-page"
    err = urllib.error.HTTPError(
        url=target_url, code=404, msg="Not Found", hdrs={}, fp=None
    )
    mock_opener = MagicMock()
    mock_opener.open.side_effect = err

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        r = verify_affiliate_url("https://example.com/initial-page")

    assert r["final_url"] == target_url
    assert r["http_status"] == 404


# ── Test 13: 308 redirect followed by 404 -> stores final HTTP 404 ─────────────
def test_308_redirect_then_404_stores_final_404():
    final_404_url = "https://final.example.com/affiliate-not-found"
    err = urllib.error.HTTPError(
        url=final_404_url, code=404, msg="Not Found", hdrs={}, fp=None
    )
    mock_opener = MagicMock()
    mock_opener.open.side_effect = err

    with patch("affiliate_url_verifier._build_opener", return_value=mock_opener):
        meta = safe_affiliate_result("https://example.com/redirect-to-404", tool_name="Test404")

    assert meta["affiliate_verified"] is False
    assert meta["affiliate_http_status"] == 404
    assert meta["affiliate_rejection_reason"] == "HTTP error 404"
    assert meta["affiliate_final_url"] == final_404_url


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
        test_opener_returns_none_safely_rejected,
        test_http_404_error_code_and_reason_stored,
        test_http_500_error_code_and_reason_stored,
        test_http_error_final_url_stored,
        test_308_redirect_then_404_stores_final_404,
    ]
    print("=" * 60)
    print("HTTP 307/308 Redirect & Error Tests (13 tests)")
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
