from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_FOLLOWR_VERIFIED_OFFER -->"
TRACKING_URL = "https://followr.ai/?ref=support22"
GUIDE_URL = "/tool/followr.html"
OFFICIAL_PRICING = "https://followr.ai/pricing"
OFFICIAL_TRIAL = "https://help.followr.ai/en/articles/12305904-refund-policy"
OFFICIAL_AFFILIATE = "https://help.followr.ai/en/articles/11390435-join-the-followr-affiliate-program"
ADMIN_HOSTS = (
    "followr.pushlapgrowth.com",
    "pushlapgrowth.com/dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Existing COSHUMA evidence preserves the exact account-specific Followr referral URL.
# - Followr first-party trial and affiliate documentation were rechecked 2026-09-13.
# - Fresh authenticated dashboard metrics are not claimed because the latest recorded
#   partner-portal access requires email-code verification.
# - Publication/link validation is never downstream revenue evidence.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Followr verified block exists but exact approved tracking URL is missing")
    if any(host in html for host in ADMIN_HOSTS):
        raise SystemExit("Followr affiliate admin URL leaked into the public buyer hub")
    print("Followr verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry and AWeber. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber and Followr. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Followr patch")
html = html.replace(old_meta, new_meta, 1)

item28 = (
    '      {"@type":"ListItem","position":28,"name":"AWeber",'
    '"url":"https://coshuma.com/tool/aweber.html"}\n'
    "    ]"
)
item29 = (
    '      {"@type":"ListItem","position":28,"name":"AWeber",'
    '"url":"https://coshuma.com/tool/aweber.html"},\n'
    '      {"@type":"ListItem","position":29,"name":"Followr",'
    '"url":"https://coshuma.com/tool/followr.html"}\n'
    "    ]"
)
if item28 not in html:
    raise SystemExit("AWeber ItemList tail missing; Followr patch requires the verified AWeber build step first")
html = html.replace(item28, item29, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Followr patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-purple-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-purple-300">AI social media · scheduling</div><h2 class="mt-1 text-3xl font-black text-white">Followr</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">3-day free trial</span></div>\n        <p class="text-sm leading-6 text-slate-300">Followr's current official refund policy documents a <strong class="text-white">free 3-day / 72-hour trial</strong> with access to platform features subject to an AI-credit limit. It is a short evaluation window, so test the networks you actually publish to, AI output quality, scheduling and analytics immediately.</p>\n        <p class="text-sm leading-6 text-slate-300">The same policy says the selected subscription is <strong class="text-white">automatically charged when the trial ends unless you cancel first</strong>. COSHUMA therefore does not present the trial as risk-free after 72 hours and does not guess a core social-plan price when Followr's public pricing page does not reliably expose those amounts.</p>\n        <p class="text-sm leading-6 text-slate-300">Followr's official affiliate documentation currently states <strong class="text-white">25% recurring commission</strong> for referred purchases. That describes the public partner program; it does not prove COSHUMA has generated a signup, customer or commission.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses only the exact account-specific customer referral URL already recorded in its approved-tracking evidence. It does not append <code class="text-purple-200">ref=support22</code> to an unverified pricing or checkout deep link and never publishes the affiliate portal as a buyer CTA.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="followr" data-cta-source="verified-deals-followr-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-purple-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-purple-500">Start Followr 3-day trial →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Review Followr buyer guide</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-purple-200 hover:text-white">Verify Followr pricing →</a><a href="{OFFICIAL_TRIAL}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-purple-200 hover:text-white">Verify trial billing →</a><a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-purple-200 hover:text-white">Verify partner terms →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact customer-facing referral URL already recorded for COSHUMA. Publication and link validation do not prove a click, signup, trial, paid customer, commission, payout or revenue; those require separate partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-followr-trial"',
    "free 3-day / 72-hour trial",
    "automatically charged when the trial ends unless you cancel first",
    "25% recurring commission",
    "do not prove a click, signup, trial, paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Followr buyer-hub patch lost required token: {token}")
if any(host in html for host in ADMIN_HOSTS):
    raise SystemExit("Followr affiliate admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Followr trial route on buyer hub")
