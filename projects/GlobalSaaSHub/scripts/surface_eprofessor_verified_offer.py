from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_EPROFESSOR_VERIFIED_OFFER -->"
TRACKING_URL = "https://eprofessor.com/invite/coshuma173"
GUIDE_URL = "/tool/eprofessor.html"
COMPARE_URL = "/compare/eprofessor-vs-kajabi.html"
OFFICIAL_PRICING = "https://eprofessor.com/page/pricing"
OFFICIAL_REFERRAL_TERMS = "https://eprofessor.com/page/referral-program"
BLOCKED_PUBLIC_TOKENS = (
    "admin.eprofessor.com/referrals",
    "admin.eprofessor.com/referral",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - authenticated eProfessor referral evidence records TRACKING_URL as the exact
#   account-issued customer referral path; do not invent a pricing/trial deep link.
# - eProfessor's current pricing page was rechecked 2026-09-13 and lists Basic $24,
#   Pro $49, Business $99 and Ultimate $149 monthly, plus a no-card free trial.
# - that same first-party pricing page conflicts on trial duration (14 days in the
#   pricing header vs seven days in the FAQ), so this hub deliberately does not
#   promise a duration and tells buyers to verify the live vendor term.
# - link publication or validation is not evidence of a signup, paid customer,
#   commission, payout or revenue.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("eProfessor verified block exists but exact approved tracking URL is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("eProfessor referral admin URL leaked into the public buyer hub")
    print("eProfessor verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels and Omi AI. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels, Omi AI and eProfessor. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind eProfessor patch")
html = html.replace(old_meta, new_meta, 1)

item34 = (
    '      {"@type":"ListItem","position":34,"name":"Omi AI",'
    '"url":"https://coshuma.com/tool/omi-ai.html"}\n'
    "    ]"
)
item35 = (
    '      {"@type":"ListItem","position":34,"name":"Omi AI",'
    '"url":"https://coshuma.com/tool/omi-ai.html"},\n'
    '      {"@type":"ListItem","position":35,"name":"eProfessor",'
    '"url":"https://coshuma.com/tool/eprofessor.html"}\n'
    "    ]"
)
if item34 not in html:
    raise SystemExit("Omi ItemList tail missing; eProfessor patch requires the verified Omi build step first")
html = html.replace(item34, item35, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind eProfessor patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-indigo-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-indigo-300">Courses, assessments & training</div><h2 class="mt-1 text-3xl font-black text-white">eProfessor</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free trial · no card required</span></div>\n        <p class="text-sm leading-7 text-slate-300">eProfessor's current pricing page lists Basic at <strong class="text-white">$24/month</strong>, Pro at <strong class="text-white">$49/month</strong>, Business at <strong class="text-white">$99/month</strong> and Ultimate at <strong class="text-white">$149/month</strong>. It currently advertises a free trial without a credit card.</p>\n        <p class="text-sm leading-7 text-amber-100">Trial-duration note: eProfessor's live pricing page currently conflicts with itself — its pricing header says 14 days while its FAQ says seven days. COSHUMA therefore does not promise a duration here; verify the live vendor term before relying on it.</p>\n        <p class="text-sm leading-7 text-slate-300">COSHUMA uses the exact referral URL issued by the authenticated eProfessor account. The vendor's referral terms say unique-link signups are tracked, but publishing or checking this link does not prove a signup, paid customer, commission or payout.</p>\n        <div class="grid gap-3 sm:grid-cols-2">\n          <a data-cta="affiliate" data-tool-id="eprofessor" data-cta-source="verified-deals-eprofessor" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-indigo-600 px-5 py-3.5 text-center font-black text-white hover:bg-indigo-500">Try eProfessor via verified referral →</a>\n          <a data-cta="official" href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/15 px-5 py-3.5 text-center font-bold text-slate-200 hover:bg-white/[0.05]">Verify live pricing & trial →</a>\n        </div>\n        <div class="flex flex-wrap gap-x-5 gap-y-2 text-xs font-bold">\n          <a href="{GUIDE_URL}" class="text-violet-300 hover:text-violet-200">Read eProfessor buyer guide →</a>\n          <a href="{COMPARE_URL}" class="text-violet-300 hover:text-violet-200">eProfessor vs Kajabi →</a>\n          <a href="{OFFICIAL_REFERRAL_TERMS}" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-white">Verify referral terms →</a>\n        </div>\n        <p class="text-xs leading-5 text-slate-500">Affiliate disclosure: COSHUMA may earn a commission if an eligible referred customer later becomes paid under eProfessor's program terms. A click, signup or free trial is not counted as revenue without partner-side paid-conversion and commission evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + "\n" + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    COMPARE_URL,
    'data-cta-source="verified-deals-eprofessor"',
    "$24/month",
    "$49/month",
    "$99/month",
    "$149/month",
    "pricing header says 14 days while its FAQ says seven days",
    "not counted as revenue without partner-side paid-conversion and commission evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"eProfessor buyer-hub patch lost required token: {token}")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("eProfessor referral admin URL leaked after patch")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified eProfessor buyer route")
