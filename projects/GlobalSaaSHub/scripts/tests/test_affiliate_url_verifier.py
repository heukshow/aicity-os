"""
tests/test_affiliate_url_verifier.py
=====================================
Official repository tests for affiliate_url_verifier.py.

Tests verify:
1. Valid affiliate URL (contains evidence markers) -> ACCEPTED
2. Generic /partners path -> REJECTED (path-based rule, no HTTP call needed)
3. Invalid/empty URL -> REJECTED
4. Evidence markers detection logic
5. safe_affiliate_url() wrapper returns None for rejected URLs

Run from project root:
    python scripts/tests/test_affiliate_url_verifier.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from affiliate_url_verifier import (
    _is_generic_partner_path,
    verify_affiliate_url,
    safe_affiliate_url,
    AFFILIATE_EVIDENCE_MARKERS,
    GENERIC_PARTNER_PATH_SUFFIXES,
)


def test_generic_partner_path_rejected_without_http_call():
    # /partners suffix should be caught before HTTP call
    assert _is_generic_partner_path("https://www.d-id.com/partners") is True
    assert _is_generic_partner_path("https://example.com/contact") is True
    assert _is_generic_partner_path("https://example.com/enterprise") is True
    assert _is_generic_partner_path("https://example.com/resellers") is True
    # Affiliate path should NOT be caught by path filter
    assert _is_generic_partner_path("https://example.com/affiliate") is False
    assert _is_generic_partner_path("https://example.com/referral") is False
    assert _is_generic_partner_path("https://partners.taskade.com") is False  # subdomain, not path


def test_invalid_urls_rejected():
    for bad_url in [None, "", "not-a-url", "ftp://example.com"]:
        r = verify_affiliate_url(bad_url)
        assert not r["accepted"], f"Expected rejection for {bad_url!r}"
        assert r["rejection_reason"], f"Expected rejection reason for {bad_url!r}"


def test_d_id_partners_rejected_by_path_rule():
    r = verify_affiliate_url("https://www.d-id.com/partners")
    assert not r["accepted"]
    assert "generic partner pattern" in r["rejection_reason"]
    assert r["http_status"] is None  # Should not have made HTTP call


def test_evidence_markers_are_populated():
    # AFFILIATE_EVIDENCE_MARKERS must include these critical terms
    for required in ["affiliate", "referral", "commission", "payout"]:
        assert required in AFFILIATE_EVIDENCE_MARKERS, f"Missing required marker: {required}"


def test_safe_affiliate_url_returns_none_for_generic_path():
    result = safe_affiliate_url("https://www.d-id.com/partners", tool_name="D-ID")
    assert result is None, "safe_affiliate_url should return None for generic partner path"


def test_safe_affiliate_url_returns_none_for_empty():
    assert safe_affiliate_url(None) is None
    assert safe_affiliate_url("") is None


if __name__ == "__main__":
    tests = [
        test_generic_partner_path_rejected_without_http_call,
        test_invalid_urls_rejected,
        test_d_id_partners_rejected_by_path_rule,
        test_evidence_markers_are_populated,
        test_safe_affiliate_url_returns_none_for_generic_path,
        test_safe_affiliate_url_returns_none_for_empty,
    ]
    print("=" * 60)
    print("affiliate_url_verifier Contract Tests")
    print("=" * 60)
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS  " + t.__name__)
            passed += 1
        except AssertionError as e:
            print("FAIL  " + t.__name__ + ": " + str(e))
            failed += 1
    print("=" * 60)
    print("Result: " + str(passed) + "/" + str(passed + failed) + " passed")
    if failed:
        print("SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)
