from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TALLY_REFERRAL_OFFER -->"
REFERRAL_URL = "https://tally.cello.so/ub0qUbuKk2f"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Idempotence + safety: if the block already exists, only accept the exact
# vendor-issued Cello/Tally customer route. Never rewrite it to a guessed URL.
if MARKER in html:
    if REFERRAL_URL not in html:
        raise SystemExit("Tally referral block exists but exact verified URL is missing")
    print("Tally verified referral offer already surfaced")
else:
    old_meta = (
        "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
        "UpLead, Jotform, Unbounce, Pictory, Brand24 and Bookyourdata. COSHUMA separates "
        "customer-facing tracking links from product claims."
    )
    new_meta = (
        "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
        "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata and Tally. COSHUMA "
        "separates customer-facing tracking links from product claims."
    )
    if old_meta not in html:
        raise SystemExit("Buyer-hub meta description changed; refusing blind patch")
    html = html.replace(old_meta, new_meta, 1)

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
    if item8 not in html:
        raise SystemExit("Buyer-hub ItemList tail changed; refusing blind patch")
    html = html.replace(item8, item9, 1)

    html = html.replace("Checked September 11, 2026", "Checked September 12, 2026", 1)

    closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
    if closing not in html:
        raise SystemExit("Buyer-hub final grid boundary changed; refusing blind patch")

    card = f'''      {MARKER}\n      <article class="rounded-3xl border border-sky-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-sky-300">Forms & surveys</div><h2 class="mt-1 text-3xl font-black text-white">Tally</h2></div><span class="rounded-full bg-sky-400/10 px-3 py-1 text-xs font-bold text-sky-200">Verified referral benefit</span></div>\n        <p class="text-sm leading-6 text-slate-300">Tally's current referral program says new users who sign up through a referral link and later become paying customers receive <strong class="text-white">50% off their subscription for 3 months</strong>. This is a referral benefit, not a public sale. COSHUMA uses only the exact personal invite URL issued through Tally's Cello-powered referral system.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="tally" data-cta-source="verified-deals-tally-referral" data-cta-page="verified-software-free-trials-deals" href="{REFERRAL_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-sky-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-sky-500">Start Tally via verified referral →</a><a href="/tool/tally.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Read Tally guide</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">Tally prohibits self-referrals and paid ads using the referral link. COSHUMA may earn 20% of eligible subscription payments, up to $150 per referred paid user. A link view is not treated as a signup, paid customer, commission or revenue event.</p>\n      </article>\n'''

    html = html.replace(closing, card + closing, 1)

    # Final hard guards: the exact URL and disclosure semantics must survive.
    required = [
        REFERRAL_URL,
        'data-cta-source="verified-deals-tally-referral"',
        "50% off their subscription for 3 months",
        "not a public sale",
        "A link view is not treated as a signup",
    ]
    for token in required:
        if token not in html:
            raise SystemExit(f"Tally buyer-hub patch lost required token: {token}")

    PAGE.write_text(html, encoding="utf-8")
    print("Surfaced verified Tally referral offer on buyer hub")

# Typedesk extends the generated ItemList from position 9 to 10. On repeated
# builds its idempotence guard exits with code 0, so catch only that normal stop
# and continue to later verified-offer steps. Any non-zero safety failure aborts.
try:
    runpy.run_path(str(ROOT / "scripts" / "surface_typedesk_verified_offer.py"), run_name="__main__")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise

# Tagshop runs after Typedesk because it extends the generated ItemList from 10
# to 11 and must see the exact verified Typedesk state first.
try:
    runpy.run_path(str(ROOT / "scripts" / "surface_tagshop_verified_offer.py"), run_name="__main__")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise

# RGE Studio / Beefree runs last because it extends the generated ItemList from
# 11 to 12 and uses only the exact referral URL issued to COSHUMA's existing
# Beefree Ambassador account.
runpy.run_path(str(ROOT / "scripts" / "surface_beefree_verified_offer.py"), run_name="__main__")
