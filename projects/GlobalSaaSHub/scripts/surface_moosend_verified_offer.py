from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_MOOSEND_VERIFIED_OFFER -->"
TRACKING_URL = "https://trymoo.moosend.com/6eappdpw04pw"
GUIDE_URL = "/best/moosend-free-trial.html"
OFFICIAL_AFFILIATE = "https://moosend.com/affiliate-program/"
ADMIN_HOSTS = (
    "partnerstack.com",
    "app.partnerstack.com",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Repository approved-tracking evidence records the exact customer-facing
#   PartnerStack route above for COSHUMA's existing Moosend relationship.
# - Current first-party Moosend terms still state a 30-day free trial and the
#   live registration page says no credit card is required to get started.
# - Current first-party affiliate material advertises tiered recurring commission
#   starting at 30% and rising to 40%; these are partner terms, not a buyer discount.
# - We do not manufacture a pricing deep link or reuse any PartnerStack admin URL.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Moosend verified block exists but exact approved tracking URL is missing")
    if any(host in html for host in ADMIN_HOSTS):
        raise SystemExit("Moosend affiliate admin URL leaked into the public buyer hub")
    print("Moosend verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap and Writesonic. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic and Moosend. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Moosend patch")
html = html.replace(old_meta, new_meta, 1)

item17 = (
    '      {"@type":"ListItem","position":17,"name":"Writesonic",'
    '"url":"https://coshuma.com/tool/writesonic.html"}\n'
    "    ]"
)
item18 = (
    '      {"@type":"ListItem","position":17,"name":"Writesonic",'
    '"url":"https://coshuma.com/tool/writesonic.html"},\n'
    '      {"@type":"ListItem","position":18,"name":"Moosend",'
    '"url":"https://coshuma.com/best/moosend-free-trial.html"}\n'
    "    ]"
)
if item17 not in html:
    raise SystemExit("Writesonic ItemList tail missing; Moosend patch requires the verified Writesonic build step first")
html = html.replace(item17, item18, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Moosend patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-indigo-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-indigo-300">Email marketing & automation</div><h2 class="mt-1 text-3xl font-black text-white">Moosend</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">30-day trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">Moosend's current terms provide a <strong class="text-white">30-day free trial</strong>, and its live registration page says <strong class="text-white">no credit card is required</strong> to get started. Use the trial to test a real campaign, one automation and your normal list workflow before deciding whether a paid plan fits.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact customer-facing PartnerStack route already verified for its existing Moosend partner account. Moosend's current affiliate page advertises recurring partner commission starting at <strong class="text-white">30%</strong> and increasing with paid referrals up to <strong class="text-white">40%</strong>. Those are partner terms, not a guaranteed buyer discount.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="moosend" data-cta-source="verified-deals-moosend-approved-link" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-indigo-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-indigo-500">Start Moosend 30-day trial →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Read Moosend trial guide</a></div>\n        <a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-indigo-200 hover:text-white">Verify Moosend affiliate terms →</a>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact Moosend customer-facing referral URL already verified for COSHUMA. COSHUMA does not guess a pricing deep link. A click, trial, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-moosend-approved-link"',
    "30-day free trial",
    "no credit card is required",
    "starting at <strong class=\"text-white\">30%</strong>",
    "up to <strong class=\"text-white\">40%</strong>",
    "not a guaranteed buyer discount",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Moosend buyer-hub patch lost required token: {token}")
if any(host in html for host in ADMIN_HOSTS):
    raise SystemExit("Moosend affiliate admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Moosend 30-day trial route on buyer hub")
