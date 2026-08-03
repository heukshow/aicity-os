"""
tests/test_manual_candidates_merge.py
======================================
Integration tests for merge_verified_manual_candidates() in auto_aggregator.py.

Tests:
 1. Existing 'krater', 'reditus', 'joiin' + verified manual candidates:
    -> 7 runtime pricing metadata fields fully updated on existing tools
 2. Unverified manual candidate:
    -> existing verified fields are NOT overwritten (immutability preserved)
 3. 142-tool base dataset + verified manual candidates (Taskade & Relevance AI):
    -> Taskade and Relevance AI correctly added as new tools
    -> Exactly 1 Taskade record (domain deduplicated)
    -> Total dataset tools becomes 144
"""

import sys, os, json, unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from auto_aggregator import merge_verified_manual_candidates

PRICING_7_METADATA_FIELDS = [
    "pricing_verified_at", "pricing_source_http_status", "pricing_source_final_url",
    "pricing_evidence_markers", "currency", "billing_period", "evidence_source_type"
]


def test_krater_reditus_joiin_pricing_metadata_migration():
    """Verify that existing krater/reditus/joiin records receive full pricing metadata updates."""
    existing_tools = [
        {"id": "krater", "name": "Krater", "official_url": "https://krater.ai/", "pricing": "Old pricing", "pricing_verified": False},
        {"id": "reditus", "name": "Reditus", "official_url": "https://www.getreditus.com/", "pricing": "Old pricing", "pricing_verified": False},
        {"id": "joiin", "name": "Joiin", "official_url": "https://www.joiin.co/", "pricing": "Old pricing", "pricing_verified": False},
    ]

    verified_candidates = [
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
        },
    ]

    merged, updated_cnt, added_cnt = merge_verified_manual_candidates(existing_tools, verified_candidates)

    assert updated_cnt == 3, f"Expected 3 updated records, got {updated_cnt}"
    assert added_cnt == 0, f"Expected 0 added records, got {added_cnt}"

    tool_dict = {t["id"]: t for t in merged}
    for tid in ["krater", "reditus", "joiin"]:
        tool = tool_dict[tid]
        assert tool["pricing_verified"] is True
        for field in PRICING_7_METADATA_FIELDS:
            assert tool.get(field) is not None, f"Tool '{tid}' missing field '{field}' after migration!"


def test_unverified_manual_candidate_does_not_overwrite_verified_data():
    """Verify that unverified candidates do NOT clear existing verified data."""
    existing_tools = [
        {
            "id": "krater",
            "name": "Krater",
            "official_url": "https://krater.ai/",
            "pricing": "Verified $200/year",
            "pricing_verified": True,
            "pricing_verified_at": "2026-08-04T00:00:00Z",
            "pricing_source_http_status": 200,
            "pricing_source_final_url": "https://krater.ai/pricing",
            "pricing_evidence_markers": ["$200", "year"],
            "currency": "USD",
            "billing_period": "annual",
            "evidence_source_type": "official_pricing_page",
        }
    ]

    unverified_candidate = [
        {
            "id": "krater",
            "name": "Krater",
            "official_url": "https://krater.ai/",
            "pricing": "See official pricing",
            "pricing_verified": False,
        }
    ]

    merged, _, _ = merge_verified_manual_candidates(existing_tools, unverified_candidate)
    krater = merged[0]
    assert krater["pricing_verified"] is True
    assert krater["pricing"] == "Verified $200/year"


def test_taskade_and_relevance_added_to_base_dataset():
    """Verify merging Taskade and Relevance AI into a 142-base dataset adds both tools."""
    base_142 = [{"id": f"tool-{i}", "name": f"Tool {i}", "official_url": f"https://tool-{i}.com/"} for i in range(142)]

    manual_fixtures = [
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
        },
    ]

    merged, updated_cnt, added_cnt = merge_verified_manual_candidates(base_142, manual_fixtures)

    assert added_cnt == 2, f"Expected 2 added tools, got {added_cnt}"
    assert len(merged) == 144, f"Expected total 144 tools, got {len(merged)}"

    taskade_records = [t for t in merged if t["id"] == "taskade"]
    assert len(taskade_records) == 1, "Exactly 1 Taskade record must exist"


if __name__ == "__main__":
    tests = [
        test_krater_reditus_joiin_pricing_metadata_migration,
        test_unverified_manual_candidate_does_not_overwrite_verified_data,
        test_taskade_and_relevance_added_to_base_dataset,
    ]
    print("=" * 60)
    print("Manual Candidate Merge Integration Tests (3 tests)")
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
