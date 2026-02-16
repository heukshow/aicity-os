import os
import json
from datetime import datetime
from db_engine import DBEngine

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRECTIVES_DIR = os.path.join(PROJECT_ROOT, 'directives')

class EducationEngine:
    def __init__(self):
        self.db = DBEngine()
        self.curriculum_file = os.path.join(DIRECTIVES_DIR, 'curriculum_db.json')

    def _load_curriculum(self):
        with open(self.curriculum_file, 'r', encoding='utf-8') as f:
            return json.load(f)['education_stages']

    def update_education_status(self):
        """Checks citizen age and updates their education stage via DB."""
        registry = self.db.get_all_citizens()
        curriculum = self._load_curriculum()
        events = []

        for citizen in registry:
            if not citizen['metadata'].get('is_alive', True):
                continue

            age = citizen['age']
            current_status = citizen['metadata'].get('education_status', {})
            current_stage = current_status.get('stage', "None")
            found_stage = "None"
            stage_info = {}

            # Determine appropriate stage based on age
            for stage_name, info in curriculum.items():
                if info['age_range'][0] <= age <= info['age_range'][1]:
                    found_stage = stage_name
                    stage_info = info
                    break

            # Handle Transition/Graduation
            if found_stage != current_stage and found_stage != "None":
                citizen['metadata']['education_status'] = {
                    "stage": found_stage,
                    "institution": stage_info['institution'],
                    "enrollment_date": str(datetime.now()),
                    "gpa": current_status.get('gpa', 4.5) # Preserve GPA if existing
                }
                
                if current_stage == "None" or current_status.get('institution') == "Home":
                    events.append(f"🎉 **[입학 축하]** {citizen['name_kr']}({age}세) 님이 {stage_info['institution']}에 입학하여 제국의 첫 배움을 시작했습니다!")
                else:
                    events.append(f"🎓 **[졸업 및 진학]** {citizen['name_kr']} 님이 {current_stage} 과정을 성공적으로 마치고 {stage_info['institution']}으로 진학했습니다!")

            # Save updated status to DB
            self.db.save_citizen(citizen)

        return events

if __name__ == "__main__":
    engine = EducationEngine()
    logs = engine.update_education_status()
    for log in logs:
        print(log)
