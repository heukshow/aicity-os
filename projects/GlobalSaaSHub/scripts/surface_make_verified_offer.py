from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_MAKE_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.make.com/?pc=coshuma"
GUIDE_URL = "/tool/make-com.html"
OFFICIAL_PRICING = "https://www.make.com/en/pricing"
OFFICIAL_AFFILIATE = "https://www.make.com/en/affiliate"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - tools.json and the existing Make buyer guide record the exact COSHUMA partner
#   route above as approved_tracking. Do not manufacture a pricing/signup deep link.
# - Make's first-party pricing page rechecked 2026-09-13 states the Free plan is
#   $0, has no time limit, and includes up to 1,000 credits/month.
# - Make's first-party affiliate page rechecked 2026-09-13 states affiliates earn
#   35% commission on referred subscription payments for 12 months.
# - Those are program terms, not evidence of COSHUMA clicks, signups or revenue.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Make verified block exists but exact approved tracking URL is missing")
    print("Make verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater and Fireflies.ai. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai and Make.com. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Make patch")
html = html.replace(old_meta, new_meta, 1)

item22 = (
    '      {"@type":"ListItem","position":22,"name":"Fireflies.ai",'
    '"url":"https://coshuma.com/best/fireflies-ai-free-plan.html"}\n'
    "    ]"
)
item23 = (
    '      {"@type":"ListItem","position":22,"name":"Fireflies.ai",'
    '"url":"https://coshuma.com/best/fireflies-ai-free-plan.html"},\n'
    '      {"@type":"ListItem","position":23,"name":"Make.com",'
    '"url":"https://coshuma.com/tool/make-com.html"}\n'
    "    ]"
)
if item22 not in html:
    raise SystemExit("Fireflies ItemList tail missing; Make patch requires the verified Fireflies build step first")
html = html.replace(item22, item23, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Make patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-purple-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-purple-300">Workflow automation</div><h2 class="mt-1 text-3xl font-black text-white">Make.com</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">$0 · no time limit</span></div>\n        <p class="text-sm leading-6 text-slate-300">Make currently lists a <strong class="text-white">$0 Free plan with no time limit</strong> and up to <strong class="text-white">1,000 credits per month</strong>. That is enough to validate a real visual automation before paying for faster schedules, higher usage or team features.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact Make partner route already recorded as approved tracking for this account. Make's current affiliate page states <strong class="text-white">35% commission for 12 months</strong> on referred subscription payments. Those are partner terms, not proof COSHUMA has earned revenue.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="make-com" data-cta-source="verified-deals-make-free" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-purple-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-purple-500">Start Make Free →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Make plans</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-purple-200 hover:text-white">Verify Make pricing →</a><a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-purple-200 hover:text-white">Verify Make partner terms →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact Make customer-facing partner URL already verified for COSHUMA. COSHUMA does not move the partner code onto a guessed pricing or signup deep link. A click, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-make-free"',
    "$0 Free plan with no time limit",
    "1,000 credits per month",
    "35% commission for 12 months",
    "not proof COSHUMA has earned revenue",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Make buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Make free-plan route on buyer hub")
