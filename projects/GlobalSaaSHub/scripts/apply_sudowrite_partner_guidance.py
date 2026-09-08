"""Apply current Sudowrite partner conversion guidance to the high-intent buyer page.

Evidence: Sudowrite Partnerships emailed support@coshuma.com on 2026-09-09 KST
(message 1a08242b5743d9a1) that its best-performing affiliate content leads with
writers' fear of losing their voice and then positions Sudowrite as a creative
partner for brainstorming, feedback and getting unstuck. The email restated the
account-specific referral URL https://www.sudowrite.com?via=sangkwon.

The patch is exact-match and idempotent. It does not invent discounts or revenue.
"""
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "best" / "sudowrite-free-trial-pricing.html"
text = PAGE.read_text(encoding="utf-8")
original = text

replacements = [
    (
        '<meta name="description" content="See Sudowrite\'s current free-trial terms, 2026 pricing, credit tiers and fiction-writing features before you subscribe. Includes a verified COSHUMA partner route." />',
        '<meta name="description" content="Worried AI will flatten your writing voice? Test Sudowrite on one real scene, then compare its free trial, 2026 pricing, credits and verified COSHUMA partner route." />',
    ),
    (
        '<meta property="og:description" content="A buyer-focused Sudowrite guide for novelists and fiction writers: free trial, current plans, credits and practical fit." />',
        '<meta property="og:description" content="Test whether Sudowrite helps you get unstuck without handing over creative control, then compare its current trial, plans and credits." />',
    ),
    (
        '"dateModified":"2026-09-06"',
        '"dateModified":"2026-09-09"',
    ),
    (
        '<div class="mb-5 inline-flex rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Official pricing checked Sep 6, 2026</div>',
        '<div class="mb-5 inline-flex rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Partner guidance updated Sep 9, 2026 · verified referral route</div>',
    ),
    (
        '<h1 class="text-4xl font-black tracking-[-0.04em] text-white sm:text-6xl">Sudowrite free trial & pricing for fiction writers</h1>',
        '<h1 class="text-4xl font-black tracking-[-0.04em] text-white sm:text-6xl">Sudowrite free trial & pricing: test AI without giving up your voice</h1>',
    ),
    (
        '<p class="mt-5 max-w-3xl text-lg leading-8 text-slate-400">Sudowrite is built around fiction workflows rather than general-purpose prompting. If you are deciding whether to pay for it, the practical questions are simple: can you test it without a card, how many credits do the plans include, and are the fiction-specific tools worth using in your drafting workflow?</p>',
        '<p class="mt-5 max-w-3xl text-lg leading-8 text-slate-400">If your hesitation is that AI will make your prose generic or dilute your voice, do not judge Sudowrite from a feature list. Test it on one scene that has been flat, one piece of dialogue that is not working, or one plot problem you have been stuck on. The useful question is whether it helps you brainstorm and revise while you remain the editor.</p>',
    ),
    (
        '>Try Sudowrite free →</a>',
        '>Try Sudowrite on one stuck scene →</a>',
    ),
    (
        '<section class="mt-12 grid gap-4 md:grid-cols-3">',
        '<section class="mt-12 rounded-3xl border border-violet-400/20 bg-violet-500/[0.06] p-6 sm:p-8"><div class="text-xs font-black uppercase tracking-widest text-violet-300">Creative-control test</div><h2 class="mt-2 text-3xl font-black">Use a real writing problem, not a demo prompt</h2><div class="mt-6 grid gap-4 md:grid-cols-3"><div class="rounded-2xl border border-white/10 bg-[#11131a] p-5"><h3 class="font-black text-white">A scene that feels flat</h3><p class="mt-2 text-sm leading-6 text-slate-400">Ask for options, then keep only what sounds like your story. The point is to create choices, not surrender authorship.</p></div><div class="rounded-2xl border border-white/10 bg-[#11131a] p-5"><h3 class="font-black text-white">Dialogue that misses the character</h3><p class="mt-2 text-sm leading-6 text-slate-400">Compare several rewrites against your established voice and reject anything that does not sound like the character.</p></div><div class="rounded-2xl border border-white/10 bg-[#11131a] p-5"><h3 class="font-black text-white">A plot hole you cannot solve</h3><p class="mt-2 text-sm leading-6 text-slate-400">Use brainstorming to generate paths forward, then make the narrative decision yourself.</p></div></div><a data-cta="affiliate" data-tool-id="sudowrite" data-cta-source="sudowrite_voice_objection" href="https://www.sudowrite.com?via=sangkwon" target="_blank" rel="sponsored noopener noreferrer" class="mt-6 inline-flex rounded-xl bg-violet-600 px-6 py-4 font-black text-white hover:bg-violet-500">Test Sudowrite on a real writing problem →</a></section>\n\n    <section class="mt-12 grid gap-4 md:grid-cols-3">',
    ),
    (
        '<h2 class="text-3xl font-black">Test the workflow before paying</h2>',
        '<h2 class="text-3xl font-black">Test whether it helps without taking over</h2>',
    ),
    (
        '<p class="mx-auto mt-3 max-w-2xl leading-7 text-slate-300">The current trial does not require a credit card. Use it on a real scene or chapter, then decide whether the fiction-specific workflow is worth a paid plan for you.</p>',
        '<p class="mx-auto mt-3 max-w-2xl leading-7 text-slate-300">Use the current no-card trial on a real scene, dialogue problem or plot block. Pay only if the fiction-specific workflow gives you useful options while you still feel in control of what stays on the page.</p>',
    ),
    (
        '>Start the Sudowrite free trial →</a>',
        '>Test one real scene with Sudowrite →</a>',
    ),
    (
        'checked against Sudowrite\'s official pricing page and documentation on Sep 6, 2026.',
        'checked against Sudowrite\'s official pricing page and documentation on Sep 9, 2026.',
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Refusing uncertain Sudowrite patch; exact source text missing: {old[:120]}")
    text = text.replace(old, new, 1)

if text != original:
    PAGE.write_text(text, encoding="utf-8")
    print("Sudowrite partner conversion guidance applied.")
else:
    print("Sudowrite partner conversion guidance already applied.")
