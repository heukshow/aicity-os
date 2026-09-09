from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "App.jsx"
HUB = ROOT / "public" / "best" / "ai-tools-to-make-money.html"

app = APP.read_text(encoding="utf-8")

replacements = [
    (
        '''            <button onClick={() => { setSearchTerm('lead'); setSelectedCategory('all'); setSelectedPricing('all'); document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }} className="inline-flex min-h-11 items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs font-bold text-amber-200 hover:bg-amber-400/20">\n              <CreditCard className="h-3.5 w-3.5" /> Get leads\n            </button>''',
        '''            <a href="/best/ai-tools-to-make-money.html#get-leads" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-xs font-bold text-amber-200 hover:bg-amber-400/20">\n              <CreditCard className="h-3.5 w-3.5" /> Get leads\n            </a>''',
    ),
    (
        '''            <button onClick={() => { setSearchTerm('content'); setSelectedCategory('all'); setSelectedPricing('all'); document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }} className="inline-flex min-h-11 items-center gap-2 rounded-full border border-fuchsia-400/20 bg-fuchsia-400/10 px-3 py-2 text-xs font-bold text-fuchsia-200 hover:bg-fuchsia-400/20">\n              <Sparkles className="h-3.5 w-3.5" /> Create content\n            </button>''',
        '''            <a href="/best/ai-tools-to-make-money.html#create-content" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-fuchsia-400/20 bg-fuchsia-400/10 px-3 py-2 text-xs font-bold text-fuchsia-200 hover:bg-fuchsia-400/20">\n              <Sparkles className="h-3.5 w-3.5" /> Create content\n            </a>''',
    ),
    (
        '''            <button onClick={() => { setSearchTerm(''); setSelectedCategory('workflow_auto'); setSelectedPricing('all'); document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }} className="inline-flex min-h-11 items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/20">\n              <Cpu className="h-3.5 w-3.5" /> Automate work\n            </button>''',
        '''            <a href="/best/ai-tools-to-make-money.html#automate-work" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/20">\n              <Cpu className="h-3.5 w-3.5" /> Automate work\n            </a>''',
    ),
    (
        '''            <button onClick={() => { setSearchTerm(''); setSelectedCategory('seo_tools'); setSelectedPricing('all'); document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }} className="inline-flex min-h-11 items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-bold text-emerald-200 hover:bg-emerald-400/20">\n              <SearchCode className="h-3.5 w-3.5" /> Grow traffic\n            </button>''',
        '''            <a href="/best/ai-tools-to-make-money.html#grow-traffic" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-bold text-emerald-200 hover:bg-emerald-400/20">\n              <SearchCode className="h-3.5 w-3.5" /> Grow traffic\n            </a>''',
    ),
    (
        'href="/best/shopify-pricing-free-trial.html" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-blue-400/20 bg-blue-400/10 px-3 py-2 text-xs font-bold text-blue-200 hover:bg-blue-400/20"',
        'href="/best/ai-tools-to-make-money.html#sell-online" className="inline-flex min-h-11 items-center gap-2 rounded-full border border-blue-400/20 bg-blue-400/10 px-3 py-2 text-xs font-bold text-blue-200 hover:bg-blue-400/20"',
    ),
]

for old, new in replacements:
    if new in app:
        continue
    if old not in app:
        raise SystemExit(f"Money-path markup changed; refusing unsafe navigation patch: {old[:90]}")
    app = app.replace(old, new, 1)

APP.write_text(app, encoding="utf-8")

hub = HUB.read_text(encoding="utf-8")
for section_id in ("get-leads", "create-content", "sell-online", "automate-work", "grow-traffic"):
    short = f'href="#{section_id}"'
    full = f'href="/best/ai-tools-to-make-money.html#{section_id}"'
    if short in hub:
        hub = hub.replace(short, full, 1)
    start = f'<section id="{section_id}" class="'
    if start in hub and f'<section id="{section_id}" class="scroll-mt-24 ' not in hub:
        hub = hub.replace(start, f'<section id="{section_id}" class="scroll-mt-24 ', 1)

HUB.write_text(hub, encoding="utf-8")
print("Money navigation hardened: homepage paths use plain links and hub anchors use full URLs")
