"""Deterministic regression coverage for unverified discovery pricing."""

import copy
import os
import sys
from unittest.mock import patch

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from auto_aggregator import merge_discovered_candidates
from validate_data import validate_dataset


PRICING_EVIDENCE_FIELDS = (
    "pricing_source_url",
    "pricing_verified_at",
    "pricing_source_http_status",
    "pricing_source_final_url",
    "pricing_evidence_markers",
    "currency",
    "billing_period",
    "evidence_source_type",
)


def candidate(tool_id):
    return {
        "id": tool_id,
        "name": tool_id.title(),
        "category": "creator",
        "category_display": "Creator & Productivity",
        "description": "Deterministic discovery regression fixture.",
        "official_url": f"https://{tool_id}.example/",
        "affiliate_url": None,
        "pricing": "Starting at $99/month",
        "pricing_source_url": f"https://{tool_id}.example/pricing",
        "pricing_verified": False,
        "pricing_verified_at": "2026-08-09T00:00:00Z",
        "pricing_source_http_status": 200,
        "pricing_source_final_url": f"https://{tool_id}.example/pricing",
        "pricing_evidence_markers": ["$99", "month"],
        "currency": "USD",
        "billing_period": "monthly",
        "evidence_source_type": "search_snippet",
        "key_features": ["Feature"],
        "rating": None,
        "logo_url": "https://example.invalid/logo.png",
        "commission": "30%",
    }


def test_meshy_typewise_evolve_are_normalized_fail_closed():
    fixtures = [candidate(tool_id) for tool_id in ("meshy", "typewise", "evolve")]
    affiliate_result = {
        "affiliate_url": None,
        "affiliate_verified": False,
        "affiliate_source_url": None,
        "affiliate_final_url": None,
        "affiliate_http_status": None,
        "affiliate_evidence_markers": [],
        "affiliate_verified_at": None,
        "affiliate_rejection_reason": "unverified fixture",
    }

    with patch("auto_aggregator.safe_affiliate_result", return_value=affiliate_result):
        merged, staged, updated = merge_discovered_candidates([], copy.deepcopy(fixtures))

    assert merged == []
    assert len(staged) == 3
    assert updated == []
    for tool in staged:
        assert tool["pricing"] == "See official pricing"
        assert tool["pricing_verified"] is False
        for field in PRICING_EVIDENCE_FIELDS:
            assert tool[field] is None, f"{tool['id']} retained {field}"

    errors = validate_dataset(staged)
    assert errors == [], "\n".join(errors)


if __name__ == "__main__":
    test_meshy_typewise_evolve_are_normalized_fail_closed()
    print("PASS: meshy/typewise/evolve discovery pricing is fail-closed")
