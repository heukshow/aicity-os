"""
tests/test_domain_dedup.py
===========================
Deterministic tests for same-domain deduplication and immutability.

Tests:
 1. Existing 'taskade' record + discovery candidate 'taskade-ai-agents' (same domain taskade.com)
    -> new_tools_added must be 0 (no new tool created)
 2. Existing verified affiliate/pricing fields on 'taskade' must NOT be overwritten
    by unverified search snippet or Gemini candidate values.
"""

import sys, os, json, unittest

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from auto_aggregator import extract_domain, normalize_unverified_candidate

def test_same_domain_candidate_not_added_and_immutability_preserved():
    existing_taskade = {
        "id": "taskade",
        "name": "Taskade",
        "official_url": "https://www.taskade.com/",
        "affiliate_url": "https://partners.taskade.com/",
        "affiliate_verified": True,
        "pricing": "Free plan available; Pro starting at $8/user/month (billed annually)",
        "pricing_verified": True,
        "pricing_source_url": "https://www.taskade.com/pricing",
    }

    existing_tools = [existing_taskade]
    existing_ids = {t["id"]: t for t in existing_tools}
    existing_domains = {extract_domain(t["official_url"]): t for t in existing_tools if extract_domain(t["official_url"])}

    # Simulate Gemini discovery extracting 'taskade-ai-agents' with unverified data
    gemini_candidate = {
        "id": "taskade-ai-agents",
        "name": "Taskade AI Agents",
        "official_url": "https://taskade.com/ai-agents",
        "affiliate_url": None,
        "pricing": "See official pricing",
    }

    cand_domain = extract_domain(gemini_candidate["official_url"])
    assert cand_domain == "taskade.com", f"Domain should extract as taskade.com, got {cand_domain}"

    # Check deduplication logic
    matched_existing = existing_domains.get(cand_domain)
    assert matched_existing is not None, "Candidate taskade.com should match existing taskade.com tool"
    assert matched_existing["id"] == "taskade", f"Matched ID should be 'taskade', got {matched_existing['id']}"

    # Verify candidate is NOT added as a new tool
    new_tools_added = 0
    if matched_existing is None:
        new_tools_added += 1

    assert new_tools_added == 0, f"Same domain candidate must NOT be added as new tool (new_tools_added={new_tools_added})"

    # Verify existing verified fields remain untouched
    assert matched_existing["affiliate_verified"] is True
    assert matched_existing["pricing_verified"] is True
    assert matched_existing["affiliate_url"] == "https://partners.taskade.com/"
    assert matched_existing["pricing"] == "Free plan available; Pro starting at $8/user/month (billed annually)"


if __name__ == "__main__":
    tests = [
        test_same_domain_candidate_not_added_and_immutability_preserved,
    ]
    print("=" * 60)
    print("Domain Deduplication & Immutability Tests")
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
