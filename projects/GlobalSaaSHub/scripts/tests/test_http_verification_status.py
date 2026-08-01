"""
tests/test_http_verification_status.py
=======================================
Verifies the http_verification_status enum contract between
verify_manual_candidates.py and validate_data.py via the shared
http_verification_status module.

Run from the project root:
    python -m pytest scripts/tests/ -v
or:
    python scripts/tests/test_http_verification_status.py
"""
import sys
import os

# Allow importing sibling scripts/ modules when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http_verification_status import (
    ALLOWED_HTTP_STATUSES,
    HTTP_VERIFIED_200,
    HTTP_REDIRECT_VERIFIED,
    HTTP_BOT_BLOCKED,
    HTTP_RATE_LIMITED,
    HTTP_ERROR,
    HTTP_NETWORK_ERROR,
    http_code_to_status,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assert_mapping(http_code, expected_constant, is_redirect=False, label=""):
    actual = http_code_to_status(http_code, is_redirect=is_redirect)
    assert actual == expected_constant, (
        f"FAIL [{label}] http_code={http_code} is_redirect={is_redirect}: "
        f"expected {expected_constant!r}, got {actual!r}"
    )

def assert_in_allowed(value, label=""):
    assert value in ALLOWED_HTTP_STATUSES, (
        f"FAIL [{label}] value={value!r} not in ALLOWED_HTTP_STATUSES"
    )

def assert_not_in_allowed(value, label=""):
    assert value not in ALLOWED_HTTP_STATUSES, (
        f"FAIL [{label}] value={value!r} unexpectedly found in ALLOWED_HTTP_STATUSES"
    )


# ---------------------------------------------------------------------------
# Test 1: HTTP 200 -> verified_http_200
# ---------------------------------------------------------------------------
def test_200_maps_to_verified_http_200():
    assert_mapping(200, HTTP_VERIFIED_200, label="200->verified_http_200")
    assert_in_allowed(HTTP_VERIFIED_200, label="verified_http_200 in allowed set")


# ---------------------------------------------------------------------------
# Test 2: HTTP 403 -> bot_blocked
# ---------------------------------------------------------------------------
def test_403_maps_to_bot_blocked():
    assert_mapping(403, HTTP_BOT_BLOCKED, label="403->bot_blocked")
    assert_in_allowed(HTTP_BOT_BLOCKED, label="bot_blocked in allowed set")


# ---------------------------------------------------------------------------
# Test 3: HTTP 429 -> rate_limited
# ---------------------------------------------------------------------------
def test_429_maps_to_rate_limited():
    assert_mapping(429, HTTP_RATE_LIMITED, label="429->rate_limited")
    assert_in_allowed(HTTP_RATE_LIMITED, label="rate_limited in allowed set")


# ---------------------------------------------------------------------------
# Test 4: HTTP 500 -> http_error
# ---------------------------------------------------------------------------
def test_500_maps_to_http_error():
    assert_mapping(500, HTTP_ERROR, label="500->http_error")
    assert_in_allowed(HTTP_ERROR, label="http_error in allowed set")


# ---------------------------------------------------------------------------
# Test 5: timeout/network failure -> network_error
# ---------------------------------------------------------------------------
def test_network_failure_maps_to_network_error():
    actual = http_code_to_status(None)
    assert actual == HTTP_NETWORK_ERROR, (
        f"FAIL: None code should return {HTTP_NETWORK_ERROR!r}, got {actual!r}"
    )
    assert_in_allowed(HTTP_NETWORK_ERROR, label="network_error in allowed set")


# ---------------------------------------------------------------------------
# Test 6: redirect -> redirect_verified
# ---------------------------------------------------------------------------
def test_redirect_maps_to_redirect_verified():
    assert_mapping(200, HTTP_REDIRECT_VERIFIED, is_redirect=True, label="redirect->redirect_verified")
    assert_in_allowed(HTTP_REDIRECT_VERIFIED, label="redirect_verified in allowed set")


# ---------------------------------------------------------------------------
# Test 7: None (unverified) passes validator
# ---------------------------------------------------------------------------
def test_none_passes_validator():
    assert_in_allowed(None, label="None passes validator")


# ---------------------------------------------------------------------------
# Test 8: Arbitrary string http_418 fails validator
# ---------------------------------------------------------------------------
def test_arbitrary_http_418_fails_validator():
    assert_not_in_allowed("http_418", label="http_418 must fail validator")


# ---------------------------------------------------------------------------
# Standalone runner (no pytest required)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tests = [
        test_200_maps_to_verified_http_200,
        test_403_maps_to_bot_blocked,
        test_429_maps_to_rate_limited,
        test_500_maps_to_http_error,
        test_network_failure_maps_to_network_error,
        test_redirect_maps_to_redirect_verified,
        test_none_passes_validator,
        test_arbitrary_http_418_fails_validator,
    ]

    print("=" * 60)
    print("http_verification_status Enum Contract Tests")
    print("=" * 60)
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
    print("=" * 60)
    total = passed + failed
    print(f"Result: {passed}/{total} passed")
    if failed:
        print("SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)
