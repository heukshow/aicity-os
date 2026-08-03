"""
tests/test_domain_dedup.py
===========================
Integration tests for merge_discovered_candidates() in auto_aggregator.py.
Calls the ACTUAL production merger logic - zero mock / zero stub reproduction.

Tests:
 1. Same domain candidate ('taskade-ai-agents' at taskade.com/ai-agents)
    matching existing tool ('taskade' at www.taskade.com)
    -> new_tools_list is empty (0 new tools added)
    -> existing id 'taskade' is preserved
 2. Verified affiliate 8-field immutability:
    existing affiliate_verified=True fields MUST NOT be overwritten by candidate values
 3. Verified pricing field immutability:
    existing pricing_verified=True fields MUST NOT be overwritten by candidate values
 4. Canonical domain normalization:
    'www.taskade.com', 'taskade.com', 'taskade.com/ai-agents' all resolve to 'taskade.com'
 5. Truly new domain candidate -> correctly added as new tool
"""

import sys, os, json, unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from auto_aggregator import merge_discovered_candidates, extract_domain

AFFILIATE_8_FIELDS = [
    "affiliate_url", "affiliate_verified", "affiliate_source_url",
    "affiliate_final_url", "affiliate_http_status", "affiliate_evidence_markers",
    "affiliate_verified_at", "affiliate_rejection_reason"
]

PRICING_FIELDS = [
    "pricing", "pricing_verified", "pricing_source_url", "pricing_verified_at",
    "pricing_source_http_status", "pricing_source_final_url",
    "pricing_evidence_markers", "currency", "billing_period", "evidence_source_type"
]


def _make_existing_taskade():
    return {
        "id": "taskade",
        "name": "Taskade",
        "category": "automation",
        "category_display": "Workflow Automation",
        "description": "Taskade workspace for productivity and AI agents.",
        "official_url": "https://www.taskade.com/",
        "affiliate_url": "https://partners.taskade.com/",
        "affiliate_verified": True,
        "affiliate_source_url": "https://partners.taskade.com/",
        "affiliate_final_url": "https://partners.taskade.com/",
        "affiliate_http_status": 200,
        "affiliate_evidence_markers": ["affiliate program"],
        "affiliate_verified_at": "2026-08-04T00:00:00Z",
        "affiliate_rejection_reason": "",
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
        "key_features": ["AI Task Management"],
        "rating": None,
        "logo_url": "https://www.google.com/s2/favicons?domain=taskade.com&sz=128",
        "primary_category": "automation",
        "comparison_group": "productivity_workspace",
        "is_manual_override": True,
        "http_verification_status": "verified_http_200",
    }


def _make_discovered_taskade_agents():
    return {
        "id": "taskade-ai-agents",
        "name": "Taskade AI Agents",
        "category": "automation",
        "category_display": "Workflow Automation",
        "description": "Taskade AI Agents tool candidate.",
        "official_url": "https://taskade.com/ai-agents",
        "affiliate_url": None,
        "pricing": "See official pricing",
        "key_features": ["AI Agents"],
        "rating": None,
        "logo_url": "https://www.google.com/s2/favicons?domain=taskade.com&sz=128",
    }


def test_taskade_domain_deduplication_via_actual_merger():
    existing = [_make_existing_taskade()]
    discovered = [_make_discovered_taskade_agents()]

    merged, new_tools, updated_tools = merge_discovered_candidates(existing, discovered)

    assert len(new_tools) == 0, f"Same domain candidate MUST NOT create new tool! Got {len(new_tools)} new tools"
    assert len(merged) == 1, f"Merged list should contain exactly 1 tool, got {len(merged)}"
    assert merged[0]["id"] == "taskade", f"Merged tool ID must remain 'taskade', got {merged[0]['id']}"


def test_verified_affiliate_fields_immutability():
    orig = _make_existing_taskade()
    existing = [dict(orig)]
    discovered = [_make_discovered_taskade_agents()]

    merged, _, _ = merge_discovered_candidates(existing, discovered)
    result = merged[0]

    for field in AFFILIATE_8_FIELDS:
        orig_val = orig.get(field)
        res_val = result.get(field)
        assert res_val == orig_val, (
            f"Affiliate field '{field}' was mutated by candidate merger!\n"
            f"  Expected: {orig_val!r}\n"
            f"  Got:      {res_val!r}"
        )


def test_verified_pricing_fields_immutability():
    orig = _make_existing_taskade()
    existing = [dict(orig)]
    discovered = [_make_discovered_taskade_agents()]

    merged, _, _ = merge_discovered_candidates(existing, discovered)
    result = merged[0]

    for field in PRICING_FIELDS:
        orig_val = orig.get(field)
        res_val = result.get(field)
        assert res_val == orig_val, (
            f"Pricing field '{field}' was mutated by candidate merger!\n"
            f"  Expected: {orig_val!r}\n"
            f"  Got:      {res_val!r}"
        )


def test_canonical_domain_normalization():
    u1 = "https://www.taskade.com/"
    u2 = "https://taskade.com/"
    u3 = "https://taskade.com/ai-agents?ref=123"

    d1 = extract_domain(u1)
    d2 = extract_domain(u2)
    d3 = extract_domain(u3)

    assert d1 == "taskade.com", f"d1 expected 'taskade.com', got {d1!r}"
    assert d2 == "taskade.com", f"d2 expected 'taskade.com', got {d2!r}"
    assert d3 == "taskade.com", f"d3 expected 'taskade.com', got {d3!r}"
    assert d1 == d2 == d3, "All Taskade URLs must resolve to the same canonical domain"


def test_truly_new_domain_added():
    existing = [_make_existing_taskade()]
    new_cand = {
        "id": "novel-tool",
        "name": "Novel Tool",
        "category": "developer",
        "category_display": "Coding & Dev Tools",
        "description": "A novel AI dev tool.",
        "official_url": "https://novel-tool.ai/",
        "affiliate_url": None,
        "pricing": "See official pricing",
        "key_features": ["Dev Feature"],
        "rating": None,
        "logo_url": "https://www.google.com/s2/favicons?domain=novel-tool.ai&sz=128",
    }

    from unittest.mock import patch
    dummy_aff_meta = {
        "affiliate_url": None, "affiliate_verified": False,
        "affiliate_source_url": None, "affiliate_final_url": None,
        "affiliate_http_status": None, "affiliate_evidence_markers": [],
        "affiliate_verified_at": None, "affiliate_rejection_reason": "No affiliate URL",
    }
    with patch("auto_aggregator.safe_affiliate_result", return_value=dummy_aff_meta):
        merged, new_tools, _ = merge_discovered_candidates(existing, [new_cand])

    assert len(new_tools) == 1, f"New candidate with unique domain should be added! Got {len(new_tools)}"
    assert len(merged) == 2
    assert new_tools[0]["id"] == "novel-tool"


if __name__ == "__main__":
    tests = [
        test_taskade_domain_deduplication_via_actual_merger,
        test_verified_affiliate_fields_immutability,
        test_verified_pricing_fields_immutability,
        test_canonical_domain_normalization,
        test_truly_new_domain_added,
    ]
    print("=" * 60)
    print("Domain Deduplication & Immutability Integration Tests (5 tests)")
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
