from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_OMI_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.omi.me/?ref=SANGKWONAN"
GUIDE_URL = "/tool/omi-ai.html"
OFFICIAL_PRODUCT = "https://www.omi.me/products/omi"
OFFICIAL_SUBSCRIPTIONS = "https://help.omi.me/en/articles/12058411-understanding-omi-subscriptions"
BLOCKED_PUBLIC_TOKENS = (
    "affiliate.omi.me",
    "affiliate.omi.me/overview",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - authenticated Omi affiliate-dashboard evidence records TRACKING_URL as the exact
#   COSHUMA customer-facing referral URL. The `ref=SANGKWONAN` key is dashboard-issued.
# - Omi's first-party product page was rechecked 2026-09-13 and currently shows the
#   device at $179 USD.
# - Omi's first-party subscription guide was rechecked 2026-09-13 and currently lists
#   Basic free with 300 listening minutes/month, Plus at $19/month and Unlimited at
#   $29/month.
# - no sale, commission, payout, discount or free-hardware claim is inferred.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Omi verified block exists but exact approved tracking URL is missing")
    if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
        raise SystemExit("Omi affiliate admin URL leaked into the public buyer hub")
    print("Omi verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip and ClickFunnels. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend, Kittl, HelpDesk, Krater, Fireflies.ai, Make.com, Voibe, Catalister, Chatbase, Gojiberry, AWeber, Followr, Novita AI, AiAssistWorks, Taskip, ClickFunnels and Omi AI. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Omi patch")
html = html.replace(old_meta, new_meta, 1)

item33 = (
    '      {"@type":"ListItem","position":33,"name":"ClickFunnels",'
    '"url":"https://coshuma.com/best/clickfunnels-free-trial.html"}\n'
    "    ]"
)
item34 = (
    '      {"@type":"ListItem","position":33,"name":"ClickFunnels",'
    '"url":"https://coshuma.com/best/clickfunnels-free-trial.html"},\n'
    '      {"@type":"ListItem","position":34,"name":"Omi AI",'
    '"url":"https://coshuma.com/tool/omi-ai.html"}\n'
    "    ]"
)
if item33 not in html:
    raise SystemExit("ClickFunnels ItemList tail missing; Omi patch requires the verified ClickFunnels build step first")
html = html.replace(item33, item34, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Omi patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-sky-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-sky-300">AI wearable + meeting memory</div><h2 class="mt-1 text-3xl font-black text-white">Omi AI</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free Basic plan</span></div>\n        <p class="text-sm leading-7 text-slate-300">Omi's current product page lists the wearable at $179. Its current help center lists a free Basic plan with 300 listening minutes per month, Plus at $19/month and Unlimited at $29/month. COSHUMA keeps the exact dashboard-issued referral route separate from those product claims.</p>\n        <ul class="space-y-2 text-sm text-slate-300">\n          <li>• Device: $179 USD on the current first-party product page.</li>\n          <li>• Basic: free, 300 listening minutes/month.</li>\n          <li>• Plus: $19/month; Unlimited: $29/month.</li>\n          <li>• Verified referral destination: exact Omi customer route issued to COSHUMA.</li>\n        </ul>\n        <div class="grid gap-3 sm:grid-cols-2">\n          <a data-cta="affiliate" data-tool-id="omi-ai" data-cta-source="verified-deals-omi" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-sky-600 px-5 py-3.5 text-center font-black text-white hover:bg-sky-500">Check Omi via verified referral →</a>\n          <a data-cta="official" href="{OFFICIAL_PRODUCT}" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-white/15 px-5 py-3.5 text-center font-bold text-slate-200 hover:bg-white/[0.05]">Verify device price →</a>\n        </div>\n        <div class="flex flex-wrap gap-x-5 gap-y-2 text-xs font-bold">\n          <a href="{GUIDE_URL}" class="text-violet-300 hover:text-violet-200">Read COSHUMA Omi buyer guide →</a>\n          <a href="{OFFICIAL_SUBSCRIPTIONS}" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-white">Verify subscriptions →</a>\n        </div>\n        <p class="text-xs leading-5 text-slate-500">Affiliate disclosure: COSHUMA may earn a commission from an eligible purchase through the verified referral route, at no extra cost to the buyer. Publication, link checks or a visit do not prove an order, commission or payout.</p>\n      </article>\n'''

html = html.replace(closing, card + "\n" + closing, 1)

if html.count(TRACKING_URL) < 1:
    raise SystemExit("Omi tracking URL missing after patch")
if any(token in html for token in BLOCKED_PUBLIC_TOKENS):
    raise SystemExit("Omi affiliate admin URL leaked after patch")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Omi buyer route")
