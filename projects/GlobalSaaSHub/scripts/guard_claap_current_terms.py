from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAAP = ROOT / "public" / "tool" / "claap.html"
HUB = ROOT / "public" / "best" / "index.html"
PRIMARY = "https://get.claap.io/rc9nqme16a9q-gfvrqk"

claap = CLAAP.read_text(encoding="utf-8")
hub = HUB.read_text(encoding="utf-8")

# Directly opened on 2026-09-11, Claap's current English first-party affiliate
# page confirms tracked referrals, 30% affiliate commission, and commissions paid
# for renewals up to 12 months, but it does not currently publish the previously
# surfaced 30%-for-2-months / 10%-for-year buyer discount. Prefer the direct live
# first-party page over stale/conflicting search-index snippets. Keep COSHUMA's
# vendor-issued tracking URL and remove only unsupported customer-benefit claims.
# Public copy must describe the buyer action, not COSHUMA's internal affiliate
# verification, manager correspondence, tracking status, or revenue workflow.

claap = claap.replace("Start Claap with partner discount →", "Start Claap →")
claap = claap.replace("Try Claap with referral discount →", "Try Claap →")
claap = claap.replace("Start Claap with verified tracking →", "Start Claap →")
claap = claap.replace("Try Claap with verified tracking →", "Try Claap →")
claap = claap.replace(
    "Partner feedback + official pricing checked Sep 15, 2026",
    "Product and pricing checked Sep 15, 2026",
)

internal_status = (
    '<p class="text-[11px] text-slate-500 leading-relaxed">Affiliate status: verified. '
    "Claap affiliate manager Lamia Karmaly supplied COSHUMA's exact customer-facing PartnerStack URLs directly by email on Sep 9, 2026. "
    'The primary Try Claap buttons use the first issued tracking URL; the pricing button remains the official live pricing page until the intended destination of the second issued URL is clarified. '
    'Link issuance does not imply a signup, commission, or sale.</p>'
)
claap = claap.replace("\n    " + internal_status, "")
claap = claap.replace(internal_status, "")

claap = claap.replace(
    '<p class="text-[11px] text-slate-500 leading-relaxed"><strong class="text-slate-300">Affiliate disclosure:</strong> COSHUMA may earn a commission if you purchase through a verified Claap affiliate link, at no extra cost to you. This does not affect our editorial assessment.</p>',
    '<p class="text-[11px] text-slate-500 leading-relaxed"><strong class="text-slate-300">Affiliate disclosure:</strong> COSHUMA may earn a commission from eligible purchases through links on this page, at no extra cost to you. This does not affect our editorial assessment.</p>',
)
claap = claap.replace(
    '<div class="p-4 rounded-xl bg-[#0b0c10] border border-[#222538] text-xs text-slate-400 leading-relaxed"><strong class="text-slate-200">Editorial note:</strong> this review uses Claap\'s current official product/security pages plus direct feedback from Claap affiliate manager Lamia Karmaly. COSHUMA does not claim hands-on testing where none was performed. Final plan limits and pricing are controlled by Claap.</div>',
    '<div class="p-4 rounded-xl bg-[#0b0c10] border border-[#222538] text-xs text-slate-400 leading-relaxed"><strong class="text-slate-200">Editorial note:</strong> this review uses Claap\'s current official product, pricing and security information. COSHUMA does not claim hands-on testing where none was performed. Final plan limits and pricing are controlled by Claap.</div>',
)

stale_offer = '<div class="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-sm text-slate-300 leading-relaxed"><strong class="text-emerald-300">Claap referral discount:</strong> Claap currently says referrals using an affiliate link get <strong class="text-white">30% off the first 2 months</strong> on a monthly plan or <strong class="text-white">10% off the first year</strong> on a yearly plan. Final eligibility and checkout terms are controlled by Claap.</div>'
claap = claap.replace("\n    " + stale_offer, "")
claap = claap.replace(stale_offer, "")

hub = hub.replace("Claap Pricing & Referral Discount Guide", "Claap Pricing & Buyer Guide")
hub = hub.replace("Claap Pricing & Verified Partner Guide", "Claap Pricing & Buyer Guide")
hub = hub.replace("AI meetings · verified partner route + referral discount", "AI meetings · pricing and plan guide")
hub = hub.replace("AI meetings · verified partner route", "AI meetings · pricing and plan guide")
hub = hub.replace("Claap Pricing & Referral Discount", "Claap Pricing & Buyer Guide")
hub = hub.replace("Claap Pricing & Verified Partner Route", "Claap Pricing & Buyer Guide")
hub = hub.replace(
    "Compare Claap's free/trial entry and plan fit, then use COSHUMA's verified referral route if it suits your workflow. Claap's official affiliate terms currently state 30% off the first 2 months on monthly plans or 10% off the first year annually.",
    "Compare Claap's free entry, current pricing and plan fit before choosing whether to upgrade.",
)
hub = hub.replace(
    "Compare Claap's free/trial entry and plan fit, then continue through COSHUMA's vendor-verified customer tracking route if the workflow fits. Confirm final pricing and any buyer offer on Claap before purchase.",
    "Compare Claap's free entry, current pricing and plan fit before choosing whether to upgrade. Confirm final pricing on Claap before purchase.",
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
    "with verified tracking →",
    "Affiliate status: verified.",
    "Claap affiliate manager Lamia Karmaly",
    "customer-facing PartnerStack URLs",
    "verified partner route",
    "Verified Partner Route",
)
for stale in stale_claims:
    if stale in claap or stale in hub:
        raise SystemExit(f"Unsupported or internal Claap public copy remains: {stale}")

if 'href="/tool/claap.html"' not in hub or "Claap Pricing & Buyer Guide" not in hub:
    raise SystemExit("Claap high-intent buyer-hub route is missing after current-terms cleanup")

CLAAP.write_text(claap, encoding="utf-8")
HUB.write_text(hub, encoding="utf-8")
print("claap-current-affiliate-terms-guard-v4")
