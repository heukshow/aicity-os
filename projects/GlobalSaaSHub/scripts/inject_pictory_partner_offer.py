from pathlib import Path
import re
import runpy

PROJECT_DIR = Path(__file__).resolve().parents[1]
PUBLIC_DIR = PROJECT_DIR / "public"
PICTORY_AFFILIATE_URL = "https://pictory.ai?fpr=sangkwon-an23"
MARKER = 'data-pictory-promo="coshuma20"'
PROMO_CTA_SOURCE = "pictory-promo-banner"
EXCLUDED_PATHS = {"best/pictory-discount-code.html"}
INVIDEO_DISCOVERY_MARKER = 'data-invideo-discovery="pictory-comparison"'

PROMO = rf'''
<section data-pictory-promo="coshuma20" class="mx-auto mb-6 max-w-4xl rounded-2xl border border-amber-400/25 bg-amber-400/[0.07] p-4 sm:p-5">
  <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
    <div>
      <div class="text-xs font-black uppercase tracking-[0.16em] text-amber-300">Current Pictory partner offer</div>
      <p class="mt-1 text-sm leading-6 text-amber-50/90"><strong>Use code COSHUMA20 for 20% off.</strong> Pictory currently advertises annual plans at up to 40% off, and Pictory's affiliate manager confirmed that combining the annual promotion with this code can produce savings of more than 52%.</p>
    </div>
    <div class="shrink-0 rounded-xl border border-amber-300/20 bg-black/20 px-4 py-2 text-center">
      <div class="text-[10px] uppercase tracking-widest text-amber-200/70">Promo code</div>
      <div class="text-lg font-black tracking-wider text-white">COSHUMA20</div>
    </div>
  </div>
  <div class="mt-4 flex flex-col gap-2 sm:flex-row">
    <a data-cta="affiliate" data-tool-id="pictory" data-cta-source="{PROMO_CTA_SOURCE}" href="{PICTORY_AFFILIATE_URL}" target="_blank" rel="sponsored noopener noreferrer" class="inline-flex flex-1 items-center justify-center rounded-xl bg-amber-300 px-5 py-3 text-sm font-black text-slate-950 transition hover:bg-amber-200">Use COSHUMA20 at Pictory →</a>
    <a href="/best/pictory-discount-code.html" class="inline-flex flex-1 items-center justify-center rounded-xl border border-amber-300/20 bg-black/20 px-5 py-3 text-sm font-bold text-amber-50 transition hover:border-amber-200/40 hover:bg-black/30">See discount details →</a>
  </div>
  <p class="mt-2 text-[11px] leading-5 text-amber-100/60">Offer details verified September 5, 2026. Promotions can change, so confirm the final price and eligibility at checkout.</p>
</section>
'''.strip()

INVIDEO_DISCOVERY = '''
<section data-invideo-discovery="pictory-comparison" class="mt-8 rounded-2xl border border-violet-400/20 bg-violet-500/[0.06] p-5 sm:p-6">
  <div class="text-xs font-black uppercase tracking-[0.16em] text-violet-300">New buyer comparison</div>
  <h2 class="mt-2 text-2xl font-black text-white">Pictory vs InVideo AI: compare the workflow before paying</h2>
  <p class="mt-2 text-sm leading-6 text-slate-300">InVideo AI is now included as a free-first prompt-to-video alternative. Compare its credit-based model with Pictory's 14-day trial and plan allowances, then use the same script in both tools before choosing.</p>
  <div class="mt-4 flex flex-col gap-2 sm:flex-row">
    <a href="/compare/pictory-vs-invideo-ai.html" class="inline-flex flex-1 items-center justify-center rounded-xl bg-violet-600 px-5 py-3 text-sm font-black text-white hover:bg-violet-500">Compare Pictory vs InVideo AI →</a>
    <a href="/tool/invideo-ai.html" class="inline-flex flex-1 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] px-5 py-3 text-sm font-bold text-slate-200 hover:bg-white/[0.06]">Read InVideo AI guide →</a>
  </div>
</section>
'''.strip()

updated = []
for path in sorted(PUBLIC_DIR.rglob("*.html")):
    relative_path = path.relative_to(PUBLIC_DIR).as_posix()
    if relative_path in EXCLUDED_PATHS:
        continue

    text = path.read_text(encoding="utf-8")
    if PICTORY_AFFILIATE_URL not in text or MARKER in text:
        continue

    new_text, count = re.subn(r"(<main\b[^>]*>)", r"\1\n" + PROMO, text, count=1, flags=re.IGNORECASE)
    if count != 1:
        raise RuntimeError(f"Could not find a single <main> insertion point in {path}")
    if PICTORY_AFFILIATE_URL not in new_text or f'data-cta-source="{PROMO_CTA_SOURCE}"' not in new_text:
        raise RuntimeError(f"Pictory promo CTA postcondition failed for {path}")

    path.write_text(new_text, encoding="utf-8")
    updated.append(path.relative_to(PROJECT_DIR).as_posix())

if not updated:
    raise RuntimeError("No Pictory affiliate pages were updated; expected at least one monetized page.")

hub = PUBLIC_DIR / "best" / "ai-video-generators.html"
hub_text = hub.read_text(encoding="utf-8")
if INVIDEO_DISCOVERY_MARKER not in hub_text:
    if "</main>" not in hub_text:
        raise RuntimeError("AI video buyer hub is missing </main>; refusing to inject InVideo discovery links.")
    hub_text = hub_text.replace("</main>", INVIDEO_DISCOVERY + "\n</main>", 1)
    hub.write_text(hub_text, encoding="utf-8")
    print("Surfaced Pictory vs InVideo AI comparison from AI video buyer hub")
else:
    print("Pictory vs InVideo AI discovery links already present on AI video buyer hub")

print(f"Injected Pictory partner offer into {len(updated)} pages")
for item in updated:
    print(f" - {item}")

runpy.run_path(str(Path(__file__).with_name("inject_jotform_partner_offer.py")), run_name="__main__")
