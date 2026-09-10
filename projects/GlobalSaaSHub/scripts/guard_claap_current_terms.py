from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAAP = ROOT / "public" / "tool" / "claap.html"
HUB = ROOT / "public" / "best" / "index.html"
PRIMARY = "https://get.claap.io/rc9nqme16a9q-gfvrqk"

claap = CLAAP.read_text(encoding="utf-8")
hub = HUB.read_text(encoding="utf-8")

# The current English first-party Claap affiliate page was rechecked on
# 2026-09-10. It confirms tracked affiliate referrals and affiliate commission,
# but no longer publishes the previously surfaced 30%-for-2-months / 10%-for-year
# buyer discount. Keep the vendor-issued tracking URL, remove only the unsupported
# customer-benefit claim, and never guess a new/deeper referral URL.

claap = claap.replace("Start Claap with partner discount →", "Start Claap with verified tracking →")
claap = claap.replace("Try Claap with referral discount →", "Try Claap with verified tracking →")

stale_offer = '<div class="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-sm text-slate-300 leading-relaxed"><strong class="text-emerald-300">Claap referral discount:</strong> Claap currently says referrals using an affiliate link get <strong class="text-white">30% off the first 2 months</strong> on a monthly plan or <strong class="text-white">10% off the first year</strong> on a yearly plan. Final eligibility and checkout terms are controlled by Claap.</div>'
claap = claap.replace("\n    " + stale_offer, "")
claap = claap.replace(stale_offer, "")

hub = hub.replace("Claap Pricing & Referral Discount Guide", "Claap Pricing & Verified Partner Guide")
hub = hub.replace("AI meetings · verified partner route + referral discount", "AI meetings · verified partner route")
hub = hub.replace("Claap Pricing & Referral Discount", "Claap Pricing & Verified Partner Route")
hub = hub.replace(
    "Compare Claap's free/trial entry and plan fit, then use COSHUMA's verified referral route if it suits your workflow. Claap's official affiliate terms currently state 30% off the first 2 months on monthly plans or 10% off the first year annually.",
    "Compare Claap's free/trial entry and plan fit, then continue through COSHUMA's vendor-verified customer tracking route if the workflow fits. Confirm final pricing and any buyer offer on Claap before purchase.",
)

if claap.count(PRIMARY) < 2:
    raise SystemExit("Claap exact vendor-issued tracking URL is not present on both revenue CTAs")
if 'data-cta="affiliate" data-tool-id="claap"' not in claap:
    raise SystemExit("Claap affiliate CTA marker is missing")
if 'href="https://www.claap.io/pricing"' not in claap:
    raise SystemExit("Claap independent official pricing-check link is missing")

stale_claims = (
    "Claap referral discount:",
    "30% off the first 2 months",
    "10% off the first year",
    "partner discount →",
    "referral discount →",
)
for stale in stale_claims:
    if stale in claap or stale in hub:
        raise SystemExit(f"Unsupported current Claap buyer-discount claim remains: {stale}")

if 'href="/tool/claap.html"' not in hub or "Claap Pricing & Verified Partner Route" not in hub:
    raise SystemExit("Claap high-intent buyer-hub route is missing after current-terms cleanup")

CLAAP.write_text(claap, encoding="utf-8")
HUB.write_text(hub, encoding="utf-8")
print("claap-current-affiliate-terms-guard-v1")
