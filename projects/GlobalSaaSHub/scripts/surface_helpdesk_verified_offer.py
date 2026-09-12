from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_HELPDESK_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.helpdesk.com/?a=8IetMhQvR&utm_campaign=pp_helpdesk-default&utm_source=PP&d=14"
GUIDE_URL = "/best/helpdesk-free-trial-pricing.html"
OFFICIAL_PRICING = "https://www.helpdesk.com/pricing/"
OFFICIAL_AFFILIATE = "https://www.text.com/partners/affiliate/"
ADMIN_HOSTS = (
    "partners.livechat.com/app/affiliate",
    "partners.livechat.com/app/",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Repository approved-tracking evidence records the exact customer-facing
#   HelpDesk campaign URL above for COSHUMA's authenticated Text Partner account.
# - HelpDesk first-party pricing rechecked 2026-09-12 states a 14-day free trial
#   with no credit card, Essential at $19/user/mo yearly ($25 monthly) and Growth
#   at $79/user/mo yearly ($99 monthly).
# - Text's first-party affiliate page says HelpDesk is an eligible Text app and
#   currently advertises up to 22% lifetime recurring commission with a 120-day
#   cookie. These are program terms, not a buyer discount or revenue evidence.
# - We never manufacture a pricing/trial deep link and never publish the partner
#   dashboard as a customer CTA.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("HelpDesk verified block exists but exact approved campaign URL is missing")
    if any(host in html for host in ADMIN_HOSTS):
        raise SystemExit("HelpDesk partner admin URL leaked into the public buyer hub")
    print("HelpDesk verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend and Kittl. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl and HelpDesk. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind HelpDesk patch")
html = html.replace(old_meta, new_meta, 1)

item19 = (
    '      {"@type":"ListItem","position":19,"name":"Kittl",'
    '"url":"https://coshuma.com/best/kittl-commercial-use-license.html"}\n'
    "    ]"
)
item20 = (
    '      {"@type":"ListItem","position":19,"name":"Kittl",'
    '"url":"https://coshuma.com/best/kittl-commercial-use-license.html"},\n'
    '      {"@type":"ListItem","position":20,"name":"HelpDesk",'
    '"url":"https://coshuma.com/best/helpdesk-free-trial-pricing.html"}\n'
    "    ]"
)
if item19 not in html:
    raise SystemExit("Kittl ItemList tail missing; HelpDesk patch requires the verified Kittl build step first")
html = html.replace(item19, item20, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind HelpDesk patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-cyan-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-cyan-300">Customer support & AI ticketing</div><h2 class="mt-1 text-3xl font-black text-white">HelpDesk</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">14 days · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">HelpDesk currently offers a <strong class="text-white">14-day free trial with no credit card required</strong>. Its current pricing page lists Essential from <strong class="text-white">$19/user/month billed annually</strong> ($25 monthly) and Growth from <strong class="text-white">$79/user/month billed annually</strong> ($99 monthly). Use the trial on real support traffic before paying for seats.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact HelpDesk customer campaign URL already verified in its authenticated Text Partner account. Text's current affiliate page lists HelpDesk as an eligible app and advertises up to <strong class="text-white">22% lifetime recurring commission</strong> with a <strong class="text-white">120-day cookie</strong>. Those are partner terms, not a buyer discount or proof that COSHUMA has earned money.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="helpdesk" data-cta-source="verified-deals-helpdesk-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-cyan-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-cyan-500">Start HelpDesk 14-day trial →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare HelpDesk pricing</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify HelpDesk pricing →</a><a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify Text partner terms →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact customer-facing HelpDesk campaign URL already verified for COSHUMA. COSHUMA does not guess a pricing deep link. A click, trial, paying customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-helpdesk-trial"',
    "14-day free trial with no credit card required",
    "$19/user/month billed annually",
    "$79/user/month billed annually",
    "22% lifetime recurring commission",
    "120-day cookie",
    "not a buyer discount or proof that COSHUMA has earned money",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"HelpDesk buyer-hub patch lost required token: {token}")
if any(host in html for host in ADMIN_HOSTS):
    raise SystemExit("HelpDesk partner admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified HelpDesk trial route on buyer hub")
