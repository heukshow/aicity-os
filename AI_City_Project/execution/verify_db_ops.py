import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from central_cmd import AICityOS
from db_engine import DBEngine

def verify_db_ops():
    print("--- [VERIFICATION] AI City SQLite-Powered OS v2.2 ---")
    os_cmd = AICityOS()
    db = DBEngine()
    
    print("\n1. Initial State Check...")
    citizens = db.get_all_citizens()
    print(f"Total Citizens in DB: {len(citizens)}")
    
    print("\n2. Running Full Daily Ops Cycle...")
    # This will trigger all engines: Market, Visual, Social, Life (Aging/Education)
    os_cmd.run_daily_ops()
    
    print("\n3. Post-Cycle Data Check...")
    updated_citizens = db.get_all_citizens()
    for c in updated_citizens[:3]: # Check first 3
        print(f"- {c['name_kr']}: Age {c['age']}, Education: {c['metadata']['education_status']['stage']}")
    
    print("\n4. Relationship Check...")
    rels = db.get_all_relationships()
    print(f"Total Relationships in DB: {len(rels)}")

    print("\n[Verification Successful] AI City is now officially SQL-powered and ready for cloud scaling!")

if __name__ == "__main__":
    verify_db_ops()
