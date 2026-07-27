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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    data_file_path = os.path.join(project_root, "data", "tools.json")
    next_data_file_path = os.path.join(project_root, "data", "tools.next.json")
    
    print(f"Project root: {project_root}")
    print(f"Operational Data file: {data_file_path}")
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
    existing_ids = {tool['id'] for tool in existing_tools}

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

    # Guard: if ALL queries returned 0 results (API ok but empty), something is wrong
    if tavily_api_fail == 0 and tavily_total_results == 0:
        print("FATAL: All Tavily API calls succeeded but returned 0 results. Aborting pipeline.")
        sys.exit(1)

    # Guard: if ALL API calls failed
    if tavily_api_success == 0:
        print(f"FATAL: All {tavily_api_fail} Tavily API calls failed. Aborting pipeline.")
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
    - affiliate_url MUST be the real, working official URL of the SaaS product. NEVER use example.com, localhost, or fake/dummy URLs.
    - key_features must be an array of exactly 4 specific string highlights (e.g., ["Feature A", "Feature B"]).
    - commission must state the commission rate (e.g., "30% Recurring", "40% Recurring (Lifetime)").

    
    JSON Schema:
    [
      {
        "id": "string (lowercase kebab-case)",
        "name": "string",
        "category": "automation" | "creator" | "developer",
        "category_display": "string",
        "description": "string (engaging, 1-2 sentence description explaining value proposition)",
        "affiliate_url": "string (main product website or official affiliate register link)",
        "pricing": "string (pricing description e.g., 'Starting at $19/mo')",
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
        # Validate schema keys
        required_keys = ['id', 'name', 'category', 'category_display', 'description', 'affiliate_url', 'pricing', 'key_features', 'rating', 'logo_url']
        if not all(k in new_tool for k in required_keys):
            print(f"Skipping tool due to missing keys: {new_tool.get('name')}")
            continue
            
        aff_url = new_tool.get('affiliate_url', '')
        if not aff_url.startswith('http'):
            print(f"Skipping tool due to invalid URL format: {new_tool.get('name')} ({aff_url})")
            continue

        # Auto resolve domain favicon logo
        if aff_url:
            try:
                domain = urllib.parse.urlparse(aff_url).netloc.replace('www.', '')
                if domain:
                    new_tool['logo_url'] = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
            except Exception:
                pass

        # Ensure commission key is removed
        if 'commission' in new_tool:
            del new_tool['commission']

        tool_id = new_tool['id']
        if tool_id not in existing_ids:
            existing_tools.append(new_tool)
            existing_ids.add(tool_id)
            new_tools_added += 1
            new_tools_list.append(new_tool)
            print(f"New tool added: {new_tool['name']}")
        else:
            for tool in existing_tools:
                if tool['id'] == tool_id and tool.get('pricing') != new_tool['pricing']:
                    updated_tools_list.append({"id": tool_id, "old_pricing": tool.get('pricing'), "new_pricing": new_tool['pricing']})
                    tool['pricing'] = new_tool['pricing']
                    updated_tools_count += 1
                    break

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

