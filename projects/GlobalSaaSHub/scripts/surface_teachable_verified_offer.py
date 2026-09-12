from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TEACHABLE_VERIFIED_OFFER -->"
TRIAL_URL = "https://partnerstack.teachable.com/COSHUMA"
DEFAULT_TRACKING_URL = "https://partnerstack.teachable.com/ce4muoxdj46j"
ADMIN_URLS = (
    "https://dash.partnerstack.com",
    "https://partnerstack.com/dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Teachable affiliate manager Camila Gouveia supplied this exact customer-facing
# PartnerStack URL to support@coshuma.com on 2026-09-09 and explicitly described
# it as COSHUMA's 30-day Free Trial route. Teachable's public pricing page currently
# advertises a 7-day free trial, so keep the vendor-issued 30-day route distinct and
# never manufacture an extended-trial parameter from the public website.
if MARKER in html:
    if TRIAL_URL not in html:
        raise SystemExit("Teachable verified block exists but exact 30-day trial URL is missing")
    if any(url in html for url in ADMIN_URLS):
        raise SystemExit("Teachable/PartnerStack admin URL leaked into the public buyer hub")
    print("Teachable verified 30-day trial already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio and BoldSign. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign and Teachable. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Teachable patch")
html = html.replace(old_meta, new_meta, 1)

item13 = (
    '      {"@type":"ListItem","position":13,"name":"BoldSign",'
    '"url":"https://coshuma.com/tool/boldsign.html"}\n'
    "    ]"
)
item14 = (
    '      {"@type":"ListItem","position":13,"name":"BoldSign",'
    '"url":"https://coshuma.com/tool/boldsign.html"},\n'
    '      {"@type":"ListItem","position":14,"name":"Teachable",'
    '"url":"https://coshuma.com/best/teachable-30-day-free-trial.html"}\n'
    "    ]"
)
if item13 not in html:
    raise SystemExit("BoldSign ItemList tail missing; Teachable patch requires the verified BoldSign build step first")
html = html.replace(item13, item14, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Teachable patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-emerald-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-emerald-300">Courses & digital products</div><h2 class="mt-1 text-3xl font-black text-white">Teachable</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Vendor-issued 30-day trial</span></div>\n        <p class="text-sm leading-6 text-slate-300">Teachable's public pricing page currently advertises a <strong class="text-white">7-day free trial</strong>. Separately, Teachable affiliate manager Camila Gouveia supplied COSHUMA the exact PartnerStack URL below and explicitly identified it as COSHUMA's <strong class="text-white">30-day Free Trial</strong> route. COSHUMA does not guess or construct longer-trial parameters.</p>\n        <p class="text-sm leading-6 text-slate-300">Teachable's current official affiliate program states <strong class="text-white">30% recurring commission for the first year</strong> on eligible referred subscriptions and a <strong class="text-white">30-day cookie window</strong>. Confirm the 30-day trial wording shown at the destination before completing signup because vendor offers can change.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="teachable" data-cta-source="verified-deals-teachable-30day-trial" data-cta-page="verified-software-free-trials-deals" href="{TRIAL_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-emerald-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-emerald-500">Open verified Teachable 30-day trial →</a><a href="/best/teachable-30-day-free-trial.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Teachable trial & pricing</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button uses the exact customer-facing extended-trial URL Teachable supplied to COSHUMA. The separate default tracking URL remains valid elsewhere, but no click, trial, signup, paid customer, commission, payout or revenue is counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRIAL_URL,
    DEFAULT_TRACKING_URL if DEFAULT_TRACKING_URL in html else TRIAL_URL,
    'data-cta-source="verified-deals-teachable-30day-trial"',
    "Vendor-issued 30-day trial",
    "30% recurring commission for the first year",
    "30-day cookie window",
    "no click, trial, signup, paid customer, commission, payout or revenue is counted",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Teachable buyer-hub patch lost required token: {token}")
if any(url in html for url in ADMIN_URLS):
    raise SystemExit("Teachable/PartnerStack admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Teachable 30-day trial on buyer hub")
