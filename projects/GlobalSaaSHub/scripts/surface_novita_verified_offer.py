from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_NOVITA_VERIFIED_OFFER -->"
TRACKING_URL = "https://novita.ai/?ref=mwjmyjy&utm_source=affiliate"
GUIDE_URL = "/tool/novita-ai.html"
OFFICIAL_SIGNUP = "https://novita.ai/user/register"
OFFICIAL_PRICING = "https://novita.ai/pricing"
OFFICIAL_AFFILIATE = "https://affiliates.novita.ai/"
OFFICIAL_TERMS = "https://affiliates.novita.ai/programs/model-api/tos/"
BLOCKED_PUBLIC_TOKENS = (
    "app.tapfiliate.com",
    "tapfiliate.com/dashboard",
    "affiliates.novita.ai/p/",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Existing COSHUMA evidence preserves the exact account-specific Novita AI referral URL.
# - Novita first-party signup and affiliate pages were rechecked 2026-09-13.
# - The public $100 offer is Sandbox credit, not a blanket credit for every Novita product.
# - Public partner terms exclude discounted/coupon credit top-ups and Baremetal from commission.
# - Publication/link validation is never downstream revenue evidence.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Novita verified block exists but exact approved tracking URL is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("Novita affiliate admin/onboarding URL leaked into the public buyer hub")
    print("Novita verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber and Followr. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr and Novita AI. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Novita patch")
html = html.replace(old_meta, new_meta, 1)

item29 = (
    '      {"@type":"ListItem","position":29,"name":"Followr",'
    '"url":"https://coshuma.com/tool/followr.html"}\n'
    "    ]"
)
item30 = (
    '      {"@type":"ListItem","position":29,"name":"Followr",'
    '"url":"https://coshuma.com/tool/followr.html"},\n'
    '      {"@type":"ListItem","position":30,"name":"Novita AI",'
    '"url":"https://coshuma.com/tool/novita-ai.html"}\n'
    "    ]"
)
if item29 not in html:
    raise SystemExit("Followr ItemList tail missing; Novita patch requires the verified Followr build step first")
html = html.replace(item29, item30, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Novita patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-cyan-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-cyan-300">AI cloud · model APIs · agent sandbox</div><h2 class="mt-1 text-3xl font-black text-white">Novita AI</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">$100 Sandbox credits · 90 days</span></div>\n        <p class="text-sm leading-6 text-slate-300">Novita AI's current signup page advertises <strong class="text-white">$100 in Agent Sandbox credits valid for 90 days</strong>. Treat this as a Sandbox evaluation budget, not a blanket $100 credit for every Novita product. Use the free period to test the agent workload you actually expect to run before topping up.</p>\n        <p class="text-sm leading-6 text-slate-300">Novita's public affiliate page currently states <strong class="text-white">10% commission on a referral's spending for the first 180 days</strong> and a <strong class="text-white">60-day cookie</strong>. Those are program terms, not evidence that COSHUMA has generated a signup, paying customer or commission.</p>\n        <p class="text-sm leading-6 text-slate-300">The current affiliate terms also narrow what qualifies: commissions apply to eligible <strong class="text-white">non-discounted credit top-ups</strong>, while promotional/coupon transactions and <strong class="text-white">Baremetal products</strong> are excluded. COSHUMA keeps those limits visible instead of treating all Novita spend as commissionable.</p>\n        <p class="text-sm leading-6 text-slate-300">The revenue CTA below uses only COSHUMA's exact account-specific Novita referral URL already recorded from the approval email and browser verification. COSHUMA does not manufacture a tracked signup, pricing or checkout deep link.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="novita-ai" data-cta-source="verified-deals-novita-sandbox" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-cyan-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-cyan-500">Explore Novita AI →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Review Novita AI buyer guide</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_SIGNUP}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify signup credits →</a><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify pricing →</a><a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify partner rate →</a><a href="{OFFICIAL_TERMS}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-cyan-200 hover:text-white">Verify commission exclusions →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact customer-facing referral URL already recorded for COSHUMA. Publication and link validation do not prove a click, signup, paid top-up, commission, payout or revenue; those require separate partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-novita-sandbox"',
    "$100 in Agent Sandbox credits valid for 90 days",
    "10% commission on a referral's spending for the first 180 days",
    "60-day cookie",
    "non-discounted credit top-ups",
    "Baremetal products",
    "do not prove a click, signup, paid top-up, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Novita buyer-hub patch lost required token: {token}")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("Novita affiliate admin/onboarding URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Novita AI Sandbox-credit route on buyer hub")
