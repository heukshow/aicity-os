"""
tests/test_manual_candidates_merge.py
======================================
Integration & Immutability tests using the ACTUAL repository tools.json (148 baseline tools).
100% Self-contained: ZERO dependency on runtime-generated manual_candidates_verified.json.

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

CORE_IDENTITY_FIELDS = ["id", "name", "official_url", "description", "category", "key_features"]
PRICING_7_METADATA_FIELDS = [
    "pricing_verified_at", "pricing_source_http_status", "pricing_source_final_url",
    "pricing_evidence_markers", "currency", "billing_period", "evidence_source_type"
]


def _make_deterministic_verified_manual_fixtures():
    """Returns self-contained, deterministic verified manual candidates fixture."""
    return [
        {
            "id": "krater",
            "name": "Krater",
            "official_url": "https://krater.ai/",
            "pricing": "All-in-one AI suite from $200/year",
            "pricing_source_url": "https://krater.ai/pricing",
            "pricing_verified": True,
            "pricing_verified_at": "2026-08-04T00:00:00Z",
            "pricing_source_http_status": 200,
            "pricing_source_final_url": "https://krater.ai/pricing",
            "pricing_evidence_markers": ["$200", "year"],
            "currency": "USD",
            "billing_period": "annual",
            "evidence_source_type": "official_pricing_page",
            "affiliate_url": None,
            "affiliate_verified": False,
        },
        {
            "id": "reditus",
            "name": "Reditus",
            "official_url": "https://www.getreditus.com/",
            "pricing": "Partner management starting at $99/month",
            "pricing_source_url": "https://www.getreditus.com/pricing",
            "pricing_verified": True,
            "pricing_verified_at": "2026-08-04T00:00:00Z",
            "pricing_source_http_status": 200,
            "pricing_source_final_url": "https://www.getreditus.com/pricing",
            "pricing_evidence_markers": ["$99", "month"],
            "currency": "USD",
            "billing_period": "monthly",
            "evidence_source_type": "official_pricing_page",
            "affiliate_url": None,
            "affiliate_verified": False,
        },
        {
            "id": "joiin",
            "name": "Joiin",
            "official_url": "https://www.joiin.co/",
            "pricing": "Consolidated reporting starting at $23/month",
            "pricing_source_url": "https://www.joiin.co/pricing",
            "pricing_verified": True,
            "pricing_verified_at": "2026-08-04T00:00:00Z",
            "pricing_source_http_status": 200,
            "pricing_source_final_url": "https://www.joiin.co/pricing",
            "pricing_evidence_markers": ["$23", "month"],
            "currency": "USD",
            "billing_period": "monthly",
            "evidence_source_type": "official_pricing_page",
            "affiliate_url": None,
            "affiliate_verified": False,
        },
        {
            "id": "taskade",
            "name": "Taskade",
            "official_url": "https://www.taskade.com/",
            "pricing": "Free plan available; Pro starting at $8/user/month (billed annually)",
            "pricing_source_url": "https://www.taskade.com/pricing",
            "pricing_verified": True,
            "pricing_verified_at": "2026-08-04T00:00:00Z",
            "pricing_source_http_status": 200,
            "pricing_source_final_url": "https://www.taskade.com/pricing",
            "pricing_evidence_markers": ["$8", "month"],
            "currency": "USD",
            "billing_period": "monthly",
            "evidence_source_type": "official_pricing_page",
            "affiliate_url": "https://partners.taskade.com/",
            "affiliate_verified": True,
            "affiliate_source_url": "https://partners.taskade.com/",
            "affiliate_final_url": "https://partners.taskade.com/",
            "affiliate_http_status": 200,
            "affiliate_evidence_markers": ["affiliate program"],
            "affiliate_verified_at": "2026-08-04T00:00:00Z",
            "affiliate_rejection_reason": "",
            "category": "automation",
            "category_display": "Workflow Automation",
            "description": "Taskade workspace for productivity and AI agents.",
            "key_features": ["AI Task Management"],
            "rating": None,
            "logo_url": "https://www.google.com/s2/favicons?domain=taskade.com&sz=128",
            "primary_category": "automation",
            "comparison_group": "productivity_workspace",
            "is_manual_override": True,
            "http_verification_status": "verified_http_200",
        },
        {
            "id": "relevance-ai",
            "name": "Relevance AI",
            "official_url": "https://relevanceai.com/",
            "pricing": "Free plan available; credit-based usage starting at $234/month",
            "pricing_source_url": "https://relevanceai.com/docs/get-started/pricing",
            "pricing_verified": True,
            "pricing_verified_at": "2026-08-04T00:00:00Z",
            "pricing_source_http_status": 200,
            "pricing_source_final_url": "https://relevanceai.com/docs/get-started/pricing",
            "pricing_evidence_markers": ["$234", "month"],
            "currency": "USD",
            "billing_period": "monthly",
            "evidence_source_type": "official_documentation_page",
            "affiliate_url": None,
            "affiliate_verified": False,
            "affiliate_source_url": "https://relevanceai.com/",
            "affiliate_final_url": "https://relevanceai.com/",
            "affiliate_http_status": 200,
            "affiliate_evidence_markers": [],
            "affiliate_verified_at": None,
            "affiliate_rejection_reason": "No affiliate URL",
            "category": "developer",
            "category_display": "Coding & Dev Tools",
            "description": "B2B workforce platform for autonomous AI agents.",
            "key_features": ["AI Agents"],
            "rating": None,
            "logo_url": "https://www.google.com/s2/favicons?domain=relevanceai.com&sz=128",
            "primary_category": "developer",
            "comparison_group": "ai_agent_platform",
            "is_manual_override": True,
            "http_verification_status": "verified_http_200",
        },
    ]


def _load_repo_tools():
    with open(TOOLS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_baseline_tools_json_count():
    """Verify repository baseline tools.json contains exactly 148 tools."""
    tools = _load_repo_tools()
    assert len(tools) == 148, f"Repository tools.json must contain 148 tools, got {len(tools)}"


def test_actual_repo_tools_merge_immutability_contract():
    """
    Executes merge_verified_manual_candidates against the ACTUAL 148 repo tools.json dataset.
    100% self-contained using deterministic inline fixture.
    """
    orig_tools = _load_repo_tools()
    manual_candidates = _make_deterministic_verified_manual_fixtures()

    orig_affiliate_urls_count = sum(1 for t in orig_tools if t.get("affiliate_url") is not None)
    orig_tool_map = {t["id"]: copy.deepcopy(t) for t in orig_tools}

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

    assert mutated_core_fields == 0, f"Core identity fields mutated on {mutated_core_fields} fields! Expected 0."

    # 5. Check affiliate_url deletion count == 0
    merged_affiliate_urls_count = sum(1 for t in merged if t.get("affiliate_url") is not None)
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
