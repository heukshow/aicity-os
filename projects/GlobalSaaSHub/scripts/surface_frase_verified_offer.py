from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_FRASE_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.frase.io/?utm_source=firstpromoter&utm_medium=affiliate&utm_campaign=affiliate_program&via=sangkwon12"
GUIDE_URL = "/tool/frase.html"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# This exact FirstPromoter customer route is already stored as affiliate_verified=true /
# approved_tracking for Frase. Never manufacture a pricing or trial deep link from it.
if MARKER in html:
    required = [TRACKING_URL, 'data-cta-source="verified-deals-frase-trial"', GUIDE_URL]
    for token in required:
        if token not in html:
            raise SystemExit(f"Frase buyer-hub block exists but required token is missing: {token}")
    print("Frase verified trial already surfaced")
else:
    closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
    if closing not in html:
        raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Frase patch")

    card = f'''      {MARKER}\n      <article class="rounded-3xl border border-violet-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-violet-300">SEO & GEO content workflow</div><h2 class="mt-1 text-3xl font-black text-white">Frase</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">7-day trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">Frase's current official pricing page offers a <strong class="text-white">7-day free trial with no credit card required</strong>. Starter currently begins at <strong class="text-white">$39/month billed yearly</strong> or $49 month to month. Use the trial to test research, drafting, SEO/GEO scoring and AI-visibility workflows on real content before choosing a paid plan.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="frase" data-cta-source="verified-deals-frase-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-violet-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-violet-500">Start Frase 7-day trial →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Frase plans</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button keeps COSHUMA's exact existing FirstPromoter customer route. COSHUMA does not guess a trial or pricing deep link. A click or trial is not counted as a signup, paid customer, commission, payout or revenue without partner-side evidence.</p>\n      </article>\n'''

    html = html.replace(closing, card + closing, 1)

    required = [
        TRACKING_URL,
        'data-cta-source="verified-deals-frase-trial"',
        "7-day free trial with no credit card required",
        "$39/month billed yearly",
        "does not guess a trial or pricing deep link",
        "not counted as a signup, paid customer, commission, payout or revenue",
    ]
    for token in required:
        if token not in html:
            raise SystemExit(f"Frase buyer-hub patch lost required token: {token}")

    PAGE.write_text(html, encoding="utf-8")
    print("Surfaced verified Frase 7-day trial on buyer hub")
