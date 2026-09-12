from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TYPEDESK_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.typedesk.com/pricing?via=sangkwon"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Idempotence + attribution safety: this buyer-hub card may only use the exact
# vendor-confirmed Typedesk pricing deep link that preserves via=sangkwon.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Typedesk verified block exists but exact tracking URL is missing")
    print("Typedesk verified buyer offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata and Tally. COSHUMA "
    "separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally and Typedesk. "
    "COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind patch")
html = html.replace(old_meta, new_meta, 1)

item9 = (
    '      {"@type":"ListItem","position":9,"name":"Tally",'
    '"url":"https://coshuma.com/tool/tally.html"}\n'
    "    ]"
)
item10 = (
    '      {"@type":"ListItem","position":9,"name":"Tally",'
    '"url":"https://coshuma.com/tool/tally.html"},\n'
    '      {"@type":"ListItem","position":10,"name":"Typedesk",'
    '"url":"https://coshuma.com/best/typedesk-pricing-free-plan.html"}\n'
    "    ]"
)
if item9 not in html:
    raise SystemExit("Tally ItemList tail missing; Typedesk patch requires the verified Tally build step first")
html = html.replace(item9, item10, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-indigo-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-indigo-300">Text expansion & support workflows</div><h2 class="mt-1 text-3xl font-black text-white">Typedesk</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free forever plan</span></div>\n        <p class="text-sm leading-6 text-slate-300">Typedesk's current official pricing page lists a Free plan for personal use with unlimited templates and up to 50 uses per week. The affiliate team also confirmed that COSHUMA may preserve its issued <code class="text-indigo-200">via=sangkwon</code> attribution on the pricing page, so the buyer-intent destination below is not a guessed deep link.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="typedesk" data-cta-source="verified-deals-typedesk-pricing" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-indigo-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-indigo-500">Check Typedesk plans →</a><a href="/best/typedesk-pricing-free-plan.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare free vs paid</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">Typedesk told COSHUMA it currently provides no affiliate coupon code. COSHUMA therefore makes no coupon or discount claim here. A visit, signup, upgrade, commission or payout is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    'data-cta-source="verified-deals-typedesk-pricing"',
    "Free plan for personal use",
    "no affiliate coupon code",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Typedesk buyer-hub patch lost required token: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Typedesk pricing route on buyer hub")
