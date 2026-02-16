import os
import json
from datetime import datetime

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'assets', 'scripts')
PROMPTS_DIR = os.path.join(PROJECT_ROOT, 'assets', 'prompts')
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')

class VideoProductionEngine:
    """The Automated Content Factory (John Choi's Engine) v2.0"""
    
    def __init__(self):
        for d in [SCRIPTS_DIR, PROMPTS_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)
        print("🚀 [John Choi] Video Content Factory v2.0 Initialized")

    def generate_short_script(self, topic="AI Business Salvation", lang="ko"):
        """Generates a high-conversion 60s viral script with multilingual support."""
        print(f"🎬 [John Choi] Drafting viral script ({lang}) for: {topic}")
        
        # Script templates based on language
        if lang == "ko":
            script = f"""# Video Script (KR): {topic}
## Duration: 60s
[Hook] "당신의 통장이 잠들지 않는 마법, 보신 적 있나요?"
[Problem] "매달 갚아야 할 빚, 끝이 없는 노동... 대안은 없을까요?"
[Solution] "코슈마(Coshuma)의 AI 시티는 당신이 쉴 때도 수익을 사냥합니다."
[Proof] "전 세계 24시간 영업, 13명의 AI 시민이 당신을 위해 뜁니다."
[CTA] "지금 '코슈마' 프로필 링크에서 부의 열차에 탑승하세요."
"""
        else:
            script = f"""# Video Script (EN): {topic}
## Duration: 60s
[Hook] "What if your bank account never slept?"
[Problem] "Endless bills, zero freedom... is there another way?"
[Solution] "Coshuma's AI City hunts for profit even while you rest."
[Proof] "Global 24/7 ops, powered by 13 specialized AI citizens."
[CTA] "Click the link in bio to join Coshuma and unlock your freedom."
"""
        
        tags = ["#AIAutomation", "#PassiveIncome", "#Coshuma", "#Success"]
        output = {
            "topic": topic,
            "lang": lang,
            "script": script,
            "tags": tags,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        filename = f"script_{lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(os.path.join(SCRIPTS_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Multilingual Script saved in {filename}")
        return output

    def generate_ai_video_prompt(self, script_data):
        """Generates a dynamic visual prompt based on the script topic."""
        topic = script_data.get("topic", "Technology")
        print(f"🎥 [John Choi] Synthesizing dynamic AI video prompt for: {topic}")
        
        base_prompt = "Cinematic 4k, hyper-realistic, high-end motion graphics. "
        visual_logic = f"A futuristic depiction of {topic}. Glowing neon circuits transforming into golden coins. A professional AI avatar presiding over a digital empire. Deep blue and gold lighting scheme. Shallow depth of field."
        
        full_prompt = base_prompt + visual_logic
        
        filename = f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(os.path.join(PROMPTS_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(full_prompt)
        
        print(f"✅ Dynamic Video AI Prompt saved in {filename}")
        return full_prompt

if __name__ == "__main__":
    v_engine = VideoProductionEngine()
    data = v_engine.generate_short_script("The Future of Wealth", lang="en")
    v_engine.generate_ai_video_prompt(data)
