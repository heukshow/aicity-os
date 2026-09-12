from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_GOJIBERRY_VERIFIED_OFFER -->"
TRACKING_URL = "https://gojiberry.ai/?ref=sangkwon"
GUIDE_URL = "/tool/gojiberry.html"
OFFICIAL_URL = "https://gojiberry.ai/"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - COSHUMA's existing approved-tracking evidence preserves this exact account-specific route.
# - Gojiberry first-party pricing and affiliate pages were rechecked 2026-09-13.
# - publication/link validation is never downstream revenue evidence.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Gojiberry verified block exists but exact approved tracking URL is missing")
    print("Gojiberry verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister and Chatbase. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase and Gojiberry. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Gojiberry patch")
html = html.replace(old_meta, new_meta, 1)

item26 = (
    '      {"@type":"ListItem","position":26,"name":"Chatbase",'
    '"url":"https://coshuma.com/tool/chatbase.html"}\n'
    "    ]"
)
item27 = (
    '      {"@type":"ListItem","position":26,"name":"Chatbase",'
    '"url":"https://coshuma.com/tool/chatbase.html"},\n'
    '      {"@type":"ListItem","position":27,"name":"Gojiberry",'
    '"url":"https://coshuma.com/tool/gojiberry.html"}\n'
    "    ]"
)
if item26 not in html:
    raise SystemExit("Chatbase ItemList tail missing; Gojiberry patch requires the verified Chatbase build step first")
html = html.replace(item26, item27, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Gojiberry patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-rose-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-rose-300">B2B sales · AI outreach</div><h2 class="mt-1 text-3xl font-black text-white">Gojiberry</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free trial</span></div>\n        <p class="text-sm leading-6 text-slate-300">Gojiberry's current official site lists <strong class="text-white">Pro at $99/month</strong> for founders and operators running outbound. The current offer includes 2 AI agents, up to 1,800 contacted prospects per month, warm-lead sourcing, a unified inbox, lead scoring, enrichment and CRM/API/MCP integrations.</p>\n        <p class="text-sm leading-6 text-slate-300">The vendor advertises a <strong class="text-white">free trial</strong> and cancel-anytime terms, making it possible to test lead quality and outreach fit before paying. Public affiliate terms currently state a 30% recurring commission structure and 30-day cookie; those program terms do not prove a COSHUMA conversion.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA preserves the exact account-specific customer referral route already recorded in approved-tracking evidence. COSHUMA does not invent a pricing deep link or reuse an admin/dashboard URL.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="gojiberry" data-cta-source="verified-deals-gojiberry-free" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-rose-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-rose-500">Try Gojiberry via verified route →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Gojiberry pricing</a></div>\n        <a href="{OFFICIAL_URL}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-rose-200 hover:text-white">Verify Gojiberry offer →</a>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact account-specific customer referral URL. Publication and link validation do not prove a click, signup, trial, paid customer, commission, payout or revenue; those require separate partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-gojiberry-free"',
    "$99/month",
    "1,800 contacted prospects per month",
    "30% recurring commission structure",
    "do not prove a click, signup, trial, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Gojiberry buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Gojiberry route on buyer hub")
