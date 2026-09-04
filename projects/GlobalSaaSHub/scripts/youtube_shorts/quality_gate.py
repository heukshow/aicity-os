#!/usr/bin/env python3
"""Pre-upload quality gate for a rendered COSHUMA YouTube Short.

Run before any upload step (manual or API). Fails closed: any check that
cannot be verified counts as a failure, it is never silently skipped.

Checks implemented:
  - video file exists and is non-empty
  - duration is in the expected Shorts range (10-60s; house style targets 30-45s)
  - resolution is exactly 1080x1920 (9:16)
  - video codec is H.264 and frame rate is sane for Shorts
  - has both a video and an audio stream
  - not a byte-for-byte duplicate of any video already in the manifest
  - already-uploaded (affiliate_target, campaign_slug) pairs cannot upload again
  - CTA URL points at coshuma.com with youtube/shorts/campaign UTM attribution
  - description/title do not contain banned unverifiable-earnings phrases
  - price, promo-code and percentage claims must be grounded in either the
    tool page or structured primary-source evidence committed for that exact
    campaign

Usage:
    python3 quality_gate.py --video path/to.mp4 --coshuma-url "https://coshuma.com/tool/x.html?..." \
        --title "..." --description "..." --affiliate-target x --campaign-slug x
Exits 0 and prints a JSON report if everything passes; exits 1 otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT / "public"
MANIFEST_JSON = ROOT / "data" / "youtube_shorts_manifest.json"
CAMPAIGNS_JSON = ROOT / "data" / "youtube_shorts_campaigns.json"

BANNED_PHRASES = [
    "guaranteed income", "guaranteed money", "get rich", "risk-free profit",
    "passive income guaranteed", "무조건 돈", "100% 수익 보장", "확정 수익",
]

TARGET_MIN_S, TARGET_MAX_S = 30, 45
HARD_MIN_S, HARD_MAX_S = 10, 60
MIN_FPS, MAX_FPS = 24.0, 60.0


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


def _load_manifest() -> dict:
    if not MANIFEST_JSON.exists():
        return {"entries": []}
    return json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))


def manifest_hashes() -> set[str]:
    return {
        e.get("video_sha256")
        for e in _load_manifest().get("entries", [])
        if e.get("video_sha256")
    }


def coshuma_page_exists(coshuma_url: str) -> bool:
    path = urlparse(coshuma_url).path
    candidate = PUBLIC_DIR / path.lstrip("/")
    return candidate.exists()


def _parse_fps(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        if "/" in value:
            num, den = value.split("/", 1)
            den_f = float(den)
            return float(num) / den_f if den_f else 0.0
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def check_video(video_path: str, report: dict) -> None:
    p = Path(video_path)
    if not p.exists() or p.stat().st_size == 0:
        report["failures"].append(f"video file missing or empty: {video_path}")
        return

    report["checks"]["file_size_bytes"] = p.stat().st_size
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
        stream = v_streams[0]
        w, h = stream.get("width"), stream.get("height")
        report["checks"]["resolution"] = f"{w}x{h}"
        if (w, h) != (1080, 1920):
            report["failures"].append(f"resolution {w}x{h} != required 1080x1920 (9:16)")

        codec = (stream.get("codec_name") or "").lower()
        report["checks"]["video_codec"] = codec or None
        if codec != "h264":
            report["failures"].append(f"video codec {codec or 'unknown'} != required h264")

        fps = _parse_fps(stream.get("avg_frame_rate") or stream.get("r_frame_rate"))
        report["checks"]["fps"] = round(fps, 3) if fps else None
        if not (MIN_FPS <= fps <= MAX_FPS):
            report["failures"].append(
                f"frame rate {fps:.3f}fps outside supported range [{MIN_FPS:.0f}, {MAX_FPS:.0f}]"
            )
        elif not (29.0 <= fps <= 31.0):
            report["warnings"].append(f"frame rate {fps:.3f}fps differs from the 30fps house target")

    if not a_streams:
        report["failures"].append("no audio stream found (voice/captions/BGM all require an audio track)")
    else:
        report["checks"]["audio_codec"] = a_streams[0].get("codec_name")


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


def check_campaign_dedup(
    affiliate_target: str | None,
    campaign_slug: str | None,
    report: dict,
) -> None:
    if not affiliate_target or not campaign_slug:
        return
    matches = [
        e for e in _load_manifest().get("entries", [])
        if e.get("affiliate_target") == affiliate_target and e.get("campaign_slug") == campaign_slug
    ]
    uploaded = [e for e in matches if e.get("status") in {"uploaded", "published", "public"}]
    if uploaded:
        ids = [e.get("youtube_video_id") for e in uploaded if e.get("youtube_video_id")]
        suffix = f" ({', '.join(ids)})" if ids else ""
        report["failures"].append(
            f"campaign already uploaded for ({affiliate_target}, {campaign_slug}){suffix}; use a new campaign slug for a new creative"
        )
    elif matches:
        report["warnings"].append(
            f"campaign ({affiliate_target}, {campaign_slug}) already has a non-uploaded manifest entry; current run may replace its ready/rendered metadata"
        )


def _campaign_verified_claims(affiliate_target: str, campaign_slug: str | None) -> dict:
    if not CAMPAIGNS_JSON.exists():
        return {}
    campaigns = json.loads(CAMPAIGNS_JSON.read_text(encoding="utf-8"))
    campaign = campaigns.get(affiliate_target) or {}
    if campaign_slug and campaign.get("campaign_slug") != campaign_slug:
        return {}
    evidence = campaign.get("evidence") or {}
    if evidence.get("claim_status") != "verified_external_primary_source":
        return {}
    claims = evidence.get("verified_claims") or {}
    return {
        "promo_codes": {str(x).upper() for x in claims.get("promo_codes", [])},
        "discount_percentages": {int(x) for x in claims.get("discount_percentages", [])},
        "prices": {str(x).replace(" ", "") for x in claims.get("prices", [])},
        "source_type": evidence.get("type"),
        "verified_at": evidence.get("verified_at"),
    }


def check_price_and_discount_claims(
    text: str | None,
    affiliate_target: str | None,
    campaign_slug: str | None,
    report: dict,
) -> None:
    if not text:
        return

    price_claims = re.findall(r"\$\s?\d[\d,]*(?:\.\d+)?(?:\s*/\s*(?:mo|month|yr|year))?", text, flags=re.I)
    code_claims = [
        m.group(1).upper()
        for m in re.finditer(
            r"\b(?:promo\s+code|code)\s*(?:is|:|=)?\s*[\"']?([A-Z][A-Z0-9_-]{3,15})\b",
            text,
        )
    ]
    pct_claims = [int(x) for x in re.findall(r"\b(\d{1,3})\s?%", text)]

    if not (price_claims or code_claims or pct_claims):
        return
    if not affiliate_target:
        report["failures"].append("numeric/promo claim present but affiliate_target was not supplied for verification")
        return

    tool_page = PUBLIC_DIR / "tool" / f"{affiliate_target}.html"
    page_text = tool_page.read_text(encoding="utf-8") if tool_page.exists() else ""
    page_compact = page_text.replace(" ", "")
    verified = _campaign_verified_claims(affiliate_target, campaign_slug)

    if verified:
        report["checks"]["promotion_evidence"] = {
            "source_type": verified.get("source_type"),
            "verified_at": verified.get("verified_at"),
            "campaign_slug": campaign_slug,
        }

    for price in price_claims:
        normalized = price.replace(" ", "")
        if normalized not in page_compact and normalized not in verified.get("prices", set()):
            report["failures"].append(
                f"description/narration states price {price!r} without matching tool-page or structured primary-source evidence"
            )

    for code in code_claims:
        if code not in page_text.upper() and code not in verified.get("promo_codes", set()):
            report["failures"].append(
                f"description/narration mentions promo code {code!r} without matching tool-page or structured primary-source evidence"
            )

    for pct in pct_claims:
        if (
            f"{pct}%" not in page_text
            and f"{pct} %" not in page_text
            and pct not in verified.get("discount_percentages", set())
        ):
            report["failures"].append(
                f"description/narration claims {pct}% without matching tool-page or structured primary-source evidence"
            )


def run_quality_gate(
    video: str,
    coshuma_url: str | None,
    title: str | None,
    description: str | None,
    affiliate_target: str | None = None,
    campaign_slug: str | None = None,
    narration: str | None = None,
) -> dict:
    report = {"checks": {}, "warnings": [], "failures": []}
    check_video(video, report)
    check_cta_url(coshuma_url, report)
    check_copy(title, description, report)
    check_campaign_dedup(affiliate_target, campaign_slug, report)
    combined_copy = "\n".join(filter(None, [description, narration]))
    check_price_and_discount_claims(combined_copy, affiliate_target, campaign_slug, report)
    report["passed"] = len(report["failures"]) == 0
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True)
    parser.add_argument("--coshuma-url", required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--description", default="")
    parser.add_argument("--affiliate-target", default=None)
    parser.add_argument("--campaign-slug", default=None)
    parser.add_argument("--narration", default=None)
    args = parser.parse_args()

    report = run_quality_gate(
        args.video,
        args.coshuma_url,
        args.title,
        args.description,
        affiliate_target=args.affiliate_target,
        campaign_slug=args.campaign_slug,
        narration=args.narration,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
