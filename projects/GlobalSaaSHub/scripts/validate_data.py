import os
import json
import re
import urllib.parse
import sys

# Force stdout and stderr to use UTF-8 to prevent encoding crashes on Windows Task Scheduler
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

ALLOWED_CATEGORIES = {
    "workflow_auto", "developer", "marketing", "analytics", "design", "security", "creator",
    "chatbots_support", "productivity", "other", "automation", "dev_coding", "voice_cloning",
    "video_gen", "writing", "image_gen", "meeting_notes", "agents", "business",
    "copywriting", "seo_tools", "scraping_data", "email_outreach", "design_art",
    "lead_gen", "ai_agent", "workspace", "video_editing", "research",
    "sales_crm", "ai_agents", "finance_billing"
}

ALLOWED_HTTP_STATUSES = {
    "verified_http_200", "redirect_verified", "bot_blocked",
    "rate_limited", "http_error", "network_error", None
}

ALLOWED_CURRENCIES = {"USD", "GBP", "EUR", "CAD", "AUD", "BRL"}
ALLOWED_BILLING_PERIODS = {"monthly", "annual", "annual/monthly", "per_user", "usage_based", "mixed"}
ALLOWED_EVIDENCE_TYPES = {"official_pricing_page", "official_help_page", "official_documentation_page", "manual_override"}


def validate_tool_record(tool: dict, all_tools: list = None, is_strict_next: bool = False) -> list:
    """
    Validates a single tool dictionary against GlobalSaaSHub schema rules.
    Pure function with zero side-effects. Returns list of error strings.
    """
    errors = []
    tid = tool.get("id")
    name = tool.get("name")

    if not tid or not isinstance(tid, str):
        errors.append(f"Tool record missing or non-string 'id': {tool}")
        return errors

    if not re.fullmatch(r"^[a-z0-9]+(-[a-z0-9]+)*$", tid):
        errors.append(f"Tool ID '{tid}' is not valid kebab-case.")

    if not name or not isinstance(name, str):
        errors.append(f"Tool '{tid}' missing or non-string 'name'.")

    cat = tool.get("category")
    if cat not in ALLOWED_CATEGORIES:
        errors.append(f"Tool '{tid}' category '{cat}' not in allowed set: {ALLOWED_CATEGORIES}")

    off_url = tool.get("official_url")
    if not off_url or not isinstance(off_url, str) or not off_url.startswith(("http://", "https://")):
        errors.append(f"Tool '{tid}' official_url '{off_url}' must start with http:// or https://")

    aff_url = tool.get("affiliate_url")
    if aff_url is not None:
        if not isinstance(aff_url, str) or not aff_url.startswith(("http://", "https://")):
            errors.append(f"Tool '{tid}' affiliate_url '{aff_url}' must be null or start with http:// or https://")

    aff_verified = tool.get("affiliate_verified", False)
    if aff_verified is True:
        if not aff_url:
            errors.append(f"Tool '{tid}' affiliate_verified is True but affiliate_url is null or empty.")
        if tool.get("affiliate_http_status") != 200:
            errors.append(f"Tool '{tid}' affiliate_verified is True but affiliate_http_status is {tool.get('affiliate_http_status')} (expected 200).")
        markers = tool.get("affiliate_evidence_markers")
        if not isinstance(markers, list) or len(markers) == 0:
            errors.append(f"Tool '{tid}' affiliate_verified is True but affiliate_evidence_markers is empty.")

    pv_flag = tool.get("pricing_verified")
    if not isinstance(pv_flag, bool):
        errors.append(f"Tool '{tid}' pricing_verified must be boolean (got {type(pv_flag).__name__}).")

    ps_url = tool.get("pricing_source_url")
    pv_at = tool.get("pricing_verified_at")
    currency = tool.get("currency")
    billing_period = tool.get("billing_period")
    evidence_type = tool.get("evidence_source_type")

    is_override = tool.get("is_manual_override")
    if not isinstance(is_override, bool):
        errors.append(f"Tool '{tid}' is_manual_override must be boolean (got {type(is_override).__name__}).")

    http_status_enum = tool.get("http_verification_status")
    if http_status_enum not in ALLOWED_HTTP_STATUSES:
        errors.append(f"Tool '{tid}' http_verification_status '{http_status_enum}' not in allowed set: {ALLOWED_HTTP_STATUSES}")

    if currency is not None and currency not in ALLOWED_CURRENCIES:
        errors.append(f"Tool '{tid}' currency '{currency}' not in allowed set: {ALLOWED_CURRENCIES}")

    if billing_period is not None and billing_period not in ALLOWED_BILLING_PERIODS:
        errors.append(f"Tool '{tid}' billing_period '{billing_period}' not in allowed set: {ALLOWED_BILLING_PERIODS}")

    if evidence_type is not None and evidence_type not in ALLOWED_EVIDENCE_TYPES:
        errors.append(f"Tool '{tid}' evidence_source_type '{evidence_type}' not in allowed set: {ALLOWED_EVIDENCE_TYPES}")

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
        if tool.get("pricing_source_http_status") is not None:
            errors.append(f"Tool '{tid}' pricing_verified is False but pricing_source_http_status is not null.")
        if tool.get("pricing_source_final_url") is not None:
            errors.append(f"Tool '{tid}' pricing_verified is False but pricing_source_final_url is not null.")
        if tool.get("pricing_evidence_markers") is not None:
            errors.append(f"Tool '{tid}' pricing_verified is False but pricing_evidence_markers is not null.")
    else:
        if not ps_url:
            errors.append(f"Tool '{tid}' pricing_verified is True but pricing_source_url is missing or null.")
        ISO_UTC_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        if not isinstance(pv_at, str) or not re.fullmatch(ISO_UTC_PATTERN, str(pv_at)):
            errors.append(f"Tool '{tid}' pricing_verified is True but pricing_verified_at '{pv_at}' must use YYYY-MM-DDTHH:MM:SSZ format.")
        if not currency:
            errors.append(f"Tool '{tid}' pricing_verified is True but currency is missing or null.")
        if not billing_period:
            errors.append(f"Tool '{tid}' pricing_verified is True but billing_period is missing or null.")
        if not evidence_type:
            errors.append(f"Tool '{tid}' pricing_verified is True but evidence_source_type is missing or null.")

        ps_status = tool.get("pricing_source_http_status")
        ps_final = tool.get("pricing_source_final_url")
        ps_markers = tool.get("pricing_evidence_markers")

        if ps_status != 200:
            errors.append(f"Tool '{tid}' pricing_verified is True but pricing_source_http_status is '{ps_status}' (expected 200).")
        if not ps_final or not isinstance(ps_final, str) or not ps_final.startswith(("http://", "https://")):
            errors.append(f"Tool '{tid}' pricing_verified is True but pricing_source_final_url '{ps_final}' is invalid.")

        if not isinstance(ps_markers, list) or len(ps_markers) == 0:
            errors.append(f"Tool '{tid}' pricing_verified is True but pricing_evidence_markers is empty or not a list.")
        else:
            if any(not isinstance(m, str) or m.strip() == "" for m in ps_markers):
                errors.append(f"Tool '{tid}' pricing_verified is True but pricing_evidence_markers contains empty or invalid strings: {ps_markers!r}.")
            has_price_marker = any(re.search(r'[\$\€\£\¥]\d+|\d+\s*(usd|eur|gbp)', str(m), re.I) for m in ps_markers)
            has_period_marker = any(re.search(r'month|monthly|year|annual|user', str(m), re.I) for m in ps_markers)
            if not has_price_marker:
                errors.append(f"Tool '{tid}' pricing_evidence_markers {ps_markers} missing price/currency marker (e.g. '$200', '$99').")
            if not has_period_marker:
                errors.append(f"Tool '{tid}' pricing_evidence_markers {ps_markers} missing billing period marker (e.g. 'year', 'month').")

        pricing_str = tool.get("pricing")
        if not isinstance(pricing_str, str) or not re.search(r"\d+", pricing_str):
            errors.append(f"Tool '{tid}' pricing_verified is True but pricing string '{pricing_str}' contains no digits.")

        if ps_url and off_url:
            ps_domain = urllib.parse.urlparse(ps_url).netloc.replace("www.", "")
            ps_path = urllib.parse.urlparse(ps_url).path.strip("/")
            off_domain = urllib.parse.urlparse(off_url).netloc.replace("www.", "")
            if ps_domain != off_domain and ps_domain not in ("getreditus.com", "joiin.co", "taskade.com", "krater.ai", "relevanceai.com"):
                errors.append(f"Tool '{tid}' pricing_source_url domain '{ps_domain}' does not match official_url domain '{off_domain}'.")
            if ps_domain == off_domain and ps_path in ("", "index.html", "index.php"):
                errors.append(f"Tool '{tid}' pricing_source_url '{ps_url}' is a simple homepage, not a verified pricing page.")

    return errors


def validate_dataset(tools: list) -> list:
    """
    Validates an entire dataset array of tools (checks individual records + dataset uniqueness).
    Pure function with zero side-effects. Returns list of error strings.
    """
    if not isinstance(tools, list):
        return ["Dataset must be a JSON array (list)."]

    all_errors = []
    seen_ids = set()
    seen_names = set()
    seen_domains = set()

    for tool in tools:
        if not isinstance(tool, dict):
            all_errors.append(f"Tool item is not a JSON object (dict): {tool}")
            continue

        errors = validate_tool_record(tool, tools)
        all_errors.extend(errors)

        tid = tool.get("id")
        name = tool.get("name")
        off_url = tool.get("official_url")
        aff_url = tool.get("affiliate_url")

        if tid:
            if tid in seen_ids:
                all_errors.append(f"Duplicate Tool ID found: '{tid}'")
            seen_ids.add(tid)

        if name and isinstance(name, str):
            norm_name = name.lower().replace(" ", "").replace("-", "").replace(".", "")
            if norm_name in seen_names:
                all_errors.append(f"Duplicate Tool Name found: '{name}' ({tid})")
            seen_names.add(norm_name)

        target_url = off_url or aff_url or ""
        if isinstance(target_url, str) and target_url.startswith("http"):
            try:
                domain = urllib.parse.urlparse(target_url).netloc.replace("www.", "")
                if domain:
                    if domain in seen_domains:
                        all_errors.append(f"Duplicate domain FAIL: '{domain}' already registered for another tool.")
                    seen_domains.add(domain)
            except Exception:
                pass

        rating = tool.get("rating")
        if rating is not None and not (isinstance(rating, (int, float)) and 1.0 <= rating <= 5.0):
            all_errors.append(f"Invalid rating value for '{name}': {rating}")

    return all_errors


def load_target_dataset(file_path: str = None) -> tuple:
    """Loads target dataset from disk. Returns (data, path)."""
    if not file_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'data', 'tools.next.json')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target dataset file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data, file_path


def main(file_path: str = None):
    print("=" * 60)
    print("🔍 CANDIDATE DATASET VALIDATION (validate_data.py)")
    
    try:
        tools, path = load_target_dataset(file_path)
        print(f"Target File: {path}")
        print("=" * 60)
        print(f"1. Total Candidate Tools Loaded: {len(tools)}")
    except Exception as e:
        print(f"❌ FATAL ERROR loading dataset: {e}")
        print("=" * 60)
        print("❌ CANDIDATE DATASET VALIDATION RESULT: FAIL")
        sys.exit(1)

    errors = validate_dataset(tools)

    id_kebab_errors = [e for e in errors if "ID" in e]
    print(f"2. ID & Kebab-case Audit:       0 issues" if len(id_kebab_errors) == 0 else f"2. ID & Kebab-case Audit:       {len(id_kebab_errors)} ISSUES FOUND")
    print(f"3. Domain Deduplication Audit:    {len(tools)} loaded")
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


if __name__ == "__main__":
    main()
