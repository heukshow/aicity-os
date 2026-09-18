from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "App.jsx"
text = APP.read_text(encoding="utf-8")

required = [
    "import allToolsData from './generated/public-tools.json';",
    "tool.is_sponsored === true",
    "tool.outbound_url",
    "data-cta={isSponsored ? 'affiliate' : 'official'}",
    "trackToolClick(tool.id, tool.name, validUrl, isSponsored)",
    "{isSponsored ? 'View current offer' : 'Visit official site'}",
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"home boundary guard missing required public marker: {marker}")

blocked = [
    "../data/tools.json",
    "affiliate_verified",
    "affiliate_status",
    "affiliate_evidence",
    "affiliate_next_action",
    "application_state",
    "PartnerStack",
    "FirstPromoter",
    "Verified affiliate paths",
    "Affiliate link verified in our records",
    "Check verified offer",
]
for token in blocked:
    if token in text:
        raise SystemExit(f"home boundary guard found forbidden internal token: {token}")

print("guard_home_affiliate_state: frontend source is customer-only; internal affiliate state absent")
