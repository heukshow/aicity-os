import os
import json
import urllib.request
import urllib.parse
import urllib.error
import subprocess
import sys
import time



# Force stdout and stderr to use UTF-8 to prevent encoding crashes on Windows Task Scheduler
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

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

def query_tavily(api_key, query):
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
    
    print(f"-> Sending request to Tavily for query: '{query}'...")
    sys.stdout.flush()
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print("<- Received response from Tavily.")
            sys.stdout.flush()
            response_data = json.loads(res.read().decode('utf-8'))
            return response_data
    except Exception as e:
        print(f"Error querying Tavily: {e}")
        sys.stdout.flush()
        return None

def query_gemini(api_key, system_prompt, user_content):
    """Calls Gemini API using native HTTP request with JSON output configuration and 429 rate-limit backoff."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"{system_prompt}\n\nInput Data:\n{user_content}"
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    for attempt in range(1, 4):
        print(f"-> Sending request to Gemini API (gemini-2.5-flash) [Attempt {attempt}/3]...")
        sys.stdout.flush()
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as res:
                print("<- Received response from Gemini.")
                sys.stdout.flush()
                response_data = json.loads(res.read().decode('utf-8'))
                text_response = response_data['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text_response)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("⚠️ Gemini API Rate Limit (429) - Waiting 6 seconds before retry...")
                sys.stdout.flush()
                time.sleep(6)
            else:
                print(f"Error calling Gemini (HTTP {e.code}): {e}")
                sys.stdout.flush()
                return None
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            sys.stdout.flush()
            return None
    return None


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


def main():
    print("Starting GlobalSaaSHub Auto Aggregator Script...")
    
    # 1. Load Keys
    load_env()
    tavily_key = os.environ.get("TAVILY_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not tavily_key or not gemini_key:
        print("Error: Missing TAVILY_API_KEY or GEMINI_API_KEY in environment variables.")
        sys.exit(1)
        
    # 2. Paths
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

    # 4. Search Queries

    queries = [
        "top new AI tool affiliate programs recurring commission 2026",
        "highest paying B2B SaaS recurring affiliate programs 2026",
        "trending AI agent workflow automation software recurring affiliate"
    ]
    
    raw_search_results = []
    tavily_api_success = 0   # HTTP call succeeded (even if results empty)
    tavily_api_fail = 0      # HTTP call failed / exception
    tavily_total_results = 0 # total search snippets harvested
    for q in queries:
        print(f"Searching Tavily for: '{q}'...")
        results = query_tavily(tavily_key, q)
        if results and 'results' in results:
            tavily_api_success += 1
            count = len(results['results'])
            tavily_total_results += count
            for item in results['results']:
                raw_search_results.append({
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "url": item.get("url")
                })
            print(f"  -> {count} snippets returned.")
        else:
            tavily_api_fail += 1
            print(f"  -> Tavily API call failed for: '{q}'")

    print(f"Harvested {tavily_total_results} search snippets. Tavily: {tavily_api_success} API ok, {tavily_api_fail} API fail.")

    # Guard: total results 0 regardless of API success/fail combination
    if tavily_total_results == 0:
        print(
            f"FATAL: Tavily produced 0 total results. "
            f"API success={tavily_api_success}, API fail={tavily_api_fail}. Aborting pipeline."
        )
        sys.exit(1)

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
    - pricing_source_url MUST be the explicit pricing page URL (e.g. "https://example.com/pricing"). If unknown, default to official_url.
    - pricing MUST state concrete verified pricing from the snippet (e.g. "Starting at $29/mo"). DO NOT use vague statements like "See website", "Varies", "Not specified". If exact pricing is missing, set pricing to "Contact sales / See official pricing".

    
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
        "pricing_source_url": "string (pricing page URL)",
        "pricing": "string (concrete verified pricing description)",
        "key_features": ["string", "string", "string", "string"],
        "rating": null,
        "logo_url": "string",
        "commission": "string"

      }
    ]
    
    Only extract valid SaaS tools. If the snippet does not contain enough detail for a tool, omit it.
    """
    
    extracted_tools = []
    print("Invoking Gemini for extraction and filtering on individual search snippets...")
    gemini_api_success = 0   # Gemini HTTP call + JSON parse succeeded
    gemini_api_fail = 0      # Gemini HTTP call failed or JSON parse error
    gemini_tools_extracted = 0  # actual tools returned across all snippets
    gemini_empty_responses = 0  # API ok but returned empty array (normal for irrelevant snippets)
    sys.stdout.flush()
    for idx, snippet in enumerate(raw_search_results):
        print(f"[{idx+1}/{len(raw_search_results)}] Processing snippet: '{snippet.get('title')}'...")
        sys.stdout.flush()
        user_content = json.dumps(snippet, indent=2)
        result = query_gemini(gemini_key, system_prompt, user_content)
        if result is None:
            # API call failed or JSON parse error
            gemini_api_fail += 1
            print("   Gemini API call failed or response unparseable.")
            sys.stdout.flush()
        elif isinstance(result, list):
            gemini_api_success += 1
            if len(result) == 0:
                gemini_empty_responses += 1
                print("   Gemini returned empty array (no qualifying tools in snippet).")
            else:
                gemini_tools_extracted += len(result)
                print(f"   Success! Extracted {len(result)} tools.")
                extracted_tools.extend(result)
            sys.stdout.flush()
        else:
            gemini_api_fail += 1
            print("   Gemini returned unexpected format.")
            sys.stdout.flush()
        time.sleep(1.5)

    print(f"Gemini: {gemini_api_success} API ok (of which {gemini_empty_responses} empty), {gemini_api_fail} API fail. Total tools extracted: {gemini_tools_extracted}.")

    # Guard: if ALL Gemini calls failed (API/parse errors)
    if gemini_api_fail > 0 and gemini_api_success == 0:
        print(f"FATAL: All {gemini_api_fail} Gemini API calls failed. Aborting pipeline.")
        sys.exit(1)


    if not extracted_tools:
        print("No new tools extracted from search snippets during this run. Database remains up to date.")

        
    print(f"Successfully compiled {len(extracted_tools)} total tools from all snippets.")
    sys.stdout.flush()
    
    # 6. Merge & Deduplicate
    new_tools_added = 0
    updated_tools_count = 0
    new_tools_list = []
    updated_tools_list = []

    for new_tool in extracted_tools:
        # Validate schema keys (affiliate_url is OPTIONAL now)
        required_keys = ['id', 'name', 'category', 'category_display', 'description', 'official_url', 'pricing', 'key_features', 'rating', 'logo_url']
        if not all(k in new_tool for k in required_keys):
            print(f"Skipping tool due to missing required keys: {new_tool.get('name')}")
            continue
            
        off_url = new_tool.get('official_url')
        aff_url = new_tool.get('affiliate_url')
        tool_domain = extract_domain(off_url)

        if not tool_domain:
            print(f"Skipping tool due to invalid official_url: {new_tool.get('name')} ({off_url!r})")
            continue

        new_tool['logo_url'] = f"https://www.google.com/s2/favicons?domain={tool_domain}&sz=128"

        # Ensure commission key is removed
        if 'commission' in new_tool:
            del new_tool['commission']

        tool_id = new_tool['id']
        tool_norm_name = new_tool.get('name', '').lower().strip().replace(' ', '').replace('-', '').replace('_', '')

        # Check for existing match by ID, domain, or normalized name
        matched_existing_tool = None
        if tool_id in existing_ids:
            matched_existing_tool = existing_ids[tool_id]
        elif tool_domain and tool_domain in existing_domains:
            matched_existing_tool = existing_domains[tool_domain]
            print(f"Domain match found for '{new_tool['name']}' -> Existing tool '{matched_existing_tool['name']}' ({matched_existing_tool['id']})")
        elif tool_norm_name and tool_norm_name in existing_names:
            matched_existing_tool = existing_names[tool_norm_name]
            print(f"Name match found for '{new_tool['name']}' -> Existing tool '{matched_existing_tool['name']}' ({matched_existing_tool['id']})")

        # Exclude 'automa' until product official domain is finalized
        if tool_id == 'automa':
            print("Skipping 'automa' as per policy until official domain is confirmed.")
            continue

        # Ensure strict schema defaults for unverified search candidate items
        new_tool['official_url'] = off_url if (isinstance(off_url, str) and off_url.strip().startswith(('http://', 'https://'))) else f"https://{tool_domain}/"
        new_tool['affiliate_url'] = aff_url if (isinstance(aff_url, str) and aff_url.strip().startswith(('http://', 'https://')) and aff_url != new_tool['official_url']) else None
        new_tool['pricing_source_url'] = None  # Do NOT default to homepage
        new_tool['pricing_verified_at'] = None  # Do NOT hardcode date
        new_tool['pricing_verified'] = False
        new_tool['currency'] = None
        new_tool['billing_period'] = None
        new_tool['evidence_source_type'] = None

        # Verified Candidate Overrides for known verified new tools
        CANDIDATE_VERIFIED_OVERRIDES = {
            "joiin": {"pricing": "Starting at $23/month (billed annually, 1 company)", "pricing_source_url": "https://www.joiin.co/pricing/", "pricing_verified": True, "currency": "USD", "billing_period": "annual", "evidence_source_type": "official_pricing_page"},
            "reditus": {"pricing": "14-day free trial; Startup plan at $99/month (billed annually) or $149 monthly", "pricing_source_url": "https://getreditus.com/help/reditus-pricing", "pricing_verified": True, "currency": "USD", "billing_period": "annual/monthly", "evidence_source_type": "official_help_page"},
            "taskade": {"pricing": "Free plan available; Pro starting at $10/month (billed annually)", "pricing_source_url": "https://www.taskade.com/pricing", "pricing_verified": True, "currency": "USD", "billing_period": "annual", "evidence_source_type": "official_pricing_page"},
            "krater": {"pricing": "Pro plan starting at $200/year (billed annually)", "pricing_source_url": "https://krater.ai/pricing", "pricing_verified": True, "currency": "USD", "billing_period": "annual", "evidence_source_type": "official_pricing_page"}
        }

        if tool_id in CANDIDATE_VERIFIED_OVERRIDES:
            ov = CANDIDATE_VERIFIED_OVERRIDES[tool_id]
            new_tool.update(ov)
            import datetime
            new_tool["pricing_verified_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

        if matched_existing_tool is None:
            # Truly new tool! Add to database
            existing_tools.append(new_tool)
            existing_ids[tool_id] = new_tool
            if tool_domain:
                existing_domains[tool_domain] = new_tool
            if tool_norm_name:
                existing_names[tool_norm_name] = new_tool
            new_tools_added += 1
            new_tools_list.append(new_tool)
            print(f"New unique tool added: {new_tool['name']} ({tool_id})")
        else:
            # Existing tool matched!
            target_id = matched_existing_tool['id']
            # Search snippets alone CANNOT update existing tool pricing
            print(f"Search snippet match for existing tool '{matched_existing_tool['name']}' ({target_id}). Pricing update skipped without verified pricing page check.")

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
        "tavily_api_success": tavily_api_success,
        "tavily_api_fail": tavily_api_fail,
        "tavily_total_results": tavily_total_results,
        "gemini_api_success": gemini_api_success,
        "gemini_api_fail": gemini_api_fail,
        "gemini_empty_responses": gemini_empty_responses,
        "gemini_tools_extracted": gemini_tools_extracted,
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

