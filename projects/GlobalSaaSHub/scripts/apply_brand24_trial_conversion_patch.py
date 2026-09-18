"""Add Brand24 trial specifics without exposing affiliate-operation details.

The insertion is anchored to the customer-visible Current pricing label rather than
an exact multiline HTML layout, so safe formatting/cleanup changes do not block the
build. The exact issued outbound URL and sponsored attribution are preserved.
"""
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "brand24.html"
MARKER = 'data-brand24-trial-proof="2026-09-09"'
TRACKING_URL = "https://try.brand24.com/8xqrjxybmsbt"
PRICING_LABEL = '<div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Current pricing</div>'

BLOCK = '''<section data-brand24-trial-proof="2026-09-09" class="rounded-3xl border border-emerald-500/25 bg-emerald-500/5 p-6 md:p-8 space-y-5">
  <div>
    <div class="text-xs uppercase tracking-widest text-emerald-300 font-bold">What the free trial actually includes</div>
    <h2 class="text-2xl md:text-3xl font-black text-white mt-1">Use Brand24's 14-day trial like a real buying test</h2>
    <p class="text-sm md:text-base text-slate-300 leading-relaxed">Brand24's current Help Center says the trial is based on the <strong class="text-white">Pro plan</strong>, lets you track up to <strong class="text-white">10 keywords</strong> and collect up to <strong class="text-white">30,000 mentions</strong>, with trial data refreshed every 24 hours. That is enough to test a real brand, competitor set and alert workflow before paying.</p>
  </div>
  <div class="grid md:grid-cols-3 gap-3 text-sm">
    <div class="rounded-2xl border border-emerald-500/15 bg-[#0d1018] p-4"><strong class="text-white">Day 1</strong><p class="mt-2 text-slate-400">Add your brand plus the competitors and topics you would genuinely monitor.</p></div>
    <div class="rounded-2xl border border-emerald-500/15 bg-[#0d1018] p-4"><strong class="text-white">During trial</strong><p class="mt-2 text-slate-400">Check mention relevance, sentiment, alert usefulness and whether the collected volume fits the paid tier you are considering.</p></div>
    <div class="rounded-2xl border border-emerald-500/15 bg-[#0d1018] p-4"><strong class="text-white">Before checkout</strong><p class="mt-2 text-slate-400">Brand24's pricing FAQ currently states a 30-day money-back guarantee after purchase, excluding custom plans and negotiated deals.</p></div>
  </div>
  <a data-cta="affiliate" data-tool-id="brand24" data-cta-source="brand24-trial-proof" href="https://try.brand24.com/8xqrjxybmsbt" target="_blank" rel="sponsored noopener noreferrer" class="block sm:inline-flex px-6 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-center">Start the 14-Day Brand24 Trial →</a>
</section>
'''

if TRACKING_URL not in BLOCK or 'rel="sponsored noopener noreferrer"' not in BLOCK:
    raise SystemExit("Brand24 trial block lost the exact customer offer URL or sponsored attribution")
for forbidden in (
    "verified partner",
    "verified affiliate",
    "tracking verification",
    "partner-side evidence",
    "affiliate evidence",
    "revenue-truth",
):
    if forbidden in BLOCK.lower():
        raise SystemExit(f"Brand24 trial block contains internal operations copy: {forbidden}")

text = PAGE.read_text(encoding="utf-8")
if MARKER in text:
    print("Brand24 trial conversion patch already present.")
    raise SystemExit(0)

label_pos = text.find(PRICING_LABEL)
if label_pos < 0:
    raise SystemExit("Refusing uncertain Brand24 patch: customer-visible Current pricing label missing")
section_pos = text.rfind("<section", 0, label_pos)
if section_pos < 0:
    raise SystemExit("Refusing uncertain Brand24 patch: pricing section boundary missing")

text = text[:section_pos] + BLOCK + text[section_pos:]
if TRACKING_URL not in text:
    raise SystemExit("Brand24 trial conversion patch failed: exact customer offer URL was lost")
PAGE.write_text(text, encoding="utf-8")
print("Brand24 trial conversion proof added using resilient customer-visible anchor.")
