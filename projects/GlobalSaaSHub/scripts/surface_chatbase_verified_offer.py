from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_CHATBASE_VERIFIED_OFFER -->"
TRACKING_URL = "https://link.chatbase.co/sang-kwon-an"
GUIDE_URL = "/tool/chatbase.html"
OFFICIAL_URL = "https://www.chatbase.co/pricing"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Chatbase support directly supplied this exact customer-facing referral route
#   after reviewing the COSHUMA partner account.
# - Chatbase first-party pricing was rechecked 2026-09-13 for the facts below.
# - publication/link validation is never downstream revenue evidence.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Chatbase verified block exists but exact approved tracking URL is missing")
    print("Chatbase verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe and Catalister. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister and Chatbase. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Chatbase patch")
html = html.replace(old_meta, new_meta, 1)

item25 = (
    '      {"@type":"ListItem","position":25,"name":"Catalister",'
    '"url":"https://coshuma.com/tool/catalister.html"}\n'
    "    ]"
)
item26 = (
    '      {"@type":"ListItem","position":25,"name":"Catalister",'
    '"url":"https://coshuma.com/tool/catalister.html"},\n'
    '      {"@type":"ListItem","position":26,"name":"Chatbase",'
    '"url":"https://coshuma.com/tool/chatbase.html"}\n'
    "    ]"
)
if item25 not in html:
    raise SystemExit("Catalister ItemList tail missing; Chatbase patch requires the verified Catalister build step first")
html = html.replace(item25, item26, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Chatbase patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-cyan-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-cyan-300">AI support agents</div><h2 class="mt-1 text-3xl font-black text-white">Chatbase</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free $0 plan</span></div>\n        <p class="text-sm leading-6 text-slate-300">Chatbase's current pricing page lists a <strong class="text-white">$0 Free plan</strong> with 50 message credits per month and one member. Free-plan agents are deleted after 14 days of inactivity, so treat it as a real evaluation tier rather than permanent unattended hosting.</p>\n        <p class="text-sm leading-6 text-slate-300">For higher usage, Chatbase currently lists Hobby at <strong class="text-white">$40/month</strong>, Standard at $150/month and Pro at $500/month; those paid tiers currently show 7-day trials. Vendor checkout controls final pricing and terms.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact customer referral route Chatbase support supplied after reviewing the partner account. COSHUMA does not invent a separate pricing affiliate deep link.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="chatbase" data-cta-source="verified-deals-chatbase-free" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-cyan-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-cyan-500">Open Chatbase via verified route →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Chatbase plans</a></div>\n        <a href="{OFFICIAL_URL}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify Chatbase pricing →</a>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact vendor-supplied customer-facing referral URL. Publication and link validation do not prove a click, signup, trial, paid customer, commission, payout or revenue; those require separate partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-chatbase-free"',
    "$0 Free plan",
    "50 message credits per month",
    "14 days of inactivity",
    "do not prove a click, signup, trial, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Chatbase buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Chatbase route on buyer hub")
