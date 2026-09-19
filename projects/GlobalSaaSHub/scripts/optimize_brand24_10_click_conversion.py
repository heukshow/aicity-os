"""Improve Brand24 click-to-trial conversion after the first verified 10-click milestone.

Vendor/PartnerStack email on 2026-09-11 KST confirmed the COSHUMA referral link
reached its first 10 clicks. It did not report signups, paid customers, commission,
or revenue, so this patch makes no conversion claim.

Brand24's current first-party Help Center says the 14-day trial is based on Pro,
supports up to 10 keywords and 30,000 mentions, and its pricing FAQ says no credit
card is required. This patch moves those concrete trial benefits next to the hero CTA
while preserving the exact already-verified PartnerStack customer URL.
"""
from pathlib import Path
import re

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "brand24.html"
TRACKING_URL = "https://try.brand24.com/8xqrjxybmsbt"
MARKER = 'data-brand24-conversion-v2="2026-09-11"'
PLAN_MARKER = 'data-brand24-plan-transition-v3="2026-09-19"'
BENEFIT = '<p data-brand24-conversion-v2="2026-09-11" class="text-xs text-emerald-200 leading-relaxed"><strong class="text-white">Trial value:</strong> Brand24 currently says the 14-day trial is based on Pro, supports up to 10 keywords and 30,000 mentions, and requires no credit card. Use the trial to test real monitoring volume before paying.</p>'

text = PAGE.read_text(encoding="utf-8")
if TRACKING_URL not in text:
    raise SystemExit("Refusing Brand24 conversion patch: verified tracking URL missing")

# Target CTAs by their stable attribution source instead of brittle full-text anchors.
hero_pattern = re.compile(r'(<a\b[^>]*data-tool-id="brand24"[^>]*data-cta-source="brand24-hero"[^>]*>)(.*?)(</a>)', re.S)
trial_pattern = re.compile(r'(<a\b[^>]*data-tool-id="brand24"[^>]*data-cta-source="brand24-trial-proof"[^>]*>)(.*?)(</a>)', re.S)

hero_match = hero_pattern.search(text)
if hero_match:
    text = hero_pattern.sub(r'\1Open Brand24 → Start 14-Day Trial — No Card\3', text, count=1)

trial_match = trial_pattern.search(text)
if trial_match:
    text = trial_pattern.sub(r'\1Start the 14-Day Pro-Level Brand24 Trial →\3', text, count=1)

# Put the concrete trial value immediately beside the primary revenue CTA. If an
# upstream copy pass changes surrounding prose, the stable CTA source still anchors it.
if MARKER not in text:
    hero_match = hero_pattern.search(text)
    if hero_match:
        text = text[:hero_match.end()] + "\n              " + BENEFIT + text[hero_match.end():]

# Make the trial-to-paid decision explicit. The trial is Pro-based, but the
# cheapest paid tiers have materially lower keyword/mention limits. This helps
# buyers avoid assuming the trial experience maps directly to Individual.
if PLAN_MARKER not in text:
    pricing_heading = '<h2 class="text-2xl md:text-3xl font-black text-white mt-1">Brand24 pricing checked September 9, 2026</h2>'
    if pricing_heading in text:
        plan_block = '''<section data-brand24-plan-transition-v3="2026-09-19" class="rounded-3xl border border-violet-500/20 bg-violet-500/5 p-6 md:p-8 space-y-5">
  <div>
    <div class="text-xs uppercase tracking-widest text-violet-300 font-bold">Before you choose a paid plan</div>
    <h2 class="text-2xl md:text-3xl font-black text-white mt-1">The trial is Pro-based — your paid plan does not have to be Pro</h2>
    <p class="text-sm md:text-base text-slate-300 leading-relaxed">Brand24's 14-day trial lets you test up to <strong class="text-white">10 keywords</strong> and <strong class="text-white">30,000 mentions</strong>. After the trial, choose by your real monitoring volume instead of copying the trial setup into a more expensive plan.</p>
  </div>
  <div class="grid md:grid-cols-3 gap-3 text-sm">
    <div class="rounded-2xl border border-violet-500/15 bg-[#0d1018] p-4"><strong class="text-white">Individual may be enough</strong><p class="mt-2 text-slate-400">Use it when 3 keywords, 2K mentions per month and one user cover the workflow you proved during the trial.</p></div>
    <div class="rounded-2xl border border-violet-500/15 bg-[#0d1018] p-4"><strong class="text-white">Team fits shared monitoring</strong><p class="mt-2 text-slate-400">Use it when you need 7 keywords, 10K mentions, unlimited users and hourly updates.</p></div>
    <div class="rounded-2xl border border-violet-500/15 bg-[#0d1018] p-4"><strong class="text-white">Compare Pro when scale matters</strong><p class="mt-2 text-slate-400">Pro raises the published limits to 12 keywords and 40K mentions with real-time updates and additional AI features.</p></div>
  </div>
  <p class="text-xs text-slate-400">The tracked offer button opens Brand24's customer site. Start the free trial there, then confirm the live plan and billing terms before purchasing.</p>
</section>
'''
        section_pos = text.rfind("<section", 0, text.find(pricing_heading))
        if section_pos >= 0:
            text = text[:section_pos] + plan_block + text[section_pos:]

# Revenue safety: never invent a pricing/signup deep link. Keep the exact issued URL.
if TRACKING_URL not in text:
    raise SystemExit("Brand24 conversion patch failed: verified tracking URL was lost")

PAGE.write_text(text, encoding="utf-8")
if MARKER in text and PLAN_MARKER in text:
    print("Brand24 conversion patch applied; trial value, trial-to-paid plan guidance and exact tracking preserved.")
elif MARKER in text:
    print("Brand24 trial value surfaced; plan-transition block could not be placed without a stable pricing anchor.")
else:
    print("Brand24 verified tracking preserved; stable hero anchor was not present, so no speculative copy insertion was made.")
