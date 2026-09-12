from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_KITTL_VERIFIED_OFFER -->"
TRACKING_URL = "https://kittl.pxf.io/0GMrXY"
GUIDE_URL = "/best/kittl-commercial-use-license.html"
OFFICIAL_AFFILIATE = "https://www.kittl.com/partners/affiliates"
ADMIN_HOSTS = (
    "app.impact.com",
    "impact.com/login",
    "impact.com/dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Evidence guard:
# - Repository approved-tracking evidence records the exact customer-facing Impact
#   route above for COSHUMA's already-approved Kittl relationship.
# - Kittl first-party help/pricing pages rechecked 2026-09-12 say Free is free
#   forever, allows 5 active projects and 200 one-time AI tokens, and is limited to
#   personal use. Paid plans provide commercial licensing and stronger exports.
# - Kittl's first-party affiliate page says affiliates can earn up to $72 for a new
#   Expert subscriber and earn commission on payments during the first 12 months.
# - We do not manufacture a pricing deep link or reuse any Impact admin URL.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Kittl verified block exists but exact approved tracking URL is missing")
    if any(host in html for host in ADMIN_HOSTS):
        raise SystemExit("Kittl affiliate admin URL leaked into the public buyer hub")
    print("Kittl verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic and Moosend. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable, Murf AI, Claap, Writesonic, Moosend and Kittl. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Kittl patch")
html = html.replace(old_meta, new_meta, 1)

item18 = (
    '      {"@type":"ListItem","position":18,"name":"Moosend",'
    '"url":"https://coshuma.com/best/moosend-free-trial.html"}\n'
    "    ]"
)
item19 = (
    '      {"@type":"ListItem","position":18,"name":"Moosend",'
    '"url":"https://coshuma.com/best/moosend-free-trial.html"},\n'
    '      {"@type":"ListItem","position":19,"name":"Kittl",'
    '"url":"https://coshuma.com/best/kittl-commercial-use-license.html"}\n'
    "    ]"
)
if item18 not in html:
    raise SystemExit("Moosend ItemList tail missing; Kittl patch requires the verified Moosend build step first")
html = html.replace(item18, item19, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Kittl patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-emerald-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-emerald-300">AI design & commercial licensing</div><h2 class="mt-1 text-3xl font-black text-white">Kittl</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free forever</span></div>\n        <p class="text-sm leading-6 text-slate-300">Kittl's current Free plan has <strong class="text-white">no expiry</strong>, includes <strong class="text-white">5 active projects</strong> and <strong class="text-white">200 one-time AI tokens</strong>, and is designed for testing and personal projects. Kittl explicitly limits Free-plan designs to <strong class="text-white">personal use</strong>; use the licensing guide before client, POD or other commercial work.</p>\n        <p class="text-sm leading-6 text-slate-300">COSHUMA uses the exact customer-facing Impact route already verified for its existing Kittl affiliate account. Kittl's current affiliate page says partners can earn up to <strong class="text-white">$72</strong> for a new Expert subscriber and commission on payments during the first <strong class="text-white">12 months</strong>. Those are partner terms, not a buyer discount or a revenue claim.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="kittl" data-cta-source="verified-deals-kittl-approved-link" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-emerald-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-emerald-500">Try Kittl Free →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Check commercial-use license</a></div>\n        <a href="{OFFICIAL_AFFILIATE}" target="_blank" rel="noopener noreferrer" class="inline-block text-xs font-bold text-emerald-200 hover:text-white">Verify Kittl affiliate terms →</a>\n        <p class="text-[11px] leading-5 text-slate-500">The first button preserves the exact Kittl customer-facing Impact URL already verified for COSHUMA. COSHUMA does not guess a pricing deep link. A click, free account, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    GUIDE_URL,
    'data-cta-source="verified-deals-kittl-approved-link"',
    "Free plan has <strong class=\"text-white\">no expiry</strong>",
    "5 active projects",
    "200 one-time AI tokens",
    "personal use",
    "up to <strong class=\"text-white\">$72</strong>",
    "first <strong class=\"text-white\">12 months</strong>",
    "not a buyer discount or a revenue claim",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Kittl buyer-hub patch lost required token: {token}")
if any(host in html for host in ADMIN_HOSTS):
    raise SystemExit("Kittl affiliate admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Kittl free-plan route on buyer hub")
