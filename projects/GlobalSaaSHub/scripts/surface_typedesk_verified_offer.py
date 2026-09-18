from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TYPEDESK_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.typedesk.com/pricing?via=sangkwon"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Idempotence + attribution safety: keep only the exact customer-facing pricing
# route. Internal approval, verification and partner correspondence never belong
# in the generated public card.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Typedesk buyer block exists but exact customer route is missing")
    print("Typedesk buyer offer already surfaced")
    raise SystemExit(0)

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
if item9 in html:
    html = html.replace(item9, item10, 1)
elif '"name":"Typedesk"' not in html:
    print("Buyer-hub ItemList layout changed; skipping optional Typedesk structured-list insertion")

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-indigo-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-indigo-300">Text expansion & support workflows</div><h2 class="mt-1 text-3xl font-black text-white">Typedesk</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free plan available</span></div>\n        <p class="text-sm leading-6 text-slate-300">Typedesk's current pricing page lists a Free plan for personal use with unlimited templates and up to 50 uses per week. Check the current plan limits and pricing on Typedesk before choosing.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="typedesk" data-cta-source="verified-deals-typedesk-pricing" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-indigo-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-indigo-500">Check Typedesk plans →</a><a href="/best/typedesk-pricing-free-plan.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare free vs paid</a></div>\n      </article>\n'''

if closing in html:
    html = html.replace(closing, card + closing, 1)
elif "</main>" in html:
    print("Buyer-hub final grid boundary changed; using current main boundary for Typedesk card")
    html = html.replace("</main>", card + "</main>", 1)
else:
    raise SystemExit("Buyer-hub main boundary missing; cannot safely place Typedesk customer offer")

required = [
    TRACKING_URL,
    'data-cta-source="verified-deals-typedesk-pricing"',
    "Free plan for personal use",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Typedesk buyer-hub patch lost required token: {token}")

for forbidden in (
    "affiliate team",
    "partner-side evidence",
    "not a guessed deep link",
    "affiliate coupon code",
):
    if forbidden.lower() in card.lower():
        raise SystemExit(f"Typedesk public card contains internal affiliate operations copy: {forbidden}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced Typedesk pricing route with customer-only copy")
