"""Apply DocsBot partner-provided conversion guidance to COSHUMA buyer pages.

Evidence: DocsBot Support replied to support@coshuma.com on 2026-09-09 KST
(message 1a0822c3c129c9aa) recommending problem-first positioning and the CTA
"Turn your knowledge into an AI agent, free." The account-specific referral URL
remains https://docsbot.ai?via=31kq9q. DocsBot also confirmed there is no separate
customer discount or limited-time affiliate promotion currently. This patch is
exact-match and idempotent; it never changes the verified referral URL.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "public"


def apply_replacements(page: Path, replacements: list[tuple[str, str]]) -> None:
    text = page.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        if new in text:
            continue
        if old not in text:
            raise SystemExit(
                f"Refusing uncertain DocsBot patch for {page.name}; "
                f"exact source text missing: {old[:120]}"
            )
        text = text.replace(old, new)

    if text != original:
        page.write_text(text, encoding="utf-8")
        print(f"DocsBot partner conversion guidance applied: {page}")
    else:
        print(f"DocsBot partner conversion guidance already applied: {page}")


apply_replacements(
    ROOT / "best" / "docsbot-free-plan-pricing.html",
    [
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
    ],
)

apply_replacements(
    ROOT / "tool" / "docsbot.html",
    [
        (
            '<p class="text-slate-400 mt-2 text-sm">Updated September 1, 2026</p>',
            '<p class="text-slate-400 mt-2 text-sm">Updated September 9, 2026</p>',
        ),
        (
            '<p class="text-slate-200 leading-relaxed">DocsBot builds AI agents from websites, documents and business knowledge for customer support and team automation. Its current product combines agentic RAG with chat widgets, actions, analytics, integrations and optional MCP workflows.</p>',
            '<p class="text-slate-200 leading-relaxed">If customers cannot find answers, support teams keep repeating the same replies, prospects leave without the information they need, or internal knowledge is scattered across too many places, DocsBot turns existing documentation, website content and files into AI chat and voice agents that can answer questions and handle common tasks.</p>',
        ),
        (
            '<div class="text-sm font-extrabold text-white">Best first step</div><p class="text-xs text-slate-300 leading-relaxed">Use the free plan to test source quality and answer accuracy before buying AI credits or larger source limits. It currently includes one bot, 50 source pages and 100 monthly AI credits.</p>',
            '<div class="text-sm font-extrabold text-white">Start with one real knowledge problem</div><p class="text-xs text-slate-300 leading-relaxed">Pick one repeated support question, sales objection or internal knowledge task, then use the free plan to test whether DocsBot gives trustworthy answers from your sources before paying for more capacity.</p>',
        ),
        (
            '>Start DocsBot Free via Verified Affiliate Link →</a>',
            '>Turn your knowledge into an AI agent, free →</a>',
        ),
        (
            '<h2 class="text-2xl md:text-3xl font-black text-white">Test answer quality before buying capacity</h2><p class="text-sm text-slate-300 max-w-2xl mx-auto">The free tier is enough to validate whether your documents produce useful answers before paying for larger source and AI-credit limits.</p>',
            '<h2 class="text-2xl md:text-3xl font-black text-white">Turn your knowledge into an AI agent, free</h2><p class="text-sm text-slate-300 max-w-2xl mx-auto">Start with a real support, sales or internal-knowledge problem. Use the free tier to validate grounded answers from your own sources, then upgrade only when real usage reaches the plan limits.</p>',
        ),
    ],
)
