import os
import google.generativeai as genai
from datetime import datetime

# Load Key
def load_env():
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                return parse_env(f)
        except UnicodeDecodeError:
            try:
                with open('.env', 'r', encoding='utf-16') as f:
                    return parse_env(f)
            except:
                pass
    return None

def parse_env(f):
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            if k == 'STITCH_API_KEY':
                return v.strip().strip('"')
    return None

API_KEY = os.environ.get("STITCH_API_KEY") or load_env()

if not API_KEY:
    print("Error: No API Key found.")
    exit(1)

genai.configure(api_key=API_KEY)
# Use a trusted model version if possible, or default to general alias
model = genai.GenerativeModel('gemini-pro')

def generate_issue():
    print("🤖 Sebastian: Researching AI Trends...")
    topic = "Top 3 AI Automation Tools for Passive Income in 2026"
    
    # 1. Strategy (Sebastian)
    strategy_prompt = f"You are Sebastian (Strategist). Analyze '{topic}' and outline 3 key points for a newsletter. High value, actionable. Korean."
    try:
        strategy = model.generate_content(strategy_prompt).text
        print("✅ Strategy Locked.")
    except Exception as e:
        print(f"Error generating strategy: {e}")
        return

    # 2. Writing (Emma)
    print("🎨 Emma: Writing Content...")
    write_prompt = f"""
    You are Emma (Editor). Based on this strategy:\n{strategy}\n
    Write a premium HTML Newsletter. 
    Style: Minimalist, Cyberpunk accents (Dark mode friendly).
    Structure:
    - Header: 'Future Digest Vol.1' (H1)
    - Intro: Hook the reader (Why this matters now).
    - Body: 3 Sections with icons (The 3 Tools).
    - Conclusion: Call to Action (Upgrade to Premium).
    - Footer: 'Published by Omega Team'.
    Output ONLY valid HTML code content (e.g., <div>...</div>). Do not include <html> or <body> tags.
    """
    try:
        content = model.generate_content(write_prompt).text
    except Exception as e:
        print(f"Error generating content: {e}")
        return
    
    # Clean up markdown code blocks if present
    content = content.replace("```html", "").replace("```", "")
    
    # Save
    filename = f"newsletter_vol1_{datetime.now().strftime('%Y%m%d')}.html"
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #888; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
    </head>
    <body>
        {content}
        <div class="footer">
            <p>&copy; 2026 Omega Team Venture. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"🚀 Newsletter Generated: {filename}")
    print("Process Complete. Open the file to review.")

if __name__ == "__main__":
    generate_issue()
