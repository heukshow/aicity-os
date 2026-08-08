import io
import json
import os
import sys
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)
import auto_aggregator as aa

SNIPPETS = [{"title": "x", "content": "y", "url": "https://example.com"}]


def http_error(code, retry_after=None):
    headers = {} if retry_after is None else {"Retry-After": retry_after}
    return urllib.error.HTTPError("https://example.invalid", code, "error", headers, io.BytesIO(b"redacted"))


def gemini_response(tools=None, malformed=False):
    response = MagicMock()
    text = "not-json" if malformed else json.dumps(tools if tools is not None else [])
    response.read.return_value = json.dumps({"candidates": [{"content": {"parts": [{"text": text}]}}]}).encode()
    response.__enter__.return_value = response
    return response


class RetryPolicyTests(unittest.TestCase):
    def call(self, side_effect):
        sleeps = []
        with patch("urllib.request.urlopen", side_effect=side_effect) as opened:
            result = aa.query_gemini_batch("secret-key", "prompt", SNIPPETS, sleep_fn=sleeps.append, random_fn=lambda: 0.0)
        return result, sleeps, opened.call_count

    def test_429_then_success(self):
        (tools, status), sleeps, calls = self.call([http_error(429), gemini_response([{"id": "a"}])])
        self.assertEqual((status, tools), ("OK", [{"id": "a"}]))
        self.assertEqual((calls, sleeps), (2, [5.0]))

    def test_503_then_success(self):
        (tools, status), sleeps, calls = self.call([http_error(503), gemini_response([])])
        self.assertEqual((status, calls, sleeps), ("OK", 2, [5.0]))

    def test_429_503_then_success(self):
        (tools, status), sleeps, calls = self.call([http_error(429), http_error(503), gemini_response([])])
        self.assertEqual((status, calls, sleeps), ("OK", 3, [5.0, 10.0]))

    def test_retry_exhaustion_is_bounded_and_partial_data_is_discarded(self):
        (_, status), sleeps, calls = self.call([http_error(503)] * 4)
        self.assertEqual(status, "RETRY_EXHAUSTED")
        self.assertEqual(calls, aa.MAX_API_ATTEMPTS)
        self.assertEqual(len(sleeps), aa.MAX_API_ATTEMPTS - 1)
        existing = [{"id": "preserved"}]
        self.assertEqual(aa.discovery_merge_input([{"id": "partial"}], True), [])
        self.assertEqual(existing, [{"id": "preserved"}])

    def test_401_and_403_do_not_retry(self):
        for code in (401, 403):
            (_, status), sleeps, calls = self.call([http_error(code)])
            self.assertEqual((status, calls, sleeps), ("AUTH_ERROR", 1, []))

    def test_400_does_not_retry(self):
        (_, status), sleeps, calls = self.call([http_error(400)])
        self.assertEqual((status, calls, sleeps), ("BAD_REQUEST", 1, []))

    def test_malformed_response_does_not_retry(self):
        (_, status), sleeps, calls = self.call([gemini_response(malformed=True)])
        self.assertEqual((status, calls, sleeps), ("PARSING_ERROR", 1, []))

    def test_retry_after_seconds_is_respected(self):
        (_, status), sleeps, calls = self.call([http_error(429, "17"), gemini_response([])])
        self.assertEqual((status, calls, sleeps), ("OK", 2, [17.0]))

    def test_only_allowlisted_statuses_retry(self):
        for code in (429, 500, 502, 503, 504):
            (_, status), _, calls = self.call([http_error(code), gemini_response([])])
            self.assertEqual((status, calls), ("OK", 2))
        for code in (400, 401, 403, 404, 422):
            (_, _), _, calls = self.call([http_error(code)])
            self.assertEqual(calls, 1)

    def test_logs_never_contain_key_request_body_or_error_body(self):
        key = "highly-secret-api-key"
        snippets = [{"content": "private-request-body"}]
        output = io.StringIO()
        with patch("urllib.request.urlopen", side_effect=http_error(503)), patch("sys.stdout", output):
            aa.query_gemini_batch(key, "private-prompt", snippets, sleep_fn=lambda _: None, random_fn=lambda: 0.0)
        log = output.getvalue()
        self.assertNotIn(key, log)
        self.assertNotIn("private-request-body", log)
        self.assertNotIn("redacted", log)

    def test_malformed_candidate_is_discarded(self):
        valid = {
            "id": "valid-tool", "name": "Valid Tool", "category": "automation",
            "category_display": "Workflow Automation", "description": "Valid",
            "official_url": "https://valid.example/", "affiliate_url": "https://valid.example/affiliate",
            "pricing_source_url": "https://valid.example/pricing", "pricing": "$10/mo",
            "key_features": ["Feature"], "rating": None, "logo_url": "https://valid.example/logo.png",
            "commission": "30%"
        }
        self.assertEqual(aa.filter_valid_gemini_candidates(["partial", {"id": "missing-fields"}, valid]), [valid])

    def test_zero_new_candidates_is_a_normal_result(self):
        self.assertEqual(aa.filter_valid_gemini_candidates([]), [])
        self.assertEqual(aa.discovery_merge_input([], False), [])

    def test_same_batch_duplicate_is_idempotent(self):
        candidate = {
            "id": "unique-tool", "name": "Unique Tool", "category": "automation",
            "category_display": "Workflow Automation", "description": "Valid",
            "official_url": "https://unique.example/", "affiliate_url": "https://unique.example/affiliate",
            "pricing_source_url": "https://unique.example/pricing", "pricing": "$10/mo",
            "key_features": ["Feature"], "rating": None, "logo_url": "https://unique.example/logo.png",
            "commission": "30%"
        }
        with patch("auto_aggregator.safe_affiliate_result", return_value={"affiliate_url": None, "affiliate_verified": False}):
            merged, added, _ = aa.merge_discovered_candidates([], [candidate, dict(candidate)])
            self.assertEqual((len(merged), len(added)), (0, 1))


class TavilyRetryTests(unittest.TestCase):
    def test_tavily_503_then_success(self):
        response = MagicMock()
        response.read.return_value = b'{"results": []}'
        response.__enter__.return_value = response
        sleeps = []
        with patch("urllib.request.urlopen", side_effect=[http_error(503), response]) as opened:
            result, status = aa.query_tavily("secret", "query", sleep_fn=sleeps.append, random_fn=lambda: 0.0)
        self.assertEqual((status, result, opened.call_count, sleeps), ("OK", {"results": []}, 2, [5.0]))

    def test_tavily_malformed_is_not_retried(self):
        response = MagicMock()
        response.read.return_value = b'{"unexpected": true}'
        response.__enter__.return_value = response
        with patch("urllib.request.urlopen", return_value=response) as opened:
            result, status = aa.query_tavily("secret", "query", sleep_fn=lambda _: None)
        self.assertEqual((result, status, opened.call_count), (None, "PARSING_ERROR", 1))


if __name__ == "__main__":
    unittest.main()
