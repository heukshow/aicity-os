"""Fail closed when COSHUMA's public affiliate policy drifts across build stages."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config" / "public_content_policy.json").read_text(encoding="utf-8"))
PACKAGE = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
BUILD = PACKAGE["scripts"]["build"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Public policy contract violation: {message}")


stages = POLICY["stages"]
disclosure = POLICY["affiliate_disclosure"]

require(POLICY.get("policy_owner") == "config/public_content_policy.json", "central policy owner changed")
require(stages["source"]["page_disclosures_allowed"] is False, "source stage must remain disclosure-neutral")
require(stages["final_dist"]["page_disclosures_required_for_affiliate_cta"] is True, "final affiliate pages must require disclosure")
require(stages["final_dist"]["fail_closed_on_internal_ops_leak"] is True, "final internal-info guard must fail closed")

# The retired post-build cleaner caused the regression by removing legally required
# page-level notices from the final bundle. It must never return to the build chain.
require("enforce_home_only_affiliate_disclosure.py" not in BUILD, "deprecated home-only final-bundle cleaner is active")

vite_at = BUILD.find("vite build")
source_guard_at = BUILD.find("self_heal_source_affiliate_disclosures.py")
final_guard_at = BUILD.find("guard_built_customer_copy.py")
artifact_guard_at = BUILD.find("guard_public_artifact_boundary.py dist")
require(vite_at >= 0, "vite build missing")
require(source_guard_at >= 0 and source_guard_at < vite_at, "source disclosure hygiene must run only before Vite")
require(final_guard_at > vite_at, "canonical final disclosure guard must run after Vite")
require(artifact_guard_at > final_guard_at, "final artifact boundary guard must run after disclosure normalization")

built_guard = (ROOT / "scripts" / "guard_built_customer_copy.py").read_text(encoding="utf-8")
tracker_guard = (ROOT / "scripts" / "verify_approved_tracking.mjs").read_text(encoding="utf-8")
artifact_guard = (ROOT / "scripts" / "guard_public_artifact_boundary.py").read_text(encoding="utf-8")

require(disclosure["homepage_text"] in built_guard, "built guard homepage disclosure differs from central policy")
require(disclosure["page_text"] in built_guard, "built guard page disclosure differs from central policy")
require(disclosure["homepage_marker"] in built_guard, "built guard homepage marker differs from central policy")
require(disclosure["page_marker"] in built_guard, "built guard page marker differs from central policy")
require("PAGE_AFFILIATE_CTA" in built_guard and "count=1" in built_guard, "built guard no longer inserts once before first affiliate CTA")

require('data-affiliate-disclosure="page"' in tracker_guard, "tracking verifier no longer checks page disclosure marker")
require("disclosure must appear before the first affiliate CTA" in tracker_guard, "tracking verifier no longer checks disclosure placement")
require('data-site-affiliate-disclosure="global"' in tracker_guard, "tracking verifier no longer checks homepage disclosure")

require("CONSUMER_AFFILIATE_DISCLOSURE" in artifact_guard, "artifact guard no longer distinguishes consumer disclosure from internal ops")
for key in ("affiliate_status", "affiliate_verified", "affiliate_evidence_markers", "revenue_truth", "browser_required_queue"):
    require(key in artifact_guard, f"artifact guard no longer fails closed on internal key: {key}")

print("PASS: central public policy contract is aligned across source hygiene, final disclosure injection, tracking verification, and artifact leak guards")
