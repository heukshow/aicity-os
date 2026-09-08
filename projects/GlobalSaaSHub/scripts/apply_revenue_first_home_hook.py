from pathlib import Path
import re

app = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = app.read_text(encoding="utf-8")

# 1) Make the product promise explicit: the subject is the AI tool, not a job or career path.
headline_variants = [
    (
        """            Find the right AI & SaaS tool
            <span className=\"block bg-gradient-to-r from-violet-300 via-white to-cyan-300 bg-clip-text text-transparent\">without wasting money.</span>""",
        """            Find AI tools you can use
            <span className=\"block bg-gradient-to-r from-violet-300 via-white to-cyan-300 bg-clip-text text-transparent\">to make money.</span>""",
    ),
    (
        """            Find AI & SaaS tools that help you
            <span className=\"block bg-gradient-to-r from-violet-300 via-white to-cyan-300 bg-clip-text text-transparent\">earn, sell and grow.</span>""",
        """            Find AI tools you can use
            <span className=\"block bg-gradient-to-r from-violet-300 via-white to-cyan-300 bg-clip-text text-transparent\">to make money.</span>""",
    ),
]
for old, new in headline_variants:
    if old in text:
        text = text.replace(old, new, 1)
        break

subtitle_variants = [
    "Compare pricing, use cases, strengths and verified public information before you subscribe. Start with what you need, not a giant software list.",
    "Find tools for getting leads, creating content, automating work and growing traffic — then compare pricing, trials and verified offers before you choose.",
]
subtitle_new = "Choose how you want to make money with AI — get leads, create content, sell online, automate work or grow traffic — then compare the tools that can help."
for old in subtitle_variants:
    if old in text:
        text = text.replace(old, subtitle_new, 1)
        break

# 2) Replace the hero category row with AI-tool revenue paths.
category_row = re.compile(
    r'''\n\s*<div className="mt-3 flex flex-wrap justify-center gap-2">\n\s*\{categories\.slice\(1, 7\)\.map\(\(cat\) => \{.*?\n\s*</div>''',
    re.S,
)
intent_row = '''
          <div className="mt-3 flex flex-wrap justify-center gap-2">
            <a href="/best/ai-tools-to-make-money.html" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-2 text-xs font-bold text-violet-200 hover:bg-violet-400/20">
              <TrendingUp className="h-3.5 w-3.5" /> Make money with AI
            </a>
            <button onClick={() => { setSearchTerm('lead'); setSelectedCategory('all'); setSelectedPricing('all'); document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }} className="inline-flex min-h-11 items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs font-bold text-amber-200 hover:bg-amber-400/20">
              <CreditCard className="h-3.5 w-3.5" /> Get leads
            </button>
            <button onClick={() => { setSearchTerm('content'); setSelectedCategory('all'); setSelectedPricing('all'); document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }} className="inline-flex min-h-11 items-center gap-2 rounded-full border border-fuchsia-400/20 bg-fuchsia-400/10 px-3 py-2 text-xs font-bold text-fuchsia-200 hover:bg-fuchsia-400/20">
              <Sparkles className="h-3.5 w-3.5" /> Create content
            </button>
            <a href="/best/shopify-pricing-free-trial.html" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-blue-400/20 bg-blue-400/10 px-3 py-2 text-xs font-bold text-blue-200 hover:bg-blue-400/20">
              <CreditCard className="h-3.5 w-3.5" /> Sell online
            </a>
            <button onClick={() => { setSearchTerm(''); setSelectedCategory('workflow_auto'); setSelectedPricing('all'); document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }} className="inline-flex min-h-11 items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/20">
              <Cpu className="h-3.5 w-3.5" /> Automate work
            </button>
            <button onClick={() => { setSearchTerm(''); setSelectedCategory('seo_tools'); setSelectedPricing('all'); document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }} className="inline-flex min-h-11 items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-bold text-emerald-200 hover:bg-emerald-400/20">
              <SearchCode className="h-3.5 w-3.5" /> Grow traffic
            </button>
          </div>'''
text, count = category_row.subn("\n" + intent_row, text, count=1)

# Handle builds where the earlier revenue row has already been applied.
if count != 1:
    existing_row = re.compile(
        r'''\n\s*<div className="mt-3 flex flex-wrap justify-center gap-2">\n\s*<button onClick=\{\(\) => \{ setSearchTerm\(''\); setSelectedCategory\('sales_crm'\).*?\n\s*</div>''',
        re.S,
    )
    text, count = existing_row.subn("\n" + intent_row, text, count=1)

if count != 1 and "Make money with AI" not in text:
    raise SystemExit("Hero revenue path row changed; refusing unsafe AI-money patch")

# 3) Remove vanity-count block from the hero. It consumes prime space without helping a buyer decide.
stats_block = re.compile(
    r'''\n\s*<div className="mx-auto mt-10 grid max-w-4xl grid-cols-3 gap-3 rounded-2xl border border-white/10 bg-white/\[0\.03\] p-3 sm:p-4">.*?\n\s*</div>\n\s*</header>''',
    re.S,
)
text, count = stats_block.subn("\n      </header>", text, count=1)
if count != 1 and "Tool profiles" in text:
    raise SystemExit("Hero stats block changed; refusing unsafe revenue-hook patch")

app.write_text(text, encoding="utf-8")
print("AI-money homepage applied: tool-first money hook, six revenue paths, vanity stats removed")
