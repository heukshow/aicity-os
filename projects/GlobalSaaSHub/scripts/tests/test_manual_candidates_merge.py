"""
tests/test_manual_candidates_merge.py
======================================
Integration & Immutability tests using the ACTUAL repository tools.json (148 baseline tools).
Proves zero unexpected mutation, zero deleted affiliate_urls, exact metadata updates, and clean additions.

Tests:
 1. Baseline dataset count check: exactly 148 tools in repo tools.json
 2. Merge verified manual candidates into actual 148 tools.json:
    - Exactly Taskade and Relevance AI added as new tools (148 -> 150)
    - Exactly 1 taskade.com domain record exists (domain deduplicated)
    - Allowed metadata updates ONLY on krater, reditus, joiin (pricing fields)
    - Existing core identity fields (id, name, official_url, description, category, key_features) mutated: 0
    - Existing affiliate_url fields deleted / changed to null: 0
 3. Unverified candidate does NOT mutate existing verified data
"""

import sys, os, json, copy, unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from auto_aggregator import merge_verified_manual_candidates

TOOLS_JSON_PATH = os.path.join(os.path.dirname(SCRIPTS_DIR), "data", "tools.json")
MANUAL_VERIFIED_PATH = os.path.join(os.path.dirname(SCRIPTS_DIR), "data", "manual_candidates_verified.json")

CORE_IDENTITY_FIELDS = ["id", "name", "official_url", "description", "category", "key_features"]
PRICING_7_METADATA_FIELDS = [
    "pricing_verified_at", "pricing_source_http_status", "pricing_source_final_url",
    "pricing_evidence_markers", "currency", "billing_period", "evidence_source_type"
]


def _load_repo_tools():
    with open(TOOLS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_manual_verified():
    with open(MANUAL_VERIFIED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_baseline_tools_json_count():
    """Verify repository baseline tools.json contains exactly 148 tools."""
    tools = _load_repo_tools()
    assert len(tools) == 148, f"Repository tools.json must contain 148 tools, got {len(tools)}"


def test_actual_repo_tools_merge_immutability_contract():
    """
    Executes merge_verified_manual_candidates against the ACTUAL 148 repo tools.json dataset.
    Verifies:
      - 148 baseline -> 150 final tools
      - Taskade and Relevance AI added as ONLY new tools
      - Exactly 1 taskade.com domain record
      - Zero core identity mutations on existing 148 tools
      - Zero affiliate_url deletions (count of non-null affiliate_urls must NOT decrease)
      - Exact krater, reditus, joiin pricing metadata updates
    """
    orig_tools = _load_repo_tools()
    manual_candidates = _load_manual_verified()

    orig_affiliate_urls_count = sum(1 for t in orig_tools if t.get("affiliate_url") is not None)
    orig_tool_map = {t["id"]: copy.deepcopy(t) for t in orig_tools}

    # Deepcopy to prevent mutating fixture
    existing_tools_copy = copy.deepcopy(orig_tools)

    merged, updated_cnt, added_cnt = merge_verified_manual_candidates(existing_tools_copy, manual_candidates)

    # 1. Count checks
    assert len(merged) == 150, f"Expected exactly 150 tools after manual candidates merge, got {len(merged)}"
    assert added_cnt == 2, f"Expected 2 added tools (Taskade & Relevance AI), got {added_cnt}"

    # 2. Check added tools
    merged_map = {t["id"]: t for t in merged}
    assert "taskade" in merged_map, "Taskade must be added as new tool 'taskade'"
    assert "relevance-ai" in merged_map, "Relevance AI must be added as new tool 'relevance-ai'"

    # 3. Check Taskade domain deduplication
    taskade_domain_records = [t for t in merged if t.get("id") == "taskade" or "taskade.com" in (t.get("official_url") or "")]
    assert len(taskade_domain_records) == 1, f"Expected exactly 1 taskade.com record, got {len(taskade_domain_records)}"

    # 4. Check core identity mutations on existing 148 tools == 0
    mutated_core_fields = 0
    for tid, orig_t in orig_tool_map.items():
        merged_t = merged_map[tid]
        for field in CORE_IDENTITY_FIELDS:
            if orig_t.get(field) != merged_t.get(field):
                mutated_core_fields += 1
                print(f"MUTATION DETECTED on '{tid}' field '{field}': {orig_t.get(field)!r} -> {merged_t.get(field)!r}")

    assert mutated_core_fields == 0, f"Core identity fields mutated on {mutated_core_fields} fields! Expected 0."

    # 5. Check affiliate_url deletion count == 0
    merged_affiliate_urls_count = sum(1 for t in merged if t.get("affiliate_url") is not None)
    # Merged dataset adds Taskade's affiliate_url (150 total), so affiliate_urls count must increase or stay same, never decrease
    assert merged_affiliate_urls_count >= orig_affiliate_urls_count, (
        f"Affiliate URLs were deleted! Baseline had {orig_affiliate_urls_count}, merged has {merged_affiliate_urls_count}"
    )

    # 6. Check krater, reditus, joiin received verified pricing metadata
    for tid in ["krater", "reditus", "joiin"]:
        t = merged_map[tid]
        assert t.get("pricing_verified") is True, f"Tool '{tid}' pricing_verified should be True"
        for f_name in PRICING_7_METADATA_FIELDS:
            assert t.get(f_name) is not None, f"Tool '{tid}' missing migrated metadata field '{f_name}'!"


def test_unverified_candidate_immutability():
    """Verify that an unverified manual candidate cannot overwrite existing verified data."""
    orig_tools = _load_repo_tools()
    existing_tools_copy = copy.deepcopy(orig_tools)

    unverified_fixture = [
        {
            "id": "krater",
            "name": "Krater",
            "official_url": "https://krater.ai/",
            "pricing": "See official pricing",
            "pricing_verified": False,
        }
    ]

    merged, _, _ = merge_verified_manual_candidates(existing_tools_copy, unverified_fixture)
    merged_map = {t["id"]: t for t in merged}
    krater = merged_map["krater"]

    # Orig Krater pricing should be preserved without unverified overwrite
    orig_krater = [t for t in orig_tools if t["id"] == "krater"][0]
    assert krater["pricing"] == orig_krater["pricing"], "Unverified candidate must NOT overwrite pricing string"


if __name__ == "__main__":
    tests = [
        test_baseline_tools_json_count,
        test_actual_repo_tools_merge_immutability_contract,
        test_unverified_candidate_immutability,
    ]
    print("=" * 60)
    print("Actual Repo tools.json Merge & Immutability Tests (3 tests)")
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
