import os
import json
import time
from datetime import datetime

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
MARKETING_LOG = os.path.join(LOGS_DIR, 'marketing_activity.log')
PII_APPROVED = False # Lord's Account Connection Status

def log_marketing(agent, action, target, result):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # If PII not approved, mark as simulation
    if not PII_APPROVED:
        result = f"SIMULATED (Waiting for Account Connection) | {result}"
        action = f"[DRY-RUN] {action}"
    
    log_entry = f"[{timestamp}] [{agent}] {action} -> {target} | Result: {result}\n"
    with open(MARKETING_LOG, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    print(log_entry.strip())

class MarketingMachine:
    """The Active Outreach Unit (Park HaeNa & Lee JiWoo)"""
    
    def run_campaign(self):
        print("🚀 [Marketing Machine] Launching active outreach campaign...")
        
        targets = [
            {"name": "Local_Cafe_Owner", "platform": "Instagram DM"},
            {"name": "Startup_CEO_K", "platform": "LinkedIn Message"},
            {"name": "Ecom_Seller_Z", "platform": "Cold Email"}
        ]
        
        for target in targets:
            # Simulated delay for 'real' feeling
            # time.sleep(1) 
            log_marketing(
                "Park HaeNa", 
                f"Sent Automated Proposal ({target['platform']})", 
                target['name'], 
                "SENT/AWAITING_REPLY"
            )
        
        print(f"✅ Campaign completed. Check logs at: {MARKETING_LOG}")

if __name__ == "__main__":
    machine = MarketingMachine()
    machine.run_campaign()
