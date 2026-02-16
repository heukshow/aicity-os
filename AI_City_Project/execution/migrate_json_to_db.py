import os
import json
from db_engine import DBEngine

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRECTIVES_DIR = os.path.join(PROJECT_ROOT, 'directives')
OPS_DIR = os.path.join(PROJECT_ROOT, 'ops')

REGISTRY_FILE = os.path.join(DIRECTIVES_DIR, 'citizen_registry.json')
SOCIAL_GRAPH_FILE = os.path.join(OPS_DIR, 'social_graph.json')

def run_migration():
    print("--- [MIGRATION] Imperial JSON to Imperial DB ---")
    db = DBEngine()
    
    # 1. Migrate Citizens
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            print(f"Migrating {len(registry)} Citizens...")
            for citizen in registry:
                db.save_citizen(citizen)
    
    # 2. Migrate Relationships
    if os.path.exists(SOCIAL_GRAPH_FILE):
        with open(SOCIAL_GRAPH_FILE, 'r', encoding='utf-8') as f:
            graph = json.load(f)
            relationships = graph.get('relationships', {})
            print(f"Migrating {len(relationships)} Relationships...")
            for pair_key, rel_data in relationships.items():
                db.save_relationship(pair_key, rel_data)

    db.close()
    print("Migration Complete.")

if __name__ == "__main__":
    run_migration()
