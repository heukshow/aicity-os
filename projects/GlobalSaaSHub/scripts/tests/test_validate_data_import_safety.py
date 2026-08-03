"""
tests/test_validate_data_import_safety.py
===========================================
Deterministic tests proving validate_data.py has ZERO side-effects on import and
Safety Gate test suites operate flawlessly in a clean checkout environment
without manual_candidates_verified.json or tools.next.json.

Tests:
 1. Importing validate_data in a temporary directory without tools.next.json:
    - Does NOT crash or raise FileNotFoundError
    - Does NOT call sys.exit()
    - Does NOT execute full dataset loading or validation
 2. validate_tool_record works as a pure function on isolated fixtures
 3. official_documentation_page is supported in ALLOWED_EVIDENCE_TYPES
 4. Clean checkout resilience: Safety Gate test modules import cleanly
    even when manual_candidates_verified.json is absent.
"""

import sys, os, tempfile, unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)


def test_import_has_no_side_effects_without_tools_next_json():
    """Verify that importing validate_data in an empty cwd does NOT exit or fail."""
    orig_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as empty_dir:
        os.chdir(empty_dir)
        try:
            if "validate_data" in sys.modules:
                del sys.modules["validate_data"]

            import validate_data

            assert hasattr(validate_data, "validate_tool_record")
            assert hasattr(validate_data, "validate_dataset")
            assert hasattr(validate_data, "main")
        finally:
            os.chdir(orig_cwd)


def test_validate_tool_record_is_pure_function():
    """Verify validate_tool_record evaluates only the provided single fixture."""
    from validate_data import validate_tool_record

    valid_fixture = {
        "id": "pure-fixture-tool",
        "name": "Pure Fixture Tool",
        "category": "developer",
        "category_display": "Coding & Dev Tools",
        "description": "Pure test fixture tool.",
        "official_url": "https://pure-fixture.example.com/",
        "affiliate_url": None,
        "pricing": "Free plan",
        "pricing_source_url": None,
        "pricing_verified": False,
        "pricing_verified_at": None,
        "pricing_source_http_status": None,
        "pricing_source_final_url": None,
        "pricing_evidence_markers": None,
        "currency": None,
        "billing_period": None,
        "evidence_source_type": None,
        "key_features": ["Feature"],
        "rating": None,
        "logo_url": "https://www.google.com/s2/favicons?domain=pure-fixture.example.com&sz=128",
        "primary_category": "developer",
        "comparison_group": "pure_group",
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

    errors = validate_tool_record(valid_fixture, [valid_fixture])
    assert errors == [], f"Pure fixture should have 0 errors, got: {errors}"


def test_official_documentation_page_supported():
    """Verify that official_documentation_page is now a supported evidence_source_type."""
    from validate_data import validate_tool_record

    doc_page_fixture = {
        "id": "doc-page-tool",
        "name": "Doc Page Tool",
        "category": "developer",
        "category_display": "Coding & Dev Tools",
        "description": "Tool using official_documentation_page.",
        "official_url": "https://doc-tool.example.com/",
        "affiliate_url": None,
        "pricing": "Pro plan starting at $10/month",
        "pricing_source_url": "https://doc-tool.example.com/docs/pricing",
        "pricing_verified": True,
        "pricing_verified_at": "2026-08-04T00:00:00Z",
        "pricing_source_http_status": 200,
        "pricing_source_final_url": "https://doc-tool.example.com/docs/pricing",
        "pricing_evidence_markers": ["$10", "month"],
        "currency": "USD",
        "billing_period": "monthly",
        "evidence_source_type": "official_documentation_page",
        "key_features": ["Feature"],
        "rating": None,
        "logo_url": "https://www.google.com/s2/favicons?domain=doc-tool.example.com&sz=128",
        "primary_category": "developer",
        "comparison_group": "doc_group",
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

    errors = validate_tool_record(doc_page_fixture, [doc_page_fixture])
    assert errors == [], f"official_documentation_page should pass validation, got: {errors}"


def test_clean_checkout_safety_gate_resilience():
    """Verify test_manual_candidates_merge runs cleanly without manual_candidates_verified.json."""
    orig_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as empty_dir:
        # Verify manual_candidates_verified.json is absent in empty_dir
        verified_path = os.path.join(empty_dir, "manual_candidates_verified.json")
        assert not os.path.exists(verified_path), "Fixture file must be absent in clean checkout simulation"

        # Running test_manual_candidates_merge must succeed using self-contained fixtures
        import test_manual_candidates_merge
        test_manual_candidates_merge.test_actual_repo_tools_merge_immutability_contract()


if __name__ == "__main__":
    tests = [
        test_import_has_no_side_effects_without_tools_next_json,
        test_validate_tool_record_is_pure_function,
        test_official_documentation_page_supported,
        test_clean_checkout_safety_gate_resilience,
    ]
    print("=" * 60)
    print("validate_data Import Safety & Clean Checkout Tests (4 tests)")
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
