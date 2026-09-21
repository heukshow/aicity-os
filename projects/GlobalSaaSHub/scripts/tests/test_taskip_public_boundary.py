from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL_PAGE = ROOT / "public" / "tool" / "taskip.html"
PRODUCER = ROOT / "scripts" / "surface_taskip_verified_offer.py"

TRACKING_URL = "https://taskip.net/?atp=qnV3mw"
PUBLIC_BANNED = (
    "Buyer-intent update · verified",
    "authenticated Taskip partner account",
    "Taskip's current public affiliate page",
    "does not copy the affiliate parameter",
    "Publication and link validation",
    "Verify affiliate terms",
)


def test_taskip_tool_page_is_customer_only():
    html = TOOL_PAGE.read_text(encoding="utf-8")
    assert "Updated Sep. 8, 2026" in html
    for phrase in PUBLIC_BANNED:
        assert phrase not in html
    assert TRACKING_URL in html
    assert 'rel="sponsored noopener noreferrer"' in html


def test_taskip_offer_producer_emits_customer_only_card():
    source = PRODUCER.read_text(encoding="utf-8")
    start = source.index("card = f'''")
    end = source.index("html = html.replace(closing, card + closing, 1)", start)
    card_source = source[start:end]

    for phrase in PUBLIC_BANNED:
        assert phrase not in card_source

    assert "{TRACKING_URL}" in card_source
    assert 'rel="sponsored nofollow noopener noreferrer"' in card_source
    assert "7 days of full access" in card_source
    assert "$12/month" in card_source
