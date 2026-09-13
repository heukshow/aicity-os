from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_OMNISEND_VERIFIED_OFFER -->"
TRACKING_URL = "https://your.omnisend.com/VOKyAj"
GUIDE_URL = "/tool/omnisend.html"
COMPARE_URL = "/compare/omnisend-vs-klaviyo-free-plan.html"
OFFICIAL_PRICING = "https://www.omnisend.com/pricing/"
OFFICIAL_PRICING_HELP = "https://support.omnisend.com/en/articles/3533018-omnisend-pricing-plans-2026"
OFFICIAL_AFFILIATE_TERMS = "https://www.omnisend.com/affiliates/"
BLOCKED_PUBLIC_TOKENS = (
    "app.impact.com",
    "impact.com/campaign-promo-signup",
    "impact.com/advertiser",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Omnisend's affiliate manager directly issued TRACKING_URL to COSHUMA as the
#   customer-facing route for Omnisend's pricing page. Preserve it exactly and do
#   not synthesize another deep link or copy tracking parameters onto arbitrary URLs.
# - current first-party pricing/help checked 2026-09-13: Free $0/month, up to 500
#   emails/month to 250 contacts, no card; Standard regular entry $16/month and Pro
#   regular entry $59/month. A current first-three-month starter discount is vendor-
#   controlled and checkout determines final eligibility/pricing.
# - current first-party affiliate page states 20% recurring commission for up to
#   24 months with a 60-day attribution window. These are program terms, not
#   evidence of COSHUMA earnings.
# - link publication or validation is not evidence of a signup, paid customer,
#   commission, payout or revenue.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Omnisend verified block exists but exact vendor-issued pricing tracker is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("Omnisend admin/onboarding URL leaked into the public buyer hub")
    print("Omnisend verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI and eProfessor. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI, eProfessor and Omnisend. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Omnisend patch")
html = html.replace(old_meta, new_meta, 1)

item35 = (
    '      {"@type":"ListItem","position":35,"name":"eProfessor",'
    '"url":"https://coshuma.com/tool/eprofessor.html"}\n'
    "    ]"
)
item36 = (
    '      {"@type":"ListItem","position":35,"name":"eProfessor",'
    '"url":"https://coshuma.com/tool/eprofessor.html"},\n'
    '      {"@type":"ListItem","position":36,"name":"Omnisend",'
    '"url":"https://coshuma.com/tool/omnisend.html"}\n'
    "    ]"
)
if item35 not in html:
    raise SystemExit("eProfessor ItemList tail missing; Omnisend patch requires the verified eProfessor build step first")
html = html.replace(item35, item36, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Omnisend patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-pink-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-pink-300">Email & SMS marketing</div><h2 class="mt-1 text-3xl font-black text-white">Omnisend</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free $0 · no card</span></div>\n        <p class="text-sm leading-7 text-slate-300">Omnisend's current Free plan is <strong class="text-white">$0/month</strong>, supports up to <strong class="text-white">500 emails/month</strong> for a maximum of <strong class="text-white">250 contacts</strong>, and does not require a credit card. Current regular entry pricing starts at <strong class="text-white">$16/month for Standard</strong> and <strong class="text-white">$59/month for Pro</strong>.</p>\n        <p class="text-sm leading-7 text-amber-100">Omnisend currently advertises a starter discount for eligible new paid subscribers who prepay three months. Because promotions and eligibility can change, COSHUMA does not hard-code a discounted checkout price here; verify the live vendor checkout before paying.</p>\n        <p class="text-sm leading-7 text-slate-300">COSHUMA uses the exact pricing-page tracking URL supplied directly by Omnisend's affiliate manager. The current affiliate page describes a <strong class="text-white">20% recurring commission</strong> for qualifying referred paying customers for up to 24 months and a 60-day attribution window. Those are program terms, not COSHUMA earnings.</p>\n        <div class="grid gap-3 sm:grid-cols-2">\n          <a data-cta="affiliate" data-tool-id="omnisend" data-cta-source="verified-deals-omnisend-pricing" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-pink-600 px-5 py-3.5 text-center font-black text-white hover:bg-pink-500">See Omnisend pricing via verified link →</a>\n          <a data-cta="official" href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/15 px-5 py-3.5 text-center font-bold text-slate-200 hover:bg-white/[0.05]">Verify live pricing →</a>\n        </div>\n        <div class="flex flex-wrap gap-x-5 gap-y-2 text-xs font-bold">\n          <a href="{GUIDE_URL}" class="text-violet-300 hover:text-violet-200">Read Omnisend buyer guide →</a>\n          <a href="{COMPARE_URL}" class="text-violet-300 hover:text-violet-200">Omnisend vs Klaviyo free plan →</a>\n          <a href="{OFFICIAL_PRICING_HELP}" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-white">Verify plan limits →</a>\n          <a href="{OFFICIAL_AFFILIATE_TERMS}" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-white">Verify affiliate terms →</a>\n        </div>\n        <p class="text-xs leading-5 text-slate-500">Affiliate disclosure: COSHUMA may earn a commission from an eligible paid subscription made through this vendor-issued tracking link. Publishing, opening or validating the link does not prove a signup, paid customer, commission, payout or revenue.</p>\n      </article>\n'''

html = html.replace(closing, card + "\n" + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    COMPARE_URL,
    'data-cta-source="verified-deals-omnisend-pricing"',
    "$0/month",
    "500 emails/month",
    "250 contacts",
    "$16/month for Standard",
    "$59/month for Pro",
    "20% recurring commission",
    "60-day attribution window",
    "does not prove a signup, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Omnisend buyer-hub patch lost required token: {token}")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("Omnisend admin/onboarding URL leaked after patch")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Omnisend pricing route")
