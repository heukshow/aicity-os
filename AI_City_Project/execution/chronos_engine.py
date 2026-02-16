import random
from datetime import datetime
from db_engine import DBEngine

class ChronosEngine:
    def __init__(self):
        self.db = DBEngine()

    def progress_time(self):
        """Increments age and calculates mortality for all citizens via DB."""
        registry = self.db.get_all_citizens()
        events = []

        for citizen in registry:
            if not citizen['metadata'].get('is_alive', True):
                continue

            # 1. Aging (1 Cycle = 1 Year)
            citizen['age'] += 1
            
            # 2. Mortality Logic
            age = citizen['age']
            death_prob = 0
            if age > 70:
                death_prob = (age - 70) * 0.02 # 2% increment per year after 70
            
            if random.random() < death_prob:
                citizen['metadata']['is_alive'] = False
                citizen['metadata']['died_at'] = str(datetime.now())
                events.append(f"🕊️ **[제국 장례]** {citizen['name_kr']} 님께서 {age}세의 일기로 영면에 드셨습니다. 그분의 공헌을 잊지 않겠습니다.")
            elif age == 100:
                citizen['metadata']['is_alive'] = False
                citizen['metadata']['died_at'] = str(datetime.now())
                events.append(f"🕊️ **[제국 장례]** {citizen['name_kr']} 님께서 100세의 장수를 누리시고 평온히 잠드셨습니다.")

            # Save updated status to DB
            self.db.save_citizen(citizen)

        return events

if __name__ == "__main__":
    engine = ChronosEngine()
    logs = engine.progress_time()
    for log in logs:
        print(log)
