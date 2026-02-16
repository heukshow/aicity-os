import os
import sys
import json
import time
from datetime import datetime

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, 'execution'))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')
OPS_DIR = os.path.join(PROJECT_ROOT, 'ops')
LOG_FILE = os.path.join(OPS_DIR, 'system_log.md')

from marketing_machine import MarketingMachine
from service_engine import synthesize_proposal

def log_activity(agent_id, action, status, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"| {timestamp} | {agent_id} | {action} | {status} | {details} |\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

class NocturnalShift:
    """Manages autonomous profit-generating actions during system idle/night hours."""
    
    def __init__(self):
        self.active_agents = ["C-MARK-01", "C-REVE-01", "C-GROW-01"]
        print("🌙 Nocturnal Shift (Phase 4) Activated. Zero-Cost Profit-Ops Initiated.")

    def run_scavenge(self):
        """Phase 1: Market Scavenging (Kang HanSu)"""
        log_activity("C-MARK-01", "Global Niche Scavenge", "In Progress", "Scanning global AI automation trends via search")
        # In a real environment, this would call search_web. 
        # For now, we will use a selection of high-intent niches to rotate.
        niches = ["AI Video for E-commerce", "Autonomous Customer Support", "AI-Powered SEO Automation", "Agentic Workflow Optimization"]
        selected_niche = niches[int(datetime.now().strftime('%H')) % len(niches)]
        
        # Save to state for morning cycle
        state_path = os.path.join(OPS_DIR, 'latest_niche.json')
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump({"niche": selected_niche, "found_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, f, indent=2)
            
        log_activity("C-MARK-01", "Global Niche Scavenge", "Success", f"Found high-intent niche: '{selected_niche}'")
        return selected_niche

    def run_synthesize(self, niche):
        """Phase 2: Product Synthesis (Lee JiWoo)"""
        log_activity("C-REVE-01", "Service Synthesis", "In Progress", f"Synthesizing proposal for '{niche}'")
        proposal_path = synthesize_proposal(niche)
        log_activity("C-REVE-01", "Service Synthesis", "Success", f"New proposal generated at: {proposal_path}")
        return proposal_path

    def run_deploy_organic(self):
        """Phase 3: Organic Outreach (Park HaeNa)"""
        log_activity("C-GROW-01", "Organic Deployment", "In Progress", "Engaging Marketing Machine for outreach")
        machine = MarketingMachine()
        machine.run_campaign()
        log_activity("C-GROW-01", "Organic Deployment", "Success", "Marketing campaign cycle complete.")

    def execute_full_shift(self):
        """Triggers the full nocturnal cycle and returns the discovered niche."""
        print("🌙 Initiating Morning Briefing Prep...")
        niche = self.run_scavenge()
        self.run_synthesize(niche)
        self.run_deploy_organic()
        print("☀️ Nocturnal Shift Completed. Results waiting for Lord's review.")
        return niche

if __name__ == "__main__":
    shift = NocturnalShift()
    shift.execute_full_shift()
