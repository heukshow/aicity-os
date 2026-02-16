from AI_City_Project.execution.central_cmd import AICityOS
import os

def test_haneul_activation():
    print("💎 [Haneul] Activating Secretary Execution Core for the Lord...")
    os_center = AICityOS()
    
    # 1. Test Imperial Agency Hunt
    leads = os_center.run_imperial_agency_hunt()
    
    print(f"\n💎 [Haneul] Hunt Results for the Lord:")
    for lead in leads:
        print(f" - Captured Lead: {lead['name']} ({lead['needs']}) in {lead['channel']}")
    
    # 2. Test Daily Ops (Briefing)
    print("\n💎 [Haneul] Preparing the Morning Briefing...")
    os_center.run_daily_ops()
    
    print("\n✅ [Haneul] Activation Test Completed. I am ready to serve 24/7.")

if __name__ == "__main__":
    test_haneul_activation()
