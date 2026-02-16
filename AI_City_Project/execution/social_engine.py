import os
import random
from db_engine import DBEngine

class SocialEngine:
    def __init__(self):
        self.db = DBEngine()

    def _get_affinity_score(self, p1, p2):
        """Calculates base compatibility using Big 5 personality traits."""
        b1 = p1['personality']['big5']
        b2 = p2['personality']['big5']
        
        # Calculate Euclidean distance between personalities (Lower distance = Higher affinity)
        dist = sum((b1[k] - b2[k])**2 for k in b1.keys())**0.5
        # Normalize: Distance 0-223 (sqrt(100^2 * 5)) -> Score 0-100
        score = max(0, 100 - (dist / 2.23))
        
        return round(score, 2)

    def update_relationships(self):
        """Main loop to tick relationship values based on interactions and affinity via DB."""
        registry = self.db.get_all_citizens()
        graph = self.db.get_all_relationships()

        interactions = []
        
        for i, c1 in enumerate(registry):
            for j, c2 in enumerate(registry):
                if i >= j: continue
                
                pair_key = f"{c1['citizen_id']}__{c2['citizen_id']}"
                if pair_key not in graph:
                    graph[pair_key] = {
                        "affinity": self._get_affinity_score(c1, c2),
                        "bond": random.uniform(0, 10), # Initial bond
                        "status": "Acquaintance",
                        "interactions_count": 0
                    }
                
                rel = graph[pair_key]
                
                # Tick Bond: If affinity is high (>70), bond grows. If low (<30), bond may decay.
                growth = (rel['affinity'] - 50) / 100 * random.uniform(0.1, 2.0)
                rel['bond'] = max(-100, min(100, rel['bond'] + growth))
                
                # Social Encounter Chance
                if random.random() < 0.2: # 20% chance of an encounter per cycle
                    rel['interactions_count'] += 1
                    rel['bond'] += random.uniform(0.5, 3.0)
                    interactions.append(f"{c1['name_kr']}와(과) {c2['name_kr']}이(가) 점심 식사 중에 깊은 대화를 나누었습니다. (친밀도: {rel['bond']:.1f})")

                # Status Promotion
                if rel['bond'] > 80 and rel['status'] != "Lover":
                    if rel['affinity'] > 85:
                        rel['status'] = "Lover"
                        interactions.append(f"⚠️ **[제국 스캔들]** {c1['name_kr']}와(과) {c2['name_kr']} 사이에 심상치 않은 기류가 감지되었습니다. (연인 관계 진입)")
                    elif rel['status'] != "Best Friend":
                        rel['status'] = "Best Friend"
                        interactions.append(f"✨ {c1['name_kr']}와(과) {c2['name_kr']}이(가) 이제 영혼의 단짝이 되었습니다.")

                # Save updated relationship to DB
                self.db.save_relationship(pair_key, rel)
            
        return interactions

if __name__ == "__main__":
    engine = SocialEngine()
    logs = engine.update_relationships()
    for log in logs:
        print(log)
