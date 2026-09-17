from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_ELEVENLABS_VERIFIED_OFFER -->"
TRACKING_URL = "https://try.elevenlabs.io/ldc2xmh2x2t5"
GUIDE_URL = "/tool/elevenlabs.html"
OFFICIAL_PRICING = "https://elevenlabs.io/pricing"
OFFICIAL_AFFILIATE = "https://elevenlabs.io/affiliates"
BLOCKED_PUBLIC_TOKENS = (
    "dash.partnerstack.com",
    "elevenlabs.partnerstack.com",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - data/tools.json already records ElevenLabs as approved_tracking with the exact
#   customer-facing default affiliate link in TRACKING_URL.
# - first-party pricing checked 2026-09-13 shows Free $0 / 10k credits monthly,
#   Starter $6 / 30k credits, Creator $22 / 121k credits and Pro $99 / 600k credits.
# - the official affiliate page checked 2026-09-13 states up to 22% on qualifying
#   subscriptions and 22% of payments for the first 12 months for new paid subscribers.
# - those public program terms are not evidence of COSHUMA clicks, customers or revenue.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("ElevenLabs verified block exists but exact issued affiliate URL is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("ElevenLabs PartnerStack/admin URL leaked into the public buyer hub")
    print("ElevenLabs verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI, eProfessor, Omnisend and CartStack. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI, eProfessor, Omnisend, CartStack and ElevenLabs. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind ElevenLabs patch")
html = html.replace(old_meta, new_meta, 1)

item37 = (
    '      {"@type":"ListItem","position":37,"name":"CartStack",'
    '"url":"https://coshuma.com/tool/cartstack.html"}\n'
    "    ]"
)
item38 = (
    '      {"@type":"ListItem","position":37,"name":"CartStack",'
    '"url":"https://coshuma.com/tool/cartstack.html"},\n'
    '      {"@type":"ListItem","position":38,"name":"ElevenLabs",'
    '"url":"https://coshuma.com/tool/elevenlabs.html"}\n'
    "    ]"
)
if item37 not in html:
    raise SystemExit("CartStack ItemList tail missing; ElevenLabs patch requires the verified CartStack build step first")
html = html.replace(item37, item38, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind ElevenLabs patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-fuchsia-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-fuchsia-300">Voice & speech AI</div><h2 class="mt-1 text-3xl font-black text-white">ElevenLabs</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free $0 · 10k credits/mo</span></div>\n        <p class="text-sm leading-7 text-slate-300">ElevenLabs' current pricing page lists a <strong class="text-white">$0 Free plan with 10,000 credits per month</strong>. Paid entry points currently include Starter at <strong class="text-white">$6/month</strong>, Creator at <strong class="text-white">$22/month</strong>, and Pro at <strong class="text-white">$99/month</strong>. Check the live pricing page before upgrading because promotions and plan details can change.</p>\n        <p class="text-sm leading-7 text-slate-300">The current public affiliate program advertises <strong class="text-white">up to 22% commission on qualifying subscriptions</strong> and states 22% of payments for the first 12 months for new paid subscriber plans. These are program terms, not COSHUMA earnings.</p>\n        <p class="text-sm leading-7 text-slate-300">COSHUMA uses only the exact customer-facing ElevenLabs affiliate URL already recorded as <strong class="text-white">approved_tracking</strong>. PartnerStack dashboard/login URLs and guessed pricing deep links are not used as buyer CTAs.</p>\n        <div class="grid gap-3 sm:grid-cols-2">\n          <a data-cta="affiliate" data-tool-id="elevenlabs" data-cta-source="verified-deals-elevenlabs-free" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-fuchsia-600 px-5 py-3.5 text-center font-black text-white hover:bg-fuchsia-500">Try ElevenLabs via verified partner link →</a>\n          <a data-cta="official" href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/15 px-5 py-3.5 text-center font-bold text-slate-200 hover:bg-white/[0.05]">Verify live pricing →</a>\n        </div>\n        <div class="flex flex-wrap gap-x-5 gap-y-2 text-xs font-bold">\n          <a href="{GUIDE_URL}" class="text-violet-300 hover:text-violet-200">Read ElevenLabs buyer guide →</a>\n          <a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="text-violet-300 hover:text-violet-200">Verify affiliate terms →</a>\n        </div>\n      </article>\n'''

html = html.replace(closing, card + "\n" + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    OFFICIAL_PRICING,
    'data-cta-source="verified-deals-elevenlabs-free"',
    "10,000 credits per month",
    "$6/month",
    "$22/month",
    "$99/month",
    "up to 22% commission",
    "first 12 months",
    "does not prove a click, signup, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"ElevenLabs buyer-hub patch lost required token: {token}")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("ElevenLabs PartnerStack/admin URL leaked after patch")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified ElevenLabs buyer route")
