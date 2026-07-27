"""
GlobalSaaSHub Data Validator (validate_data.py)
==============================================
Validates candidate dataset (tools.next.json) before any HTML generation or DB commit.
Checks:
- Required schema fields and non-empty strings
- Alphanumeric kebab-case IDs
- Duplicate IDs, normalized names, or official domain URLs
- Valid http/https affiliate URLs
- Rating format (must be None or float 1.0-5.0)
- Prevents catastrophic data drops (must have >= 130 tools)
"""
import os
import sys
import json
import urllib.parse


if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEXT_JSON = os.path.join(PROJECT_DIR, "data", "tools.next.json")
if not os.path.exists(NEXT_JSON):
    print("❌ FATAL: Candidate dataset tools.next.json is strictly required but missing.")
    sys.exit(1)

TARGET_FILE = NEXT_JSON

print("=" * 60)
print(f"🔍 CANDIDATE DATASET VALIDATION (validate_data.py)")
print(f"Target File: {TARGET_FILE}")
print("=" * 60)

try:

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        tools = json.load(f)
except Exception as e:
    print(f"❌ FATAL: Failed to parse JSON candidate dataset: {e}")
    sys.exit(1)

total_count = len(tools)
print(f"1. Total Candidate Tools Loaded: {total_count}")

if total_count < 130:
    print(f"❌ FATAL: Candidate dataset tool count ({total_count}) dropped below safe minimum threshold (130).")
    sys.exit(1)

seen_ids = set()
seen_names = set()
seen_domains = set()
errors = []

import re

for idx, tool in enumerate(tools):
    tid = tool.get("id")
    name = tool.get("name")
    aff_url = tool.get("affiliate_url")
    rating = tool.get("rating")
    
    # 1. Required fields
    if not tid or not name or not aff_url:
        errors.append(f"Tool #{idx+1} missing required id, name, or affiliate_url.")
        continue

    # 1b. Kebab-case Alphanumeric ID format check
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', str(tid)):
        errors.append(f"Tool #{idx+1} ID '{tid}' is not valid lowercase kebab-case.")

        
    # 2. Duplicate ID
    if tid in seen_ids:
        errors.append(f"Duplicate Tool ID found: '{tid}'")
    seen_ids.add(tid)
    
    # 3. Duplicate Normalized Name
    norm_name = name.lower().replace(" ", "").replace("-", "").replace(".", "")
    if norm_name in seen_names:
        errors.append(f"Duplicate Tool Name found: '{name}' ({tid})")
    seen_names.add(norm_name)
    
    # 4. URL Validation & Domain Deduplication
    # Explicit allowlist: only verified cases where two DISTINCT products legitimately share a domain.
    # - Same-service ID variants (e.g., "make" vs "make-com") must be MERGED in tools.json, not allowlisted.
    # - Only add entries here with evidence of a real acquisition or genuinely separate products.
    # Format: { "domain": {"ids": ["tool-id-1", "tool-id-2"], "reason": "source / evidence"} }
    DOMAIN_ALLOWLIST = {
        # No verified entries yet. Add only with explicit evidence.
    }
    if not aff_url.startswith("http"):
        errors.append(f"Invalid URL scheme for '{name}': {aff_url}")
    else:
        try:
            domain = urllib.parse.urlparse(aff_url).netloc.replace("www.", "")
            if domain and domain in seen_domains:
                # Check allowlist
                allowlist_entry = DOMAIN_ALLOWLIST.get(domain)
                if allowlist_entry and tid in allowlist_entry["ids"]:
                    print(f"ℹ️ Allowlisted shared domain '{domain}' for '{name}' ({tid}): {allowlist_entry['reason']}")
                else:
                    errors.append(f"Duplicate domain FAIL: '{domain}' already registered. Tool '{name}' ({tid}) must be merged or added to verified allowlist.")
            if domain:
                seen_domains.add(domain)
        except Exception:
            pass


    # 5. Rating Validation
    if rating is not None and not (isinstance(rating, (int, float)) and 1.0 <= rating <= 5.0):
        errors.append(f"Invalid rating value for '{name}': {rating}")

id_kebab_errors = [e for e in errors if "ID" in e]
print(f"2. ID & Kebab-case Audit:       0 issues" if len(id_kebab_errors) == 0 else f"2. ID & Kebab-case Audit:       {len(id_kebab_errors)} ISSUES FOUND")
print(f"3. Domain Deduplication Audit:    {len(seen_domains)} unique domains")
print(f"4. URL Scheme & Domain Check:     Format check only (No live HTTP ping)")
print(f"5. Total Validation Errors:       {len(errors)}")



print("=" * 60)
if errors:
    print("❌ CANDIDATE DATASET VALIDATION RESULT: FAIL")
    for err in errors[:10]:
        print(f"   - {err}")
    print("=" * 60)
    sys.exit(1)
else:
    print("✅ CANDIDATE DATASET VALIDATION RESULT: PASS")
    print("=" * 60)
    sys.exit(0)
