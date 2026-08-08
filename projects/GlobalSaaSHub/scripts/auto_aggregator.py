import os
import json
import urllib.request
import urllib.parse
import urllib.error
import email.utils
import random
import re
import subprocess
import sys
import time
from affiliate_url_verifier import safe_affiliate_result



# Force stdout and stderr to use UTF-8 to prevent encoding crashes on Windows Task Scheduler
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

def normalize_unverified_candidate(new_tool, official_url, affiliate_url):
    """Normalizes any new search candidate item to ensure strict schema compliance and unverified state."""
    normalized = dict(new_tool)

    normalized["official_url"] = official_url
    normalized["affiliate_url"] = affiliate_url

    # Search snippets are not official pricing verification. Fail closed: an
    # unverified discovery may not retain a claimed price or any evidence
    # metadata, even when the extraction model supplied plausible values.
    normalized["pricing"] = "See official pricing"
    normalized["pricing_verified"] = False
    normalized["pricing_source_url"] = None
    normalized["pricing_verified_at"] = None
    normalized["pricing_source_http_status"] = None
    normalized["pricing_source_final_url"] = None
    normalized["pricing_evidence_markers"] = None
    normalized["currency"] = None
    normalized["billing_period"] = None
    normalized["evidence_source_type"] = None

    normalized["is_manual_override"] = False
    normalized["http_verification_status"] = None

    return normalized


def merge_discovered_candidates(existing_tools, discovered_candidates):
    """
    Core Production/Dry-run candidate merger logic.

    Rules:
      1. Deduplicates by ID, canonical official domain (extract_domain), or normalized name.
      2. If domain matches an existing tool (e.g. taskade.com), NO new tool is created
         even if candidate has a different ID (e.g. 'taskade-ai-agents').
      3. Immutability Contract:
         - If existing tool has affiliate_verified=True, candidate CANNOT overwrite any affiliate_* fields.
         - If existing tool has pricing_verified=True, candidate CANNOT overwrite any pricing_* fields.
      4. Only truly new candidates (unmatched domain/ID/name) are normalized and added.

    Returns:
      (merged_tools, new_tools_list, updated_tools_list)
    """
    merged_tools = [dict(t) for t in existing_tools]
    existing_ids = {t["id"]: t for t in merged_tools}
    existing_domains = {}
    existing_names = {}

    for tool in merged_tools:
        source_url = tool.get("official_url") or tool.get("affiliate_url") or ""
        dom = extract_domain(source_url)
        if dom:
            existing_domains[dom] = tool
        norm_n = tool.get("name", "").lower().strip().replace(" ", "").replace("-", "").replace("_", "")
        if norm_n:
            existing_names[norm_n] = tool

    new_tools_list = []
    updated_tools_list = []

    AFFILIATE_KEYS = [
        "affiliate_url", "affiliate_verified", "affiliate_source_url",
        "affiliate_final_url", "affiliate_http_status", "affiliate_evidence_markers",
        "affiliate_verified_at", "affiliate_rejection_reason"
    ]
    PRICING_KEYS = [
        "pricing", "pricing_verified", "pricing_source_url", "pricing_verified_at",
        "pricing_source_http_status", "pricing_source_final_url",
        "pricing_evidence_markers", "currency", "billing_period", "evidence_source_type"
    ]

    for new_tool in discovered_candidates:
        required_keys = ['id', 'name', 'category', 'category_display', 'description', 'official_url', 'pricing', 'key_features', 'rating', 'logo_url']
        if not all(k in new_tool for k in required_keys):
            print(f"Skipping tool due to missing required keys: {new_tool.get('name')}")
            continue

        off_url = new_tool.get("official_url")
        aff_url = new_tool.get("affiliate_url")
        tool_domain = extract_domain(off_url)

        if not tool_domain:
            print(f"Skipping tool due to invalid official_url: {new_tool.get('name')} ({off_url!r})")
            continue

        tool_id = new_tool["id"]
        tool_norm_name = new_tool.get("name", "").lower().strip().replace(" ", "").replace("-", "").replace("_", "")

        # Exclude 'automa' until official domain is confirmed
        if tool_id == "automa":
            print("Skipping 'automa' as per policy until official domain is confirmed.")
            continue

        # Check for existing match by ID, domain, or normalized name
        matched = None
        if tool_id in existing_ids:
            matched = existing_ids[tool_id]
        elif tool_domain and tool_domain in existing_domains:
            matched = existing_domains[tool_domain]
            print(f"Domain match found for '{new_tool['name']}' ({tool_domain}) -> Existing tool '{matched['name']}' ({matched['id']})")
        elif tool_norm_name and tool_norm_name in existing_names:
            matched = existing_names[tool_norm_name]
            print(f"Name match found for '{new_tool['name']}' -> Existing tool '{matched['name']}' ({matched['id']})")

        if matched is None:
            # Truly new tool! Verify affiliate and normalize
            valid_off_url = off_url if (isinstance(off_url, str) and off_url.strip().startswith(('http://', 'https://'))) else f"https://{tool_domain}/"
            aff_meta = safe_affiliate_result(aff_url, tool_name=new_tool.get('name', ''))
            normalized_new_tool = normalize_unverified_candidate(new_tool, valid_off_url, aff_meta["affiliate_url"])
            normalized_new_tool.update(aff_meta)
            normalized_new_tool['logo_url'] = f"https://www.google.com/s2/favicons?domain={tool_domain}&sz=128"
            if 'commission' in normalized_new_tool:
                del normalized_new_tool['commission']

            merged_tools.append(normalized_new_tool)
            existing_ids[tool_id] = normalized_new_tool
            if tool_domain:
                existing_domains[tool_domain] = normalized_new_tool
            if tool_norm_name:
                existing_names[tool_norm_name] = normalized_new_tool
            new_tools_list.append(normalized_new_tool)
            print(f"New unique tool added: {normalized_new_tool['name']} ({tool_id})")
        else:
            # Existing tool matched! Preserve verified affiliate and pricing fields
            target_id = matched["id"]
            print(f"Match for existing tool '{matched['name']}' ({target_id}). Preserving verified contract fields.")

            # Immutability check: if verified, DO NOT overwrite with candidate unverified values
            # (No-op on verified fields ensures existing verified contracts are preserved 100%)

    return merged_tools, new_tools_list, updated_tools_list


def merge_verified_manual_candidates(existing_tools, verified_manual_candidates):
    """
    Merges verified manual candidates into existing_tools dataset.

    Rules:
      1. Matches by ID, canonical domain (extract_domain), or normalized name.
      2. If matched:
         - Existing ID and identity preserved.
         - If candidate has pricing_verified=True, update all pricing verification metadata
           (pricing, pricing_source_url, pricing_verified, pricing_verified_at,
            pricing_source_http_status, pricing_source_final_url, pricing_evidence_markers,
            currency, billing_period, evidence_source_type) into existing tool record.
         - If candidate has affiliate_verified=True, update verified affiliate metadata.
         - Unverified candidate fields NEVER overwrite existing verified data.
      3. If unmatched (e.g. Taskade, Relevance AI):
         - Added as new tool.

    Returns:
      (merged_tools, updated_count, added_count)
    """
    merged_tools = [dict(t) for t in existing_tools]
    existing_ids = {t["id"]: t for t in merged_tools}
    existing_domains = {}
    existing_names = {}

    for tool in merged_tools:
        source_url = tool.get("official_url") or tool.get("affiliate_url") or ""
        dom = extract_domain(source_url)
        if dom:
            existing_domains[dom] = tool
        norm_n = tool.get("name", "").lower().strip().replace(" ", "").replace("-", "").replace("_", "")
        if norm_n:
            existing_names[norm_n] = tool

    updated_count = 0
    added_count = 0

    PRICING_UPDATE_KEYS = [
        "pricing", "pricing_verified", "pricing_source_url", "pricing_verified_at",
        "pricing_source_http_status", "pricing_source_final_url",
        "pricing_evidence_markers", "currency", "billing_period", "evidence_source_type"
    ]
    AFFILIATE_UPDATE_KEYS = [
        "affiliate_url", "affiliate_verified", "affiliate_source_url",
        "affiliate_final_url", "affiliate_http_status", "affiliate_evidence_markers",
        "affiliate_verified_at", "affiliate_rejection_reason"
    ]

    for m_tool in verified_manual_candidates:
        m_id = m_tool.get("id")
        m_url = m_tool.get("official_url") or m_tool.get("affiliate_url") or ""
        m_dom = extract_domain(m_url)
        m_norm = m_tool.get("name", "").lower().strip().replace(" ", "").replace("-", "").replace("_", "")

        matched = None
        if m_id in existing_ids:
            matched = existing_ids[m_id]
        elif m_dom and m_dom in existing_domains:
            matched = existing_domains[m_dom]
        elif m_norm and m_norm in existing_names:
            matched = existing_names[m_norm]

        if matched is None:
            # Truly new manual candidate (e.g. Taskade, Relevance AI)
            new_record = dict(m_tool)
            merged_tools.append(new_record)
            existing_ids[m_id] = new_record
            if m_dom:
                existing_domains[m_dom] = new_record
            if m_norm:
                existing_names[m_norm] = new_record
            added_count += 1
            print(f"Added new manual candidate tool: '{new_record['name']}' ({m_id})")
        else:
            # Existing tool matched! Update verified metadata
            print(f"Existing tool match for manual candidate '{m_tool.get('name')}' -> '{matched['name']}' ({matched['id']}).")
            if m_tool.get("pricing_verified") is True:
                for k in PRICING_UPDATE_KEYS:
                    if k in m_tool:
                        matched[k] = m_tool[k]
                print(f"  -> Updated verified pricing metadata on '{matched['id']}'.")
            if m_tool.get("affiliate_verified") is True:
                for k in AFFILIATE_UPDATE_KEYS:
                    if k in m_tool:
                        matched[k] = m_tool[k]
                print(f"  -> Updated verified affiliate metadata on '{matched['id']}'.")
            updated_count += 1

    return merged_tools, updated_count, added_count

def load_env():
    """Loads environment variables from the root .env file."""
    # Look for .env in the current directory, parent, or grandparent
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '.env'),
        os.path.join(os.path.dirname(__file__), '..', '.env'),
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
        os.path.abspath('.env')
    ]
    
    env_vars = {}
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, val = line.split('=', 1)
                        env_vars[key.strip()] = val.strip()
            print(f"Loaded environment variables from: {path}")
            break
            
    # Set loaded env vars to os.environ (always override to avoid stale/suspended keys)
    for k, v in env_vars.items():
        os.environ[k] = v

RETRYABLE_HTTP_STATUS = frozenset({429, 500, 502, 503, 504})
AUTH_HTTP_STATUS = frozenset({401, 403})
MAX_API_ATTEMPTS = 4
BASE_BACKOFF_SECONDS = 5.0
MAX_BACKOFF_SECONDS = 60.0
JITTER_RATIO = 0.20

GEMINI_CANDIDATE_REQUIRED_KEYS = frozenset({
    "id", "name", "category", "category_display", "description",
    "official_url", "affiliate_url", "pricing_source_url", "pricing",
    "key_features", "rating", "logo_url", "commission"
})
GEMINI_CATEGORY_DISPLAY = {
    "automation": "Workflow Automation",
    "creator": "Creator & Productivity",
    "developer": "Developer APIs",
}


def _retry_after_seconds(headers, now_fn=time.time):
    """Parse Retry-After seconds or HTTP-date without logging header contents."""
    if not headers:
        return None
    value = headers.get("Retry-After")
    if not value:
        return None
    try:
        return max(0.0, float(value.strip()))
    except (TypeError, ValueError):
        try:
            parsed = email.utils.parsedate_to_datetime(value)
            return max(0.0, parsed.timestamp() - now_fn())
        except (TypeError, ValueError, OverflowError):
            return None


def _retry_delay(attempt, headers=None, random_fn=random.random):
    """Return bounded exponential delay with positive jitter; Retry-After wins."""
    retry_after = _retry_after_seconds(headers)
    if retry_after is not None:
        return min(retry_after, MAX_BACKOFF_SECONDS)
    base = min(BASE_BACKOFF_SECONDS * (2 ** (attempt - 1)), MAX_BACKOFF_SECONDS)
    return min(base * (1.0 + JITTER_RATIO * random_fn()), MAX_BACKOFF_SECONDS)


def _http_status_reason(code):
    if code in AUTH_HTTP_STATUS:
        return "AUTH_ERROR"
    if code == 400:
        return "BAD_REQUEST"
    if code in RETRYABLE_HTTP_STATUS:
        return "RETRY_EXHAUSTED"
    return "HTTP_ERROR"


def filter_valid_gemini_candidates(candidates):
    """Drop malformed candidate items without retaining partial item data."""
    valid = []
    for index, candidate in enumerate(candidates, start=1):
        category = candidate.get("category") if isinstance(candidate, dict) else None
        candidate_id = candidate.get("id") if isinstance(candidate, dict) else None
        official_url = candidate.get("official_url") if isinstance(candidate, dict) else None
        key_features = candidate.get("key_features") if isinstance(candidate, dict) else None
        is_valid = (
            isinstance(candidate, dict)
            and GEMINI_CANDIDATE_REQUIRED_KEYS.issubset(candidate)
            and isinstance(candidate_id, str)
            and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", candidate_id) is not None
            and category in GEMINI_CATEGORY_DISPLAY
            and candidate.get("category_display") == GEMINI_CATEGORY_DISPLAY.get(category)
            and isinstance(official_url, str)
            and official_url.startswith(("http://", "https://"))
            and isinstance(key_features, list)
            and all(isinstance(feature, str) for feature in key_features)
        )
        if is_valid:
            valid.append(candidate)
        else:
            print(f"Gemini candidate [{index}] failed schema validation and was discarded.")
    return valid


def query_tavily(api_key, query, sleep_fn=time.sleep, random_fn=random.random):
    """Performs an advanced web search using Tavily API."""
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": 4
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers=headers, 
        method='POST'
    )
    
    for attempt in range(1, MAX_API_ATTEMPTS + 1):
        print(f"-> Tavily request [Attempt {attempt}/{MAX_API_ATTEMPTS}].")
        sys.stdout.flush()
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                response_data = json.loads(res.read().decode('utf-8'))
                if not isinstance(response_data, dict) or not isinstance(response_data.get("results"), list):
                    print("Tavily returned a malformed response; not retrying.")
                    return None, "PARSING_ERROR"
                return response_data, "OK"
        except urllib.error.HTTPError as exc:
            if exc.code in RETRYABLE_HTTP_STATUS and attempt < MAX_API_ATTEMPTS:
                delay = _retry_delay(attempt, exc.headers, random_fn)
                print(f"Tavily HTTP {exc.code}; retrying in {delay:.2f}s.")
                sleep_fn(delay)
                continue
            reason = _http_status_reason(exc.code)
            print(f"Tavily HTTP {exc.code}; status={reason}; no further retry.")
            return None, reason
        except json.JSONDecodeError:
            print("Tavily returned invalid JSON; not retrying.")
            return None, "PARSING_ERROR"
        except Exception as exc:
            print(f"Tavily network failure ({type(exc).__name__}); not retrying.")
            return None, "NETWORK_ERROR"

    return None, "RETRY_EXHAUSTED"

MAX_GEMINI_BATCH_SIZE = 10


def build_gemini_url(api_key: str) -> str:
    """Builds the canonical Gemini generateContent API URL."""
    return f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"


def query_gemini_batch(api_key, system_prompt, snippets_batch, sleep_fn=time.sleep, random_fn=random.random):
    """Call Gemini with bounded retries and return (tools, auditable status)."""
    endpoint_url = build_gemini_url(api_key)
    headers = {"Content-Type": "application/json"}
    user_content = json.dumps(snippets_batch, indent=2)
    prompt = f"{system_prompt}\n\nInput Search Snippets Batch ({len(snippets_batch)} items):\n{user_content}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    payload_bytes = json.dumps(data).encode('utf-8')

    for attempt in range(1, MAX_API_ATTEMPTS + 1):
        print(f"-> Gemini request [Batch size: {len(snippets_batch)}, Attempt {attempt}/{MAX_API_ATTEMPTS}].")
        sys.stdout.flush()
        req = urllib.request.Request(endpoint_url, data=payload_bytes, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=90) as res:
                response_data = json.loads(res.read().decode('utf-8'))
                text_response = response_data['candidates'][0]['content']['parts'][0]['text']
                parsed_tools = json.loads(text_response)
                if not isinstance(parsed_tools, list):
                    print("Gemini output is not a JSON array; not retrying.")
                    return None, 'PARSING_ERROR'
                return parsed_tools, 'OK'
        except urllib.error.HTTPError as exc:
            if exc.code in RETRYABLE_HTTP_STATUS and attempt < MAX_API_ATTEMPTS:
                delay = _retry_delay(attempt, exc.headers, random_fn)
                print(f"Gemini HTTP {exc.code}; retrying in {delay:.2f}s.")
                sys.stdout.flush()
                sleep_fn(delay)
                continue
            reason = _http_status_reason(exc.code)
            print(f"Gemini HTTP {exc.code}; status={reason}; no further retry.")
            return None, reason
        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
            print("Gemini response schema/JSON parse error; not retrying.")
            return None, 'PARSING_ERROR'
        except Exception as exc:
            print(f"Gemini network failure ({type(exc).__name__}); not retrying.")
            return None, 'NETWORK_ERROR'

    return None, 'RETRY_EXHAUSTED'


def discovery_merge_input(extracted_tools, degraded_mode):
    """Discard partial run-local discovery whenever any batch was skipped."""
    return [] if degraded_mode else list(extracted_tools)


def extract_domain(url):
    if not isinstance(url, str):
        return ""
    value = url.strip()
    if not value.startswith(("http://", "https://")):
        return ""
    try:
        dom = urllib.parse.urlparse(value).netloc.lower()
        if dom.startswith("www."):
            dom = dom[4:]
        return dom
    except Exception:
        return ""


def main(base_dir=None):
    print("Starting GlobalSaaSHub Auto Aggregator Script...")
    
    # 1. Load Keys
    load_env()
    tavily_key = os.environ.get("TAVILY_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not tavily_key or not gemini_key:
        print("Error: Missing TAVILY_API_KEY or GEMINI_API_KEY in environment variables.")
        sys.exit(1)
        
    # 2. Paths
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file_path = os.path.join(base_dir, 'data', 'tools.json')
    next_data_file_path = os.path.join(base_dir, 'data', 'tools.next.json')

    print(f"Base Data file: {data_file_path}")
    print(f"Next Target Data file: {next_data_file_path}")

    
    # 3. Load Existing Tools
    existing_tools = []
    if os.path.exists(data_file_path):
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                existing_tools = json.load(f)
            print(f"Loaded {len(existing_tools)} existing tools from database.")
        except Exception as e:
            print(f"Fatal database read error: {e}")
            sys.exit(1)
    existing_ids = {tool['id']: tool for tool in existing_tools}
    existing_domains = {}
    existing_names = {}
    for tool in existing_tools:
        source_url = tool.get("official_url") or tool.get("affiliate_url") or ""
        dom = extract_domain(source_url)
        if dom:
            existing_domains[dom] = tool
        norm_n = tool.get('name', '').lower().strip().replace(' ', '').replace('-', '').replace('_', '')
        if norm_n:
            existing_names[norm_n] = tool

    # Merge isolated runtime manual_candidates_verified.json with strict fail-closed behavior
    manual_verified_file = os.path.join(base_dir, 'data', 'manual_candidates_verified.json')

    if not os.path.exists(manual_verified_file):
        print(f"❌ FATAL: manual_candidates_verified.json is missing at {manual_verified_file}. Run verify_manual_candidates.py first.")
        sys.exit(1)

    try:
        with open(manual_verified_file, 'r', encoding='utf-8') as f:
            manual_tools = json.load(f)
        if not isinstance(manual_tools, list):
            print(f"❌ FATAL: Manual candidates file {manual_verified_file} must be a JSON array.")
            sys.exit(1)
        print(f"Loaded {len(manual_tools)} manual candidate tools from {manual_verified_file}.")
        existing_tools, manual_updated, manual_added = merge_verified_manual_candidates(existing_tools, manual_tools)
        print(f"Successfully merged manual candidates into dataset (updated: {manual_updated}, added: {manual_added}).")
    except Exception as e:
        print(f"❌ FATAL: Failed to read or parse manual candidates file {manual_verified_file}: {e}")
        sys.exit(1)

    # 4. Search Queries

    queries = [
        "top new AI tool affiliate programs recurring commission 2026",
        "highest paying B2B SaaS recurring affiliate programs 2026",
        "trending AI agent workflow automation software recurring affiliate"
    ]
    
    raw_search_results = []
    tavily_api_success = 0
    tavily_api_fail = 0
    tavily_total_results = 0
    discovery_batches = []
    for query_index, query in enumerate(queries, start=1):
        print(f"Searching Tavily query [{query_index}/{len(queries)}].")
        tavily_response = query_tavily(tavily_key, query)
        if isinstance(tavily_response, tuple) and len(tavily_response) == 2:
            results, tavily_status = tavily_response
        else:  # Backward-compatible dependency injection for deterministic tests.
            results, tavily_status = tavily_response, "OK"
        if results is not None:
            tavily_api_success += 1
            count = len(results["results"])
            tavily_total_results += count
            for item in results["results"]:
                raw_search_results.append({
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "url": item.get("url")
                })
            discovery_batches.append({"provider": "tavily", "batch": query_index, "status": "completed", "reason": "ok", "result_count": count})
            print(f"  -> {count} snippets returned.")
        else:
            tavily_api_fail += 1
            discovery_batches.append({"provider": "tavily", "batch": query_index, "status": "skipped_with_reason", "reason": tavily_status, "result_count": 0})
            print(f"  -> Tavily query skipped_with_reason={tavily_status}.")
            if tavily_status in ("AUTH_ERROR", "BAD_REQUEST", "HTTP_ERROR"):
                print("FATAL: non-transient Tavily HTTP failure; stopping without modifying production data.")
                sys.exit(1)

    print(f"Harvested {tavily_total_results} search snippets. Tavily: {tavily_api_success} API ok, {tavily_api_fail} API fail.")
    if tavily_total_results == 0:
        print("DEGRADED: Tavily produced 0 results; continuing with the preserved candidate corpus.")

    # 5. Process with Gemini
    system_prompt = """
    You are a B2B SaaS and AI affiliate marketing database architect. 
    Analyze the provided web search snippets and extract high-quality SaaS or AI tools that offer recurring/recurring-lifetime affiliate commissions.
    
    Output MUST be a JSON array of objects with the exact schema below.
    Schema Rules:
    - category must be strictly one of: "automation", "creator", "developer"
    - category_display must match: "Workflow Automation" (for automation), "Creator & Productivity" (for creator), "Developer APIs" (for developer)
    - id must be lowercase, alphanumeric, separated by dashes (e.g., "gohighlevel", "notion-ai").
    - logo_url must be a premium high-quality placeholder image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150&auto=format&fit=crop&q=60" (or similar technology placeholder from unsplash).
    - official_url MUST be the root domain URL of the product website (e.g. "https://example.com/").
    - affiliate_url MUST be the official affiliate/partner program link or referral URL (e.g. "https://example.com/affiliate"). If unknown, default to official_url.
    - Discovery output is UNVERIFIED. pricing_source_url MUST be null; a later official-page verification step is the only path that may set it.
    - pricing MUST be "See official pricing". Never infer or copy a numeric price from a search snippet.

    
    JSON Schema:
    [
      {
        "id": "string (lowercase kebab-case)",
        "name": "string",
        "category": "automation" | "creator" | "developer",
        "category_display": "string",
        "description": "string (engaging, 1-2 sentence description explaining value proposition)",
        "official_url": "string (root domain product URL)",
        "affiliate_url": "string (affiliate or referral program link)",
        "pricing_source_url": null,
        "pricing": "See official pricing",
        "key_features": ["string", "string", "string", "string"],
        "rating": null,
        "logo_url": "string",
        "commission": "string"

      }
    ]
    
    Only extract valid SaaS tools. If the snippet does not contain enough detail for a tool, omit it.
    """
    
    extracted_tools = []
    print(f"Invoking Gemini for extraction in chunks of max {MAX_GEMINI_BATCH_SIZE} snippets...")
    gemini_api_success = 0
    gemini_api_fail = 0
    gemini_tools_extracted = 0
    gemini_status_reason = "ok"
    degraded_mode = False

    sys.stdout.flush()

    # Split raw_search_results into batches of max MAX_GEMINI_BATCH_SIZE (e.g. 12 -> 10 + 2)
    snippet_chunks = [
        raw_search_results[i:i + MAX_GEMINI_BATCH_SIZE]
        for i in range(0, len(raw_search_results), MAX_GEMINI_BATCH_SIZE)
    ]

    for b_idx, chunk in enumerate(snippet_chunks):
        batch_number = b_idx + 1
        print(f"Processing Gemini snippet chunk [{batch_number}/{len(snippet_chunks)}] ({len(chunk)} items)...")
        batch_result, status_reason = query_gemini_batch(gemini_key, system_prompt, chunk)
        if status_reason == 'OK' and isinstance(batch_result, list):
            batch_result = filter_valid_gemini_candidates(batch_result)
            gemini_api_success += 1
            gemini_tools_extracted += len(batch_result)
            extracted_tools.extend(batch_result)
            discovery_batches.append({"provider": "gemini", "batch": batch_number, "status": "completed", "reason": "ok", "result_count": len(batch_result)})
            print(f"  Chunk [{batch_number}] OK; extracted {len(batch_result)} tools.")
        else:
            gemini_api_fail += 1
            discovery_batches.append({"provider": "gemini", "batch": batch_number, "status": "skipped_with_reason", "reason": status_reason, "result_count": 0})
            print(f"  Chunk [{batch_number}] skipped_with_reason={status_reason}.")
            if status_reason in ('AUTH_ERROR', 'BAD_REQUEST', 'HTTP_ERROR', 'PARSING_ERROR'):
                print("FATAL: non-transient Gemini request or response-schema failure; stopping without modifying production data.")
                sys.exit(1)

    degraded_mode = tavily_api_fail > 0 or gemini_api_fail > 0 or not raw_search_results
    if not snippet_chunks:
        gemini_status_reason = "skipped_no_tavily_results"
    elif gemini_api_success == len(snippet_chunks):
        gemini_status_reason = "ok"
    elif gemini_api_success > 0:
        gemini_status_reason = "partial_skipped"
    else:
        gemini_status_reason = "all_batches_skipped"

    print(f"Gemini Summary: success={gemini_api_success}, fail={gemini_api_fail}, status={gemini_status_reason}, extracted={gemini_tools_extracted}, degraded_mode={degraded_mode}")
    if degraded_mode:
        print("DEGRADED: discovery is incomplete; discarding all run-local discoveries and preserving the candidate corpus.")
    elif not extracted_tools:
        print("Discovery completed with zero valid new tools; continuing validation/build.")

    print(f"Successfully compiled {len(extracted_tools)} total tools from discovery.")
    sys.stdout.flush()

    # Any incomplete discovery is all-or-nothing: never merge partial run-local results.
    merge_input = discovery_merge_input(extracted_tools, degraded_mode)
    existing_tools, new_tools_list, updated_tools_list = merge_discovered_candidates(existing_tools, merge_input)
    new_tools_added = len(new_tools_list)
    updated_tools_count = len(updated_tools_list)

    # 7. Write Back to Sandbox Next File
    try:
        with open(next_data_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_tools, f, indent=2, ensure_ascii=False)
        print(f"Sandbox tools.next.json successfully generated. Added {new_tools_added} new tools, updated {updated_tools_count} existing tools. Sandbox total count: {len(existing_tools)}.")
    except Exception as e:
        print(f"Error writing sandbox tools.next.json: {e}")
        sys.exit(1)

    # 8. Write Artifact Summary JSONs for CI validation
    data_dir = os.path.dirname(next_data_file_path)
    summary = {
        "artifact_schema_version": "1.0",
        "source_head_sha": os.environ.get("GITHUB_SHA", "local-dev"),
        "source_run_id": str(os.environ.get("GITHUB_RUN_ID", "local-run")),
        "dry_run": os.environ.get("DRY_RUN", "true").lower() == "true",
        "failure_test": os.environ.get("FAILURE_TEST", "false").lower() == "true",
        "tavily_api_success": tavily_api_success,
        "tavily_api_fail": tavily_api_fail,
        "tavily_total_results": tavily_total_results,
        "gemini_api_success": gemini_api_success,
        "gemini_api_fail": gemini_api_fail,
        "gemini_status": gemini_status_reason.lower(),
        "gemini_api_ok": gemini_api_success,
        "gemini_tools_extracted": gemini_tools_extracted,
        "automated_discovery_added": new_tools_added,
        "degraded_mode": degraded_mode,
        "discovery_complete": not degraded_mode,
        "discovery_batches": discovery_batches,
        "new_tools_added": new_tools_added,
        "updated_tools_count": updated_tools_count,
        "sandbox_total": len(existing_tools)
    }

    with open(os.path.join(data_dir, "run_summary.json"), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(os.path.join(data_dir, "new_tools_discovered.json"), 'w', encoding='utf-8') as f:
        json.dump(new_tools_list, f, indent=2, ensure_ascii=False)
    with open(os.path.join(data_dir, "price_updated_tools.json"), 'w', encoding='utf-8') as f:
        json.dump(updated_tools_list, f, indent=2, ensure_ascii=False)
    print(f"Artifact summary files written to {data_dir}")

    print("Auto Aggregator Script completed successfully.")



if __name__ == "__main__":
    main()
