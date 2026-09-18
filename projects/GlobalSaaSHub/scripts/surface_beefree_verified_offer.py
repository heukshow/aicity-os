from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_BEEFREE_VERIFIED_OFFER -->"
TRACKING_URL = "https://partners.beefree.io/kqi520hezix2"
ADMIN_HOST = "partnerstack.com"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Keep the exact customer route, but never expose account, dashboard, approval,
# verification, or revenue-state details in public copy.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("RGE Studio buyer block exists but exact customer route is missing")
    if ADMIN_HOST in html.lower():
        raise SystemExit("RGE Studio admin host leaked into the public buyer hub")
    print("RGE Studio buyer offer already surfaced")
    raise SystemExit(0)

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
if item11 in html:
    html = html.replace(item11, item12, 1)
elif '"name":"RGE Studio (formerly Beefree)"' not in html:
    print("Buyer-hub ItemList layout changed; skipping optional RGE Studio structured-list insertion")

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-lime-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-lime-300">Email design & collaboration</div><h2 class="mt-1 text-3xl font-black text-white">RGE Studio <span class="text-base font-semibold text-slate-400">(formerly Beefree)</span></h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">15-day trial</span></div>\n        <p class="text-sm leading-6 text-slate-300">RGE Studio's current pricing lists <strong class="text-white">Starter $0</strong>, <strong class="text-white">Professional $30/month or $25/month billed yearly</strong>, <strong class="text-white">Business $160/month or $134/month billed yearly</strong>, and Enterprise at custom pricing. Its pricing page also offers a <strong class="text-white">15-day free trial</strong>. Check the current terms before upgrading.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="beefree" data-cta-source="buyer-hub-rge-studio" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-lime-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-lime-500">Try RGE Studio →</a><a href="/tool/beefree.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare RGE Studio plans</a></div>\n      </article>\n'''

if closing in html:
    html = html.replace(closing, card + closing, 1)
elif "</main>" in html:
    print("Buyer-hub final grid boundary changed; using current main boundary for RGE Studio card")
    html = html.replace("</main>", card + "</main>", 1)
else:
    raise SystemExit("Buyer-hub main boundary missing; cannot safely place RGE Studio customer offer")

required = [
    TRACKING_URL,
    'data-cta-source="buyer-hub-rge-studio"',
    "15-day free trial",
    "Professional $30/month or $25/month billed yearly",
]
for token in required:
    if token not in html:
        raise SystemExit(f"RGE Studio buyer-hub patch lost required token: {token}")

forbidden_public = (
    ADMIN_HOST,
    "PartnerStack",
    "approved partner",
    "existing Beefree Ambassador account",
    "partner-side evidence",
    "revenue truth",
    "verification mechanism",
)
for token in forbidden_public:
    if token.lower() in card.lower():
        raise SystemExit(f"RGE Studio public card contains internal-only copy: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced RGE Studio trial offer with customer-only copy")
