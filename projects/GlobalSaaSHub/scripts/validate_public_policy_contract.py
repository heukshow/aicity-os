"""Fail closed when COSHUMA's public affiliate policy drifts across build stages."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config" / "public_content_policy.json").read_text(encoding="utf-8"))
PACKAGE = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
PREBUILD = PACKAGE["scripts"].get("prebuild", "")
BUILD = PACKAGE["scripts"]["build"]
PUBLIC = ROOT / "public"
PUBLIC_TEXT_EXTENSIONS = {".html", ".txt", ".xml", ".json", ".js", ".webmanifest"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Public policy contract violation: {message}")


stages = POLICY["stages"]
disclosure = POLICY["affiliate_disclosure"]
source = stages["source"]
final_dist = stages["final_dist"]

require(POLICY.get("policy_owner") == "config/public_content_policy.json", "central policy owner changed")
require(source.get("page_disclosures_required_for_affiliate_cta") is True, "source affiliate pages must require disclosure")
require(source.get("homepage_disclosure_required") is True, "source homepage disclosure must remain required")
require(source.get("fail_closed_on_internal_ops_leak") is True, "source internal-info guard must fail closed")
require(final_dist.get("page_disclosures_required_for_affiliate_cta") is True, "final affiliate pages must require disclosure")
require(final_dist.get("homepage_disclosure_required") is True, "final homepage disclosure must remain required")
require(final_dist.get("fail_closed_on_internal_ops_leak") is True, "final internal-info guard must fail closed")

raw_prebuild_at = PREBUILD.find("guard_raw_public_source.py")
policy_prebuild_at = PREBUILD.find("validate_public_policy_contract.py")
require(raw_prebuild_at >= 0, "raw public source guard missing from prebuild")
require(policy_prebuild_at >= 0, "public policy validator missing from prebuild")
require(raw_prebuild_at < policy_prebuild_at, "raw public source guard must run before policy validation and build sanitizers")

raw_build_at = BUILD.find("guard_raw_public_source.py")
customer_sanitizer_at = BUILD.find("guard_customer_only_copy.py")
require(raw_build_at >= 0, "generated public-source guard missing from build")
require(customer_sanitizer_at >= 0, "customer-copy sanitizer missing from build")
require(raw_build_at < customer_sanitizer_at, "generated public source must fail closed before broad customer-copy sanitization")

require("enforce_home_only_affiliate_disclosure.py" not in BUILD, "deprecated home-only final-bundle cleaner is active")

vite_at = BUILD.find("vite build")
source_normalizer_at = BUILD.find("self_heal_source_affiliate_disclosures.py")
source_boundary_at = BUILD.find("guard_public_source_boundary.py")
final_guard_at = BUILD.find("guard_built_customer_copy.py")
artifact_guard_at = BUILD.find("guard_public_artifact_boundary.py dist")
require(vite_at >= 0, "vite build missing")
require(source_normalizer_at >= 0 and source_normalizer_at < source_boundary_at, "source disclosure normalizer must run before source boundary validation")
require(source_boundary_at > source_normalizer_at and source_boundary_at < vite_at, "source disclosure boundary must run after source normalization and before Vite")
require(final_guard_at > vite_at, "canonical final disclosure guard must run after Vite")
require(artifact_guard_at > final_guard_at, "final artifact boundary guard must run after disclosure normalization")

source_normalizer = (ROOT / "scripts" / "self_heal_source_affiliate_disclosures.py").read_text(encoding="utf-8")
source_guard = (ROOT / "scripts" / "guard_public_source_boundary.py").read_text(encoding="utf-8")
built_guard = (ROOT / "scripts" / "guard_built_customer_copy.py").read_text(encoding="utf-8")
tracker_guard = (ROOT / "scripts" / "verify_approved_tracking.mjs").read_text(encoding="utf-8")
artifact_guard = (ROOT / "scripts" / "guard_public_artifact_boundary.py").read_text(encoding="utf-8")
raw_guard = (ROOT / "scripts" / "guard_raw_public_source.py").read_text(encoding="utf-8")
public_copy_guard = (ROOT / "scripts" / "guard_public_copy.py").read_text(encoding="utf-8")
buyer_box_generator = (ROOT / "scripts" / "inject_buyer_decision_boxes.mjs").read_text(encoding="utf-8")
source_boundary_guard = source_guard

require("strip_general_notice" not in source_normalizer, "legacy page-disclosure removal logic is still active")
require(
    "Consumer-facing affiliate disclosures are required public content" in public_copy_guard,
    "public copy guard no longer preserves marked consumer affiliate disclosures",
)
require(
    "re.sub(r'<p\\b[^>]*data-affiliate-disclosure" not in public_copy_guard,
    "public copy guard still directly strips marked page affiliate disclosures",
)
page_normalizer_uses_policy = (
    ("PAGE_DISCLOSURE" in source_normalizer and 'DISCLOSURE["page_text"]' in source_normalizer)
    or ("PAGE_NOTICE" in source_normalizer and 'DISC["page_text"]' in source_normalizer)
)
home_normalizer_uses_policy = (
    ("HOME_DISCLOSURE" in source_normalizer and 'DISCLOSURE["homepage_text"]' in source_normalizer)
    or ("HOME_NOTICE" in source_normalizer and 'DISC["homepage_text"]' in source_normalizer)
)
require(page_normalizer_uses_policy, "source normalizer no longer preserves canonical page disclosure")
require(home_normalizer_uses_policy, "source normalizer no longer preserves homepage disclosure")
require('data-affiliate-disclosure="page"' in source_guard, "source boundary no longer checks page disclosure marker")
require("consumer disclosure must appear before the first affiliate CTA" in source_guard, "source boundary no longer checks disclosure placement")
require('data-site-affiliate-disclosure="global"' in source_guard, "source boundary no longer checks homepage disclosure")

require(disclosure["homepage_text"] in built_guard, "built guard homepage disclosure differs from central policy")
require(disclosure["page_text"] in built_guard, "built guard page disclosure differs from central policy")
require(disclosure["homepage_marker"] in built_guard, "built guard homepage marker differs from central policy")
require(disclosure["page_marker"] in built_guard, "built guard page marker differs from central policy")
require("PAGE_AFFILIATE_CTA" in built_guard and "count=1" in built_guard, "built guard no longer inserts once before first affiliate CTA")

require(disclosure["page_marker"] in source_boundary_guard, "source boundary no longer checks page disclosure marker")
require("consumer disclosure must appear before the first affiliate CTA" in source_boundary_guard, "source boundary no longer checks disclosure placement")
require(disclosure["homepage_marker"] in source_boundary_guard, "source boundary no longer checks homepage disclosure")
require('data-affiliate-disclosure="page"' in tracker_guard, "tracking verifier no longer checks page disclosure marker")
require("disclosure must appear before the first affiliate CTA" in tracker_guard, "tracking verifier no longer checks disclosure placement")
require('data-site-affiliate-disclosure="global"' in tracker_guard, "tracking verifier no longer checks homepage disclosure")

require("CONSUMER_AFFILIATE_DISCLOSURE" in artifact_guard, "artifact guard no longer distinguishes consumer disclosure from internal ops")
for key in ("affiliate_status", "affiliate_verified", "affiliate_evidence_markers", "revenue_truth", "browser_required_queue"):
    require(key in artifact_guard, f"artifact guard no longer fails closed on internal key: {key}")

for network in ("PartnerStack", "FirstPromoter", "Impact", "Dub", "Cello", "Tolt", "Awin", "CJ"):
    require(network in raw_guard, f"raw source guard no longer covers central network label: {network}")
    require(network in artifact_guard, f"artifact guard no longer covers central network label: {network}")
require("URL_RE.sub" in raw_guard, "raw source guard no longer masks tracking URLs before scanning")

# Public HTML generators must consume the explicit customer-only projection rather than
# reading raw private affiliate state. This catches architectural recurrence even when
# downstream leak scanners happen to sanitize the final bytes successfully.
require("build_public_tools.mjs" in buyer_box_generator, "buyer-box generator no longer refreshes the customer-only projection")
require("public-tools.json" in buyer_box_generator, "buyer-box generator no longer consumes the customer-only projection")
for forbidden in ("data/tools.json", "affiliate_status", "affiliate_verified", "affiliate_url", "official_evidence_url"):
    require(forbidden not in buyer_box_generator, f"buyer-box public generator reads private field/path: {forbidden}")
require("is_sponsored" in buyer_box_generator, "buyer-box generator no longer uses customer-safe sponsorship state")
require("outbound_url" in buyer_box_generator, "buyer-box generator no longer uses customer-safe outbound URL")

# Producer contract: retain the existing status guard and add a separate narrow
# provenance guard so private operational evidence can stay internal while customer-page
# producers cannot reintroduce who supplied or verified a tracking route.
PUBLIC_COPY_PRODUCERS = (
    ROOT / "scripts" / "generate_seo_pages.py",
    ROOT / "scripts" / "finalize_omnisend_tracking.py",
)
producer_forbidden = re.compile(
    r"not\\s+yet\\s+editorially\\s+rated|editorial\\s+review\\s+in\\s+progress|"
    r"review\\s+pending|affiliate\\s+approved|pending\\s+verification|"
    r"(?:affiliate|partner|referral)[-\\s]+(?:status|facts|terms)",
    re.I,
)
producer_provenance_forbidden = re.compile(
    r"(?:senior\s+)?affiliate\s+marketing\s+manager[^.\n<>]{0,180}(?:supplied|provided)|"
    r"approval\s+email[^.\n<>]{0,220}(?:tracking|referral|affiliate)|"
    r"Impact\s+Assets",
    re.I,
)
producer_errors = []
for path in PUBLIC_COPY_PRODUCERS:
    text = path.read_text(encoding="utf-8")
    match = producer_forbidden.search(text)
    if match:
        producer_errors.append(f"{path.relative_to(ROOT).as_posix()}: {match.group(0)}")
    provenance_match = producer_provenance_forbidden.search(text)
    if provenance_match:
        producer_errors.append(f"{path.relative_to(ROOT).as_posix()}: provenance: {provenance_match.group(0)}")
if producer_errors:
    raise SystemExit(
        "Public policy contract violation: a customer-page producer contains internal status/provenance copy:\n"
        + "\n".join(producer_errors)
    )

raw_status_patterns = {
    "affiliate-revenue-state-copy": re.compile(r"\baffiliate/revenue\s+link\b", re.I),
    "application-verification-copy": re.compile(
        r"\b(?:affiliate|partner|referral|creator)\b[^.\n<>]{0,120}"
        r"\b(?:application|enrollment|link|tracking|program)\b[^.\n<>]{0,120}"
        r"\b(?:being\s+verified|verification\s+pending|pending\s+verification|under\s+review)\b",
        re.I,
    ),
}
raw_errors = []
for path in PUBLIC.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in PUBLIC_TEXT_EXTENSIONS:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for label, pattern in raw_status_patterns.items():
        match = pattern.search(text)
        if match:
            raw_errors.append(f"{path.relative_to(ROOT).as_posix()}: {label}: {match.group(0)}")
if raw_errors:
    raise SystemExit(
        "Public policy contract violation: raw customer source contains internal application/verification state:\n"
        + "\n".join(raw_errors[:50])
    )

print("PASS: central public policy is aligned across source disclosures, internal-data boundaries, final disclosures, tracking verification, and artifact leak guards")
