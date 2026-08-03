"""
tests/test_auto_aggregator_main_flow.py
========================================
E2E Mock execution flow tests for auto_aggregator.py main():
 1. Verifies baseline 148 tools + 2 verified manual candidates = 150 candidate tools.
 2. Verifies 12 search snippets are split into 10 + 2 (2 Gemini batch calls).
 3. Verifies full 429 failure triggers degraded mode, writing 150 tools to tools.next.json with gemini_status='rate_limited'.
 4. Verifies partial 429 failure records gemini_status='partial_rate_limited' with degraded_mode=True.
"""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

import auto_aggregator as aa

MOCK_12_SNIPPETS = {
    "results": [
        {"title": f"Title {i}", "content": f"Content {i}", "url": f"https://tool{i}.com"}
        for i in range(4)
    ]
}


class TestAutoAggregatorMainFlow(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(SCRIPTS_DIR)
        self.tools_path = os.path.join(self.base_dir, "data", "tools.json")
        self.next_tools_path = os.path.join(self.base_dir, "data", "tools.next.json")
        self.summary_path = os.path.join(self.base_dir, "data", "run_summary.json")
        self.manual_path = os.path.join(self.base_dir, "data", "manual_candidates_verified.json")

    @patch("auto_aggregator.load_env")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "mock_tavily", "GEMINI_API_KEY": "mock_gemini"})
    @patch("auto_aggregator.query_tavily", return_value=MOCK_12_SNIPPETS)
    @patch("auto_aggregator.query_gemini_batch")
    def test_main_flow_full_429_degraded_mode(self, mock_gemini_batch, mock_tavily, mock_env):
        """Verify main() with 12 snippets and 429 on all batches produces 150 tools and rate_limited status."""
        mock_gemini_batch.return_value = (None, "RATE_LIMITED")

        aa.main()

        # Check 1: query_gemini_batch called exactly 2 times (10 items + 2 items)
        self.assertEqual(mock_gemini_batch.call_count, 2)
        call_chunk_lens = [len(call_args[0][2]) for call_args in mock_gemini_batch.call_args_list]
        self.assertEqual(call_chunk_lens, [10, 2])

        # Check 2: tools.next.json created and contains 150 tools
        self.assertTrue(os.path.exists(self.next_tools_path))
        with open(self.next_tools_path, "r", encoding="utf-8") as f:
            next_tools = json.load(f)
        self.assertEqual(len(next_tools), 150)

        # Check 3: run_summary.json contains rate_limited and degraded_mode=True
        self.assertTrue(os.path.exists(self.summary_path))
        with open(self.summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["gemini_status"], "rate_limited")
        self.assertEqual(summary["degraded_mode"], True)
        self.assertEqual(summary["sandbox_total"], 150)

    @patch("auto_aggregator.load_env")
    @patch.dict(os.environ, {"TAVILY_API_KEY": "mock_tavily", "GEMINI_API_KEY": "mock_gemini"})
    @patch("auto_aggregator.query_tavily", return_value=MOCK_12_SNIPPETS)
    @patch("auto_aggregator.query_gemini_batch")
    def test_main_flow_partial_429_degraded_mode(self, mock_gemini_batch, mock_tavily, mock_env):
        """Verify main() with 1 chunk OK and 1 chunk 429 produces partial_rate_limited status."""
        mock_tool = {
            "id": "discovered-tool-1",
            "name": "Discovered Tool One",
            "category": "automation",
            "category_display": "Workflow Automation",
            "description": "Desc",
            "official_url": "https://discoveredtool1.com/",
            "affiliate_url": "https://discoveredtool1.com/",
            "pricing_source_url": "https://discoveredtool1.com/pricing",
            "pricing": "Starting at $10/mo",
            "key_features": ["Feature"],
            "rating": None,
            "logo_url": "https://logo.com",
            "commission": "30%"
        }
        # First chunk returns OK, second chunk returns RATE_LIMITED
        mock_gemini_batch.side_effect = [
            ([mock_tool], "OK"),
            (None, "RATE_LIMITED")
        ]

        aa.main()

        self.assertEqual(mock_gemini_batch.call_count, 2)
        with open(self.summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["gemini_status"], "partial_rate_limited")
        self.assertEqual(summary["degraded_mode"], True)
        self.assertEqual(summary["sandbox_total"], 151)


if __name__ == "__main__":
    unittest.main()
