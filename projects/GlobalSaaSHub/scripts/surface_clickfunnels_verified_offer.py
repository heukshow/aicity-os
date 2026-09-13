from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_CLICKFUNNELS_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.clickfunnels.com/signup-flow?aff=b57f3056884d05b842f607e32347df542821875bbe3209a214141aa32a210532"
GUIDE_URL = "/best/clickfunnels-free-trial.html"
OFFICIAL_PRICING = "https://www.clickfunnels.com/pricing"
OFFICIAL_TRIAL_BILLING = "https://support.clickfunnels.com/en/articles/12734363-will-i-be-billed-automatically-after-the-free-14-day-trial-period"
BLOCKED_PUBLIC_TOKENS = (
    "affiliates.clickfunnels.com/login",
    "affiliate-center.clickfunnels.com",
    "clickfunnels.com/affiliate-dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - authenticated ClickFunnels affiliate evidence records TRACKING_URL as the exact
#   customer-facing Free Trial campaign route and records 0 commissions / 0
#   conversions at the 2026-09-08 verification time.
# - ClickFunnels' current first-party pricing page was rechecked 2026-09-13 and
#   exposes Start Free Trial for Launch, Scale and Optimize. The current official
#   support article says the card on file is charged after 14 days unless canceled.
# - no guessed pricing deep link is used; the issued campaign URL stays intact.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("ClickFunnels verified block exists but exact approved tracking URL is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("ClickFunnels affiliate admin URL leaked into the public buyer hub")
    print("ClickFunnels verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks and Taskip. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip and ClickFunnels. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind ClickFunnels patch")
html = html.replace(old_meta, new_meta, 1)

item32 = (
    '      {"@type":"ListItem","position":32,"name":"Taskip",'
    '"url":"https://coshuma.com/tool/taskip.html"}\n'
    "    ]"
)
item33 = (
    '      {"@type":"ListItem","position":32,"name":"Taskip",'
    '"url":"https://coshuma.com/tool/taskip.html"},\n'
    '      {"@type":"ListItem","position":33,"name":"ClickFunnels",'
    '"url":"https://coshuma.com/best/clickfunnels-free-trial.html"}\n'
    "    ]"
)
if item32 not in html:
    raise SystemExit("Taskip ItemList tail missing; ClickFunnels patch requires the verified Taskip build step first")
html = html.replace(item32, item33, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind ClickFunnels patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-violet-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-violet-300">Sales funnels & checkout flows</div><h2 class="mt-1 text-3xl font-black text-white">ClickFunnels</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">14-day free trial</span></div>\n        <p class="text-sm leading-6 text-slate-300">ClickFunnels' current pricing page exposes <strong class="text-white">Start Free Trial</strong> for Launch, Scale and Optimize. The current monthly view lists Launch at <strong class="text-white">$97/month</strong>, Scale at <strong class="text-white">$197/month</strong> and Optimize at <strong class="text-white">$297/month</strong>; the annual-billing view shows lower effective monthly prices.</p>\n        <p class="text-sm leading-6 text-slate-300">ClickFunnels' official support documentation says the trial is <strong class="text-white">14 days</strong> and the card on file is automatically charged when the trial ends unless the account is canceled or scheduled to cancel first. Use the trial to validate one real funnel, checkout and follow-up path before paying.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA preserves the exact customer-facing Free Trial campaign URL previously recovered from the authenticated ClickFunnels affiliate dashboard. It does not append the affiliate token to a guessed pricing or checkout URL.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="clickfunnels" data-cta-source="verified-deals-clickfunnels-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-violet-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-violet-500">Start ClickFunnels trial →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Review ClickFunnels trial</a></div>\n        <div class="flex flex-wrap gap-4"><a href="{OFFICIAL_PRICING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-violet-200 hover:text-white">Verify current pricing →</a><a href="{OFFICIAL_TRIAL_BILLING}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-violet-200 hover:text-white">Verify trial billing →</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The affiliate dashboard showed $0 commissions and 0 conversions at the September 8 verification time. That historical snapshot is not treated as a current total. Publication, link validation or a trial start does not prove a paid customer, commission, payout or revenue.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-clickfunnels-trial"',
    "14-day free trial",
    "$97/month",
    "$197/month",
    "$297/month",
    "does not append the affiliate token to a guessed pricing or checkout URL",
    "historical snapshot is not treated as a current total",
    "does not prove a paid customer, commission, payout or revenue",
]
for token in required:
    if token not in html:
        raise SystemExit(f"ClickFunnels buyer-hub patch lost required token: {token}")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("ClickFunnels affiliate admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified ClickFunnels trial route on buyer hub")
