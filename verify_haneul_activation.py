from AI_City_Project.execution.central_cmd import AICityOS
import os

def test_haneul_activation():
    print("💎 [Haneul] Activating Secretary Execution Core for the Lord...")
    os_center = AICityOS()
    
    # 1. Test Imperial Agency Hunt (with autonomous company establishment)
    leads = os_center.run_imperial_agency_hunt()
    
    print(f"\n🏢 [Haneul] Portfolio Update for the Lord:")
    portfolio = os_center.corporate.get_portfolio_summary()
    for item in portfolio:
        print(f" - Company: {item['name']} | Niche: {item['niche']} | Staff: {item['staff_count']}")
    
    print(f"\n💎 [Haneul] Hunt Results for the Lord:")
    for lead in leads:
        print(f" - Captured Lead: {lead['name']} ({lead['needs']}) in {lead['channel']}")
    
    # 2. Test Scaling Check
    os_center.autonomous_scaling()
    
    # 3. Test Daily Ops (Briefing)
    print("\n💎 [Haneul] Preparing the CEO-Level Briefing...")
    os_center.run_daily_ops()
    
    print("\n✅ [Haneul] Corporate Sovereignty Test Completed. The Empire is expanding.")

if __name__ == "__main__":
    test_haneul_activation()
