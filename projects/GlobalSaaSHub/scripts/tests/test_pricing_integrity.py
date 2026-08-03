"""
tests/test_pricing_integrity.py
================================
Deterministic tests for pricing data integrity contract rules in validate_data.py.

Tests:
 1. pricing_verified=True, empty pricing_evidence_markers -> FAIL
 2. pricing_verified=True, empty string in pricing_evidence_markers -> FAIL
 3. pricing_verified=True, pricing string with no digits -> FAIL
 4. pricing_verified=True, currency is null/empty -> FAIL
 5. pricing_verified=True, billing_period is null/empty -> FAIL
 6. Valid pricing record -> PASS
"""

import sys, os, json, unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from validate_data import validate_tool_record

def _make_base_verified_tool():
    return {
        "id": "test-pricing-tool",
        "name": "Test Pricing Tool",
        "category": "automation",
        "category_display": "Workflow Automation",
        "description": "A valid test tool for pricing integrity test suite.",
        "official_url": "https://example.com/",
        "affiliate_url": None,
        "pricing": "Pro plan at $50/month",
        "pricing_source_url": "https://example.com/pricing",
        "pricing_verified": True,
        "pricing_verified_at": "2026-08-04T00:00:00Z",
        "pricing_source_http_status": 200,
        "pricing_source_final_url": "https://example.com/pricing",
        "pricing_evidence_markers": ["$50", "month"],
        "currency": "USD",
        "billing_period": "monthly",
        "evidence_source_type": "official_pricing_page",
        "key_features": ["Feature 1"],
        "rating": None,
        "logo_url": "https://www.google.com/s2/favicons?domain=example.com&sz=128",
        "primary_category": "automation",
        "comparison_group": "test_group",
        "is_manual_override": True,
        "http_verification_status": "verified_http_200",
        "affiliate_verified": False,
        "affiliate_source_url": None,
        "affiliate_final_url": None,
        "affiliate_http_status": None,
        "affiliate_evidence_markers": [],
        "affiliate_verified_at": None,
        "affiliate_rejection_reason": "No affiliate URL",
    }


def test_valid_pricing_record_passes():
    tool = _make_base_verified_tool()
    errors = validate_tool_record(tool, [tool])
    assert len(errors) == 0, f"Valid pricing tool should pass, got errors: {errors}"


def test_empty_evidence_markers_fails():
    tool = _make_base_verified_tool()
    tool["pricing_evidence_markers"] = []
    errors = validate_tool_record(tool, [tool])
    assert any("pricing_evidence_markers" in e for e in errors), f"Should fail on empty markers, got: {errors}"


def test_empty_string_in_markers_fails():
    tool = _make_base_verified_tool()
    tool["pricing_evidence_markers"] = ["$50", ""]
    errors = validate_tool_record(tool, [tool])
    assert any("pricing_evidence_markers" in e for e in errors), f"Should fail on empty string marker, got: {errors}"


def test_no_digits_in_pricing_string_fails():
    tool = _make_base_verified_tool()
    tool["pricing"] = "Free plan available; Pro starting at /user/month"
    errors = validate_tool_record(tool, [tool])
    assert any("contains no digits" in e for e in errors), f"Should fail on no digits in pricing, got: {errors}"


def test_null_currency_fails():
    tool = _make_base_verified_tool()
    tool["currency"] = None
    errors = validate_tool_record(tool, [tool])
    assert any("currency" in e for e in errors), f"Should fail on null currency, got: {errors}"


def test_null_billing_period_fails():
    tool = _make_base_verified_tool()
    tool["billing_period"] = None
    errors = validate_tool_record(tool, [tool])
    assert any("billing_period" in e for e in errors), f"Should fail on null billing_period, got: {errors}"


if __name__ == "__main__":
    tests = [
        test_valid_pricing_record_passes,
        test_empty_evidence_markers_fails,
        test_empty_string_in_markers_fails,
        test_no_digits_in_pricing_string_fails,
        test_null_currency_fails,
        test_null_billing_period_fails,
    ]
    print("=" * 60)
    print("Pricing Integrity Contract Tests (6 tests)")
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
    print(f"Result: {passed}/{passed+failed} passed")
    sys.exit(1 if failed else 0)
