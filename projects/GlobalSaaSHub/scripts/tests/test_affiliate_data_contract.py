"""Fail closed unless affiliate_url is an approved, account-specific tracking URL."""

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILES = (PROJECT_ROOT / "data" / "tools.json", PROJECT_ROOT / "data" / "tools.next.json")
TRACKING_KEYS = {"aff", "affiliate", "affiliate_id", "fpr", "fp_ref", "ref", "referral", "rui", "sa", "tag", "via"}


def _has_tracking_identifier(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    has_query_id = any(key.lower() in TRACKING_KEYS and any(value.strip() for value in values) for key, values in query.items())
    return has_query_id or parsed.path.strip("/") != ""


def test_affiliate_urls_are_approved_unique_tracking_links():
    for data_file in DATA_FILES:
        tools = json.loads(data_file.read_text(encoding="utf-8"))
        for tool in tools:
            affiliate_url = tool.get("affiliate_url")
            if affiliate_url is None:
                continue
            assert tool.get("affiliate_status") == "approved_tracking", (
                f"{data_file.name}: {tool['name']} has affiliate_url without approved_tracking status"
            )
            assert tool.get("affiliate_verified") is True
            assert affiliate_url.rstrip("/") != tool["official_url"].rstrip("/")
            assert _has_tracking_identifier(affiliate_url), (
                f"{data_file.name}: {tool['name']} affiliate_url lacks a unique tracking identifier"
            )


if __name__ == "__main__":
    test_affiliate_urls_are_approved_unique_tracking_links()
    print("PASS affiliate data contract")
