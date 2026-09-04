from pathlib import Path
import re

PROJECT_DIR = Path(__file__).resolve().parents[1]
PUBLIC_DIR = PROJECT_DIR / "public"
PICTORY_AFFILIATE_URL = "https://pictory.ai?fpr=sangkwon-an23"
MARKER = 'data-pictory-promo="coshuma20"'

PROMO = r'''
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
  <p class="mt-2 text-[11px] leading-5 text-amber-100/60">Offer details verified September 5, 2026. Promotions can change, so confirm the final price and eligibility at checkout.</p>
</section>
'''.strip()

updated = []
for path in sorted(PUBLIC_DIR.rglob("*.html")):
    text = path.read_text(encoding="utf-8")
    if PICTORY_AFFILIATE_URL not in text or MARKER in text:
        continue

    new_text, count = re.subn(r"(<main\b[^>]*>)", r"\1\n" + PROMO, text, count=1, flags=re.IGNORECASE)
    if count != 1:
        raise RuntimeError(f"Could not find a single <main> insertion point in {path}")

    path.write_text(new_text, encoding="utf-8")
    updated.append(path.relative_to(PROJECT_DIR).as_posix())

if not updated:
    raise RuntimeError("No Pictory affiliate pages were updated; expected at least one monetized page.")

print(f"Injected Pictory partner offer into {len(updated)} pages")
for item in updated:
    print(f" - {item}")
