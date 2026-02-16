import os
import google.generativeai as genai
from datetime import datetime
import re

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
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_blog_post():
    print("🤖 Sebastian: Researching High-Traffic Keywords...")
    
    # 1. Keyword Research (Sebastian)
    keyword_prompt = "You are Sebastian (SEO Strategist). Suggest ONE high-potential keyword for an AI automation blog targeting beginners in Korea. Output ONLY the keyword."
    keyword = "AI 수익화 기초" # Default fallback
    try:
        response = model.generate_content(keyword_prompt)
        if response and response.text:
            keyword = response.text.strip()
            print(f"✅ Target Keyword: {keyword}")
        else:
            print("⚠️ API returned empty. Using fallback keyword.")
    except Exception as e:
        print(f"⚠️ Error generating keyword: {e}. Using fallback.")

    # 2. Writing (Emma)
    print("🎨 Emma: Writing SEO Article...")
    write_prompt = f"""
    You are Emma (Content Writer). Write a 1,500-character SEO Blog Post about '{keyword}'.
    Target Audience: Korean beginners interested in passive income.
    Tone: Encouraging, Professional, easy to read.
    Format: HTML (No <html>/<body> tags, just content).
    Structure:
    - H1: Catchy Title including '{keyword}'
    - Intro: Hook the reader.
    - H2: Why this matters
    - H2: How to start (3 steps)
    - H2: Conclusion
    - Call to Action: Link to 'index.html' for the newsletter.
    Output ONLY valid HTML code.
    """
    
    content = f"""
    <h1>{keyword} 완전 정복 가이드</h1>
    <p>AI로 돈을 버는 것은 더 이상 꿈이 아닙니다. 지금 바로 시작하세요.</p>
    <h2>왜 지금인가?</h2>
    <p>기술의 발전 속도가 빠릅니다. 먼저 선점하는 사람이 승리합니다.</p>
    <h2>시작하는 3가지 단계</h2>
    <ul>
        <li>1. AI 툴 익히기</li>
        <li>2. 작은 프로젝트 시작하기</li>
        <li>3. 수익화 모델 붙이기</li>
    </ul>
    <h2>결론</h2>
    <p>지금 바로 Omega Team과 함께하세요.</p>
    <a href="/index.html">뉴스레터 구독하기</a>
    """ # Fallback content
    
    try:
        response = model.generate_content(write_prompt)
        if response and response.text:
            content = response.text.replace("```html", "").replace("```", "")
            print("✅ Content Generated via API.")
        else:
            print("⚠️ API returned empty. Using fallback content.")
    except Exception as e:
        print(f"⚠️ Error generating content: {e}. Using fallback.")
    
    # Create valid HTML file
    slug = re.sub(r'[^a-z0-9]', '-', keyword.lower()) or "new-post"
    filename = f"posts/{datetime.now().strftime('%Y%m%d')}_{slug}.html"
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{keyword} - Omega Blog</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Pretendard', sans-serif; background-color: #0f172a; color: #e2e8f0; }}
            article {{ max-width: 700px; margin: 0 auto; padding: 40px 20px; }}
            h1 {{ font-size: 2.5rem; font-weight: 800; color: #38bdf8; margin-bottom: 20px; }}
            h2 {{ font-size: 1.8rem; font-weight: 700; color: #a5f3fc; margin-top: 40px; margin-bottom: 15px; }}
            p {{ margin-bottom: 15px; line-height: 1.8; color: #cbd5e1; }}
            ul {{ list-style-type: disc; padding-left: 20px; margin-bottom: 20px; color: #cbd5e1; }}
            li {{ margin-bottom: 10px; }}
            a {{ color: #60a5fa; text-decoration: underline; }}
            .back-link {{ display: block; margin-bottom: 40px; color: #94a3b8; text-decoration: none; }}
            .back-link:hover {{ color: #fff; }}
        </style>
    </head>
    <body>
        <article>
            <a href="/index.html" class="back-link">← 메인으로 돌아가기</a>
            {content}
            <div style="background: rgba(30,41,59,0.5); border: 1px solid #334155; padding: 30px; border-radius: 15px; margin-top: 50px; text-align: center;">
                <h3 style="font-size: 1.5rem; font-weight: bold; margin-bottom: 10px;">더 많은 정보를 원하시나요?</h3>
                <p>매주 AI 트렌드를 받아보세요.</p>
                <a href="/index.html" style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); color: white; padding: 12px 25px; border-radius: 10px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px;">무료 뉴스레터 구독하기</a>
            </div>
        </article>
    </body>
    </html>
    """
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"🚀 Blog Post Generated: {filename}")

if __name__ == "__main__":
    if not os.path.exists('posts'):
        os.makedirs('posts')
    generate_blog_post()
