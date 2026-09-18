from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_FRASE_OFFER_CARD -->"
LEGACY_MARKER = "<!-- COSHUMA_FRASE_VERIFIED_OFFER -->"
TRACKING_URL = "https://www.frase.io/?utm_source=firstpromoter&utm_medium=affiliate&utm_campaign=affiliate_program&via=sangkwon12"
GUIDE_URL = "/tool/frase.html"

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")
html = html.replace(LEGACY_MARKER, MARKER)

if MARKER in html:
    required = [TRACKING_URL, 'data-cta-source="current-offers-frase-trial"', GUIDE_URL]
    for token in required:
        if token not in html:
            raise SystemExit(f"Frase buyer-hub card exists but required token is missing: {token}")
    if "Affiliate disclosure:" not in html and 'data-affiliate-disclosure=' not in html:
        raise SystemExit("Frase offer card is missing the required customer-facing affiliate disclosure")
    PAGE.write_text(html, encoding="utf-8")
    print("Frase 7-day trial already surfaced with customer-only copy")
    raise SystemExit(0)

card = f'''      {MARKER}
      <article class="rounded-3xl border border-violet-400/25 bg-[#11131a] p-7 space-y-5">
        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-violet-300">SEO & GEO content workflow</div><h2 class="mt-1 text-3xl font-black text-white">Frase</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">7-day trial · no card</span></div>
        <p class="text-sm leading-6 text-slate-300">Frase's current pricing page offers a <strong class="text-white">7-day free trial with no credit card required</strong>. Starter currently begins at <strong class="text-white">$39/month billed yearly</strong> or $49 month to month. Use the trial to test research, drafting, SEO/GEO scoring and AI-visibility workflows on real content before choosing a paid plan.</p>
        <p data-affiliate-disclosure="true" class="text-[11px] leading-relaxed text-slate-500"><strong>Affiliate disclosure:</strong> COSHUMA may earn a commission if you purchase through this link, at no extra cost to you.</p>
        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="frase" data-cta-source="current-offers-frase-trial" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-violet-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-violet-500">Start Frase 7-day trial →</a><a href="{GUIDE_URL}" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Frase plans</a></div>
      </article>
'''

closing = re.search(
    r'(<section class="rounded-3xl border border-white/10 bg=\[#11131a\] p-7 md:p-9">\s*<h2 class="text-2xl font-black text-white">How this list is selected</h2>)',
    html,
)
if closing:
    html = html[:closing.start()] + card + html[closing.start():]
elif "</main>" in html:
    html = html.replace("</main>", card + "</main>", 1)
else:
    raise SystemExit("Buyer-hub main boundary missing; cannot safely place Frase offer")

required = [
    TRACKING_URL,
    'data-cta-source="current-offers-frase-trial"',
    "7-day free trial with no credit card required",
    "$39/month billed yearly",
    "Affiliate disclosure:",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Frase buyer-hub patch lost required token: {token}")

visible = html.replace(TRACKING_URL, "")
for forbidden in (
    "FirstPromoter",
    "affiliate_verified",
    "approved_tracking",
    "exact existing",
    "partner-side evidence",
    "not counted as a signup, paid customer, commission, payout or revenue",
):
    if forbidden.lower() in visible.lower():
        raise SystemExit(f"Frase buyer-hub customer copy still contains internal wording: {forbidden}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced Frase 7-day trial with customer-only disclosure")
