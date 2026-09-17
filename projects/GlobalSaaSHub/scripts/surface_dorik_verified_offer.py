from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_DORIK_VERIFIED_OFFER -->"
TRACKING_URL = "https://dorik.com/?ref=coshuma"
GUIDE_URL = "/tool/dorik.html"
OFFICIAL_PRICING = "https://dorik.com/pricing"
OFFICIAL_AFFILIATE_TERMS = "https://help.dorik.com/en/article/partner-program-details-terms-97s9i5/"
BLOCKED_PUBLIC_TOKENS = (
    'href="https://partners.dorik.com',
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - data/tools.json records Dorik as approved_tracking and preserves the exact
#   customer-facing referral URL in TRACKING_URL.
# - Dorik's live pricing page checked 2026-09-13 states a 7-day free trial and
#   current monthly Personal $29, Business $59 and Agency $99 pricing.
# - Dorik's formal first-party partner terms, updated 2026-07-31 and checked
#   2026-09-13, state 40% on the first purchase and a 90-day attribution cookie.
#   They do not specify a renewal commission percentage, so older/marketing
#   recurring-rate claims are intentionally not surfaced as verified terms here.
# - those public program terms and link publication are not COSHUMA revenue evidence.
if MARKER in html:
    marker_start = html.index(MARKER)
    marker_end = html.find("</article>", marker_start)
    if marker_end < 0:
        raise SystemExit("Dorik verified marker exists but card boundary is missing")
    existing_card = html[marker_start:marker_end]
    if TRACKING_URL not in existing_card:
        raise SystemExit("Dorik verified block exists but exact issued affiliate URL is missing")
    if any(token in existing_card for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("Dorik partner/admin URL leaked into the Dorik buyer card")
    print("Dorik verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI, eProfessor, Omnisend, CartStack and ElevenLabs. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI, eProfessor, Omnisend, CartStack, ElevenLabs and Dorik. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Dorik patch")
html = html.replace(old_meta, new_meta, 1)

item38 = (
    '      {"@type":"ListItem","position":38,"name":"ElevenLabs",'
    '"url":"https://coshuma.com/tool/elevenlabs.html"}\n'
    "    ]"
)
item39 = (
    '      {"@type":"ListItem","position":38,"name":"ElevenLabs",'
    '"url":"https://coshuma.com/tool/elevenlabs.html"},\n'
    '      {"@type":"ListItem","position":39,"name":"Dorik",'
    '"url":"https://coshuma.com/tool/dorik.html"}\n'
    "    ]"
)
if item38 not in html:
    raise SystemExit("ElevenLabs ItemList tail missing; Dorik patch requires the verified ElevenLabs build step first")
html = html.replace(item38, item39, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Dorik patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-cyan-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-cyan-300">AI website builder</div><h2 class="mt-1 text-3xl font-black text-white">Dorik</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">7-day free trial</span></div>\n        <p class="text-sm leading-7 text-slate-300">Dorik's live pricing page currently offers a <strong class="text-white">7-day free trial</strong>. Current month-to-month prices are <strong class="text-white">Personal $29/month</strong>, <strong class="text-white">Business $59/month</strong>, and <strong class="text-white">Agency $99/month</strong>. Annual, two-year and lifetime options are also published, so verify the live pricing page before purchasing.</p>\n        <p class="text-sm leading-7 text-slate-300">Use the 7-day trial to check whether Dorik fits your site-building workflow, then compare the current Personal, Business and Agency limits before choosing a paid term.</p>\n        <div class="grid gap-3 sm:grid-cols-2">\n          <a data-cta="affiliate" data-tool-id="dorik" data-cta-source="verified-deals-dorik-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-cyan-600 px-5 py-3.5 text-center font-black text-white hover:bg-cyan-500">Try Dorik →</a>\n          <a data-cta="official" href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/15 px-5 py-3.5 text-center font-bold text-slate-200 hover:bg-white/[0.05]">Verify live pricing →</a>\n        </div>\n        <div class="flex flex-wrap gap-x-5 gap-y-2 text-xs font-bold">\n          <a href="{GUIDE_URL}" class="text-violet-300 hover:text-violet-200">Read Dorik buyer guide →</a>\n        </div>\n      </article>\n'''

if any(token in card for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("Dorik partner/admin URL leaked into generated Dorik buyer card")
html = html.replace(closing, card + "\n" + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    OFFICIAL_PRICING,
    'data-cta-source="verified-deals-dorik-trial"',
    "7-day free trial",
    "Personal $29/month",
    "Business $59/month",
    "Agency $99/month",
    "fits your site-building workflow",
    "Try Dorik →",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Dorik buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced Dorik buyer offer")
