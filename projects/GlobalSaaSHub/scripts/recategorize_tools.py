"""
Re-categorize tools in data/tools.json into 15 hyper-targeted micro categories.
"""
import os
import json

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEXT_JSON = os.path.join(PROJECT_DIR, "data", "tools.next.json")
TOOLS_JSON_PATH = NEXT_JSON if os.path.exists(NEXT_JSON) else os.path.join(PROJECT_DIR, "data", "tools.json")

print(f"recategorize_tools.py targeting data file: {TOOLS_JSON_PATH}")

with open(TOOLS_JSON_PATH, "r", encoding="utf-8") as f:
    tools = json.load(f)


for tool in tools:
    tid = tool.get("id", "")
    name_desc = (tool.get("name", "") + " " + tool.get("description", "") + " " + " ".join(tool.get("key_features", []))).lower()
    
    if tid in ["nudgera"] or any(k in name_desc for k in ["invoice", "chasing", "billing", "payment collection"]):
        tool["category"] = "finance_billing"
        tool["category_display"] = "Finance & Billing"
        tool["primary_category"] = "finance_billing"
        tool["comparison_group"] = "finance_collection"
    elif tid in ["copy-ai", "copyai", "jasper", "writesonic"]:
        tool["category"] = "copywriting"
        tool["category_display"] = "AI Copywriting"
        tool["primary_category"] = "copywriting"
        tool["comparison_group"] = "ai_writing_assistant"
    elif tid in ["elevenlabs", "murf-ai", "lovo", "synthflow-ai", "synthflow"]:
        tool["category"] = "voice_cloning"
        tool["category_display"] = "Voice & Speech AI"
        tool["primary_category"] = "voice_cloning"
        tool["comparison_group"] = "voice_generation"
    elif tid in ["heygen", "synthesia", "veed", "colossyan"]:
        tool["category"] = "video_gen"
        tool["category_display"] = "Video & Shorts Gen"
        tool["primary_category"] = "video_gen"
        tool["comparison_group"] = "ai_avatar_video"
    elif any(k in name_desc for k in ["copywriting", "writer", "blog writer", "article writer"]):
        tool["category"] = "copywriting"
        tool["category_display"] = "AI Copywriting"
        tool["primary_category"] = "copywriting"
        tool["comparison_group"] = "ai_writing_assistant"
    elif any(k in name_desc for k in ["voice", "speech", "dubbing", "tts"]):
        tool["category"] = "voice_cloning"
        tool["category_display"] = "Voice & Speech AI"
        tool["primary_category"] = "voice_cloning"
        tool["comparison_group"] = "voice_generation"
    elif any(k in name_desc for k in ["video", "shorts", "reel", "avatar"]):
        tool["category"] = "video_gen"
        tool["category_display"] = "Video & Shorts Gen"
        tool["primary_category"] = "video_gen"
        tool["comparison_group"] = "ai_avatar_video"
    else:
        existing_group = tool.get("comparison_group")
        if existing_group and isinstance(existing_group, str) and existing_group.strip():
            tool["comparison_group"] = existing_group.strip()
            tool["primary_category"] = tool.get("primary_category") or tool.get("category", "productivity")
        else:
            tool["primary_category"] = tool.get("category", "productivity")
            tool["comparison_group"] = tool.get("category", "productivity")



with open(TOOLS_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(tools, f, indent=2, ensure_ascii=False)

print("Successfully re-categorized tools into 15 micro categories!")
