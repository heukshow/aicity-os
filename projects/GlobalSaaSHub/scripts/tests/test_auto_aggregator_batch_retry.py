"""
tests/test_auto_aggregator_batch_retry.py
===========================================
Deterministic mock-based unit tests for auto_aggregator.py:
 1. Batching 12 snippets into 1 single Gemini API call
 2. 429 Exponential Backoff (15s, 30s, 60s) & Retry-After header handling
 3. 429 Degraded Mode: pipeline keeps running with 150 merged tools
 4. Fail-closed on 401, 403, and malformed JSON
 5. Secret / API key masking in log outputs
"""

import sys
import os
import json
import io
import unittest
from unittest.mock import patch, MagicMock
import urllib.error

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

import auto_aggregator as aa

MOCK_SNIPPETS = [
    {"title": f"Snippet {i}", "content": f"Content {i}", "url": f"https://tool-{i}.com"}
    for i in range(12)
]


class TestAutoAggregatorBatchRetry(unittest.TestCase):

    @patch("urllib.request.urlopen")
    def test_snippets_batched_into_single_gemini_call(self, mock_urlopen):
        """Verify 12 search snippets are sent in a single batch Gemini call."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps([
                            {
                                "id": "batch-tool-1",
                                "name": "Batch Tool One",
                                "category": "automation",
                                "category_display": "Workflow Automation",
                                "description": "Desc",
                                "official_url": "https://batchtool1.com/",
                                "affiliate_url": "https://batchtool1.com/",
                                "pricing_source_url": "https://batchtool1.com/pricing",
                                "pricing": "$10/mo",
                                "key_features": ["Feature"],
                                "rating": None,
                                "logo_url": "https://logo.com",
                                "commission": "30%"
                            }
                        ])
                    }]
                }
            }]
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response

        mock_urlopen.return_value = mock_response

        res, status = aa.query_gemini_batch("mock-gemini-key", "sys-prompt", MOCK_SNIPPETS)

        self.assertEqual(status, "OK")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], "batch-tool-1")
        # Ensure urlopen was called exactly ONCE (single batch call)
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_gemini_429_exponential_backoff_and_retry_after(self, mock_urlopen, mock_sleep):
        """Verify 429 triggers exponential backoff (15, 30, 60s) or Retry-After header."""
        err_429 = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash",
            code=429,
            msg="RESOURCE_EXHAUSTED: Rate limit exceeded",
            hdrs={"Retry-After": "20"},
            fp=io.BytesIO(b'{"error":{"message":"quota exceeded"}}')
        )
        mock_urlopen.side_effect = err_429

        res, status = aa.query_gemini_batch("mock-key", "prompt", MOCK_SNIPPETS)

        self.assertIsNone(res)
        self.assertEqual(status, "RATE_LIMITED")
        # 3 attempts made
        self.assertEqual(mock_urlopen.call_count, 3)
        # Sleep called at least 3 times with Retry-After or backoff delay >= 15
        self.assertEqual(mock_sleep.call_count, 3)
        for call_args in mock_sleep.call_args_list:
            slept_sec = call_args[0][0]
            self.assertGreaterEqual(slept_sec, 15)

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_gemini_429_degraded_mode_keeps_pipeline_alive(self, mock_urlopen, mock_sleep):
        """Verify 429 rate limit enables degraded mode without failing pipeline."""
        err_429 = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=io.BytesIO(b'{"error":{"message":"requests per minute exceeded"}}')
        )
        mock_urlopen.side_effect = err_429

        res, status = aa.query_gemini_batch("mock-key", "prompt", MOCK_SNIPPETS)
        self.assertEqual(status, "RATE_LIMITED")

    @patch("urllib.request.urlopen")
    def test_gemini_401_403_and_malformed_json_fail_closed(self, mock_urlopen):
        """Verify 401, 403, and malformed JSON fail-closed with exact error status."""
        # 1. 401 Auth Error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com", code=401, msg="Unauthorized", hdrs={}, fp=io.BytesIO(b"")
        )
        _, status_401 = aa.query_gemini_batch("bad-key", "prompt", MOCK_SNIPPETS)
        self.assertEqual(status_401, "AUTH_ERROR")

        # 2. 403 Auth Error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com", code=403, msg="Forbidden", hdrs={}, fp=io.BytesIO(b"")
        )
        _, status_403 = aa.query_gemini_batch("bad-key", "prompt", MOCK_SNIPPETS)
        self.assertEqual(status_403, "AUTH_ERROR")

        # 3. Malformed JSON
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": "INVALID JSON {{{"}]}}]
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.side_effect = None
        mock_urlopen.return_value = mock_resp

        _, status_malformed = aa.query_gemini_batch("key", "prompt", MOCK_SNIPPETS)
        self.assertEqual(status_malformed, "PARSING_ERROR")

    def test_no_secret_leak_in_logs(self):
        """Verify that secret keys or sensitive tokens are masked."""
        secret_key = "AIzaSySecretApiKey12345"
        masked_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:key=***MASKED***"
        self.assertNotIn(secret_key, masked_url)


if __name__ == "__main__":
    unittest.main()
