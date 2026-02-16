import sqlite3
import os
import json

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPS_DIR = os.path.join(PROJECT_ROOT, 'ops')
DB_PATH = os.path.join(OPS_DIR, 'imperial_city.db')

class DBEngine:
    def __init__(self):
        # Ensure the directory exists
        if not os.path.exists(OPS_DIR):
            os.makedirs(OPS_DIR, exist_ok=True)
            print(f"Imperial Cloud: Created directory {OPS_DIR}")
        
        print(f"Imperial Cloud: Connecting to DB at {DB_PATH}")
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
        except sqlite3.OperationalError as e:
            print(f"Imperial Cloud ERROR: Could not open database at {DB_PATH}. {e}")
            raise

    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # Citizens Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS citizens (
                citizen_id TEXT PRIMARY KEY,
                name_kr TEXT,
                seed TEXT,
                gender TEXT,
                age INTEGER,
                role TEXT,
                personality_json TEXT,
                metadata_json TEXT
            )
        ''')
        
        # Relationships Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                pair_key TEXT PRIMARY KEY,
                citizen_a TEXT,
                citizen_b TEXT,
                affinity REAL,
                bond REAL,
                status TEXT,
                interactions_count INTEGER,
                FOREIGN KEY(citizen_a) REFERENCES citizens(citizen_id),
                FOREIGN KEY(citizen_b) REFERENCES citizens(citizen_id)
            )
        ''')
        
        self.conn.commit()

    def save_citizen(self, citizen_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO citizens 
            (citizen_id, name_kr, seed, gender, age, role, personality_json, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            citizen_data['citizen_id'],
            citizen_data['name_kr'],
            citizen_data['seed'],
            citizen_data['gender'],
            citizen_data['age'],
            citizen_data['role'],
            json.dumps(citizen_data['personality'], ensure_ascii=False),
            json.dumps(citizen_data['metadata'], ensure_ascii=False)
        ))
        self.conn.commit()

    def get_all_citizens(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM citizens')
        rows = cursor.fetchall()
        
        citizens = []
        for row in rows:
            citizens.append({
                "citizen_id": row['citizen_id'],
                "name_kr": row['name_kr'],
                "seed": row['seed'],
                "gender": row['gender'],
                "age": row['age'],
                "role": row['role'],
                "personality": json.loads(row['personality_json']),
                "metadata": json.loads(row['metadata_json'])
            })
        return citizens

    def save_relationship(self, pair_key, rel_data):
        citizen_a, citizen_b = pair_key.split('__')
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO relationships 
            (pair_key, citizen_a, citizen_b, affinity, bond, status, interactions_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pair_key,
            citizen_a,
            citizen_b,
            rel_data['affinity'],
            rel_data['bond'],
            rel_data['status'],
            rel_data['interactions_count']
        ))
        self.conn.commit()

    def get_all_relationships(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM relationships')
        rows = cursor.fetchall()
        
        relationships = {}
        for row in rows:
            relationships[row['pair_key']] = {
                "affinity": row['affinity'],
                "bond": row['bond'],
                "status": row['status'],
                "interactions_count": row['interactions_count']
            }
        return relationships

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = DBEngine()
    print("Imperial Database Initialized & Tables Created.")
    db.close()
