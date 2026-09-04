"""Tests for scripts/youtube_shorts/*.py (content selection, metadata, quality gate).

Uses tempfile-generated fixtures only (no repo-committed binary video assets),
matching this repo's existing test-isolation convention
(see test_auto_aggregator_main_flow.py).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]  # projects/GlobalSaaSHub
sys.path.insert(0, str(REPO_ROOT / "scripts" / "youtube_shorts"))

import select_content  # noqa: E402
import generate_metadata  # noqa: E402
import quality_gate  # noqa: E402


def _make_test_video(path: Path, width=1080, height=1920, duration=5, with_audio=True):
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:d={duration}",
    ]
    if with_audio:
        cmd += ["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration}"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
    if with_audio:
        cmd += ["-c:a", "aac", "-shortest"]
    cmd += [str(path)]
    subprocess.run(cmd, check=True, capture_output=True)


def test_is_generic_homepage_url_rejects_bare_homepage():
    assert select_content.is_generic_homepage_url("https://www.example.com/", "https://www.example.com/")
    assert select_content.is_generic_homepage_url("https://www.example.com", "")


def test_is_generic_homepage_url_accepts_real_tracking_links():
    assert not select_content.is_generic_homepage_url("https://www.gohighlevel.com/?fp_ref=sangkwon56", "https://www.gohighlevel.com/")
    assert not select_content.is_generic_homepage_url("https://vidiq.com/coshuma", "https://vidiq.com/")


def test_build_candidates_never_returns_generic_homepage_only_tools():
    candidates = select_content.build_candidates()
    for c in candidates:
        assert "?" in c["affiliate_url"] or any(
            marker in c["affiliate_url"] for marker in ("/ref", "/via", "fp_ref", "coshuma", "/partner")
        )


def test_build_candidates_skips_manifest_covered_tools_by_default():
    candidates = select_content.build_candidates()
    ids = {c["affiliate_target"] for c in candidates}
    assert "gohighlevel" not in ids
    assert "vidiq" not in ids
    assert "descript" not in ids


def test_build_candidates_respects_explicit_exclude():
    all_candidates = {c["affiliate_target"] for c in select_content.build_candidates()}
    if not all_candidates:
        pytest.skip("no eligible candidates in current tools.json")
    one = next(iter(all_candidates))
    filtered = {c["affiliate_target"] for c in select_content.build_candidates(exclude_ids={one})}
    assert one not in filtered


def test_generate_metadata_utm_params_match_attribution_js_contract():
    result = generate_metadata.generate("vidiq", "vidiq_wave2", "Struggling with YouTube SEO?")
    assert "utm_source=youtube" in result["coshuma_url"]
    assert "utm_medium=shorts" in result["coshuma_url"]
    assert "utm_campaign=vidiq_wave2" in result["coshuma_url"]
    assert result["coshuma_url"].startswith("https://coshuma.com/tool/vidiq.html")


def test_generate_metadata_default_excludes_direct_affiliate_link():
    result = generate_metadata.generate("vidiq", "vidiq_wave2", "Struggling with YouTube SEO?")
    assert "vidiq.com/coshuma" not in result["description"]


def test_generate_metadata_can_include_direct_affiliate_link_when_asked():
    result = generate_metadata.generate(
        "vidiq", "vidiq_wave2", "Struggling with YouTube SEO?", include_direct_affiliate_link=True
    )
    assert "vidiq.com/coshuma" in result["description"]
    assert "Affiliate Disclosure" in result["description"]


def test_generate_metadata_rejects_banned_phrases():
    with pytest.raises(ValueError):
        generate_metadata.build_description(
            {"name": "X"}, "https://coshuma.com/tool/x.html", "This tool gives you guaranteed income!"
        )


def test_quality_gate_passes_on_correct_spec_video():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "ok.mp4"
        _make_test_video(video_path, 1080, 1920, duration=35)
        report = quality_gate.run_quality_gate(
            str(video_path),
            "https://coshuma.com/tool/gohighlevel.html?utm_source=youtube&utm_medium=shorts&utm_campaign=test",
            "A fine title",
            "A fine description with no banned claims.",
        )
        assert report["passed"], report["failures"]
        assert report["checks"]["resolution"] == "1080x1920"


def test_quality_gate_fails_on_wrong_resolution():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "wrong_res.mp4"
        _make_test_video(video_path, 1920, 1080, duration=35)
        report = quality_gate.run_quality_gate(
            str(video_path),
            "https://coshuma.com/tool/gohighlevel.html?utm_source=youtube&utm_medium=shorts&utm_campaign=test",
            "T", "D",
        )
        assert not report["passed"]
        assert any("resolution" in f for f in report["failures"])


def test_quality_gate_fails_on_missing_audio():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "silent.mp4"
        _make_test_video(video_path, 1080, 1920, duration=35, with_audio=False)
        report = quality_gate.run_quality_gate(
            str(video_path),
            "https://coshuma.com/tool/gohighlevel.html?utm_source=youtube&utm_medium=shorts&utm_campaign=test",
            "T", "D",
        )
        assert not report["passed"]
        assert any("audio" in f for f in report["failures"])


def test_quality_gate_fails_on_out_of_range_duration():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "tooshort.mp4"
        _make_test_video(video_path, 1080, 1920, duration=3)
        report = quality_gate.run_quality_gate(
            str(video_path),
            "https://coshuma.com/tool/gohighlevel.html?utm_source=youtube&utm_medium=shorts&utm_campaign=test",
            "T", "D",
        )
        assert not report["passed"]
        assert any("duration" in f for f in report["failures"])


def test_quality_gate_fails_on_bad_cta_host():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "ok2.mp4"
        _make_test_video(video_path, 1080, 1920, duration=35)
        report = quality_gate.run_quality_gate(
            str(video_path),
            "https://www.gohighlevel.com/?fp_ref=sangkwon56",
            "T", "D",
        )
        assert not report["passed"]
        assert any("host" in f for f in report["failures"])


def test_quality_gate_fails_on_duplicate_of_manifest_entry():
    manifest = json.loads((REPO_ROOT / "data" / "youtube_shorts_manifest.json").read_text(encoding="utf-8"))
    known_hash = manifest["entries"][0]["video_sha256"]
    assert known_hash in quality_gate.manifest_hashes()


def test_quality_gate_flags_banned_earnings_claims():
    with tempfile.TemporaryDirectory() as tmp:
        video_path = Path(tmp) / "ok3.mp4"
        _make_test_video(video_path, 1080, 1920, duration=35)
        report = quality_gate.run_quality_gate(
            str(video_path),
            "https://coshuma.com/tool/gohighlevel.html?utm_source=youtube&utm_medium=shorts&utm_campaign=test",
            "Guaranteed income with this tool!",
            "D",
        )
        assert not report["passed"]
        assert any("banned" in f for f in report["failures"])
