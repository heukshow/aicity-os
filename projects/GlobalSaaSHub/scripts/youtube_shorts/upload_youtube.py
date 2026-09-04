#!/usr/bin/env python3
"""Upload a rendered Short with YouTube Data API v3 using OAuth refresh-token credentials.

Credentials are read only from environment variables:
  YOUTUBE_CLIENT_ID
  YOUTUBE_CLIENT_SECRET
  YOUTUBE_REFRESH_TOKEN

Default visibility is private. This module never creates or modifies Google
Cloud projects and never performs the interactive OAuth consent flow.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_JSON = ROOT / "data" / "youtube_shorts_manifest.json"
TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_INIT_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"


def require_env() -> dict:
    names = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    values = {name: os.environ.get(name) for name in names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError("Missing YouTube OAuth environment variables: " + ", ".join(missing))
    return values


def access_token(creds: dict) -> str:
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": creds["YOUTUBE_CLIENT_ID"],
            "client_secret": creds["YOUTUBE_CLIENT_SECRET"],
            "refresh_token": creds["YOUTUBE_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"OAuth refresh failed ({response.status_code}): {response.text[:500]}")
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("OAuth refresh response did not contain access_token")
    return token


def upload(video: Path, title: str, description: str, privacy: str = "private") -> str:
    if privacy not in {"private", "unlisted", "public"}:
        raise ValueError("privacy must be private, unlisted, or public")
    if not video.exists() or video.stat().st_size == 0:
        raise FileNotFoundError(video)

    token = access_token(require_env())
    metadata = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "categoryId": "28"
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }
    init = requests.post(
        UPLOAD_INIT_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(video.stat().st_size),
        },
        json=metadata,
        timeout=30,
    )
    if init.status_code not in {200, 201}:
        raise RuntimeError(f"YouTube upload initialization failed ({init.status_code}): {init.text[:800]}")
    location = init.headers.get("Location")
    if not location:
        raise RuntimeError("YouTube resumable upload response did not include Location header")

    with video.open("rb") as fh:
        put = requests.put(
            location,
            headers={"Content-Type": "video/mp4"},
            data=fh,
            timeout=900,
        )
    if put.status_code not in {200, 201}:
        raise RuntimeError(f"YouTube video upload failed ({put.status_code}): {put.text[:800]}")
    video_id = put.json().get("id")
    if not video_id:
        raise RuntimeError("YouTube upload succeeded without a returned video id")
    return video_id


def record_manifest(campaign_slug: str, video_id: str, privacy: str) -> None:
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    matches = [e for e in manifest.get("entries", []) if e.get("campaign_slug") == campaign_slug]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one manifest entry for campaign_slug={campaign_slug}, found {len(matches)}")
    entry = matches[0]
    entry["youtube_video_id"] = video_id
    entry["youtube_url"] = f"https://youtube.com/shorts/{video_id}"
    entry["uploaded_at"] = datetime.now(timezone.utc).isoformat()
    entry["youtube_privacy"] = privacy
    entry["status"] = "uploaded_private" if privacy == "private" else "uploaded"
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--campaign-slug", required=True)
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    args = parser.parse_args()

    video_id = upload(Path(args.video), args.title, args.description, args.privacy)
    record_manifest(args.campaign_slug, video_id, args.privacy)
    print(json.dumps({"youtube_video_id": video_id, "privacy": args.privacy}, indent=2))


if __name__ == "__main__":
    main()
