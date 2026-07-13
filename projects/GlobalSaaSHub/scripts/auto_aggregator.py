import os
import json
import urllib.request
import urllib.parse
import sys

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
    """Calls Gemini API using native HTTP request with JSON output configuration."""
    # Using gemini-2.5-flash as it supports JSON schema and is highly efficient
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
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers=headers, 
        method='POST'
    )
    
    print("-> Sending request to Gemini API (gemini-2.5-flash)...")
    sys.stdout.flush()
    try:
        with urllib.request.urlopen(req, timeout=90) as res:
            print("<- Received response from Gemini.")
            sys.stdout.flush()
            response_data = json.loads(res.read().decode('utf-8'))
            text_response = response_data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text_response)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        sys.stdout.flush()
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
    
    print(f"Project root: {project_root}")
    print(f"Data file: {data_file_path}")
    
    # 3. Load Existing Tools
    existing_tools = []
    if os.path.exists(data_file_path):
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                existing_tools = json.load(f)
            print(f"Loaded {len(existing_tools)} existing tools from database.")
        except Exception as e:
            print(f"Warning: Could not read existing tools, starting fresh. Error: {e}")
            
    existing_ids = {tool['id'] for tool in existing_tools}
    
    # 4. Search Queries
    queries = [
        "top new AI tool affiliate programs recurring commission 2026",
        "highest paying B2B SaaS recurring affiliate programs 2026",
        "trending AI agent workflow automation software recurring affiliate"
    ]
    
    raw_search_results = []
    for q in queries:
        print(f"Searching Tavily for: '{q}'...")
        results = query_tavily(tavily_key, q)
        if results and 'results' in results:
            for item in results['results']:
                raw_search_results.append({
                    "title": item.get("title"),
                    "content": item.get("content"),
                    "url": item.get("url")
                })
                
    print(f"Harvested {len(raw_search_results)} search snippets.")
    
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
        "rating": float (between 4.2 and 5.0),
        "logo_url": "string",
        "commission": "string"
      }
    ]
    
    Only extract valid SaaS tools. If the snippet does not contain enough detail for a tool, omit it.
    """
    
    extracted_tools = []
    print("Invoking Gemini for extraction and filtering on individual search snippets...")
    sys.stdout.flush()
    for idx, snippet in enumerate(raw_search_results):
        print(f"[{idx+1}/{len(raw_search_results)}] Processing snippet: '{snippet.get('title')}'...")
        sys.stdout.flush()
        user_content = json.dumps(snippet, indent=2)
        result = query_gemini(gemini_key, system_prompt, user_content)
        if result and isinstance(result, list):
            print(f"   Success! Extracted {len(result)} tools.")
            sys.stdout.flush()
            extracted_tools.extend(result)
        else:
            print("   No tools extracted or API call failed.")
            sys.stdout.flush()

    if not extracted_tools:
        print("Error: No tools were extracted from any search snippets.")
        sys.exit(1)
        
    print(f"Successfully compiled {len(extracted_tools)} total tools from all snippets.")
    sys.stdout.flush()
    
    # 6. Merge & Deduplicate
    new_tools_added = 0
    for new_tool in extracted_tools:
        # Validate schema keys
        required_keys = ['id', 'name', 'category', 'category_display', 'description', 'affiliate_url', 'pricing', 'key_features', 'rating', 'logo_url', 'commission']
        if not all(k in new_tool for k in required_keys):
            print(f"Skipping tool due to missing keys: {new_tool.get('name')}")
            continue
            
        tool_id = new_tool['id']
        if tool_id not in existing_ids:
            existing_tools.append(new_tool)
            existing_ids.add(tool_id)
            new_tools_added += 1
            print(f"New tool added: {new_tool['name']} ({new_tool['commission']})")
        else:
            # Optionally update pricing or commission if changed
            for tool in existing_tools:
                if tool['id'] == tool_id:
                    tool['pricing'] = new_tool['pricing']
                    tool['commission'] = new_tool['commission']
                    break
                    
    # 7. Write Back to File
    if new_tools_added > 0:
        try:
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_tools, f, indent=2, ensure_ascii=False)
            print(f"Database successfully updated. Added {new_tools_added} new tools. Total count: {len(existing_tools)}.")
        except Exception as e:
            print(f"Error writing to database: {e}")
            sys.exit(1)
    else:
        print("No new unique tools found during this cycle. Database is up to date.")
        
    print("Auto Aggregator Script completed successfully.")

if __name__ == "__main__":
    main()
