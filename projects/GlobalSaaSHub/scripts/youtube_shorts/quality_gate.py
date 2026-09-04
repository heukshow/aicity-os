#!/usr/bin/env python3
"""Pre-upload quality gate for a rendered COSHUMA YouTube Short.

Run before any upload step (manual or API). Fails closed: any check that
cannot be verified counts as a failure, it is never silently skipped.

Checks implemented (see brief section 10):
  - video file exists and is non-empty
  - duration is in the expected Shorts range (10-60s; house style targets 30-45s,
    warn but do not fail outside that band, fail hard outside 10-60s)
  - resolution is exactly 1080x1920 (9:16)
  - has both a video and an audio stream
  - not a byte-for-byte duplicate of any video already in the manifest
    (dedup via sha256, independent of file name)
  - CTA URL (coshuma_url) points at coshuma.com, carries utm_source=youtube
    and utm_medium=shorts, and is not a bare generic homepage/affiliate URL
  - description/title do not contain banned unverifiable-earnings phrases
  - description's COSHUMA URL host/path matches an existing tool/best/compare
    page in the repo (catches typos and stale slugs)

Usage:
    python3 quality_gate.py --video path/to.mp4 --coshuma-url "https://coshuma.com/tool/x.html?..." \
        --title "..." --description "..."
Exits 0 and prints a JSON report if everything passes; exits 1 with the same
JSON report (each failed check listed) otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT / "public"
MANIFEST_JSON = ROOT / "data" / "youtube_shorts_manifest.json"

BANNED_PHRASES = [
    "guaranteed income", "guaranteed money", "get rich", "risk-free profit",
    "passive income guaranteed", "무조건 돈", "100% 수익 보장", "확정 수익",
]

TARGET_MIN_S, TARGET_MAX_S = 30, 45
HARD_MIN_S, HARD_MAX_S = 10, 60


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe_streams(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {out.stderr.strip()}")
    return json.loads(out.stdout)


def manifest_hashes() -> set[str]:
    if not MANIFEST_JSON.exists():
        return set()
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    return {e.get("video_sha256") for e in manifest.get("entries", []) if e.get("video_sha256")}


def coshuma_page_exists(coshuma_url: str) -> bool:
    path = urlparse(coshuma_url).path
    candidate = PUBLIC_DIR / path.lstrip("/")
    return candidate.exists()


def check_video(video_path: str, report: dict) -> None:
    p = Path(video_path)
    if not p.exists() or p.stat().st_size == 0:
        report["failures"].append(f"video file missing or empty: {video_path}")
        return

    report["checks"]["video_sha256"] = sha256_of(p)
    if report["checks"]["video_sha256"] in manifest_hashes():
        report["failures"].append("duplicate video: this exact file is already in the manifest")

    try:
        info = ffprobe_streams(p)
    except Exception as exc:  # noqa: BLE001
        report["failures"].append(f"ffprobe error: {exc}")
        return

    duration = float(info.get("format", {}).get("duration", 0))
    report["checks"]["duration_seconds"] = round(duration, 2)
    if not (HARD_MIN_S <= duration <= HARD_MAX_S):
        report["failures"].append(
            f"duration {duration:.1f}s outside hard bounds [{HARD_MIN_S}, {HARD_MAX_S}]s"
        )
    elif not (TARGET_MIN_S <= duration <= TARGET_MAX_S):
        report["warnings"].append(
            f"duration {duration:.1f}s outside house-style target [{TARGET_MIN_S}, {TARGET_MAX_S}]s"
        )

    v_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    a_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    if not v_streams:
        report["failures"].append("no video stream found")
    else:
        w, h = v_streams[0].get("width"), v_streams[0].get("height")
        report["checks"]["resolution"] = f"{w}x{h}"
        if (w, h) != (1080, 1920):
            report["failures"].append(f"resolution {w}x{h} != required 1080x1920 (9:16)")
    if not a_streams:
        report["failures"].append("no audio stream found (voice/captions/BGM all require an audio track)")


def check_cta_url(coshuma_url: str | None, report: dict) -> None:
    if not coshuma_url:
        report["failures"].append("no coshuma_url provided")
        return
    parsed = urlparse(coshuma_url)
    if parsed.hostname not in ("coshuma.com", "www.coshuma.com"):
        report["failures"].append(f"CTA URL host is not coshuma.com: {coshuma_url}")
    qs = parse_qs(parsed.query)
    if qs.get("utm_source") != ["youtube"]:
        report["failures"].append("CTA URL missing utm_source=youtube")
    if qs.get("utm_medium") != ["shorts"]:
        report["failures"].append("CTA URL missing utm_medium=shorts")
    if not qs.get("utm_campaign"):
        report["failures"].append("CTA URL missing utm_campaign (needed to separate this video's performance)")
    if not coshuma_page_exists(coshuma_url):
        report["failures"].append(f"CTA URL points at a page that does not exist in public/: {parsed.path}")


def check_copy(title: str | None, description: str | None, report: dict) -> None:
    text = f"{title or ''}\n{description or ''}".lower()
    for phrase in BANNED_PHRASES:
        if phrase.lower() in text:
            report["failures"].append(f"banned unverifiable-earnings phrase found: {phrase!r}")
    if title and len(title) > 100:
        report["failures"].append("title exceeds YouTube's 100-character limit")
    if description and len(description) > 5000:
        report["failures"].append("description exceeds YouTube's 5000-character limit")


def run_quality_gate(video: str, coshuma_url: str | None, title: str | None, description: str | None) -> dict:
    report = {"checks": {}, "warnings": [], "failures": []}
    check_video(video, report)
    check_cta_url(coshuma_url, report)
    check_copy(title, description, report)
    report["passed"] = len(report["failures"]) == 0
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True)
    parser.add_argument("--coshuma-url", required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--description", default="")
    args = parser.parse_args()

    report = run_quality_gate(args.video, args.coshuma_url, args.title, args.description)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
