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
    off_url = tool.get("official_url")
    aff_url = tool.get("affiliate_url")
    currency = tool.get("currency")
    billing_period = tool.get("billing_period")
    evidence_type = tool.get("evidence_source_type")
    rating = tool.get("rating")
    
    # 1. Required fields
    if not tid or not name or not off_url:
        errors.append(f"Tool #{idx+1} missing required id, name, or official_url.")
        continue

    # 1b. Kebab-case Alphanumeric ID format check
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', str(tid)):
        errors.append(f"Tool #{idx+1} ID '{tid}' is not valid lowercase kebab-case.")

    # 1c. Strict Field Type & URL format checks
    if not off_url.startswith("https://") and not off_url.startswith("http://"):
        errors.append(f"Tool '{tid}' official_url is not a valid HTTP/HTTPS URL: '{off_url}'")

    if aff_url is not None and not aff_url.startswith("https://") and not aff_url.startswith("http://"):
        errors.append(f"Tool '{tid}' affiliate_url is not a valid HTTP/HTTPS URL: '{aff_url}'")

    if ps_url is not None and not ps_url.startswith("https://") and not ps_url.startswith("http://"):
        errors.append(f"Tool '{tid}' pricing_source_url is not a valid HTTP/HTTPS URL: '{ps_url}'")

    if not isinstance(pv_flag, bool):
        errors.append(f"Tool '{tid}' pricing_verified must be boolean (got {type(pv_flag).__name__}).")

    # Allowed enum values
    ALLOWED_CURRENCIES = {"USD", "GBP", "EUR", "CAD", "AUD", "BRL"}
    ALLOWED_BILLING_PERIODS = {"monthly", "annual", "annual/monthly", "per_user", "usage_based", "mixed"}
    ALLOWED_EVIDENCE_TYPES = {"official_pricing_page", "official_help_page", "manual_override"}

    if currency is not None and currency not in ALLOWED_CURRENCIES:
        errors.append(f"Tool '{tid}' currency '{currency}' not in allowed set: {ALLOWED_CURRENCIES}")

    if billing_period is not None and billing_period not in ALLOWED_BILLING_PERIODS:
        errors.append(f"Tool '{tid}' billing_period '{billing_period}' not in allowed set: {ALLOWED_BILLING_PERIODS}")

    if evidence_type is not None and evidence_type not in ALLOWED_EVIDENCE_TYPES:
        errors.append(f"Tool '{tid}' evidence_source_type '{evidence_type}' not in allowed set: {ALLOWED_EVIDENCE_TYPES}")

    # Strict verified/unverified state consistency
    if not pv_flag:
        if ps_url is not None:
            errors.append(f"Tool '{tid}' pricing_verified is False but pricing_source_url is not null.")
        if pv_at is not None:
            errors.append(f"Tool '{tid}' pricing_verified is False but pricing_verified_at is not null.")
        if evidence_type is not None:
            errors.append(f"Tool '{tid}' pricing_verified is False but evidence_source_type is not null.")
        if currency is not None:
            errors.append(f"Tool '{tid}' pricing_verified is False but currency is not null.")
        if billing_period is not None:
            errors.append(f"Tool '{tid}' pricing_verified is False but billing_period is not null.")
    else:
        if not ps_url:
            errors.append(f"Tool '{tid}' pricing_verified is True but pricing_source_url is missing or null.")
        if not pv_at or not re.match(r'^\d{4}-\d{2}-\d{2}$', str(pv_at)):
            errors.append(f"Tool '{tid}' pricing_verified is True but pricing_verified_at '{pv_at}' is not a valid YYYY-MM-DD date.")
        if not currency:
            errors.append(f"Tool '{tid}' pricing_verified is True but currency is missing or null.")
        if not billing_period:
            errors.append(f"Tool '{tid}' pricing_verified is True but billing_period is missing or null.")
        if not evidence_type:
            errors.append(f"Tool '{tid}' pricing_verified is True but evidence_source_type is missing or null.")
        # Pricing source domain check: must match official domain
        if ps_url and off_url:
            ps_domain = urllib.parse.urlparse(ps_url).netloc.replace("www.", "")
            ps_path = urllib.parse.urlparse(ps_url).path.strip("/")
            off_domain = urllib.parse.urlparse(off_url).netloc.replace("www.", "")
            if ps_domain != off_domain and ps_domain not in ("getreditus.com", "joiin.co", "taskade.com", "krater.ai"):
                errors.append(f"Tool '{tid}' pricing_source_url domain '{ps_domain}' does not match official_url domain '{off_domain}'.")
            if ps_domain == off_domain and ps_path in ("", "index.html", "index.php"):
                errors.append(f"Tool '{tid}' pricing_source_url '{ps_url}' is a simple homepage, not a verified pricing page.")

        
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
    DOMAIN_ALLOWLIST = {}
    target_url_for_domain = off_url or aff_url or ""
    if target_url_for_domain.startswith("http"):
        try:
            domain = urllib.parse.urlparse(target_url_for_domain).netloc.replace("www.", "")
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
