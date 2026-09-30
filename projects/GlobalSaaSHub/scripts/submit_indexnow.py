#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://api.indexnow.org/indexnow"

def get(url: str, timeout: int = 12) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "COSHUMA-IndexNow/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read(512).decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(512).decode("utf-8", errors="ignore")

def post_json(url: str, payload: dict, timeout: int = 20) -> tuple[int, str]:
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "COSHUMA-IndexNow/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, res.read(1024).decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(1024).decode("utf-8", errors="ignore")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls-file", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--key-location", required=True)
    args = parser.parse_args()

    doc = json.loads(Path(args.urls_file).read_text(encoding="utf-8"))
    urls = doc.get("urlList") or []
    if not urls:
        print("IndexNow: no changed URLs to submit")
        return 0

    if len(urls) > 10000:
        raise SystemExit("IndexNow refuses more than 10,000 URLs per request")

    expected = args.key.strip()
    key_ready = False
    for attempt in range(10):
        status, body = get(args.key_location)
        if status == 200 and body.strip() == expected:
            key_ready = True
            break
        if attempt < 9:
            time.sleep(3)
    if not key_ready:
        raise SystemExit("IndexNow key is not yet reachable on the canonical domain")

    payload = {
        "host": "coshuma.com",
        "key": expected,
        "keyLocation": args.key_location,
        "urlList": urls,
    }

    last_status = None
    last_body = ""
    max_attempts = 20
    for attempt in range(max_attempts):
        status, body = post_json(ENDPOINT, payload)
        last_status, last_body = status, body
        if status in (200, 202):
            print(json.dumps({
                "endpoint": ENDPOINT,
                "status": status,
                "url_count": len(urls),
                "bootstrap": bool(doc.get("bootstrap")),
            }))
            return 0

        verification_pending = (
            status == 403
            and "SiteVerificationNotCompleted" in body
        )
        transient = status in (429, 500, 502, 503, 504)
        if not verification_pending and not transient:
            break

        if attempt < max_attempts - 1:
            if verification_pending:
                time.sleep(10)
            else:
                time.sleep(min(20, 4 * (attempt + 1)))

    raise SystemExit(f"IndexNow submission failed: HTTP {last_status} {last_body[:300]}")

if __name__ == "__main__":
    raise SystemExit(main())
