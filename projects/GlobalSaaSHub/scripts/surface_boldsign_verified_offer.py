from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_BOLDSIGN_VERIFIED_OFFER -->"
TRACKING_URL = "https://boldsign.com?via=sangkwon"
ADMIN_URL = "https://affiliates.boldsign.com/login"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Keep the exact customer route, but never expose account, dashboard, approval,
# verification, cookie-attribution, or revenue-state details in public copy.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("BoldSign buyer block exists but exact customer route is missing")
    if ADMIN_URL in html:
        raise SystemExit("BoldSign affiliate dashboard URL leaked into the public buyer hub")
    print("BoldSign buyer offer already surfaced")
    raise SystemExit(0)

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
if item12 in html:
    html = html.replace(item12, item13, 1)
elif '"name":"BoldSign"' not in html:
    print("Buyer-hub ItemList layout changed; skipping optional BoldSign structured-list insertion")

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-blue-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-blue-300">eSignature & document workflows</div><h2 class="mt-1 text-3xl font-black text-white">BoldSign</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">30-day trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">BoldSign's current official site advertises a <strong class="text-white">30-day free trial with no credit card required</strong>. Use the trial to test the signing and document workflow you actually need, then confirm the current plan and billing terms before upgrading.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="boldsign" data-cta-source="buyer-hub-boldsign" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-blue-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-blue-500">Try BoldSign →</a><a href="/tool/boldsign.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare BoldSign plans</a></div>\n      </article>\n'''

if closing in html:
    html = html.replace(closing, card + closing, 1)
elif "</main>" in html:
    print("Buyer-hub final grid boundary changed; using current main boundary for BoldSign card")
    html = html.replace("</main>", card + "</main>", 1)
else:
    raise SystemExit("Buyer-hub main boundary missing; cannot safely place BoldSign customer offer")

required = [
    TRACKING_URL,
    'data-cta-source="buyer-hub-boldsign"',
    "30-day free trial with no credit card required",
]
for token in required:
    if token not in html:
        raise SystemExit(f"BoldSign buyer-hub patch lost required token: {token}")
if ADMIN_URL in html:
    raise SystemExit("BoldSign affiliate dashboard URL leaked into the public buyer hub")

forbidden_public = (
    "PartnerStack",
    "approved partner",
    "affiliate program",
    "cookie window",
    "partner-side evidence",
    "revenue truth",
    "verification mechanism",
)
for token in forbidden_public:
    if token.lower() in card.lower():
        raise SystemExit(f"BoldSign public card contains internal-only copy: {token}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced BoldSign trial offer with customer-only copy")
