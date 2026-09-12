from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_BOLDSIGN_VERIFIED_OFFER -->"
TRACKING_URL = "https://boldsign.com?via=sangkwon"
ADMIN_URL = "https://affiliates.boldsign.com/login"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Vendor support confirmed on 2026-09-11 that this existing referral entry URL
# should continue to be used; pricing/trial attribution persists via cookies when
# the visitor stays in the same browser. Do not manufacture a deep link.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("BoldSign verified block exists but exact referral URL is missing")
    if ADMIN_URL in html:
        raise SystemExit("BoldSign affiliate dashboard URL leaked into the public buyer hub")
    print("BoldSign verified buyer offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI and RGE Studio. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio and BoldSign. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind BoldSign patch")
html = html.replace(old_meta, new_meta, 1)

item12 = (
    '      {"@type":"ListItem","position":12,"name":"RGE Studio (formerly Beefree)",'
    '"url":"https://coshuma.com/tool/beefree.html"}\n'
    "    ]"
)
item13 = (
    '      {"@type":"ListItem","position":12,"name":"RGE Studio (formerly Beefree)",'
    '"url":"https://coshuma.com/tool/beefree.html"},\n'
    '      {"@type":"ListItem","position":13,"name":"BoldSign",'
    '"url":"https://coshuma.com/tool/boldsign.html"}\n'
    "    ]"
)
if item12 not in html:
    raise SystemExit("RGE Studio ItemList tail missing; BoldSign patch requires the verified Beefree build step first")
html = html.replace(item12, item13, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind BoldSign patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-blue-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-blue-300">eSignature & document workflows</div><h2 class="mt-1 text-3xl font-black text-white">BoldSign</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">30-day trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">BoldSign's current official site advertises a <strong class="text-white">30-day free trial with no credit card required</strong>. Its affiliate program currently states <strong class="text-white">30% commission for the first 12 months</strong> on eligible paid referrals, a <strong class="text-white">90-day cookie window</strong>, and no minimum payout threshold.</p>\n        <p class="text-sm leading-6 text-slate-300">BoldSign support directly confirmed to COSHUMA on September 11, 2026 that a separate pricing or trial affiliate deep link is not required. Visitors should enter through the exact existing referral URL below and stay in the same browser while navigating to pricing or the trial so cookie attribution can remain intact.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="boldsign" data-cta-source="verified-deals-boldsign-issued-referral" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-blue-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-blue-500">Open BoldSign via verified referral →</a><a href="/tool/boldsign.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare BoldSign plans</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">Do not switch browser/device, use private browsing, or clear cookies before signup/purchase if you want the existing referral attribution preserved. A click, trial, signup, paid customer, commission or payout is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    'data-cta-source="verified-deals-boldsign-issued-referral"',
    "30-day free trial with no credit card required",
    "30% commission for the first 12 months",
    "90-day cookie window",
    "separate pricing or trial affiliate deep link is not required",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"BoldSign buyer-hub patch lost required token: {token}")
if ADMIN_URL in html:
    raise SystemExit("BoldSign affiliate dashboard URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified BoldSign referral route on buyer hub")
