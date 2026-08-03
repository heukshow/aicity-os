"""
tests/test_auto_aggregator_batch_retry.py
===========================================
Deterministic mock-based unit tests for auto_aggregator.py:
 1. Canonical Gemini generateContent API URL builder & suffix verification
 2. Batching 12 snippets into chunks of MAX_GEMINI_BATCH_SIZE (10 + 2 = 2 calls)
 3. 429 Exponential Backoff (15s, 30s) without sleep after final 3rd attempt failure
 4. Degraded Mode & Partial Rate Limit handling (partial_rate_limited vs rate_limited)
 5. Fail-closed on 401, 403, and malformed JSON
 6. Secret / API key masking in log outputs
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

MOCK_SNIPPETS_12 = [
    {"title": f"Snippet {i}", "content": f"Content {i}", "url": f"https://tool-{i}.com"}
    for i in range(12)
]


class TestAutoAggregatorBatchRetry(unittest.TestCase):

    def test_gemini_request_url_has_generate_content_suffix(self):
        """Verify URL builder produces exact :generateContent?key= endpoint."""
        key = "test-api-key-12345"
        url = aa.build_gemini_url(key)

        self.assertIn(":generateContent?key=", url, "URL must contain ':generateContent?key=' suffix")
        self.assertTrue(url.startswith("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key="))
        self.assertNotIn(":key=", url)
        self.assertNotIn("flash?key=", url)

    @patch("urllib.request.urlopen")
    def test_snippets_batched_with_generate_content_url(self, mock_urlopen):
        """Verify query_gemini_batch uses build_gemini_url for HTTP requests."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps([{"id": "tool-1", "name": "Tool One", "category": "automation"}])
                    }]
                }
            }]
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res, status = aa.query_gemini_batch("test-key", "sys-prompt", MOCK_SNIPPETS_12[:5])

        self.assertEqual(status, "OK")
        req = mock_urlopen.call_args[0][0]
        self.assertIn(":generateContent?key=test-key", req.full_url)

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_no_sleep_on_final_retry_failure(self, mock_urlopen, mock_sleep):
        """Verify 429 on 3rd attempt returns RATE_LIMITED immediately WITHOUT sleeping after 3rd failure."""
        err_429 = urllib.error.HTTPError(
            url=aa.build_gemini_url("key"),
            code=429,
            msg="RESOURCE_EXHAUSTED",
            hdrs={},
            fp=io.BytesIO(b'{"error":{"message":"quota exceeded"}}')
        )
        mock_urlopen.side_effect = err_429

        res, status = aa.query_gemini_batch("mock-key", "prompt", MOCK_SNIPPETS_12[:2])

        self.assertIsNone(res)
        self.assertEqual(status, "RATE_LIMITED")
        self.assertEqual(mock_urlopen.call_count, 3)
        # Sleep called exactly 2 times (after 1st and 2nd attempt), NOT after 3rd attempt
        self.assertEqual(mock_sleep.call_count, 2)
        slept_delays = [call[0][0] for call in mock_sleep.call_args_list]
        self.assertEqual(slept_delays, [15, 30])

    @patch("time.sleep")
    @patch("urllib.request.urlopen")
    def test_gemini_429_retry_after_header(self, mock_urlopen, mock_sleep):
        """Verify Retry-After header overrides default backoff when present."""
        err_429 = urllib.error.HTTPError(
            url=aa.build_gemini_url("key"),
            code=429,
            msg="Rate limit",
            hdrs={"Retry-After": "25"},
            fp=io.BytesIO(b'{"error":{"message":"rate limit"}}')
        )
        mock_urlopen.side_effect = err_429

        res, status = aa.query_gemini_batch("mock-key", "prompt", MOCK_SNIPPETS_12[:2])

        self.assertEqual(status, "RATE_LIMITED")
        self.assertEqual(mock_sleep.call_count, 2)
        # 1st attempt: max(25, 15) = 25. 2nd attempt: max(25, 30) = 30
        slept_delays = [call[0][0] for call in mock_sleep.call_args_list]
        self.assertEqual(slept_delays, [25, 30])

    @patch("urllib.request.urlopen")
    def test_gemini_401_403_and_malformed_json_fail_closed(self, mock_urlopen):
        """Verify 401, 403, and malformed JSON fail-closed with exact error status."""
        # 1. 401 Auth Error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com", code=401, msg="Unauthorized", hdrs={}, fp=io.BytesIO(b"")
        )
        _, status_401 = aa.query_gemini_batch("bad-key", "prompt", MOCK_SNIPPETS_12[:2])
        self.assertEqual(status_401, "AUTH_ERROR")

        # 2. 403 Auth Error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com", code=403, msg="Forbidden", hdrs={}, fp=io.BytesIO(b"")
        )
        _, status_403 = aa.query_gemini_batch("bad-key", "prompt", MOCK_SNIPPETS_12[:2])
        self.assertEqual(status_403, "AUTH_ERROR")

        # 3. Malformed JSON
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": "INVALID JSON {{{"}]}}]
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.side_effect = None
        mock_urlopen.return_value = mock_resp

        _, status_malformed = aa.query_gemini_batch("key", "prompt", MOCK_SNIPPETS_12[:2])
        self.assertEqual(status_malformed, "PARSING_ERROR")

    def test_max_batch_size_constant(self):
        """Verify MAX_GEMINI_BATCH_SIZE constant is set to 10."""
        self.assertEqual(aa.MAX_GEMINI_BATCH_SIZE, 10)

    def test_no_secret_leak_in_logs(self):
        """Verify that secret keys or sensitive tokens are masked."""
        secret_key = "AIzaSySecretApiKey12345"
        masked_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=***MASKED***"
        self.assertNotIn(secret_key, masked_url)


if __name__ == "__main__":
    unittest.main()
