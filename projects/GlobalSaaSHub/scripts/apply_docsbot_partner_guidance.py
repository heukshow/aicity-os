"""Apply DocsBot partner-provided conversion guidance to the buyer page.

Evidence: DocsBot Support replied to support@coshuma.com on 2026-09-09 KST
(message 1a0822c3c129c9aa) recommending problem-first positioning and the CTA
"Turn your knowledge into an AI agent, free." The account-specific referral URL
remains https://docsbot.ai?via=31kq9q. This patch is exact-match and idempotent.
"""
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "best" / "docsbot-free-plan-pricing.html"
text = PAGE.read_text(encoding="utf-8")
original = text

replacements = [
    (
        '<h1 class="mt-5 text-4xl sm:text-6xl font-black tracking-[-0.04em] text-white">Test DocsBot free before paying for more capacity</h1>',
        '<h1 class="mt-5 text-4xl sm:text-6xl font-black tracking-[-0.04em] text-white">Turn scattered knowledge into an AI agent before you pay</h1>',
    ),
    (
        '<p class="mt-5 max-w-3xl text-lg leading-8 text-slate-300">DocsBot\'s official pricing page currently lists a <strong class="text-white">$0 free plan with no credit card required</strong>. It is enough to test one knowledge bot on a small source set before deciding whether larger page, AI-credit, action or team limits are worth paying for.</p>',
        '<p class="mt-5 max-w-3xl text-lg leading-8 text-slate-300">If customers cannot find answers, your team keeps repeating the same replies, prospects leave with questions, or internal knowledge is scattered across docs, sites and files, DocsBot can turn that knowledge into AI chat and voice agents. Its official pricing page currently lists a <strong class="text-white">$0 free plan with no credit card required</strong>, so you can test the workflow before paying.</p>',
    ),
    (
        '<div class="rounded-2xl border border-emerald-400/25 bg-emerald-400/[0.07] p-5"><div class="text-xs uppercase tracking-[0.18em] text-emerald-200/80 font-black">Buyer Decision Box</div><h2 class="mt-2 text-2xl font-black text-white">Best first step for most buyers</h2><ol class="mt-4 space-y-2 text-sm leading-6 text-slate-300 list-decimal pl-5"><li>Open DocsBot through COSHUMA\'s verified referral route.</li><li>Create one bot and load a representative subset of your real documentation.</li><li>Use the 100 monthly AI credits to test answer quality, grounding and source coverage.</li><li>Upgrade only if you need more source pages, AI credits, actions, analytics or team seats.</li></ol></div>',
        '<div class="rounded-2xl border border-emerald-400/25 bg-emerald-400/[0.07] p-5"><div class="text-xs uppercase tracking-[0.18em] text-emerald-200/80 font-black">Buyer Decision Box</div><h2 class="mt-2 text-2xl font-black text-white">Start with the support or knowledge problem</h2><ol class="mt-4 space-y-2 text-sm leading-6 text-slate-300 list-decimal pl-5"><li>Pick one repeated support question, sales objection, or internal knowledge task.</li><li>Load a representative subset of your documentation, website content or files.</li><li>Use the free plan to test whether the agent gives trustworthy, grounded answers.</li><li>Upgrade only when source, AI-credit, action, analytics or team limits block real usage.</li></ol></div>',
    ),
    (
        '>Start DocsBot free →</a>',
        '>Turn your knowledge into an AI agent, free →</a>',
    ),
    (
        '>Start through COSHUMA →</a>',
        '>Turn your knowledge into an AI agent, free →</a>',
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Refusing uncertain DocsBot patch; exact source text missing: {old[:120]}")
    text = text.replace(old, new)

if text != original:
    PAGE.write_text(text, encoding="utf-8")
    print("DocsBot partner conversion guidance applied.")
else:
    print("DocsBot partner conversion guidance already applied.")
