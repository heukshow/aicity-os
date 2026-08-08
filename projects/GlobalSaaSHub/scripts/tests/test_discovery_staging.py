"""Regression coverage for the fail-closed discovery staging boundary."""

import copy
import json
import os
import sys
import tempfile
from unittest.mock import patch

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

import auto_aggregator as aa
from auto_aggregator import merge_discovered_candidates


def candidate(tool_id):
    return {
        "id": tool_id,
        "name": tool_id.title(),
        "category": "creator",
        "category_display": "Creator & Productivity",
        "description": "Deterministic discovery staging fixture.",
        "official_url": f"https://{tool_id}.example/",
        "affiliate_url": None,
        "pricing_source_url": f"https://{tool_id}.example/pricing",
        "pricing": "$99/month",
        "pricing_verified": False,
        "key_features": ["Feature"],
        "rating": None,
        "logo_url": "https://example.invalid/logo.png",
        "commission": "30%",
    }


def test_new_discoveries_are_staged_and_never_enter_candidate_corpus():
    baseline = [{
        "id": "existing-tool",
        "name": "Existing Tool",
        "official_url": "https://existing.example/",
    }]
    discoveries = [candidate(tool_id) for tool_id in ("meshy", "modelence", "typewise", "evolve")]
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
        merged, staged, updated = merge_discovered_candidates(copy.deepcopy(baseline), discoveries)

    assert merged == baseline
    assert updated == []
    assert [tool["id"] for tool in staged] == ["meshy", "modelence", "typewise", "evolve"]
    assert not ({tool["id"] for tool in merged} & {tool["id"] for tool in staged})
    for tool in staged:
        assert tool["pricing"] == "See official pricing"
        assert tool["pricing_verified"] is False
        assert tool["pricing_source_url"] is None


def test_main_writes_staging_report_without_changing_tools_next():
    discoveries = [candidate(tool_id) for tool_id in ("meshy", "modelence", "typewise", "evolve")]
    tavily_result = ({"results": [{"title": "fixture", "content": "fixture", "url": "https://example.invalid"}]}, "OK")

    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = os.path.join(temp_dir, "data")
        os.makedirs(data_dir)
        baseline = [{"id": "existing-tool", "name": "Existing Tool", "official_url": "https://existing.example/"}]
        with open(os.path.join(data_dir, "tools.json"), "w", encoding="utf-8") as handle:
            json.dump(baseline, handle)
        with open(os.path.join(data_dir, "manual_candidates_verified.json"), "w", encoding="utf-8") as handle:
            json.dump([], handle)

        with (
            patch("auto_aggregator.load_env"),
            patch.dict(os.environ, {"TAVILY_API_KEY": "fixture", "GEMINI_API_KEY": "fixture"}),
            patch("auto_aggregator.query_tavily", return_value=tavily_result),
            patch("auto_aggregator.query_gemini_batch", return_value=(discoveries, "OK")),
            patch("auto_aggregator.safe_affiliate_result", return_value={
                "affiliate_url": None,
                "affiliate_verified": False,
                "affiliate_source_url": None,
                "affiliate_final_url": None,
                "affiliate_http_status": None,
                "affiliate_evidence_markers": [],
                "affiliate_verified_at": None,
                "affiliate_rejection_reason": "unverified fixture",
            }),
        ):
            aa.main(base_dir=temp_dir)

        with open(os.path.join(data_dir, "tools.next.json"), encoding="utf-8") as handle:
            tools_next = json.load(handle)
        with open(os.path.join(data_dir, "new_tools_discovered.json"), encoding="utf-8") as handle:
            staged = json.load(handle)
        with open(os.path.join(data_dir, "run_summary.json"), encoding="utf-8") as handle:
            summary = json.load(handle)

        assert tools_next == baseline
        assert [tool["id"] for tool in staged] == ["meshy", "modelence", "typewise", "evolve"]
        assert summary["new_tools_added"] == 0
        assert summary["automated_discovery_added"] == 0
        assert summary["automated_discovery_staged"] == 4
        assert summary["sandbox_total"] == 1


if __name__ == "__main__":
    test_new_discoveries_are_staged_and_never_enter_candidate_corpus()
    test_main_writes_staging_report_without_changing_tools_next()
    print("PASS: meshy/modelence/typewise/evolve are staged outside tools.next.json")
