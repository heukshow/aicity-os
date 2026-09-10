from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAAP = ROOT / "public" / "tool" / "claap.html"
HUB = ROOT / "public" / "best" / "index.html"
PRIMARY = "https://get.claap.io/rc9nqme16a9q-gfvrqk"

claap = CLAAP.read_text(encoding="utf-8")
hub = HUB.read_text(encoding="utf-8")

# The current English first-party Claap affiliate page was rechecked on
# 2026-09-11. The buyer-discount FAQ is visible again and explicitly states that
# referrals receive 30% off the first 2 months on monthly plans or 10% off the
# first year on yearly plans. Restore only that first-party buyer benefit beside
# COSHUMA's separately vendor-verified tracking URL. Never guess a deeper URL.

claap = claap.replace("Start Claap with verified tracking →", "Start Claap with partner discount →")
claap = claap.replace("Try Claap with verified tracking →", "Try Claap with referral discount →")

offer = '<div class="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-sm text-slate-300 leading-relaxed"><strong class="text-emerald-300">Claap referral discount:</strong> Claap currently says referrals using an affiliate link get <strong class="text-white">30% off the first 2 months</strong> on a monthly plan or <strong class="text-white">10% off the first year</strong> on a yearly plan. Final eligibility and checkout terms are controlled by Claap.</div>'
if offer not in claap:
    status_marker = '    <p class="text-[11px] text-slate-500 leading-relaxed">Affiliate status: verified.'
    if status_marker not in claap:
        raise SystemExit("Claap verified affiliate-status marker missing; refusing uncertain discount insertion")
    claap = claap.replace(status_marker, "    " + offer + "\n" + status_marker, 1)

hub = hub.replace("Claap Pricing & Verified Partner Guide", "Claap Pricing & Referral Discount Guide")
hub = hub.replace("AI meetings · verified partner route", "AI meetings · verified partner route + referral discount")
hub = hub.replace("Claap Pricing & Verified Partner Route", "Claap Pricing & Referral Discount")
hub = hub.replace(
    "Compare Claap's free/trial entry and plan fit, then continue through COSHUMA's vendor-verified customer tracking route if the workflow fits. Confirm final pricing and any buyer offer on Claap before purchase.",
    "Compare Claap's free/trial entry and plan fit, then use COSHUMA's verified referral route if it suits your workflow. Claap's official affiliate terms currently state 30% off the first 2 months on monthly plans or 10% off the first year annually.",
)

if claap.count(PRIMARY) < 2:
    raise SystemExit("Claap exact vendor-issued tracking URL is not present on both revenue CTAs")
if 'data-cta="affiliate" data-tool-id="claap"' not in claap:
    raise SystemExit("Claap affiliate CTA marker is missing")
if 'href="https://www.claap.io/pricing"' not in claap:
    raise SystemExit("Claap independent official pricing-check link is missing")

required_claims = (
    "Claap referral discount:",
    "30% off the first 2 months",
    "10% off the first year",
    "partner discount →",
    "referral discount →",
)
for required in required_claims:
    if required not in claap:
        raise SystemExit(f"Current Claap buyer-discount claim missing from tool page: {required}")

hub_required = (
    "Claap Pricing & Referral Discount Guide",
    "AI meetings · verified partner route + referral discount",
    "Claap Pricing & Referral Discount",
    "30% off the first 2 months",
    "10% off the first year",
)
for required in hub_required:
    if required not in hub:
        raise SystemExit(f"Current Claap buyer-discount claim missing from buyer hub: {required}")

if 'href="/tool/claap.html"' not in hub:
    raise SystemExit("Claap high-intent buyer-hub route is missing after current-terms restore")

CLAAP.write_text(claap, encoding="utf-8")
HUB.write_text(hub, encoding="utf-8")
print("claap-current-affiliate-terms-guard-v2")
