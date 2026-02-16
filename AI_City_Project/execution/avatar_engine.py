import os
import json
from datetime import datetime

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AVATARS_DIR = os.path.join(PROJECT_ROOT, 'assets', 'avatars')
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'assets', 'scripts')
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')

if not os.path.exists(AVATARS_DIR):
    os.makedirs(AVATARS_DIR)

from typing import Dict, Any

class AvatarEngine:
    """The Imperial Avatar Management Engine (Visualizing Citizens)"""
    
    def __init__(self):
        self.avatar_registry: Dict[str, Any] = self._load_registry()

    def _load_registry(self):
        registry_path = os.path.join(AVATARS_DIR, 'registry.json')
        if os.path.exists(registry_path):
            with open(registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"avatars": {}}

    def _save_registry(self):
        registry_path = os.path.join(AVATARS_DIR, 'registry.json')
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.avatar_registry, f, indent=2, ensure_ascii=False)

    def get_avatar_status(self, agent_id):
        """Returns the visual status of a citizen."""
        avatar = self.avatar_registry["avatars"].get(agent_id)
        if not avatar:
            return "None"
        return "Animated" if avatar.get("animated") else "Portrait_Only"

    def register_avatar(self, agent_name, image_path, age, style):
        """Registers a generated portrait to the citizen library."""
        self.avatar_registry["avatars"][agent_name] = {
            "image_path": image_path,
            "age": age,
            "style": style,
            "animated": False,
            "registered_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self._save_registry()
        print(f"🎭 [Avatar] Citizen '{agent_name}' registered successfully.")

    def get_lip_sync_prompt(self, agent_name, script_text):
        """Generates a prompt/package for Talking Head synthesis (SadTalker/HeyGen style)."""
        avatar = self.avatar_registry["avatars"].get(agent_name)
        if not avatar:
            return f"Error: No avatar registered for '{agent_name}'."

        prompt = {
            "agent": agent_name,
            "source_image": avatar["image_path"],
            "script": script_text,
            "animation_style": "Realistic_Professional",
            "lip_sync_mode": "High_Precision",
            "instruction": "Animate the lips to match the provided script with subtle head movements."
        }
        
        filename = f"animation_prep_{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(os.path.join(OUTPUTS_DIR, filename), 'w', encoding='utf-8') as f:
            json.dump(prompt, f, indent=2, ensure_ascii=False)
            
        print(f"🎬 [Avatar] Animation prep for '{agent_name}' saved to {filename}")
        return prompt

if __name__ == "__main__":
    engine = AvatarEngine()
    # Mock registration
    engine.register_avatar("강한수", "assets/avatars/agent_hanhsu.png", 35, "Professional Suit")
    engine.get_lip_sync_prompt("강한수", "당신의 통장이 잠들지 않는 마법, 보신 적 있나요?")
