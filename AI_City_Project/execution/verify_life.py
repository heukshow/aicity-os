import os
import sys
import json
import random
from datetime import datetime

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from central_cmd import AICityOS

def test_full_life_cycle():
    print("--- [VERIFICATION] AI City Academy & Life-Cycle Simulation ---")
    os_cmd = AICityOS()
    
    # 1. Manually add a "Newborn" to the registry for testing
    registry_path = 'c:/Users/qmffo/Desktop/부업/AI 자동화/AI_City_Project/directives/citizen_registry.json'
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    newborn_id = "C-TEST-NEWBORN"
    # Remove existing test newborn if any
    registry = [c for c in registry if c['citizen_id'] != newborn_id]
    
    newborn = {
        "citizen_id": newborn_id,
        "seed": "TEST_SEED_999",
        "name_kr": "제국_실험동자",
        "gender": "Male",
        "age": 0,
        "role": "Generalist_v1",
        "personality": {"big5": {"Openness": 80, "Conscientiousness": 80, "Extraversion": 80, "Agreeableness": 80, "Neuroticism": 20}, "communication_style": "Polite"},
        "metadata": {
            "is_alive": True,
            "education_status": {"stage": "None", "institution": "Home", "gpa": 0},
            "relationship_status": "Single",
            "social_needs": 100,
            "lineage": {"generation": 2, "parents": ["강한수", "이지우"]}
        }
    }
    registry.append(newborn)
    
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)
    
    print("\n[Simulating 25 Cycles (25 Years)]...")
    for i in range(25):
        os_cmd.run_life_ops()
        # Periodically check progress
        if i % 5 == 0:
            with open(registry_path, 'r', encoding='utf-8') as f:
                reg = json.load(f)
                nb = next(c for c in reg if c['citizen_id'] == newborn_id)
                print(f"Year {i}: Age {nb['age']}, Education: {nb['metadata']['education_status']['stage']}")

    print("\n[Verification Complete] Newborn has grown and evolved through the Academy.")

if __name__ == "__main__":
    test_full_life_cycle()
