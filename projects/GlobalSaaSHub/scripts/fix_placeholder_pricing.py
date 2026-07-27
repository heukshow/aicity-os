"""
Fix placeholder pricing strings like '$X/mo' in data/tools.json
"""
import os
import json

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_JSON_PATH = os.path.join(PROJECT_DIR, "data", "tools.json")

pricing_fixes = {
    "bolddesk": "Free plan / $12/mo",
    "brand24": "Starting at $79/mo",
    "socialchamp-io": "Starting at $29/mo",
    "triple-whale": "Starting at $129/mo",
    "boldsign": "Starting at $10/mo",
    "privy": "Starting at $30/mo",
    "aweber": "Free plan / $12.50/mo",
    "unbounce": "Starting at $99/mo",
    "moosend": "Starting at $9/mo",
    "reply-io": "Starting at $60/mo",
    "omnisend": "Free plan / $16/mo"
}

with open(TOOLS_JSON_PATH, "r", encoding="utf-8") as f:
    tools = json.load(f)

updated_count = 0
for tool in tools:
    pricing = tool.get("pricing", "")
    if "$X" in pricing or "Starting at $X" in pricing:
        tool_id = tool.get("id", "")
        if tool_id in pricing_fixes:
            tool["pricing"] = pricing_fixes[tool_id]
        else:
            tool["pricing"] = "Check website for pricing"
        updated_count += 1

with open(TOOLS_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(tools, f, indent=2, ensure_ascii=False)

print(f"Fixed {updated_count} tools with $X placeholder pricing in tools.json!")
