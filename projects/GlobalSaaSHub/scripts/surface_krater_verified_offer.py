from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_KRATER_VERIFIED_OFFER -->"
TRACKING_URL = "https://go.krater.ai/sang-kwon-an"
GUIDE_URL = "/best/krater-ai-pricing.html"
OFFICIAL_PRICING = "https://krater.ai/pricing"
OFFICIAL_AFFILIATE = "https://krater.ai/affiliate"
ADMIN_HOSTS = (
    "partners.dub.co/",
    "app.dub.co/",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Authenticated Dub evidence already records the exact customer-facing Krater
#   route above as approved_tracking for COSHUMA.
# - Krater first-party pricing rechecked 2026-09-12 lists Pro at $200/year with
#   1,500 credits/month, Ultra at $490/year with 4,000 credits/month, and Max at
#   $1,190/year with selectable monthly credits.
# - Krater's first-party affiliate page currently states 25% recurring commission
#   for 12 months from the referred customer's first purchase and defines a valid
#   conversion as a paid subscription. These are partner terms, not revenue proof.
# - We never manufacture a pricing deep link and never publish the Dub dashboard
#   or application route as a customer CTA.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Krater verified block exists but exact approved tracking URL is missing")
    if any(host in html for host in ADMIN_HOSTS):
        raise SystemExit("Krater Dub admin URL leaked into the public buyer hub")
    print("Krater verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl and HelpDesk. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk and Krater. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Krater patch")
html = html.replace(old_meta, new_meta, 1)

item20 = (
    '      {"@type":"ListItem","position":20,"name":"HelpDesk",'
    '"url":"https://coshuma.com/best/helpdesk-free-trial-pricing.html"}\n'
    "    ]"
)
item21 = (
    '      {"@type":"ListItem","position":20,"name":"HelpDesk",'
    '"url":"https://coshuma.com/best/helpdesk-free-trial-pricing.html"},\n'
    '      {"@type":"ListItem","position":21,"name":"Krater",'
    '"url":"https://coshuma.com/best/krater-ai-pricing.html"}\n'
    "    ]"
)
if item20 not in html:
    raise SystemExit("HelpDesk ItemList tail missing; Krater patch requires the verified HelpDesk build step first")
html = html.replace(item20, item21, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Krater patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-emerald-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-emerald-300">All-in-one AI workspace</div><h2 class="mt-1 text-3xl font-black text-white">Krater</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Verified Dub route</span></div>\n        <p class="text-sm leading-6 text-slate-300">Krater's current yearly pricing lists <strong class="text-white">Pro at $200/year with 1,500 credits/month</strong>, <strong class="text-white">Ultra at $490/year with 4,000 credits/month</strong>, and <strong class="text-white">Max at $1,190/year</strong> with selectable monthly credits. Compare expected monthly usage before choosing a tier.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact customer-facing Krater route already verified in its authenticated Dub partner account. Krater's current affiliate page states <strong class="text-white">25% recurring commission for 12 months</strong> from a referred customer's first purchase and defines a valid conversion as a paid subscription. Those are partner terms, not proof COSHUMA has earned money.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="krater" data-cta-source="verified-deals-krater-approved-link" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-emerald-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-emerald-500">Open Krater via COSHUMA →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Krater plans</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-emerald-200 hover:text-white">Verify Krater pricing →</a><a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-emerald-200 hover:text-white">Verify Krater partner terms →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact customer-facing URL previously issued in COSHUMA's authenticated Dub dashboard. COSHUMA does not guess a pricing deep link. A click, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-krater-approved-link"',
    "$200/year with 1,500 credits/month",
    "$490/year with 4,000 credits/month",
    "$1,190/year",
    "25% recurring commission for 12 months",
    "not proof COSHUMA has earned money",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Krater buyer-hub patch lost required token: {token}")
if any(host in html for host in ADMIN_HOSTS):
    raise SystemExit("Krater Dub admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Krater buyer route on buyer hub")
