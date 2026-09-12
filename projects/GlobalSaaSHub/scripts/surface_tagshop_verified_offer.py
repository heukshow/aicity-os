from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TAGSHOP_VERIFIED_OFFER -->"
TRACKING_URL = "https://tagshop.ai?via=coshuma-22501e"
ADMIN_URL = "https://tagshop.firstpromoter.com/login"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Idempotence + attribution safety: the vendor confirmed that this exact issued
# entry URL tracks referrals/conversions site-wide. Do not invent pricing/trial
# deep links by moving the via parameter onto arbitrary Tagshop URLs.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Tagshop verified block exists but exact issued referral URL is missing")
    if ADMIN_URL in html:
        raise SystemExit("Tagshop admin dashboard URL leaked into the public buyer hub")
    print("Tagshop verified buyer offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally and Typedesk. "
    "COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk and "
    "Tagshop AI. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Tagshop patch")
html = html.replace(old_meta, new_meta, 1)

item10 = (
    '      {"@type":"ListItem","position":10,"name":"Typedesk",'
    '"url":"https://coshuma.com/best/typedesk-pricing-free-plan.html"}\n'
    "    ]"
)
item11 = (
    '      {"@type":"ListItem","position":10,"name":"Typedesk",'
    '"url":"https://coshuma.com/best/typedesk-pricing-free-plan.html"},\n'
    '      {"@type":"ListItem","position":11,"name":"Tagshop AI",'
    '"url":"https://coshuma.com/best/tagshop-ai-free-trial-pricing.html"}\n'
    "    ]"
)
if item10 not in html:
    raise SystemExit("Typedesk ItemList tail missing; Tagshop patch requires the verified Typedesk build step first")
html = html.replace(item10, item11, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Tagshop patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-fuchsia-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-fuchsia-300">AI UGC video ads</div><h2 class="mt-1 text-3xl font-black text-white">Tagshop AI</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">14-day trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">Tagshop's current official help center lists a <strong class="text-white">14-day free trial with full platform access and no credit card required</strong>. Tagshop also directly confirmed to COSHUMA on September 12, 2026 that the exact issued referral URL below automatically tracks referrals and conversions across the site.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="tagshop-ai" data-cta-source="verified-deals-tagshop-issued-referral" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-fuchsia-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-fuchsia-500">Start Tagshop trial via verified referral →</a><a href="/best/tagshop-ai-free-trial-pricing.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Read trial & pricing guide</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">COSHUMA uses only Tagshop's exact issued referral entry URL; no separate pricing/trial affiliate deep link has been issued or inferred. A click, referred signup, paying customer, commission or payout is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    'data-cta-source="verified-deals-tagshop-issued-referral"',
    "14-day free trial with full platform access and no credit card required",
    "no separate pricing/trial affiliate deep link has been issued or inferred",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Tagshop buyer-hub patch lost required token: {token}")
if ADMIN_URL in html:
    raise SystemExit("Tagshop admin dashboard URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Tagshop referral route on buyer hub")
