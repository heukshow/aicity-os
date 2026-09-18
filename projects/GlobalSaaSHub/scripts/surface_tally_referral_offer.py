from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TALLY_REFERRAL_OFFER -->"
REFERRAL_URL = "https://tally.cello.so/ub0qUbuKk2f"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Idempotence + safety: if the block already exists, only accept the exact
# vendor-issued customer URL. Never rewrite it to a guessed URL.
if MARKER in html:
    if REFERRAL_URL not in html:
        raise SystemExit("Tally referral block exists but exact verified URL is missing")
    print("Tally customer offer already surfaced")
else:
    item8 = (
        '      {"@type":"ListItem","position":8,"name":"Brand24",'
        '"url":"https://coshuma.com/best/brand24-free-trial.html"}\n'
        "    ]"
    )
    item9 = (
        '      {"@type":"ListItem","position":8,"name":"Brand24",'
        '"url":"https://coshuma.com/best/brand24-free-trial.html"},\n'
        '      {"@type":"ListItem","position":9,"name":"Tally",'
        '"url":"https://coshuma.com/tool/tally.html"}\n'
        "    ]"
    )
    if item8 in html:
        html = html.replace(item8, item9, 1)
    elif '"name":"Tally"' not in html:
        print("Buyer-hub ItemList layout changed; skipping optional Tally structured-list insertion")

    html = html.replace("Checked September 11, 2026", "Checked September 12, 2026", 1)

    closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
    if closing not in html:
        print("Buyer-hub final grid boundary changed; using current main boundary for Tally card")

    card = f'''      {MARKER}\n      <article class="rounded-3xl border border-sky-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-sky-300">Forms & surveys</div><h2 class="mt-1 text-3xl font-black text-white">Tally</h2></div><span class="rounded-full bg-sky-400/10 px-3 py-1 text-xs font-bold text-sky-200">50% referral benefit</span></div>\n        <p class="text-sm leading-6 text-slate-300">Eligible new users who sign up through this Tally invitation and later become paying customers can receive <strong class="text-white">50% off their subscription for 3 months</strong>. This is a referral benefit, not a public sale. Confirm the final discount and billing terms on Tally before paying.</p>\n        <p data-affiliate-disclosure="true" class="text-[11px] leading-relaxed text-slate-500"><strong>Affiliate disclosure:</strong> COSHUMA may earn a commission if you purchase through this link, at no extra cost to you.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="tally" data-cta-source="verified-deals-tally-referral" data-cta-page="verified-software-free-trials-deals" href="{REFERRAL_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-sky-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-sky-500">Start Tally with referral benefit →</a><a href="/tool/tally.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Read Tally guide</a></div>\n      </article>\n'''

    if closing in html:
        html = html.replace(closing, card + closing, 1)
    elif "</main>" in html:
        html = html.replace("</main>", card + "</main>", 1)
    else:
        raise SystemExit("Buyer-hub main boundary missing; cannot safely place Tally customer offer")

    required = [
        REFERRAL_URL,
        'data-cta-source="verified-deals-tally-referral"',
        "50% off their subscription for 3 months",
        "not a public sale",
    ]
    for token in required:
        if token not in html:
            raise SystemExit(f"Tally buyer-hub patch lost required token: {token}")

    print("Surfaced Tally referral benefit with customer-facing affiliate disclosure")

if MARKER in html and "Affiliate disclosure:" not in html and 'data-affiliate-disclosure=' not in html:
    raise SystemExit("Tally buyer-hub affiliate CTA is missing required customer-facing disclosure")

HANDOFF_META = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk and "
    "Tagshop AI. COSHUMA separates customer-facing tracking links from product claims."
)
html = re.sub(
    r'(<meta\s+name="description"\s+content=")[^"]*("\s*/?>)',
    lambda m: m.group(1) + HANDOFF_META + m.group(2),
    html,
    count=1,
    flags=re.I,
)
PAGE.write_text(html, encoding="utf-8")

try:
    runpy.run_path(str(ROOT / "scripts" / "surface_typedesk_verified_offer.py"), run_name="__main__")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise

try:
    runpy.run_path(str(ROOT / "scripts" / "surface_tagshop_verified_offer.py"), run_name="__main__")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise

runpy.run_path(str(ROOT / "scripts" / "surface_beefree_verified_offer.py"), run_name="__main__")
runpy.run_path(str(ROOT / "scripts" / "surface_boldsign_verified_offer.py"), run_name="__main__")

try:
    runpy.run_path(str(ROOT / "scripts" / "surface_teachable_verified_offer.py"), run_name="__main__")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise

runpy.run_path(str(ROOT / "scripts" / "surface_frase_verified_offer.py"), run_name="__main__")
