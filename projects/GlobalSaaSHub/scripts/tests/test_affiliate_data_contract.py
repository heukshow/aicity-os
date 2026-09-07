"""Fail closed unless affiliate_url is an approved, account-specific tracking URL."""

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILES = (PROJECT_ROOT / "data" / "tools.json", PROJECT_ROOT / "data" / "tools.next.json")
TRACKING_KEYS = {"aff", "affiliate", "affiliate_id", "fpr", "fp_ref", "pc", "ref", "referral", "rui", "sa", "tag", "via"}


def _has_tracking_identifier(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    # Taskip's confirmed COSHUMA referral uses `atp` at the site root.
    if parsed.hostname == "taskip.net" and query.get("atp") == ["qnV3mw"]:
        return True
    # CartStack's confirmed COSHUMA referral uses `afmc` at the site root.
    if parsed.hostname == "www.cartstack.com" and query.get("afmc") == ["wb"]:
        return True
    # Jotform's confirmed COSHUMA customer links use `partner`, including at root.
    if parsed.hostname == "www.jotform.com" and query.get("partner") == ["coshuma"]:
        return True
    # Verified HelpDesk and Text Partner campaigns use `a` as their account ID.
    if parsed.hostname in {"www.helpdesk.com", "www.text.com"} and any(value.strip() for value in query.get("a", [])):
        return True
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


def test_helpdesk_tracking_identifier():
    exact_url = "https://www.helpdesk.com/?a=8IetMhQvR&utm_campaign=pp_helpdesk-default&utm_source=PP&d=14"
    for data_file in DATA_FILES:
        tool = next(item for item in json.loads(data_file.read_text(encoding="utf-8")) if item["id"] == "helpdesk")
        assert tool["affiliate_status"] == "approved_tracking"
        assert tool["affiliate_verified"] is True
        assert tool["affiliate_url"] == exact_url
        assert _has_tracking_identifier(tool["affiliate_url"])
    assert not _has_tracking_identifier("https://www.helpdesk.com/")
    assert not _has_tracking_identifier("https://www.helpdesk.com/?a=&utm_source=PP&d=14")
    assert not _has_tracking_identifier("https://unrelated.invalid/?a=8IetMhQvR")


def test_text_tracking_identifier():
    exact_url = "https://www.text.com/?a=8IetMhQvR&utm_campaign=pp_text-wins-martech-awards&utm_source=PP"
    for data_file in DATA_FILES:
        tool = next(item for item in json.loads(data_file.read_text(encoding="utf-8")) if item["id"] == "text")
        assert tool["affiliate_status"] == "approved_tracking"
        assert tool["affiliate_verified"] is True
        assert tool["affiliate_url"] == exact_url
        assert _has_tracking_identifier(tool["affiliate_url"])
    assert not _has_tracking_identifier("https://www.text.com/")
    assert not _has_tracking_identifier("https://www.text.com/?utm_campaign=pp_text-wins-martech-awards&utm_source=PP")
    assert not _has_tracking_identifier("https://www.text.com/?a=&utm_source=PP")
    assert not _has_tracking_identifier("https://www.text.com/?a=%20&utm_source=PP")
    assert not _has_tracking_identifier("https://www.text.com.unrelated.invalid/?a=8IetMhQvR")


def test_jotform_tracking_identifier():
    assert _has_tracking_identifier("https://www.jotform.com/?partner=coshuma")
    assert _has_tracking_identifier("https://www.jotform.com/ai/agents/?partner=coshuma")
    assert not _has_tracking_identifier("https://www.jotform.com/")
    assert not _has_tracking_identifier("https://www.jotform.com/?partner=")
    assert not _has_tracking_identifier("https://www.jotform.com/?partner=%20")
    assert not _has_tracking_identifier("https://www.jotform.com/?partner=unconfirmed")
    assert not _has_tracking_identifier("https://www.jotform.com/?utm_source=coshuma")
    assert not _has_tracking_identifier("https://www.jotform.com.unrelated.invalid/?partner=coshuma")
    assert not _has_tracking_identifier("https://unrelated.invalid/?partner=coshuma")


def test_cartstack_tracking_identifier():
    assert _has_tracking_identifier("http://www.cartstack.com/?afmc=wb")
    assert not _has_tracking_identifier("http://www.cartstack.com/")
    assert not _has_tracking_identifier("http://www.cartstack.com/?afmc=")
    assert not _has_tracking_identifier("http://www.cartstack.com/?afmc=%20")
    assert not _has_tracking_identifier("http://www.cartstack.com/?afmc=unconfirmed")
    assert not _has_tracking_identifier("http://www.cartstack.com/?utm_source=wb")
    assert not _has_tracking_identifier("http://www.cartstack.com.unrelated.invalid/?afmc=wb")
    assert not _has_tracking_identifier("http://unrelated.invalid/?afmc=wb")


def test_taskip_tracking_identifier():
    assert _has_tracking_identifier("https://taskip.net/?atp=qnV3mw")
    assert not _has_tracking_identifier("https://taskip.net/")
    assert not _has_tracking_identifier("https://taskip.net/?atp=")
    assert not _has_tracking_identifier("https://taskip.net/?atp=%20")
    assert not _has_tracking_identifier("https://taskip.net/?atp=unconfirmed")
    assert not _has_tracking_identifier("https://taskip.net/?utm_source=qnV3mw")
    assert not _has_tracking_identifier("https://taskip.net.unrelated.invalid/?atp=qnV3mw")
    assert not _has_tracking_identifier("https://unrelated.invalid/?atp=qnV3mw")


if __name__ == "__main__":
    test_helpdesk_tracking_identifier()
    test_text_tracking_identifier()
    test_jotform_tracking_identifier()
    test_cartstack_tracking_identifier()
    test_taskip_tracking_identifier()
    test_affiliate_urls_are_approved_unique_tracking_links()
    print("PASS affiliate data contract")
