from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_AWEBER_VERIFIED_OFFER -->"
AUTHORITATIVE_URL = "https://www.aweber.com/easy-email.htm?id=561868"
TRACKING_URL = "https://www.aweber.com/pricing.htm?id=561868"
GUIDE_URL = "/tool/aweber.html"
OFFICIAL_URL = "https://www.aweber.com/pricing.htm"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - COSHUMA already stores the issued account referral URL as approved_tracking.
# - AWeber first-party Advocate docs explicitly permit appending the advocate id to
#   any aweber.com page, so the pricing deep link is allowed rather than guessed.
# - First-party pricing/trial/program terms were rechecked 2026-09-13.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("AWeber verified block exists but approved pricing tracking URL is missing")
    print("AWeber verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase and Gojiberry. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry and AWeber. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind AWeber patch")
html = html.replace(old_meta, new_meta, 1)

item27 = (
    '      {"@type":"ListItem","position":27,"name":"Gojiberry",'
    '"url":"https://coshuma.com/tool/gojiberry.html"}\n'
    "    ]"
)
item28 = (
    '      {"@type":"ListItem","position":27,"name":"Gojiberry",'
    '"url":"https://coshuma.com/tool/gojiberry.html"},\n'
    '      {"@type":"ListItem","position":28,"name":"AWeber",'
    '"url":"https://coshuma.com/tool/aweber.html"}\n'
    "    ]"
)
if item27 not in html:
    raise SystemExit("Gojiberry ItemList tail missing; AWeber patch requires the verified Gojiberry build step first")
html = html.replace(item27, item28, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind AWeber patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-sky-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-sky-300">Email marketing · automation</div><h2 class="mt-1 text-3xl font-black text-white">AWeber</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">14-day trial</span></div>\n        <p class="text-sm leading-6 text-slate-300">AWeber's current official pricing page offers a <strong class="text-white">14-day free trial</strong>. For the displayed 0-500 subscriber tier, Lite is currently shown at <strong class="text-white">$12.49/month billed annually</strong> and Plus at <strong class="text-white">$19.99/month billed annually</strong>. Check the vendor page for the live monthly option and subscriber-tier price before purchase.</p>\n        <p class="text-sm leading-6 text-slate-300">AWeber's trial documentation says the card on file is automatically charged when the trial ends unless you cancel first. Its Advocate documentation currently describes a <strong class="text-white">90-day referral cookie</strong> and <strong class="text-white">30%-50% recurring commission tiers</strong> for paid referrals; those are program terms, not proof of COSHUMA revenue.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA's issued account referral route is <code class="text-sky-200">{AUTHORITATIVE_URL}</code>. AWeber explicitly documents that the advocate ID may be appended to any AWeber page while preserving referral tracking, so this buyer CTA uses the approved pricing deep link instead of an invented route or dashboard URL.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="aweber" data-cta-source="verified-deals-aweber-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-sky-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-sky-500">Start AWeber 14-day trial →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Review AWeber pricing</a></div>\n        <a href="{OFFICIAL_URL}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-sky-200 hover:text-white">Verify AWeber pricing →</a>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves COSHUMA's approved advocate attribution on AWeber's pricing page. Publication and link validation do not prove a click, signup, trial, paid customer, commission, payout or revenue; those require separate partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    AUTHORITATIVE_URL,
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-aweber-trial"',
    "14-day free trial",
    "$12.49/month billed annually",
    "$19.99/month billed annually",
    "90-day referral cookie",
    "30%-50% recurring commission tiers",
    "do not prove a click, signup, trial, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"AWeber buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified AWeber route on buyer hub")
