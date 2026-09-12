from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_AIASSISTWORKS_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.aiassistworks.com/?via=coshuma"
GUIDE_URL = "/best/aiassistworks-coupon-code.html"
OFFICIAL_PRICING = "https://www.aiassistworks.com/pricing"
OFFICIAL_AFFILIATE = "https://www.aiassistworks.com/affiliate-program"
BLOCKED_PUBLIC_TOKENS = (
    "aiassistworks.affonso.io",
    "affonso.io/login",
    "affonso.io/dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - authenticated Affonso evidence in approved-tracking-2026-09-08.json records
#   this exact customer-facing URL after the existing COSHUMA affiliate onboarding.
# - first-party homepage/pricing/affiliate pages were rechecked 2026-09-13.
# - the current 25OFF code is a public vendor promotion; it is not an account-specific
#   coupon and must not be presented as COSHUMA-exclusive.
# - no pricing or checkout affiliate deep link was issued, so keep the exact homepage
#   referral route rather than manufacturing ?via=coshuma on another path.
# - publication/link validation is never downstream revenue evidence.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("AiAssistWorks verified block exists but exact approved tracking URL is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("AiAssistWorks affiliate admin URL leaked into the public buyer hub")
    print("AiAssistWorks verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr and Novita AI. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI and AiAssistWorks. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind AiAssistWorks patch")
html = html.replace(old_meta, new_meta, 1)

item30 = (
    '      {"@type":"ListItem","position":30,"name":"Novita AI",'
    '"url":"https://coshuma.com/tool/novita-ai.html"}\n'
    "    ]"
)
item31 = (
    '      {"@type":"ListItem","position":30,"name":"Novita AI",'
    '"url":"https://coshuma.com/tool/novita-ai.html"},\n'
    '      {"@type":"ListItem","position":31,"name":"AiAssistWorks",'
    '"url":"https://coshuma.com/best/aiassistworks-coupon-code.html"}\n'
    "    ]"
)
if item30 not in html:
    raise SystemExit("Novita ItemList tail missing; AiAssistWorks patch requires the verified Novita build step first")
html = html.replace(item30, item31, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind AiAssistWorks patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-indigo-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-indigo-300">AI for Sheets, Docs & Slides</div><h2 class="mt-1 text-3xl font-black text-white">AiAssistWorks</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free forever · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">AiAssistWorks currently advertises a <strong class="text-white">Free Lite plan with no expiry and no credit card required</strong>. The Lite plan includes <strong class="text-white">100 execution credits per month</strong> and uses your own AI-provider API key, so it is a low-friction way to test real Google Sheets, Docs and Slides workflows before paying for the add-on.</p>\n        <p class="text-sm leading-6 text-slate-300">The vendor's pricing page currently shows public code <strong class="text-white">25OFF</strong> for <strong class="text-white">25% recurring off monthly and yearly Plus plans</strong>: Monthly is displayed as $6 → <strong class="text-white">$4.50/month</strong>, while Yearly is displayed as $4 → <strong class="text-white">$3.00/month</strong> equivalent. This is a public vendor promotion, not a COSHUMA-exclusive coupon; checkout controls final eligibility and terms.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses only the exact customer-facing Affonso referral URL already issued to its existing account. The current public affiliate page lists strong commission terms, but those terms are <strong class="text-white">not evidence of any COSHUMA signup, paid customer, commission or payout</strong>.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="aiassistworks" data-cta-source="verified-deals-aiassistworks-free" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-indigo-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-indigo-500">Try AiAssistWorks free →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Check 25OFF & pricing</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-indigo-200 hover:text-white">Verify current pricing →</a><a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-indigo-200 hover:text-white">Verify partner terms →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact customer-facing referral URL already issued to COSHUMA. COSHUMA does not copy the referral parameter onto a guessed pricing or checkout URL. Publication and link validation do not prove a click, signup, paid customer, commission, payout or revenue.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-aiassistworks-free"',
    "Free Lite plan with no expiry and no credit card required",
    "100 execution credits per month",
    "25OFF",
    "25% recurring off monthly and yearly Plus plans",
    "$4.50/month",
    "$3.00/month",
    "not evidence of any COSHUMA signup, paid customer, commission or payout",
    "do not prove a click, signup, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"AiAssistWorks buyer-hub patch lost required token: {token}")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("AiAssistWorks affiliate admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified AiAssistWorks free-plan route on buyer hub")
