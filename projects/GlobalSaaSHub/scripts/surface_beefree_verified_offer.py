from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_BEEFREE_VERIFIED_OFFER -->"
TRACKING_URL = "https://partners.beefree.io/kqi520hezix2"
ADMIN_HOST = "partnerstack.com"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Beefree verified block exists but exact issued referral URL is missing")
    print("Beefree verified buyer offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk and "
    "Tagshop AI. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI and RGE Studio. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Beefree patch")
html = html.replace(old_meta, new_meta, 1)

item11 = (
    '      {"@type":"ListItem","position":11,"name":"Tagshop AI",'
    '"url":"https://coshuma.com/best/tagshop-ai-free-trial-pricing.html"}\n'
    "    ]"
)
item12 = (
    '      {"@type":"ListItem","position":11,"name":"Tagshop AI",'
    '"url":"https://coshuma.com/best/tagshop-ai-free-trial-pricing.html"},\n'
    '      {"@type":"ListItem","position":12,"name":"RGE Studio (formerly Beefree)",'
    '"url":"https://coshuma.com/tool/beefree.html"}\n'
    "    ]"
)
if item11 not in html:
    raise SystemExit("Tagshop ItemList tail missing; Beefree patch requires the verified Tagshop build step first")
html = html.replace(item11, item12, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Beefree patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-lime-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-lime-300">Email design & collaboration</div><h2 class="mt-1 text-3xl font-black text-white">RGE Studio <span class="text-base font-semibold text-slate-400">(formerly Beefree)</span></h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free entry · verified referral</span></div>\n        <p class="text-sm leading-6 text-slate-300">Beefree's partner team supplied COSHUMA with current conversion guidance for RGE Studio: real-time co-editing, commenting and review, brand controls, sending-platform connectors/HTML export, and an AI Assistant. The same partner message lists a Free tier plus a paid Team tier at <strong class="text-white">$30/month or $25/month with annual purchase</strong>. Final checkout pricing can change.</p>\n        <p class="text-sm leading-6 text-slate-300">Beefree's official Ambassador page currently states that approved partners earn <strong class="text-white">20% of first-year revenue</strong> from new attributed RGE Studio customers and uses a <strong class="text-white">90-day referral cookie</strong>. This commission is paid by the vendor; it does not add a buyer fee.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="beefree" data-cta-source="verified-deals-beefree-issued-referral" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-lime-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-lime-500">Open RGE Studio via verified referral →</a><a href="/tool/beefree.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare RGE Studio plans</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">COSHUMA uses only the exact customer-facing referral URL issued to its existing Beefree Ambassador account. A generic product/pricing page, PartnerStack dashboard or guessed deep link is not treated as a revenue link. Clicks, sign-ups, paid customers, commissions and payouts remain unverified until partner-side evidence appears.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    'data-cta-source="verified-deals-beefree-issued-referral"',
    "20% of first-year revenue",
    "90-day referral cookie",
    "remain unverified until partner-side evidence appears",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Beefree buyer-hub patch lost required token: {token}")

# Safety: no PartnerStack admin/dashboard URL should be publicly emitted by this patch.
if ADMIN_HOST in card.lower():
    raise SystemExit("Beefree public card unexpectedly contains a PartnerStack admin host")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Beefree/RGE Studio referral route on buyer hub")
