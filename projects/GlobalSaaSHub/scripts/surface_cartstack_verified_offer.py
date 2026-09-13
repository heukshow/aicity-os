from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_CARTSTACK_VERIFIED_OFFER -->"
TRACKING_URL = "http://www.cartstack.com/?afmc=wb"
GUIDE_URL = "/tool/cartstack.html"
COMPARE_URL = "/compare/cartstack-vs-aweber.html"
OFFICIAL_PRICING = "https://www.cartstack.com/pricing/"
BLOCKED_PUBLIC_TOKENS = (
    "cartstack.leaddyno.com/p/",
    "admin.cartstack.com",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - CartStack's referral-program welcome email (Gmail message 1a05d03d6d5957d8)
#   directly issued TRACKING_URL and states that clicks followed by signups are
#   credited to the referral account.
# - the same email includes a separate LeadDyno dashboard URL; that is administrative
#   and must never be surfaced as a customer destination.
# - current first-party pricing checked 2026-09-13 advertises a 14-day risk-free
#   trial with no credit card required. Paid pricing scales with monthly order volume,
#   so the central offer deliberately avoids freezing one paid price.
# - publication or validation of this route is not evidence of a click, signup,
#   paid customer, commission, payout or revenue.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("CartStack verified block exists but exact issued referral URL is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("CartStack admin/referral-dashboard URL leaked into the public buyer hub")
    print("CartStack verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI, eProfessor and Omnisend. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI, eProfessor, Omnisend and CartStack. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind CartStack patch")
html = html.replace(old_meta, new_meta, 1)

item36 = (
    '      {"@type":"ListItem","position":36,"name":"Omnisend",'
    '"url":"https://coshuma.com/tool/omnisend.html"}\n'
    "    ]"
)
item37 = (
    '      {"@type":"ListItem","position":36,"name":"Omnisend",'
    '"url":"https://coshuma.com/tool/omnisend.html"},\n'
    '      {"@type":"ListItem","position":37,"name":"CartStack",'
    '"url":"https://coshuma.com/tool/cartstack.html"}\n'
    "    ]"
)
if item36 not in html:
    raise SystemExit("Omnisend ItemList tail missing; CartStack patch requires the verified Omnisend build step first")
html = html.replace(item36, item37, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind CartStack patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-orange-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-orange-300">Cart & visitor recovery</div><h2 class="mt-1 text-3xl font-black text-white">CartStack</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">14-day trial · no card</span></div>\n        <p class="text-sm leading-7 text-slate-300">CartStack's current pricing page advertises a <strong class="text-white">14-day risk-free trial</strong> with <strong class="text-white">no credit card required</strong>. The platform focuses on recovering abandoned carts and visitors through email, with SMS, push and onsite conversion tools available across its plan mix.</p>\n        <p class="text-sm leading-7 text-slate-300">Paid pricing scales with a site's monthly order volume, so COSHUMA does not freeze a single paid price here. Use the live pricing page to confirm the current tier for your order volume before upgrading.</p>\n        <p class="text-sm leading-7 text-slate-300">COSHUMA uses the exact referral URL issued in CartStack's referral-program welcome email. That email states that a visitor who clicks the issued link and then signs up is credited to the referral account. The separate referral-dashboard URL remains private and is not used as a buyer link.</p>\n        <div class="grid gap-3 sm:grid-cols-2">\n          <a data-cta="affiliate" data-tool-id="cartstack" data-cta-source="verified-deals-cartstack" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-orange-600 px-5 py-3.5 text-center font-black text-white hover:bg-orange-500">Try CartStack via verified referral →</a>\n          <a data-cta="official" href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/15 px-5 py-3.5 text-center font-bold text-slate-200 hover:bg-white/[0.05]">Verify live pricing & trial →</a>\n        </div>\n        <div class="flex flex-wrap gap-x-5 gap-y-2 text-xs font-bold">\n          <a href="{GUIDE_URL}" class="text-violet-300 hover:text-violet-200">Read CartStack buyer guide →</a>\n          <a href="{COMPARE_URL}" class="text-violet-300 hover:text-violet-200">CartStack vs AWeber →</a>\n        </div>\n        <p class="text-xs leading-5 text-slate-500">Affiliate disclosure: COSHUMA may receive referral credit if an eligible visitor signs up through this vendor-issued link under CartStack's program terms. Publishing, opening or validating the link does not prove a click, signup, paid customer, commission, payout or revenue.</p>\n      </article>\n'''

html = html.replace(closing, card + "\n" + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    COMPARE_URL,
    'data-cta-source="verified-deals-cartstack"',
    "14-day risk-free trial",
    "no credit card required",
    "monthly order volume",
    "credited to the referral account",
    "does not prove a click, signup, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"CartStack buyer-hub patch lost required token: {token}")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("CartStack admin/referral-dashboard URL leaked after patch")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified CartStack buyer route")
