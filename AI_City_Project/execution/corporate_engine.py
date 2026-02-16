import os
import json
from datetime import datetime

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRECTIVES_DIR = os.path.join(PROJECT_ROOT, 'directives')
REGISTRY_FILE = os.path.join(DIRECTIVES_DIR, 'corporate_registry.json')

class CorporateEngine:
    """Manages virtual corporate entities and their strategic alignment (Haneul's Executive Tool)."""
    
    def __init__(self, db_engine=None):
        self.db = db_engine
        if not os.path.exists(REGISTRY_FILE):
            with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def establish_company(self, name, niche, founder_id="C-SECRETARY-01"):
        """Establishes a new virtual corporation under the Imperial Crown."""
        print(f"🏢 [Haneul] Establishing Virtual Inc: '{name}' (Niche: {niche})")
        
        company_id = f"INC-{abs(hash(name)) % 10000:04d}"
        new_company = {
            "company_id": company_id,
            "name": name,
            "niche": niche,
            "founded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "founder": founder_id,
            "staff": [],
            "status": "Active",
            "kpi": {"revenue_target": 5000000, "current_profit": 0, "roi": 0.0},
            "projects": []
        }
        
        with open(REGISTRY_FILE, 'r+', encoding='utf-8') as f:
            companies = json.load(f)
            companies.append(new_company)
            f.seek(0)
            json.dump(companies, f, indent=4, ensure_ascii=False)
            f.truncate()
            
        return company_id

    def appoint_staff(self, company_id, citizen_id, role="Executive"):
        """Assigns a citizen to a specific company."""
        with open(REGISTRY_FILE, 'r+', encoding='utf-8') as f:
            companies = json.load(f)
            for c in companies:
                if c['company_id'] == company_id:
                    if not any(s['id'] == citizen_id for s in c['staff']):
                        c['staff'].append({"id": citizen_id, "role": role})
                        print(f"🤝 [Haneul] Appointed {citizen_id} to {c['name']} as {role}.")
                    break
            f.seek(0)
            json.dump(companies, f, indent=4, ensure_ascii=False)
            f.truncate()

    def get_portfolio_summary(self):
        """Returns a summary of all active corporations for CEO briefing."""
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            companies = json.load(f)
        
        summary = []
        for c in companies:
            summary.append({
                "name": c['name'],
                "niche": c['niche'],
                "profit": c['kpi']['current_profit'],
                "staff_count": len(c['staff']),
                "status": c['status']
            })
        return summary

if __name__ == "__main__":
    # Test: Establishing the first Imperial Agency
    engine = CorporateEngine()
    inc_id = engine.establish_company("Imperial Video Lab", "AI Auto-Video Production")
    engine.appoint_staff(inc_id, "C-VIDE-01", role="CEO of Media")
    engine.appoint_staff(inc_id, "C-MARK-01", role="Growth Hacker")
    
    print("\n🏢 [Haneul] Portfolio Review:")
    for item in engine.get_portfolio_summary():
        print(f" - {item['name']}: {item['status']} | Profit: {item['profit']} KRW | Staff: {item['staff_count']}")
