from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_VOIBE_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.getvoibe.com/?aff=G5Yr5D"
GUIDE_URL = "/tool/voibe.html"
OFFICIAL_PRICING = "https://www.getvoibe.com/"
OFFICIAL_TRIAL = "https://www.getvoibe.com/help/free-trial/"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - authenticated Lemon Squeezy evidence in approved-tracking-2026-09-08.json
#   records this exact customer-facing affiliate URL after the Voibe program became Active.
# - first-party Voibe pages rechecked 2026-09-13 distinguish free download (no card)
#   from the 7-day Pro subscription trial (card required, no charge until day 8).
# - link issuance or a validation visit is not evidence of a customer conversion or revenue.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Voibe verified block exists but exact approved tracking URL is missing")
    print("Voibe verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai and Make.com. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com and Voibe. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Voibe patch")
html = html.replace(old_meta, new_meta, 1)

item23 = (
    '      {"@type":"ListItem","position":23,"name":"Make.com",'
    '"url":"https://coshuma.com/tool/make-com.html"}\n'
    "    ]"
)
item24 = (
    '      {"@type":"ListItem","position":23,"name":"Make.com",'
    '"url":"https://coshuma.com/tool/make-com.html"},\n'
    '      {"@type":"ListItem","position":24,"name":"Voibe",'
    '"url":"https://coshuma.com/tool/voibe.html"}\n'
    "    ]"
)
if item23 not in html:
    raise SystemExit("Make ItemList tail missing; Voibe patch requires the verified Make build step first")
html = html.replace(item23, item24, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Voibe patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-sky-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-sky-300">Private voice dictation</div><h2 class="mt-1 text-3xl font-black text-white">Voibe</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free download · 7-day Pro trial</span></div>\n        <p class="text-sm leading-6 text-slate-300">Voibe's current first-party site lets you <strong class="text-white">download and start without a credit card</strong>. Its separate 7-day Pro Monthly/Annual trial requires a card on file, but the trial help page says there is <strong class="text-white">no charge until day 8</strong> if you continue.</p>\n        <p class="text-sm leading-6 text-slate-300">At the time checked, Voibe lists Monthly at <strong class="text-white">$7.50/month</strong>, Annual at <strong class="text-white">$59/year</strong> and Lifetime at <strong class="text-white">$149</strong>, plus a stated 30-day money-back guarantee. Vendor checkout controls the final price and terms.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact Voibe affiliate URL previously issued by the authenticated Lemon Squeezy program after the program became Active. The link being active is not proof of a signup, paid customer, commission or revenue.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="voibe" data-cta-source="verified-deals-voibe-free" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-sky-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-sky-500">Try Voibe free →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Voibe plans</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-sky-200 hover:text-white">Verify Voibe pricing →</a><a href="{OFFICIAL_TRIAL}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-sky-200 hover:text-white">Verify trial terms →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact customer-facing affiliate URL issued to COSHUMA. COSHUMA does not move the affiliate parameter onto a guessed pricing or checkout deep link. A click, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-voibe-free"',
    "download and start without a credit card",
    "no charge until day 8",
    "$7.50/month",
    "$59/year",
    "$149",
    "not proof of a signup, paid customer, commission or revenue",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Voibe buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Voibe free-download/trial route on buyer hub")
