from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "tool" / "livechat.html"
TRACKING_URL = "https://www.livechat.com/?a=8IetMhQv&utm_campaign=pp_livechat-default&utm_source=PP"
OFFICIAL_PRICING = "https://www.livechat.com/pricing/"

html = PAGE.read_text(encoding="utf-8")

# Keep the exact verified customer-facing route as the single commercial CTA.
affiliate_anchor = re.compile(
    r'<a\b[^>]*data-cta="affiliate"[^>]*data-tool-id="livechat"[^>]*>.*?</a>',
    re.I | re.S,
)
replacement = (
    '<a data-cta="affiliate" data-tool-id="livechat" data-cta-source="livechat_trial_primary" '
    f'href="{TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer" '
    'class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center '
    'hover:bg-purple-500 transition-all flex items-center justify-center gap-2">'
    '<span>Open LiveChat and start the free trial</span><span>→</span></a>'
)
html, count = affiliate_anchor.subn(replacement, html, count=1)
if count != 1:
    raise SystemExit("LiveChat conversion patch: expected exactly one existing affiliate CTA")

old_pricing = (
    'All paid tiers can be evaluated with a 14-day free trial. No credit card is required. '
    'Confirm final terms on the <a href="https://www.livechat.com/pricing/" target="_blank" '
    'rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">official LiveChat pricing page</a>.'
)
new_pricing = (
    'All paid tiers can be evaluated with a 14-day free trial and no credit card is required. '
    'The current pricing page also lists monthly billing at <strong class="text-slate-300">$25 Starter</strong>, '
    '<strong class="text-slate-300">$59 Team</strong> and <strong class="text-slate-300">$89 Business</strong>. '
    'Starter is limited to one user, while Team adds unlimited users, unlimited campaigns and unlimited chat history. '
    'Confirm final terms on the <a href="https://www.livechat.com/pricing/" target="_blank" '
    'rel="noopener noreferrer" class="text-purple-300 hover:text-purple-200">official LiveChat pricing page</a>.'
)
if new_pricing not in html:
    if old_pricing not in html:
        raise SystemExit("LiveChat conversion patch: pricing paragraph changed unexpectedly")
    html = html.replace(old_pricing, new_pricing, 1)

decision_marker = '<!-- COSHUMA_LIVECHAT_PLAN_DECISION -->'
if decision_marker not in html:
    faq = '<section class="space-y-4 pt-4 border-t border-[#222538]"> <h2 class="text-xl font-bold text-white">LiveChat pricing FAQ</h2>'
    if faq not in html:
        raise SystemExit("LiveChat conversion patch: FAQ insertion point missing")
    decision = (
        decision_marker +
        '<section class="p-6 rounded-2xl bg-purple-500/5 border border-purple-500/20 space-y-4"> '
        '<div class="text-xs uppercase tracking-wider font-bold text-purple-300">Which plan should you test?</div> '
        '<div class="grid gap-4 md:grid-cols-2"> '
        '<div class="p-4 rounded-xl bg-[#181a29] border border-[#222538]"><h3 class="font-bold text-white">Start with Starter if one user is enough</h3>'
        '<p class="mt-2 text-sm text-slate-300 leading-relaxed">Starter is the lowest-cost test path when one person will handle chat. Use the trial to confirm widget setup, visitor conversations and whether the 60-day chat history is enough.</p></div> '
        '<div class="p-4 rounded-xl bg-[#181a29] border border-purple-500/30"><h3 class="font-bold text-white">Test Team if support is shared</h3>'
        '<p class="mt-2 text-sm text-slate-300 leading-relaxed">Team is the more relevant test for multi-agent support because it adds unlimited users, unlimited campaigns, unlimited chat history and basic reporting. Compare the extra seat cost against the collaboration features you actually need.</p></div> '
        '</div></section> '
    )
    html = html.replace(faq, decision + faq, 1)

if TRACKING_URL not in html:
    raise SystemExit("LiveChat conversion patch: verified tracking URL missing")
if OFFICIAL_PRICING not in html:
    raise SystemExit("LiveChat conversion patch: official pricing source missing")
if "$25 Starter" not in html or "$59 Team" not in html or "$89 Business" not in html:
    raise SystemExit("LiveChat conversion patch: monthly price comparison missing")
if decision_marker not in html:
    raise SystemExit("LiveChat conversion patch: plan decision block missing")

PAGE.write_text(html, encoding="utf-8")
print("LiveChat buyer conversion patch applied after public-source generators.")
