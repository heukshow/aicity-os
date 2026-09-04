"""Tests for the render/upload extension without making network calls."""
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "youtube_shorts"))

import generate_script  # noqa: E402
import render_short  # noqa: E402
import upload_youtube  # noqa: E402


def test_pictory_campaign_is_evidence_bounded_and_tracks_money_hub():
    script = generate_script.generate("pictory")
    assert script["campaign_slug"] == "pictory_coshuma20"
    assert script["source_page"] == "/best/ai-video-generators.html"
    assert "COSHUMA20" in script["narration"]
    assert "52%" in script["narration"]
    assert script["evidence"]["type"] == "affiliate_manager_email"


def test_pictory_script_has_no_banned_earnings_claims():
    script = generate_script.generate("pictory")
    lowered = script["narration"].lower()
    for phrase in generate_script.BANNED:
        assert phrase.lower() not in lowered


def test_wrap_card_keeps_copy_readable():
    wrapped = render_short.wrap_card("This is a reasonably long sentence that should wrap for a vertical card", width=18)
    assert "\n" in wrapped
    assert max(len(line) for line in wrapped.splitlines()) <= 25


def test_upload_module_fails_closed_when_oauth_env_missing(monkeypatch):
    for name in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError) as exc:
        upload_youtube.require_env()
    assert "YOUTUBE_CLIENT_ID" in str(exc.value)
    assert "YOUTUBE_REFRESH_TOKEN" in str(exc.value)


def test_upload_module_accepts_private_only_known_privacy_values(monkeypatch, tmp_path):
    video = tmp_path / "x.mp4"
    video.write_bytes(b"not-a-real-video")
    with pytest.raises(ValueError):
        upload_youtube.upload(video, "T", "D", privacy="friends-only")
