#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
import requests

OUT = Path("/tmp/coshuma-character-short.mp4")
TMP = Path("/tmp/coshuma-sendcloud-video")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VOICE = "en-US-AriaNeural"

SEGMENTS = [
    {
        "key": "00-intro",
        "title": "Sendcloud Workflow",
        "subtitle": "From store connection to shipping analytics",
        "narration": "Sendcloud can centralize ecommerce shipping from store connection to post-purchase tracking. Here is a quick look at the workflow using official platform recordings provided to COSHUMA by Sendcloud.",
    },
    {
        "key": "01-connect",
        "title": "1. Store connection",
        "url": "https://media.ffycdn.net/eu/sendcloud/bMR7aoXQSMqjMADkkgsk.mov",
        "narration": "First, connect your ecommerce store. This example shows the WooCommerce integration flow.",
    },
    {
        "key": "02-rates",
        "title": "2. Sendcloud carrier rates",
        "url": "https://media.ffycdn.net/eu/sendcloud/pw9nMBiu1wQTgLa7J49L.mov",
        "narration": "Next, activate Sendcloud shipping rates to start using supported carriers.",
    },
    {
        "key": "03-contract",
        "title": "3. Existing carrier contract",
        "url": "https://media.ffycdn.net/eu/sendcloud/z7ni2xabBNht15YhjE8T.mov",
        "narration": "If you already have a carrier agreement, you can also connect your own contract.",
    },
    {
        "key": "04-calculator",
        "title": "4. Rate calculator",
        "url": "https://media.ffycdn.net/eu/sendcloud/tiZCMgPpTd1E3o7mm7R1.mov",
        "narration": "The rate calculator helps compare carrier options and estimated shipping costs before choosing.",
    },
    {
        "key": "05-orders",
        "title": "5. Order processing",
        "url": "https://media.ffycdn.net/eu/sendcloud/WMLZsSzsDbVnbm72ZXTz.mov",
        "narration": "Orders then flow into the Sendcloud dashboard, where labels and shipments can be processed in bulk.",
    },
    {
        "key": "06-rules",
        "title": "6. Shipping rules",
        "url": "https://media.ffycdn.net/eu/sendcloud/8KvFVp185rxXj3HiVsfW.mov",
        "narration": "Shipping rules automate decisions based on order conditions, reducing repetitive manual work.",
    },
    {
        "key": "07-tracking",
        "title": "7. Tracking emails",
        "url": "https://media.ffycdn.net/eu/sendcloud/KQurG1B8fdCsUSbZ7KiQ.mov",
        "narration": "You can also configure branded tracking emails to keep customers updated after purchase.",
    },
    {
        "key": "08-analytics",
        "title": "8. Analytics",
        "url": "https://media.ffycdn.net/eu/sendcloud/w2fNWn1uZ6Xaks9FyQWD.mov",
        "narration": "Finally, analytics brings shipment performance into one place for ongoing operational review.",
    },
    {
        "key": "09-outro",
        "title": "Test the workflow before you pay",
        "subtitle": "Current plans and terms: coshuma.com/tool/sendcloud.html",
        "narration": "Use these workflows during the free trial to see whether Sendcloud fits your store. Check current plans and terms on COSHUMA before you pay.",
    },
]


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1", str(path),
    ], text=True)
    return float(out.strip())


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


async def make_voice(text: str, target: Path) -> None:
    await edge_tts.Communicate(text, VOICE, rate="-2%").save(str(target))


def download(url: str, target: Path) -> None:
    with requests.get(url, timeout=120, stream=True) as response:
        response.raise_for_status()
        with target.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)


def render_card(item: dict, audio: Path, target: Path, outro: bool = False) -> None:
    d = duration(audio) + 1.0
    title = esc(item["title"])
    subtitle = esc(item.get("subtitle", ""))
    disclosure = "Affiliate disclosure: COSHUMA may earn a commission from eligible partner links." if outro else "Official Sendcloud platform recordings supplied for partner content."
    vf = (
        f"drawtext=fontfile={FONT_BOLD}:text='{title}':fontcolor=white:fontsize=70:"
        "x=(w-text_w)/2:y=390,"
        f"drawtext=fontfile={FONT_REG}:text='{subtitle}':fontcolor=white@0.78:fontsize=32:"
        "x=(w-text_w)/2:y=500,"
        f"drawtext=fontfile={FONT_REG}:text='{esc(disclosure)}':fontcolor=white@0.55:fontsize=24:"
        "x=(w-text_w)/2:y=965"
    )
    run(
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x0b0c10:s=1920x1080:r=30:d={d:.3f}",
        "-i", str(audio), "-vf", vf, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-r", "30", "-shortest", str(target)
    )


def render_clip(item: dict, source: Path, audio: Path, target: Path) -> None:
    title = esc(item["title"])
    vf = (
        "scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,"
        "drawbox=x=0:y=0:w=iw:h=145:color=black@0.70:t=fill,"
        f"drawtext=fontfile={FONT_BOLD}:text='{title}':fontcolor=white:fontsize=50:x=70:y=48,"
        "drawbox=x=0:y=1000:w=iw:h=80:color=black@0.55:t=fill,"
        f"drawtext=fontfile={FONT_REG}:text='COSHUMA  |  Official Sendcloud screen recording':"
        "fontcolor=white@0.78:fontsize=22:x=60:y=1028"
    )
    run(
        "ffmpeg", "-y", "-i", str(source), "-i", str(audio), "-vf", vf,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-ar", "48000", "-r", "30", "-shortest", str(target)
    )


async def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    audit = []
    for index, item in enumerate(SEGMENTS):
        audio = TMP / f"{item['key']}.mp3"
        await make_voice(item["narration"], audio)
        target = TMP / f"{index:02d}.mp4"
        if item.get("url"):
            source = TMP / f"{item['key']}.mov"
            download(item["url"], source)
            render_clip(item, source, audio, target)
            audit.append({"title": item["title"], "source": item["url"], "source_bytes": source.stat().st_size})
        else:
            render_card(item, audio, target, outro=index == len(SEGMENTS) - 1)
        rendered.append(target)

    concat = TMP / "concat.txt"
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in rendered) + "\n", encoding="utf-8")
    run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(OUT))
    report = {
        "output": str(OUT),
        "duration_seconds": round(duration(OUT), 3),
        "size_bytes": OUT.stat().st_size,
        "source_assets": audit,
        "voice": VOICE,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
