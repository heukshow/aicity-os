"""
Verify Manual Candidates Pricing (verify_manual_candidates.py)
=============================================================
Performs strict SSL HTTP verification of manual_candidates.json items.
Validates pricing_source_url HTTP 200 status, final redirected URL, and exact pricing_evidence_markers text in HTML body.
Saves verified runtime metadata to data/manual_candidates_verified.json.
Fail-closed: Exits with code 1 if manual_candidates.json cannot be parsed.
"""
import os
import sys
import json
import ssl
import urllib.request
from datetime import datetime, timezone

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUAL_FILE = os.path.join(PROJECT_DIR, "data", "manual_candidates.json")
VERIFIED_OUTPUT_FILE = os.path.join(PROJECT_DIR, "data", "manual_candidates_verified.json")

print("=" * 60)
print("🔒 VERIFY MANUAL CANDIDATES PRICING (verify_manual_candidates.py)")
print(f"Target Manual Candidates File: {MANUAL_FILE}")
print("=" * 60)

# Fail-closed check
if not os.path.exists(MANUAL_FILE):
    print(f"❌ FATAL: {MANUAL_FILE} does not exist.")
    sys.exit(1)

try:
    with open(MANUAL_FILE, "r", encoding="utf-8") as f:
        manual_candidates = json.load(f)
    if not isinstance(manual_candidates, list):
        print("❌ FATAL: manual_candidates.json must contain a JSON array.")
        sys.exit(1)
except Exception as e:
    print(f"❌ FATAL: Failed to read manual_candidates.json: {e}")
    sys.exit(1)

# Strict SSL Context
ssl_context = ssl.create_default_context()
now_iso_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

verified_candidates = []

for idx, tool in enumerate(manual_candidates):
    tid = tool.get("id")
    name = tool.get("name")
    off_url = tool.get("official_url")
    ps_url = tool.get("pricing_source_url")
    pv_flag = tool.get("pricing_verified")

    if not tid or not name or not off_url:
        print(f"❌ FATAL: Candidate #{idx+1} missing required id, name, or official_url.")
        sys.exit(1)

    tool["is_manual_override"] = True

    # 1. Verify Homepage Official URL SSL & HTTP
    req_off = urllib.request.Request(
        off_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    )
    try:
        res_off = urllib.request.urlopen(req_off, context=ssl_context, timeout=10)
        tool["http_verification_status"] = "verified_http_200"
    except urllib.error.HTTPError as e:
        if e.code == 403:
            tool["http_verification_status"] = "bot_blocked"
        else:
            tool["http_verification_status"] = f"http_{e.code}"
    except Exception:
        tool["http_verification_status"] = "failed"

    # 2. Verify Pricing Source URL & Evidence Markers if pricing_verified=true
    if pv_flag is True and ps_url:
        evidence_markers = tool.get("pricing_evidence_markers") or []
        req_ps = urllib.request.Request(
            ps_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        try:
            res_ps = urllib.request.urlopen(req_ps, context=ssl_context, timeout=10)
            status_code = res_ps.getcode()
            final_url = res_ps.geturl()
            raw_html_body = res_ps.read().decode("utf-8", errors="ignore")

            import html
            import re

            normalized_body = html.unescape(raw_html_body)
            normalized_body = re.sub(r"\s+", " ", normalized_body).casefold()

            valid_markers = (
                isinstance(evidence_markers, list)
                and len(evidence_markers) > 0
                and all(isinstance(marker, str) and bool(marker.strip()) for marker in evidence_markers)
            )

            missing_markers = []
            if valid_markers:
                for marker in evidence_markers:
                    normalized_marker = re.sub(r"\s+", " ", html.unescape(marker).strip()).casefold()
                    if normalized_marker not in normalized_body:
                        missing_markers.append(marker)

            verification_passed = (
                status_code == 200
                and valid_markers
                and not missing_markers
            )

            if verification_passed:
                tool["pricing_verified"] = True
                tool["pricing_verified_at"] = now_iso_utc
                tool["pricing_source_http_status"] = 200
                tool["pricing_source_final_url"] = final_url
                print(f"✅ Verified Pricing for '{name}' ({tid}): HTTP 200 | All Markers Verified: {evidence_markers}")
            else:
                print(f"⚠️ Pricing Evidence Failed for '{name}' ({tid}): Status={status_code}, Missing Markers={missing_markers}")
                tool["pricing"] = "See official pricing"
                tool["pricing_verified"] = False
                tool["pricing_source_url"] = None
                tool["pricing_verified_at"] = None
                tool["pricing_source_http_status"] = None
                tool["pricing_source_final_url"] = None
                tool["pricing_evidence_markers"] = None
                tool["currency"] = None
                tool["billing_period"] = None
                tool["evidence_source_type"] = None
        except Exception as e:
            print(f"⚠️ Pricing HTTP Request Failed for '{name}' ({tid}): {e}")
            tool["pricing"] = "See official pricing"
            tool["pricing_verified"] = False
            tool["pricing_source_url"] = None
            tool["pricing_verified_at"] = None
            tool["pricing_source_http_status"] = None
            tool["pricing_source_final_url"] = None
            tool["pricing_evidence_markers"] = None
            tool["currency"] = None
            tool["billing_period"] = None
            tool["evidence_source_type"] = None
    else:
        tool["pricing_verified"] = False
        tool["pricing_source_url"] = None
        tool["pricing_verified_at"] = None
        tool["pricing_source_http_status"] = None
        tool["pricing_source_final_url"] = None
        tool["pricing_evidence_markers"] = None
        tool["currency"] = None
        tool["billing_period"] = None
        tool["evidence_source_type"] = None

    verified_candidates.append(tool)

# Save runtime verified output
with open(VERIFIED_OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(verified_candidates, f, indent=2, ensure_ascii=False)

print(f"✅ Successfully verified and saved {len(verified_candidates)} manual candidates to {VERIFIED_OUTPUT_FILE}")
