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
    assert report["checks"]["promotion_evidence"]["verified_at"] == "2026-09-04"


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


def test_wrong_campaign_slug_does_not_inherit_pictory_primary_source_evidence():
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
