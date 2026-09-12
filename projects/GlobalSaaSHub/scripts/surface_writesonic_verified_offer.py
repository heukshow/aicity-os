from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_WRITESONIC_VERIFIED_OFFER -->"
TRACKING_URL = "https://writesonic.com?fp_ref=sang-kwon-f5452a"
OFFICIAL_PRICING = "https://writesonic.com/pricing"
ADMIN_HOSTS = (
    "affiliates.writesonic.com",
    "firstpromoter.com",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Repository approved-tracking state records the exact customer-facing URL above
#   from Writesonic's welcome/approval evidence and marks it approved_tracking.
# - Current first-party Writesonic affiliate material rechecked 2026-09-12 says the
#   free trial requires no card, and the current affiliate program advertises 20%
#   recurring commission for up to 12 months with a 60-day cookie.
# - We do not manufacture a pricing deep link by copying fp_ref onto /pricing.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Writesonic verified block exists but exact vendor-issued tracking URL is missing")
    if any(host in html for host in ADMIN_HOSTS):
        raise SystemExit("Writesonic affiliate admin URL leaked into the public buyer hub")
    print("Writesonic verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI and Claap. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap and Writesonic. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Writesonic patch")
html = html.replace(old_meta, new_meta, 1)

item16 = (
    '      {"@type":"ListItem","position":16,"name":"Claap",'
    '"url":"https://coshuma.com/tool/claap.html"}\n'
    "    ]"
)
item17 = (
    '      {"@type":"ListItem","position":16,"name":"Claap",'
    '"url":"https://coshuma.com/tool/claap.html"},\n'
    '      {"@type":"ListItem","position":17,"name":"Writesonic",'
    '"url":"https://coshuma.com/tool/writesonic.html"}\n'
    "    ]"
)
if item16 not in html:
    raise SystemExit("Claap ItemList tail missing; Writesonic patch requires the verified Claap build step first")
html = html.replace(item16, item17, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Writesonic patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-sky-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-sky-300">AI search visibility & content</div><h2 class="mt-1 text-3xl font-black text-white">Writesonic</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">Writesonic's current first-party affiliate page says its free trial can show an AI visibility score across major AI platforms and requires <strong class="text-white">no card</strong>. Use the trial to check whether the product fits your AI-search and content workflow before considering a paid plan.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact customer-facing referral URL already issued for its Writesonic partner account. Writesonic's current first-party affiliate page advertises <strong class="text-white">20% recurring commission for up to 12 months</strong> with a <strong class="text-white">60-day cookie</strong>. Those are affiliate terms, not a guaranteed buyer discount.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="writesonic" data-cta-source="verified-deals-writesonic-approved-link" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-sky-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-sky-500">Start Writesonic via verified partner link →</a><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Check live Writesonic pricing</a></div>\n        <a href="/tool/writesonic.html" class="inline-block text-xs font-bold text-sky-200 hover:text-white">Read the Writesonic buyer guide →</a>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact Writesonic customer-facing referral URL already verified for COSHUMA. The pricing button is a separate official non-affiliate reference; COSHUMA does not guess a pricing deep link. A click, trial, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    OFFICIAL_PRICING,
    'data-cta-source="verified-deals-writesonic-approved-link"',
    "Free trial",
    "no card",
    "20% recurring commission for up to 12 months",
    "60-day cookie",
    "does not guess a pricing deep link",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Writesonic buyer-hub patch lost required token: {token}")
if any(host in html for host in ADMIN_HOSTS):
    raise SystemExit("Writesonic affiliate admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Writesonic free-trial route on buyer hub")
