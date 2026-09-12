from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_FIREFLIES_VERIFIED_OFFER -->"
TRACKING_URL = "https://fireflies.ai/?fpr=sangkwon53"
GUIDE_URL = "/best/fireflies-ai-free-plan.html"
OFFICIAL_PRICING = "https://fireflies.ai/pricing"
OFFICIAL_AFFILIATE = "https://fireflies.ai/affiliate"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - COSHUMA's existing Fireflies buyer guide records that Fireflies Partnerships
#   reconfirmed the exact customer-facing referral URL above to support@coshuma.com.
# - Fireflies' first-party pricing rechecked 2026-09-13 lists a $0 Free plan and
#   labels it free forever, with unlimited transcription subject to usage rules,
#   limited AI summaries, 400 minutes of storage/team and 20 AI credits.
# - Fireflies' current first-party affiliate page states purchases within the
#   90-day referral window can earn up to 30% recurring commission per successful
#   sale for 12 months. Those are program terms, not proof of COSHUMA revenue.
# - This script preserves the issued root referral URL instead of manufacturing a
#   pricing/signup deep link by moving the referral parameter onto another path.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Fireflies verified block exists but exact approved tracking URL is missing")
    print("Fireflies verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk and Krater. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater and Fireflies.ai. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Fireflies patch")
html = html.replace(old_meta, new_meta, 1)

item21 = (
    '      {"@type":"ListItem","position":21,"name":"Krater",'
    '"url":"https://coshuma.com/best/krater-ai-pricing.html"}\n'
    "    ]"
)
item22 = (
    '      {"@type":"ListItem","position":21,"name":"Krater",'
    '"url":"https://coshuma.com/best/krater-ai-pricing.html"},\n'
    '      {"@type":"ListItem","position":22,"name":"Fireflies.ai",'
    '"url":"https://coshuma.com/best/fireflies-ai-free-plan.html"}\n'
    "    ]"
)
if item21 not in html:
    raise SystemExit("Krater ItemList tail missing; Fireflies patch requires the verified Krater build step first")
html = html.replace(item21, item22, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Fireflies patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-orange-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-orange-300">AI meeting notes</div><h2 class="mt-1 text-3xl font-black text-white">Fireflies.ai</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">$0 · free forever</span></div>\n        <p class="text-sm leading-6 text-slate-300">Fireflies currently lists a <strong class="text-white">$0 Free plan</strong> and labels it <strong class="text-white">free forever</strong>. The plan includes unlimited transcription subject to Fireflies usage rules, limited AI summaries, 400 minutes of storage per team and 20 AI credits, so a buyer can test real meetings before paying.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact customer-facing referral URL that Fireflies Partnerships reconfirmed for the existing account. Fireflies' current affiliate terms describe a <strong class="text-white">90-day referral window</strong> and up to <strong class="text-white">30% recurring commission for 12 months</strong> on successful purchases. Those are partner terms, not proof COSHUMA has earned revenue.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="fireflies-ai" data-cta-source="verified-deals-fireflies-free" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-orange-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-orange-500">Start Fireflies Free →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Fireflies plans</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-orange-200 hover:text-white">Verify Fireflies pricing →</a><a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-orange-200 hover:text-white">Verify Fireflies partner terms →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves only the exact Fireflies customer-facing referral URL already verified for COSHUMA. COSHUMA does not move the referral parameter onto a guessed pricing or signup deep link. A click, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-fireflies-free"',
    "$0 Free plan",
    "free forever",
    "90-day referral window",
    "30% recurring commission for 12 months",
    "not proof COSHUMA has earned revenue",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Fireflies buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Fireflies free-plan route on buyer hub")
