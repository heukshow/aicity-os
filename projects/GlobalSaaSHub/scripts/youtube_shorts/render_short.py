#!/usr/bin/env python3
"""Render a free, deterministic COSHUMA vertical Short with ffmpeg + espeak-ng.

This renderer is intentionally self-contained: no paid API and no external
media download. It produces the established COSHUMA card/motion-graphic style
at 1080x1920 with spoken narration and timed text cards. It is suitable for
dry-run validation and can be replaced with a richer verified media asset when
one is available.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

import generate_script

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "data" / "youtube_shorts_output"


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def probe_duration(path: Path) -> float:
    out = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ])
    return float(out.stdout.strip())


def font_path() -> str:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return item
    raise RuntimeError("No supported system font found for ffmpeg drawtext")


def wrap_card(text: str, width: int = 27) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False))


def render(tool_id: str, output: str | None = None) -> dict:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe are required")
    speaker = shutil.which("espeak-ng") or shutil.which("espeak")
    if not speaker:
        raise RuntimeError("espeak-ng (or espeak) is required for free narration")

    script = generate_script.generate(tool_id)
    out_dir = DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path(output) if output else out_dir / f"coshuma_{script['campaign_slug']}.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="coshuma-short-") as tmp:
        tmpdir = Path(tmp)
        wav = tmpdir / "narration.wav"
        run([speaker, "-v", "en-us", "-s", "165", "-w", str(wav), script["narration"]])
        narration_duration = probe_duration(wav)
        duration = max(32.0, min(55.0, narration_duration + 2.5))
        if narration_duration > 54.0:
            raise RuntimeError(f"Narration too long for Shorts house style: {narration_duration:.1f}s")

        cards = script["cards"]
        card_files = []
        for i, card in enumerate(cards):
            p = tmpdir / f"card_{i}.txt"
            p.write_text(wrap_card(card), encoding="utf-8")
            card_files.append(p)

        font = font_path()
        slot = duration / len(card_files)
        escaped_comma = r"\,"
        filters = [
            "drawbox=x=70:y=120:w=940:h=1460:color=0x151827@0.96:t=fill",
            f"drawtext=fontfile='{font}':text='COSHUMA':fontcolor=0xC4B5FD:fontsize=58:x=(w-text_w)/2:y=175",
            f"drawtext=fontfile='{font}':text='{script['tool_name']}':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=285",
        ]
        for i, card_file in enumerate(card_files):
            start = i * slot
            end = duration if i == len(card_files) - 1 else (i + 1) * slot
            filters.append(
                "drawtext="
                f"fontfile='{font}':textfile='{card_file}':"
                "fontcolor=white:fontsize=56:line_spacing=18:"
                "x=(w-text_w)/2:y=(h-text_h)/2:"
                f"enable='between(t{escaped_comma}{start:.3f}{escaped_comma}{end:.3f})'"
            )
        filters.extend([
            "drawbox=x=90:y=1660:w=900:h=150:color=0x7C3AED@0.92:t=fill",
            f"drawtext=fontfile='{font}':text='Full guide: coshuma.com':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=1708",
        ])

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x090B11:s=1080x1920:r=30:d={duration:.3f}",
            "-i", str(wav),
            "-vf", ",".join(filters),
            "-af", "apad",
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart",
            str(out_path),
        ]
        run(cmd)

    return {
        "tool_id": tool_id,
        "campaign_slug": script["campaign_slug"],
        "script_hash": script["script_hash"],
        "output": str(out_path),
        "duration_seconds": round(probe_duration(out_path), 2),
        "resolution": "1080x1920",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool_id")
    parser.add_argument("--output")
    args = parser.parse_args()
    print(json.dumps(render(args.tool_id, args.output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
