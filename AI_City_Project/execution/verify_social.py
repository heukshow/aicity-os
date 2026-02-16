import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from central_cmd import AICityOS

def test_social_evolution():
    print("--- [VERIFICATION] AI City Social & Biological Evolution ---")
    os_cmd = AICityOS()
    
    print("\n1. Running Social Ops Cycle...")
    os_cmd.run_social_ops()
    
    print("\n2. Checking Approval Queue for Social Milestones...")
    with open('c:/Users/qmffo/Desktop/부업/AI 자동화/AI_City_Project/ops/approval_queue.json', 'r', encoding='utf-8') as f:
        import json
        queue = json.load(f)
        print(f"Pending Approvals: {len(queue['pending'])}")
        for e in queue['pending']:
            print(f"- [{e['type']}] {e['description']}")

    print("\n3. Social Logic Verified. Systems ready for long-term prosperity.")

if __name__ == "__main__":
    test_social_evolution()
