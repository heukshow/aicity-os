#!/usr/bin/env python3
"""Build a photorealistic-host COSHUMA Short from real product web UI captures.

The presenter is a stable photorealistic master image reused across episodes.
The browser frames are live captures of official product pages/docs. The output
is a vertical Short with natural TTS, real UI, cursor highlights, and minimal
on-screen copy. No paid generation API is required.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
REQ = ROOT / "data" / "youtube_character_upload_request.json"
OUT = Path("/tmp/coshuma-character-short.mp4")
TMP = Path("/tmp/coshuma-real-ui")

W, H = 1080, 1920
BG = (8, 12, 20)
PANEL = (18, 24, 38)
WHITE = (244, 247, 252)
MUTED = (170, 181, 199)
PURPLE = (124, 58, 237)
TEAL = (45, 212, 191)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MIN_CAPTURE_BYTES = 4_000


def run(cmd: list[str], **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def font(sz: int, bold: bool = True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, sz)


def chrome_bin() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("No headless Chrome/Chromium binary found")


def screenshot(urls: list[str], out: Path) -> str:
    """Capture the first usable official page; never substitute a fabricated UI."""
    last_error = None
    for url in urls:
        try:
            if out.exists():
                out.unlink()
            run([
                chrome_bin(), "--headless=new", "--no-sandbox", "--disable-gpu",
                "--hide-scrollbars", "--window-size=1440,900",
                "--virtual-time-budget=5000",
                f"--screenshot={out}", url,
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if out.exists() and out.stat().st_size >= MIN_CAPTURE_BYTES:
                with Image.open(out) as probe:
                    if probe.width >= 1000 and probe.height >= 600:
                        return url
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"No usable official browser capture for {out.name}; last_error={last_error}")


def rounded_paste(bg: Image.Image, im: Image.Image, box: tuple[int, int, int, int], radius=28):
    x, y, w, h = box
    im = ImageOps.fit(im, (w, h), Image.Resampling.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    bg.paste(im, (x, y), mask)


def screen_frame(bg: Image.Image, shot: Image.Image, box, cursor=(0.72, 0.35)):
    x, y, w, h = box
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle((x - 10, y - 42, x + w + 10, y + h + 10), radius=30,
                        fill=(25, 30, 44), outline=(65, 75, 96), width=3)
    d.rounded_rectangle((x, y - 30, x + w, y), radius=12, fill=(45, 52, 68))
    for i, color in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse((x + 18 + i * 30, y - 20, x + 30 + i * 30, y - 8), fill=color)
    inner = ImageOps.fit(shot, (w, h), Image.Resampling.LANCZOS, centering=(0.5, 0.15))
    bg.paste(inner, (x, y))
    cx = x + int(cursor[0] * w)
    cy = y + int(cursor[1] * h)
    d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), outline=(255, 85, 85), width=8)
    d.polygon(((cx, cy), (cx + 18, cy + 42), (cx + 26, cy + 22), (cx + 48, cy + 18)), fill=WHITE)


def presenter(bg: Image.Image, person: Image.Image, box):
    x, y, w, h = box
    rounded_paste(bg, person, box, 36)
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle((x + 18, y + h - 116, x + w - 18, y + h - 20), radius=24, fill=(8, 12, 20))
    d.text((x + 40, y + h - 96), "CORA", font=font(42), fill=WHITE)
    d.text((x + 40, y + h - 51), "COSHUMA TOOL GUIDE", font=font(20), fill=TEAL)


def title(bg: Image.Image, kicker: str, main: str, sub: str):
    d = ImageDraw.Draw(bg)
    d.text((72, 62), kicker, font=font(26), fill=TEAL)
    d.text((72, 105), main, font=font(52), fill=WHITE)
    d.text((72, 174), sub, font=font(27, False), fill=MUTED)


def make_scene(idx: int, person: Image.Image, shot: Image.Image, kicker: str, main: str,
               sub: str, cursor, bottom: str, layout: str) -> Path:
    bg = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(bg)
    d.rectangle((0, 0, W, 12), fill=PURPLE)
    d.rectangle((W - 180, 0, W, 12), fill=TEAL)
    title(bg, kicker, main, sub)
    if layout == "split":
        presenter(bg, person, (70, 350, 330, 1040))
        screen_frame(bg, shot, (430, 350, 590, 1040), cursor)
        by = 1570
    else:
        screen_frame(bg, shot, (70, 320, 940, 1120), cursor)
        presenter(bg, person, (735, 1470, 275, 390))
        by = 1480
    d.rounded_rectangle((70, by, 1010, 1830), radius=34, fill=PANEL)
    d.text((105, by + 74), bottom, font=font(34), fill=WHITE)
    d.text((105, by + 137), "Real product UI — not a text-only slideshow", font=font(23, False), fill=MUTED)
    if idx == 5:
        d.text((105, by + 191), "coshuma.com/tool/chatbase.html", font=font(25), fill=TEAL)
    path = TMP / f"scene{idx}.jpg"
    bg.save(path, quality=94)
    return path


def build() -> dict:
    request = json.loads(REQ.read_text(encoding="utf-8"))
    TMP.mkdir(parents=True, exist_ok=True)

    presenter_url = request["presenter_image_url"]
    run(["curl", "-fL", "--retry", "3", presenter_url, "-o", str(TMP / "presenter.jpg")])

    # Every fallback is still an official Chatbase page. We prefer the exact docs
    # section but gracefully use the full guide/home/pricing page if an anchor
    # produces a tiny screenshot on GitHub's headless browser.
    captures = [
        (["https://www.chatbase.co/"], "home.png"),
        ([
            "https://www.chatbase.co/docs/user-guides/quick-start/your-first-agent#navigate-to-your-dashboard",
            "https://www.chatbase.co/docs/user-guides/quick-start/your-first-agent",
            "https://www.chatbase.co/",
        ], "agent.png"),
        ([
            "https://www.chatbase.co/docs/user-guides/quick-start/your-first-agent#choose-your-training-data",
            "https://www.chatbase.co/docs/user-guides/quick-start/your-first-agent",
            "https://www.chatbase.co/",
        ], "data.png"),
        (["https://www.chatbase.co/pricing", "https://www.chatbase.co/"], "pricing.png"),
    ]
    capture_sources = {}
    for urls, name in captures:
        capture_sources[name] = screenshot(urls, TMP / name)

    person = Image.open(TMP / "presenter.jpg").convert("RGB")
    home = Image.open(TMP / "home.png").convert("RGB")
    agent = Image.open(TMP / "agent.png").convert("RGB")
    data = Image.open(TMP / "data.png").convert("RGB")
    pricing = Image.open(TMP / "pricing.png").convert("RGB")

    scenes = [
        make_scene(1, person, home, "COSHUMA • CHATBASE", "STOP REPEATING SUPPORT",
                   "Train an agent on the business knowledge you already have.", (0.76, 0.18),
                   "REAL TOOL • REAL WORKFLOW", "split"),
        make_scene(2, person, agent, "STEP 1", "CREATE THE AGENT",
                   "Start from Chatbase's real workflow.", (0.73, 0.50),
                   "CREATE → TRAIN → TEST", "full"),
        make_scene(3, person, data, "STEP 2", "CONNECT REAL DATA",
                   "Use websites, documents, Q&A or Notion.", (0.63, 0.49),
                   "WEBSITE • DOCS • Q&A • NOTION", "full"),
        make_scene(4, person, home, "STEP 3", "DEPLOY WHERE CUSTOMERS ASK",
                   "Use the agent for repetitive customer conversations.", (0.71, 0.56),
                   "CHAT • EMAIL • VOICE", "full"),
        make_scene(5, person, pricing, "BUSINESS ANGLE", "SELL THE IMPLEMENTATION",
                   "Setup, training, deployment and maintenance are real services.", (0.72, 0.22),
                   "SETUP • DEPLOY • MAINTAIN", "split"),
    ]

    voice = TMP / "voice.mp3"
    run(["edge-tts", "--voice", "en-US-AriaNeural", "--rate=+10%",
         "--text", request["narration"], "--write-media", str(voice)])

    clips: list[Path] = []
    for i, scene in enumerate(scenes, start=1):
        clip = TMP / f"clip{i}.mp4"
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(scene), "-t", "6.8",
            "-vf", "scale=1080:1920,zoompan=z='min(zoom+0.00035,1.035)':d=204:s=1080x1920:fps=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", str(clip)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clips.append(clip)

    concat = TMP / "list.txt"
    concat.write_text("\n".join(f"file '{path}'" for path in clips) + "\n", encoding="utf-8")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-i", str(voice),
        "-filter_complex", "[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[a1]",
        "-map", "0:v", "-map", "[a1]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", str(OUT)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "stream=width,height",
        "-show_entries", "format=duration,size", "-of", "json", str(OUT)
    ], text=True))
    probe["capture_sources"] = capture_sources
    return probe


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
