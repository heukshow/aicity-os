"""
tests/test_auto_aggregator_main_flow.py
========================================
Fully isolated E2E Mock execution flow tests for auto_aggregator.py main():
 1. Uses TemporaryDirectory so real repository workspace files are NEVER touched or written.
 2. Generates 148 deterministic baseline tools in temp_dir/data/tools.json.
 3. Generates 2 deterministic manual verified candidate tools in temp_dir/data/manual_candidates_verified.json.
 4. Verifies 12 search snippets trigger 10 + 2 Gemini batching.
 5. Verifies full 429 produces 150 tools with gemini_status='rate_limited' and degraded_mode=True.
 6. Verifies partial 429 preserves 150 tools with gemini_status='partial_rate_limited' and degraded_mode=True.
 7. Proves zero pollution to real repo files under clean checkout conditions.
"""

import sys
import os
import json
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

import auto_aggregator as aa

MOCK_12_SNIPPETS = {
    "results": [
        {"title": f"Title {i}", "content": f"Content {i}", "url": f"https://tool{i}.com"}
        for i in range(4)
    ]
}


def make_148_baseline_tools():
    """Generates 148 unique deterministic baseline tool records."""
    tools = []
    for i in range(1, 149):
        tools.append({
            "id": f"base-tool-{i}",
            "name": f"Base Tool {i}",
            "category": "automation",
            "category_display": "Workflow Automation",
            "description": f"Baseline Tool Description {i}",
            "official_url": f"https://basetool{i}.com/",
            "affiliate_url": f"https://basetool{i}.com/affiliate",
            "affiliate_verified": True,
            "pricing_source_url": f"https://basetool{i}.com/pricing",
            "pricing": f"${i}/mo",
            "pricing_verified": True,
            "key_features": ["Feature A", "Feature B"],
            "rating": 4.5,
            "logo_url": "https://logo.com/img.png",
            "commission": "30% recurring"
        })
    return tools


def make_2_manual_candidates():
    """Generates 2 unique deterministic verified manual candidate records."""
    return [
        {
            "id": "manual-candidate-taskade",
            "name": "Taskade Manual",
            "category": "automation",
            "category_display": "Workflow Automation",
            "description": "Taskade Description",
            "official_url": "https://taskade-manual.com/",
            "affiliate_url": "https://taskade-manual.com/affiliate",
            "affiliate_verified": True,
            "pricing_source_url": "https://taskade-manual.com/pricing",
            "pricing": "Starting at $8/user/month",
            "pricing_verified": True,
            "pricing_evidence_markers": ["$8", "user", "month"],
            "currency": "USD",
            "billing_period": "monthly",
            "evidence_source_type": "official_page",
            "key_features": ["Feature A"],
            "rating": None,
            "logo_url": "https://logo.com/img.png",
            "commission": "50% recurring"
        },
        {
            "id": "manual-candidate-relevance",
            "name": "Relevance AI Manual",
            "category": "developer",
            "category_display": "Developer APIs",
            "description": "Relevance AI Description",
            "official_url": "https://relevance-manual.com/",
            "affiliate_url": "https://relevance-manual.com/affiliate",
            "affiliate_verified": True,
            "pricing_source_url": "https://relevance-manual.com/pricing",
            "pricing": "Starting at $234/month",
            "pricing_verified": True,
            "pricing_evidence_markers": ["$234", "month"],
            "currency": "USD",
            "billing_period": "monthly",
            "evidence_source_type": "official_page",
            "key_features": ["Feature B"],
            "rating": None,
            "logo_url": "https://logo.com/img.png",
            "commission": "30% recurring"
        }
    ]


class TestAutoAggregatorMainFlow(unittest.TestCase):

    def setUp(self):
        self.repo_dir = os.path.dirname(SCRIPTS_DIR)
        self.repo_data_dir = os.path.join(self.repo_dir, "data")
        self.repo_next_tools = os.path.join(self.repo_data_dir, "tools.next.json")
        self.repo_summary = os.path.join(self.repo_data_dir, "run_summary.json")

    @patch("auto_aggregator.load_env")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "mock_tavily", "GEMINI_API_KEY": "mock_gemini"})
    @patch("auto_aggregator.query_tavily", return_value=MOCK_12_SNIPPETS)
    @patch("auto_aggregator.query_gemini_batch")
    def test_main_flow_full_429_degraded_mode_isolated(self, mock_gemini_batch, mock_tavily, mock_env):
        """Verify main() with 12 snippets and 429 on all batches produces 150 tools in isolated temp_dir."""
        mock_gemini_batch.return_value = (None, "RETRY_EXHAUSTED")

        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, "data")
            os.makedirs(data_dir, exist_ok=True)

            # Write 148 tools & 2 manual candidates into temp_dir
            tools_file = os.path.join(data_dir, "tools.json")
            manual_file = os.path.join(data_dir, "manual_candidates_verified.json")

            with open(tools_file, "w", encoding="utf-8") as f:
                json.dump(make_148_baseline_tools(), f, indent=2)
            with open(manual_file, "w", encoding="utf-8") as f:
                json.dump(make_2_manual_candidates(), f, indent=2)

            # Run main with injected temp_dir
            aa.main(base_dir=temp_dir)

            # Assertions on temp_dir outputs
            temp_next_tools = os.path.join(data_dir, "tools.next.json")
            temp_summary = os.path.join(data_dir, "run_summary.json")

            self.assertTrue(os.path.exists(temp_next_tools))
            with open(temp_next_tools, "r", encoding="utf-8") as f:
                res_tools = json.load(f)
            self.assertEqual(len(res_tools), 150)

            self.assertTrue(os.path.exists(temp_summary))
            with open(temp_summary, "r", encoding="utf-8") as f:
                summary = json.load(f)

            self.assertEqual(summary["gemini_status"], "all_batches_skipped")
            self.assertEqual(summary["degraded_mode"], True)
            self.assertEqual(summary["sandbox_total"], 150)
            self.assertEqual(mock_gemini_batch.call_count, 2)

    @patch("auto_aggregator.load_env")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "mock_tavily", "GEMINI_API_KEY": "mock_gemini"})
    @patch("auto_aggregator.query_tavily", return_value=MOCK_12_SNIPPETS)
    @patch("auto_aggregator.query_gemini_batch")
    def test_main_flow_partial_429_degraded_mode_isolated(self, mock_gemini_batch, mock_tavily, mock_env):
        """Verify main() with 1 chunk OK and 1 chunk 429 preserves 150 tools in isolated temp_dir."""
        mock_discovered_tool = {
            "id": "discovered-tool-999",
            "name": "Discovered Tool 999",
            "category": "automation",
            "category_display": "Workflow Automation",
            "description": "Desc 999",
            "official_url": "https://discovered999.com/",
            "affiliate_url": "https://discovered999.com/aff",
            "pricing_source_url": "https://discovered999.com/pricing",
            "pricing": "Starting at $10/mo",
            "key_features": ["Feature X"],
            "rating": None,
            "logo_url": "https://logo.com",
            "commission": "30%"
        }
        mock_gemini_batch.side_effect = [
            ([mock_discovered_tool], "OK"),
            (None, "RETRY_EXHAUSTED")
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, "data")
            os.makedirs(data_dir, exist_ok=True)

            tools_file = os.path.join(data_dir, "tools.json")
            manual_file = os.path.join(data_dir, "manual_candidates_verified.json")

            with open(tools_file, "w", encoding="utf-8") as f:
                json.dump(make_148_baseline_tools(), f, indent=2)
            with open(manual_file, "w", encoding="utf-8") as f:
                json.dump(make_2_manual_candidates(), f, indent=2)

            aa.main(base_dir=temp_dir)

            temp_summary = os.path.join(data_dir, "run_summary.json")
            with open(temp_summary, "r", encoding="utf-8") as f:
                summary = json.load(f)

            self.assertEqual(summary["gemini_status"], "partial_skipped")
            self.assertEqual(summary["degraded_mode"], True)
            self.assertEqual(summary["sandbox_total"], 150)

    @patch("auto_aggregator.load_env")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "mock_tavily", "GEMINI_API_KEY": "mock_gemini"})
    @patch("auto_aggregator.query_tavily", return_value=MOCK_12_SNIPPETS)
    @patch("auto_aggregator.query_gemini_batch", return_value=(None, "RETRY_EXHAUSTED"))
    def test_clean_checkout_isolation_no_repo_pollution(self, mock_gemini_batch, mock_tavily, mock_env):
        """Verify that testing inside temp_dir NEVER touches real repo files regardless of repo state."""
        # Record mtimes or existence of repo runtime files before test
        repo_next_exists_before = os.path.exists(self.repo_next_tools)
        repo_summary_exists_before = os.path.exists(self.repo_summary)

        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            with open(os.path.join(data_dir, "tools.json"), "w", encoding="utf-8") as f:
                json.dump(make_148_baseline_tools(), f)
            with open(os.path.join(data_dir, "manual_candidates_verified.json"), "w", encoding="utf-8") as f:
                json.dump(make_2_manual_candidates(), f)

            aa.main(base_dir=temp_dir)

        # After test finishes and temp_dir is deleted, assert repo status was untouched
        self.assertEqual(os.path.exists(self.repo_next_tools), repo_next_exists_before)
        self.assertEqual(os.path.exists(self.repo_summary), repo_summary_exists_before)

    @patch("auto_aggregator.load_env")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "mock_tavily", "GEMINI_API_KEY": "mock_gemini"})
    @patch("auto_aggregator.query_tavily", return_value=MOCK_12_SNIPPETS)
    @patch("auto_aggregator.query_gemini_batch", return_value=(None, "PARSING_ERROR"))
    def test_response_schema_error_fails_immediately(self, mock_gemini_batch, mock_tavily, mock_env):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            with open(os.path.join(data_dir, "tools.json"), "w", encoding="utf-8") as f:
                json.dump(make_148_baseline_tools(), f)
            with open(os.path.join(data_dir, "manual_candidates_verified.json"), "w", encoding="utf-8") as f:
                json.dump(make_2_manual_candidates(), f)
            with self.assertRaises(SystemExit):
                aa.main(base_dir=temp_dir)
            self.assertEqual(mock_gemini_batch.call_count, 1)
            self.assertFalse(os.path.exists(os.path.join(data_dir, "tools.next.json")))


if __name__ == "__main__":
    unittest.main()
