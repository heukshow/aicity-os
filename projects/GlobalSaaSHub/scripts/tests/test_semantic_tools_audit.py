import copy
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "semantic_tools_audit.py"
SPEC = importlib.util.spec_from_file_location("semantic_tools_audit", SCRIPT)
audit = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(audit)


def tool(tool_id="one"):
    return {"id": tool_id, "name": "One", "url": "https://one.example", "category": "AI", "description": "Description", "pricing": {"amount": 10, "currency": "USD"}, "affiliate_url": "https://one.example/ref", "affiliate_verified": True, "rating": 4.5, "status": "active", "pricing_verified_at": "2026-08-03T00:00:00Z"}


def result(before, after, before_raw=None, after_raw=None): return audit.audit_datasets(before, after, before_raw, after_raw)


def test_pricing_verified_at_five_changes_pass():
    before = [tool(str(i)) for i in range(5)]; after = copy.deepcopy(before)
    for item in after: item["pricing_verified_at"] = "2026-08-04T00:00:00Z"
    manifest = result(before, after)
    assert manifest["status"] == "PASS" and manifest["volatile_only_diff_count"] == 5 and manifest["forbidden_diff_count"] == 0


def test_affiliate_url_change_fails():
    before = [tool()]; after = copy.deepcopy(before); after[0]["affiliate_url"] = "https://evil.example/ref"
    assert result(before, after)["status"] == "FAIL"


def test_tool_deleted_fails(): assert result([tool("one"), tool("two")], [tool("one")])["status"] == "FAIL"
def test_tool_added_fails(): assert result([tool("one")], [tool("one"), tool("two")])["status"] == "FAIL"


def test_duplicate_id_fails():
    try: result([tool()], [tool(), tool()]); assert False
    except audit.AuditError: pass


def test_key_order_change_passes():
    before = [tool()]; after = [dict(reversed(list(before[0].items())))]
    assert result(before, after)["status"] == "PASS"


def test_tool_order_change_passes():
    before = [tool("one"), tool("two")]
    assert result(before, list(reversed(copy.deepcopy(before))))["status"] == "PASS"


def test_type_change_fails():
    before = [tool()]; after = copy.deepcopy(before); after[0]["rating"] = "4.5"
    assert result(before, after)["status"] == "FAIL"


def test_unlisted_timestamp_like_field_change_fails():
    before = [tool()]; before[0]["reviewed_timestamp"] = "2026-08-03T00:00:00Z"; after = copy.deepcopy(before); after[0]["reviewed_timestamp"] = "2026-08-04T00:00:00Z"
    assert result(before, after)["status"] == "FAIL"


def test_raw_sha_diff_semantic_sha_same_passes():
    before = [tool()]; after = copy.deepcopy(before); after[0]["pricing_verified_at"] = "2026-08-04T00:00:00Z"
    manifest = result(before, after, b"raw-before", b"raw-after")
    assert manifest["raw_sha256_before"] != manifest["raw_sha256_after"] and manifest["semantic_sha256_before"] == manifest["semantic_sha256_after"] and manifest["status"] == "PASS"


def test_manifest_round_trip_validation():
    expected = result([tool()], [tool()]); audit.validate_manifest(expected, copy.deepcopy(expected)); tampered = copy.deepcopy(expected); tampered["forbidden_diff_count"] = 1
    try: audit.validate_manifest(expected, tampered); assert False
    except audit.AuditError: pass


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]; passed = 0
    for case in tests:
        try: case(); print(f"PASS  {case.__name__}"); passed += 1
        except Exception as exc: print(f"FAIL  {case.__name__}: {type(exc).__name__}: {exc}")
    print(f"Result: {passed}/{len(tests)} passed"); raise SystemExit(0 if passed == len(tests) else 1)
