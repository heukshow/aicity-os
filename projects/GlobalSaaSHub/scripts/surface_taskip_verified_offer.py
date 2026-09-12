from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TASKIP_VERIFIED_OFFER -->"
TRACKING_URL = "https://taskip.net/?atp=qnV3mw"
GUIDE_URL = "/tool/taskip.html"
OFFICIAL_PRICING = "https://www.taskip.net/price-plan/"
OFFICIAL_AFFILIATE = "https://www.taskip.net/affiliates/"
BLOCKED_PUBLIC_TOKENS = (
    "affiliate.taskip.net",
    "taskip.net/affiliate/login",
    "taskip.net/dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - authenticated affiliate evidence records this exact customer-facing Taskip URL.
# - Taskip first-party pricing and affiliate pages were rechecked 2026-09-13.
# - no tracked pricing/trial deep link has been issued, so preserve the exact homepage
#   affiliate URL instead of manufacturing an atp parameter on another path.
# - public affiliate terms are not evidence of COSHUMA revenue.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Taskip verified block exists but exact approved tracking URL is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("Taskip affiliate admin URL leaked into the public buyer hub")
    print("Taskip verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI and AiAssistWorks. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks and Taskip. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Taskip patch")
html = html.replace(old_meta, new_meta, 1)

item31 = (
    '      {"@type":"ListItem","position":31,"name":"AiAssistWorks",'
    '"url":"https://coshuma.com/best/aiassistworks-coupon-code.html"}\n'
    "    ]"
)
item32 = (
    '      {"@type":"ListItem","position":31,"name":"AiAssistWorks",'
    '"url":"https://coshuma.com/best/aiassistworks-coupon-code.html"},\n'
    '      {"@type":"ListItem","position":32,"name":"Taskip",'
    '"url":"https://coshuma.com/tool/taskip.html"}\n'
    "    ]"
)
if item31 not in html:
    raise SystemExit("AiAssistWorks ItemList tail missing; Taskip patch requires the verified AiAssistWorks build step first")
html = html.replace(item31, item32, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Taskip patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-cyan-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-cyan-300">AI-first client portal for agencies</div><h2 class="mt-1 text-3xl font-black text-white">Taskip</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">7-day premium trial · no card to sign up</span></div>\n        <p class="text-sm leading-6 text-slate-300">Taskip's current first-party pricing page says its premium trial provides <strong class="text-white">7 days of full access</strong>, and its signup FAQ says <strong class="text-white">no credit card is needed to start</strong>. The current monthly pricing view starts the Freelancer plan at <strong class="text-white">$12/month</strong>.</p>\n        <p class="text-sm leading-6 text-slate-300">Taskip combines a client portal with CRM, projects, invoicing, e-signatures, support and automation for agencies. COSHUMA uses only the exact customer-facing affiliate URL previously issued by the authenticated Taskip partner account.</p>\n        <p class="text-sm leading-6 text-slate-300">Taskip's current public affiliate page advertises <strong class="text-white">30% commission on the initial purchase</strong> of referred customers. That is a program term, not evidence that COSHUMA has produced a signup, paid customer, commission or payout.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="taskip" data-cta-source="verified-deals-taskip-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-cyan-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-cyan-500">Explore Taskip via COSHUMA →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Review Taskip</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify current pricing & trial →</a><a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify affiliate terms →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact Taskip customer URL issued to COSHUMA. COSHUMA does not copy the affiliate parameter onto a guessed pricing, trial or checkout deep link. Publication and link validation do not prove a click, signup, paid customer, commission, payout or revenue.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-taskip-trial"',
    "7 days of full access",
    "no credit card is needed to start",
    "$12/month",
    "30% commission on the initial purchase",
    "does not copy the affiliate parameter onto a guessed pricing, trial or checkout deep link",
    "do not prove a click, signup, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Taskip buyer-hub patch lost required token: {token}")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("Taskip affiliate admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Taskip trial route on buyer hub")
