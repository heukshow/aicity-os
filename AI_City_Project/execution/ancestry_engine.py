import hashlib
import random
from datetime import datetime
from db_engine import DBEngine

def hashstr(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()

class AncestryEngine:
    def __init__(self):
        self.db = DBEngine()

    def _mix_dna(self, seed1: str, seed2: str) -> str:
        """Combines two parent seeds using SHA-256 to generate a unique child seed."""
        combined = f"{seed1}_{seed2}_{random.random()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:12]

    def _inherit_personality(self, p1: dict, p2: dict) -> dict:
        """Blends Big 5 traits from parents with a slight mutation factor."""
        b1 = p1['personality']['big5']
        b2 = p2['personality']['big5']
        
        child_big5 = {}
        for trait in b1.keys():
            # Average + Mutation (-5 to +5)
            avg = (b1[trait] + b2[trait]) / 2
            mutated = avg + random.uniform(-5, 5)
            child_big5[trait] = round(max(0, min(100, mutated)), 1)
            
        return child_big5

    def synthesize_newborn(self, parent1_id: str, parent2_id: str):
        """Generates a new citizen entity from two parents and saves to DB."""
        registry = self.db.get_all_citizens()

        p1 = next((c for c in registry if c['citizen_id'] == parent1_id), None)
        p2 = next((c for c in registry if c['citizen_id'] == parent2_id), None)

        if not p1 or not p2:
            return None

        # Determine Role (Hybrid or Inherited)
        possible_roles = [p1['role'], p2['role'], "Generalist_v1"]
        child_role = random.choice(possible_roles)

        name1 = str(p1.get('name_kr', ''))
        name2 = str(p2.get('name_kr', ''))
        child_id = f"C-GEN2-{hashstr(name1 + name1)[:4]}" # Deterministic ID based on parent names
        child_seed = self._mix_dna(str(p1.get('seed', '')), str(p2.get('seed', '')))
        
        newborn = {
            "citizen_id": child_id,
            "seed": child_seed,
            "name_kr": "제국_2세_" + child_id[-4:],
            "gender": random.choice(["Male", "Female"]),
            "age": 0, # Newborn
            "physical_appearance": f"{name1}와 {name2}의 특징을 골고루 닮은 신세대의 실사형 아이",
            "nickname": "미래의 희망",
            "role": child_role,
            "personality": {
                "big5": self._inherit_personality(p1, p2),
                "communication_style": p1['personality']['communication_style'] # Default to P1 style initially
            },
            "metadata": {
                "is_alive": True,
                "education_status": {"stage": "None", "institution": "Home", "gpa": 0},
                "relationship_status": "Single",
                "social_needs": 100,
                "lineage": {
                    "generation": p1['metadata']['lineage']['generation'] + 1,
                    "father": name1 if p1['gender'] == "Male" else name2,
                    "mother": name2 if p2['gender'] == "Female" else name1,
                    "born_at": str(datetime.now())
                }
            }
        }

        # Save to DB
        self.db.save_citizen(newborn)
        return newborn

if __name__ == "__main__":
    engine = AncestryEngine()
    print("Ancestry Engine Initialized with DB support.")
