"""Add official Brand24 trial specifics to the high-impression buyer page.

Search Console's last healthy snapshot showed /tool/brand24.html at 163 impressions
and 0 search clicks. Brand24's current first-party help states the 14-day trial is
based on Pro, supports up to 10 keywords and 30k mentions, and refreshes trial data
every 24h. The official pricing FAQ also states a 30-day money-back guarantee after
purchase, excluding custom plans/deals. This patch keeps the already verified COSHUMA
partner URL unchanged and adds a buyer-decision block with a separately attributable
CTA.
"""
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "brand24.html"
MARKER = 'data-brand24-trial-proof="2026-09-09"'
ANCHOR = '      <section class="rounded-3xl border border-[#262a3d] bg-[#121520] p-6 md:p-8 space-y-5">\n        <div>\n          <div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Current pricing</div>'

BLOCK = '''      <section data-brand24-trial-proof="2026-09-09" class="rounded-3xl border border-emerald-500/25 bg-emerald-500/5 p-6 md:p-8 space-y-5">
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
        <a data-cta="affiliate" data-tool-id="brand24" data-cta-source="brand24-trial-proof" href="https://try.brand24.com/8xqrjxybmsbt" target="_blank" rel="sponsored noopener noreferrer" class="block sm:inline-flex px-6 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-center">Run the 14-day Brand24 test via COSHUMA →</a>
        <p class="text-[11px] text-slate-500 leading-relaxed">COSHUMA may earn a commission on an eligible paid conversion attributed through this verified Brand24 partner link. Trial access does not prove a signup, sale or commission.</p>
      </section>

'''

text = PAGE.read_text(encoding="utf-8")
if MARKER in text:
    print("Brand24 trial conversion patch already present.")
    raise SystemExit(0)
if ANCHOR not in text:
    raise SystemExit("Refusing uncertain Brand24 patch: pricing-section anchor missing")
text = text.replace(ANCHOR, BLOCK + ANCHOR, 1)
PAGE.write_text(text, encoding="utf-8")
print("Brand24 trial conversion proof added.")
