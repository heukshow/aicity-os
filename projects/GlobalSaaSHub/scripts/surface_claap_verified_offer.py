from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_CLAAP_VERIFIED_OFFER -->"
TRACKING_URL = "https://get.claap.io/rc9nqme16a9q-gfvrqk"
OFFICIAL_PRICING = "https://www.claap.io/pricing"
ADMIN_URLS = (
    "https://dash.partnerstack.com",
    "https://partnerstack.com/dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# COSHUMA's exact Claap customer-facing PartnerStack route was copied directly
# from the existing partner account by Claap affiliate manager Lamia Karmaly and
# is preserved in approved-tracking evidence. Current first-party pages rechecked
# 2026-09-12 show a Basic free entry plan, paid plans beginning at EUR 24/license/mo
# on the public homepage, and no credit card required to start. The live affiliate
# page currently confirms 30% commission on referred paid-plan conversions but does
# not reliably expose a specific buyer discount, so this hub must not advertise one.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Claap verified block exists but exact vendor-confirmed tracking URL is missing")
    if any(url in html for url in ADMIN_URLS):
        raise SystemExit("Claap/PartnerStack admin URL leaked into the public buyer hub")
    print("Claap verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable and Murf AI. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI and Claap. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Claap patch")
html = html.replace(old_meta, new_meta, 1)

item15 = (
    '      {"@type":"ListItem","position":15,"name":"Murf AI",'
    '"url":"https://coshuma.com/tool/murf-ai.html"}\n'
    "    ]"
)
item16 = (
    '      {"@type":"ListItem","position":15,"name":"Murf AI",'
    '"url":"https://coshuma.com/tool/murf-ai.html"},\n'
    '      {"@type":"ListItem","position":16,"name":"Claap",'
    '"url":"https://coshuma.com/tool/claap.html"}\n'
    "    ]"
)
if item15 not in html:
    raise SystemExit("Murf ItemList tail missing; Claap patch requires the verified Murf build step first")
html = html.replace(item15, item16, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Claap patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-indigo-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-indigo-300">AI meetings & revenue workflows</div><h2 class="mt-1 text-3xl font-black text-white">Claap</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free plan · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">Claap's current first-party site lists a <strong class="text-white">Basic free plan</strong> and says you can start without a credit card. The current homepage lists Pro from <strong class="text-white">€24 per license/month</strong> and Business from <strong class="text-white">€48 per license/month</strong>; check live pricing before purchase because billing options can change.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA has a vendor-confirmed customer tracking route for Claap. Claap's live affiliate page confirms referral tracking starts when the prospect first visits through the affiliate link and currently advertises a 30% affiliate commission on referred paid-plan conversions. COSHUMA does <strong class="text-white">not</strong> advertise a specific buyer discount because the live first-party page does not currently confirm one.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="claap" data-cta-source="verified-deals-claap-approved-link" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-indigo-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-indigo-500">Start Claap via verified partner link →</a><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Check live Claap pricing</a></div>\n        <a href="/tool/claap.html" class="inline-block text-xs font-bold text-indigo-200 hover:text-white">Read the Claap buyer guide →</a>\n        <p class="text-[11px] leading-5 text-slate-500">The first button uses the exact Claap customer-facing URL confirmed for COSHUMA. PartnerStack/admin URLs and guessed pricing deep links are not used. A click, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    OFFICIAL_PRICING,
    'data-cta-source="verified-deals-claap-approved-link"',
    "Basic free plan",
    "without a credit card",
    "does <strong class=\"text-white\">not</strong> advertise a specific buyer discount",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Claap buyer-hub patch lost required token: {token}")
if any(url in html for url in ADMIN_URLS):
    raise SystemExit("Claap/PartnerStack admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Claap free-entry route on buyer hub")
