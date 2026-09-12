from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_CATALISTER_VERIFIED_OFFER -->"
TRACKING_URL = "https://app.catalister.com/signup?via=coshuma"
GUIDE_URL = "/tool/catalister.html"
OFFICIAL_URL = "https://catalister.com/"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - authenticated Catalister dashboard evidence records this exact customer-facing
#   referral URL and a signup destination retaining via=coshuma.
# - Catalister first-party pages rechecked 2026-09-13 advertise a free 7-day trial
#   with no credit card required and the plan prices used below.
# - a link being issued or visited is not evidence of signup, sale or commission.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Catalister verified block exists but exact approved tracking URL is missing")
    print("Catalister verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com and Voibe. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe and Catalister. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Catalister patch")
html = html.replace(old_meta, new_meta, 1)

item24 = (
    '      {"@type":"ListItem","position":24,"name":"Voibe",'
    '"url":"https://coshuma.com/tool/voibe.html"}\n'
    "    ]"
)
item25 = (
    '      {"@type":"ListItem","position":24,"name":"Voibe",'
    '"url":"https://coshuma.com/tool/voibe.html"},\n'
    '      {"@type":"ListItem","position":25,"name":"Catalister",'
    '"url":"https://coshuma.com/tool/catalister.html"}\n'
    "    ]"
)
if item24 not in html:
    raise SystemExit("Voibe ItemList tail missing; Catalister patch requires the verified Voibe build step first")
html = html.replace(item24, item25, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Catalister patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-purple-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-purple-300">Shopify listing automation</div><h2 class="mt-1 text-3xl font-black text-white">Catalister</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">7-day free trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">Catalister's current first-party site advertises a <strong class="text-white">free 7-day trial with no credit card required</strong>. It is built around Shopify product research, AI-generated listings and relisting, plus product-level Google Ads analysis.</p>\n        <p class="text-sm leading-6 text-slate-300">At the time checked, monthly plans start at <strong class="text-white">€14.99</strong> for Starter, then €24.99 Stacker, €34.99 Scaler and €59.99 Slayer. Vendor checkout controls final pricing, taxes and terms.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact customer signup referral URL previously issued inside the authenticated Catalister affiliate dashboard. COSHUMA does not move <code class="text-purple-200">via=coshuma</code> onto a guessed pricing or checkout URL.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="catalister" data-cta-source="verified-deals-catalister-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-purple-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-purple-500">Start Catalister free trial →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Catalister plans</a></div>\n        <a href="{OFFICIAL_URL}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-purple-200 hover:text-white">Verify Catalister pricing & trial →</a>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact account-issued customer-facing referral URL. Publication and link validation do not prove a click, trial, paid customer, commission, payout or revenue; those require separate partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-catalister-trial"',
    "free 7-day trial with no credit card required",
    "€14.99",
    "via=coshuma",
    "do not prove a click, trial, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Catalister buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Catalister free-trial route on buyer hub")
