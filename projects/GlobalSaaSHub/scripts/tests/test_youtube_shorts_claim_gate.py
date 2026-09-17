"""Regression tests for Shorts promotion evidence and campaign dedup gates."""
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "youtube_shorts"))

import quality_gate  # noqa: E402


def _report():
    return {"checks": {}, "warnings": [], "failures": []}


def test_pictory_partner_email_claims_are_allowed_only_by_structured_verified_evidence():
    report = _report()
    quality_gate.check_price_and_discount_claims(
        "Use code COSHUMA20 for 20% off. The current annual offer is 40% and combined savings can exceed 52%.",
        "pictory",
        "pictory_coshuma20",
        report,
    )
    assert report["failures"] == []
    assert report["checks"]["promotion_evidence"]["source_type"] == "affiliate_manager_email"
    assert report["checks"]["promotion_evidence"]["reference_field"] == "gmail_message_id"
    assert report["checks"]["promotion_evidence"]["reference_value"] == "1a06d0ec1bf6a3a8"


def test_verified_claim_without_checkable_reference_is_not_trusted(monkeypatch, tmp_path):
    """claim_status alone is self-certification; it must not be trusted unless
    it also carries a concrete, re-checkable reference (e.g. a Gmail message
    id) to the primary source. Isolate the campaign evidence path from the
    legitimate tool-page fallback so this test checks only that contract."""
    campaigns_path = tmp_path / "youtube_shorts_campaigns.json"
    campaigns_path.write_text(
        """
        {
          "pictory": {
            "campaign_slug": "pictory_coshuma20",
            "evidence": {
              "type": "affiliate_manager_email",
              "claim_status": "verified_external_primary_source",
              "note": "trust me, I read an email",
              "verified_claims": {"promo_codes": ["COSHUMA20"], "discount_percentages": [20, 40, 52]}
            }
          }
        }
        """,
        encoding="utf-8",
    )
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    monkeypatch.setattr(quality_gate, "CAMPAIGNS_JSON", campaigns_path)
    monkeypatch.setattr(quality_gate, "PUBLIC_DIR", public_dir)

    report = _report()
    quality_gate.check_price_and_discount_claims(
        "Use code COSHUMA20 for 20% off.",
        "pictory",
        "pictory_coshuma20",
        report,
    )
    assert any("COSHUMA20" in failure for failure in report["failures"])
    assert "promotion_evidence" not in report["checks"]


def test_unknown_promo_code_fails_closed():
    report = _report()
    quality_gate.check_price_and_discount_claims(
        "Use code MADEUP99 for 20% off.",
        "pictory",
        "pictory_coshuma20",
        report,
    )
    assert any("MADEUP99" in failure for failure in report["failures"])


def test_unverified_percentage_fails_closed_even_when_campaign_has_other_verified_percentages():
    report = _report()
    quality_gate.check_price_and_discount_claims(
        "Save 73% with this offer.",
        "pictory",
        "pictory_coshuma20",
        report,
    )
    assert any("73%" in failure for failure in report["failures"])


def test_wrong_campaign_slug_does_not_inherit_pictory_primary_source_evidence(monkeypatch, tmp_path):
    # The real Pictory tool page currently contains COSHUMA20/20%, which is a
    # separate valid evidence source. Remove that fallback here so this test
    # verifies only that campaign-scoped primary-source evidence does not leak.
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    monkeypatch.setattr(quality_gate, "PUBLIC_DIR", public_dir)

    report = _report()
    quality_gate.check_price_and_discount_claims(
        "Use code COSHUMA20 for 20% off.",
        "pictory",
        "some_other_campaign",
        report,
    )
    assert report["failures"]


def test_uploaded_campaign_pair_is_blocked_from_duplicate_upload():
    report = _report()
    quality_gate.check_campaign_dedup("gohighlevel", "gohighlevel", report)
    assert any("already uploaded" in failure for failure in report["failures"])


def test_fps_fraction_parser_handles_standard_ntsc_rate():
    assert round(quality_gate._parse_fps("30000/1001"), 3) == 29.97
