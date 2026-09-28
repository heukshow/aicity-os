#!/usr/bin/env python3
"""Render a verified COSHUMA Short from a real UI screen capture.

This renderer is intentionally deterministic:
- actual browser/app capture is the primary visual
- 1080x1920 H.264/AAC output at 30fps
- narration is loudness-normalized
- captions are one line at a time to avoid giant/garbled subtitle rendering
- output never truncates narration
- 30-45s house-style duration is enforced
- final result is held on screen after the interaction sequence

Example:
  python3 render_verified_short.py \
    --capture raw.mp4 \
    --voice narration.mp3 \
    --final-still final.png \
    --captions captions.json \
    --crop 900:0:720:1080 \
    --capture-seconds 21 \
    --label "COSHUMA / REAL CANVA EDITOR" \
    --output out.mp4
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import tempfile
from pathlib import Path

TARGET_MIN_S = 30.0
TARGET_MAX_S = 45.0
VOICE_TAIL_S = 1.5
DEFAULT_FONT_SIZE = 38
MAX_CAPTION_CHARS = 56


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    return float(out.stdout.strip())


def compute_target_duration(voice_seconds: float, capture_seconds: float) -> float:
    duration = max(TARGET_MIN_S, voice_seconds + VOICE_TAIL_S, capture_seconds + 2.0)
    if duration > TARGET_MAX_S:
        raise ValueError(
            f"required output duration {duration:.2f}s exceeds {TARGET_MAX_S:.0f}s house limit"
        )
    return round(duration, 3)


def load_captions(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("captions") if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        raise ValueError("captions JSON must contain a non-empty captions list")
    out = []
    for i, item in enumerate(items, 1):
        text = " ".join(str(item["text"]).split())
        start = float(item["start"])
        end = float(item["end"])
        if not text:
            raise ValueError(f"caption {i} is empty")
        if len(text) > MAX_CAPTION_CHARS:
            raise ValueError(
                f"caption {i} exceeds {MAX_CAPTION_CHARS} chars; split it into one-line phrases"
            )
        if start < 0 or end <= start:
            raise ValueError(f"caption {i} has invalid timing")
        out.append({"text": text, "start": start, "end": end})
    return out


def parse_crop(value: str) -> tuple[int, int, int, int]:
    try:
        x, y, w, h = (int(v) for v in value.split(":"))
    except Exception as exc:
        raise ValueError("--crop must be x:y:width:height") from exc
    if min(x, y, w, h) < 0 or w == 0 or h == 0:
        raise ValueError("--crop values must be non-negative and width/height > 0")
    return x, y, w, h


def make_visual_filter(crop: tuple[int, int, int, int], label: str) -> str:
    x, y, w, h = crop
    safe_label = label.replace("'", "’").replace(":", " -")
    return (
        f"crop={w}:{h}:{x}:{y},"
        "scale=1000:1500,"
        "pad=1080:1920:40:130:color=0x080B14,"
        "drawbox=x=40:y=34:w=520:h=66:color=0x6D4AFF@0.95:t=fill,"
        f"drawtext=font='Arial':text='{safe_label}':"
        "fontcolor=white:fontsize=30:x=64:y=53"
    )


def render(args: argparse.Namespace) -> dict:
    capture = Path(args.capture).resolve()
    voice = Path(args.voice).resolve()
    final_still = Path(args.final_still).resolve()
    output = Path(args.output).resolve()
    captions_path = Path(args.captions).resolve()
    for path in (capture, voice, final_still, captions_path):
        if not path.exists():
            raise FileNotFoundError(path)

    captions = load_captions(captions_path)
    voice_s = probe_duration(voice)
    capture_s = min(float(args.capture_seconds), probe_duration(capture))
    target_s = compute_target_duration(voice_s, capture_s)
    final_hold_s = round(target_s - capture_s, 3)
    crop = parse_crop(args.crop)

    with tempfile.TemporaryDirectory(prefix="coshuma_short_") as tmp:
        tmpdir = Path(tmp)
        editor = tmpdir / "editor.mp4"
        still = tmpdir / "still.mp4"
        visual = tmpdir / "visual.mp4"

        editor_filter = make_visual_filter(crop, args.label)
        still_filter = make_visual_filter(crop, args.final_label)

        _run([
            "ffmpeg", "-y", "-i", str(capture), "-t", str(capture_s),
            "-vf", editor_filter, "-an", "-c:v", "libx264", "-preset", "medium",
            "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30", str(editor),
        ])
        _run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(final_still), "-t", str(final_hold_s),
            "-vf", still_filter, "-an", "-c:v", "libx264", "-preset", "medium",
            "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30", str(still),
        ])
        _run([
            "ffmpeg", "-y", "-i", str(editor), "-i", str(still),
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
            "-map", "[v]", "-t", str(target_s), "-c:v", "libx264",
            "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(visual),
        ])

        filters = []
        for i, cap in enumerate(captions, 1):
            capfile = tmpdir / f"cap_{i:02d}.txt"
            capfile.write_text(cap["text"], encoding="utf-8", newline="\n")
            filters.append(
                "drawtext=font='Arial':"
                f"textfile='{capfile.as_posix()}':"
                f"fontcolor=white:fontsize={args.caption_font_size}:"
                "box=1:boxcolor=black@0.74:boxborderw=14:"
                "x=(w-text_w)/2:y=h-260:"
                f"enable='between(t,{cap['start']:.3f},{cap['end']:.3f})'"
            )
        vf = ",".join(filters)

        output.parent.mkdir(parents=True, exist_ok=True)
        _run([
            "ffmpeg", "-y", "-i", str(visual), "-i", str(voice),
            "-vf", vf,
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,apad=pad_dur=5",
            "-t", str(target_s),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", str(output),
        ])

    return {
        "output": str(output),
        "duration_seconds": target_s,
        "voice_seconds": round(voice_s, 3),
        "capture_seconds": capture_s,
        "final_hold_seconds": final_hold_s,
        "caption_count": len(captions),
        "resolution": "1080x1920",
        "video_codec": "h264",
        "audio_codec": "aac",
        "fps": 30,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", required=True)
    p.add_argument("--voice", required=True)
    p.add_argument("--final-still", required=True)
    p.add_argument("--captions", required=True)
    p.add_argument("--crop", required=True, help="x:y:width:height in the source capture")
    p.add_argument("--capture-seconds", type=float, required=True)
    p.add_argument("--label", default="COSHUMA / REAL PRODUCT")
    p.add_argument("--final-label", default="COSHUMA / FINAL RESULT")
    p.add_argument("--caption-font-size", type=int, default=DEFAULT_FONT_SIZE)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    print(json.dumps(render(args), indent=2))


if __name__ == "__main__":
    main()
