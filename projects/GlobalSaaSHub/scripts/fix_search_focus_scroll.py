from pathlib import Path

app = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = app.read_text(encoding="utf-8")

focus_scroll = "              onFocus={() => document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'center' })}\n"
if focus_scroll in text:
    text = text.replace(focus_scroll, "", 1)
elif "onFocus={() => document.getElementById('directory')?.scrollIntoView" in text:
    raise SystemExit("Search focus auto-scroll still exists but exact patch no longer matches; refusing unsafe edit")

autocomplete_old = '''                  <a key={tool.id} href={`/tool/${tool.id}.html`} className="flex items-center justify-between border-b border-white/5 px-4 py-3 last:border-0 hover:bg-white/5">
                    <span className="font-semibold text-white">{tool.name}</span>
                    <span className="text-xs text-slate-500">{tool.category_display}</span>
                  </a>'''

autocomplete_new = '''                  <a key={tool.id} href={`/tool/${tool.id}.html`} className="flex items-center justify-between gap-4 border-b border-white/5 px-4 py-3 last:border-0 hover:bg-white/5">
                    <span className="min-w-0 text-left">
                      <span className="block truncate font-semibold text-white">{tool.name}</span>
                      <span className="mt-0.5 block truncate text-xs text-slate-500">{tool.category_display}</span>
                    </span>
                    <span className="shrink-0 rounded-lg border border-white/10 bg-white/[0.04] px-2.5 py-1 text-xs font-semibold text-slate-300">{tool.pricing || 'Check pricing'}</span>
                  </a>'''

autocomplete_with_detail_route = autocomplete_new.replace(
    'href={`/tool/${tool.id}.html`}', 'href={tool.detail_url || `/tool/${tool.id}.html`}')
if autocomplete_new not in text and autocomplete_with_detail_route not in text:
    if autocomplete_old not in text:
        raise SystemExit("Autocomplete markup changed; refusing unsafe UX patch")
    text = text.replace(autocomplete_old, autocomplete_new, 1)

quick_filters_anchor = '''          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {categories.slice(1, 7).map((cat) => {'''

quick_filters_new = '''          <div className="mt-5 flex flex-wrap justify-center gap-2">
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
                setSelectedPricing('free');
                document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }}
              className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-bold text-emerald-200 hover:bg-emerald-400/20"
            >
              Free / trial
            </button>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
                setSelectedPricing('under20');
                document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }}
              className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/20"
            >
              Under $20
            </button>
          </div>

          <div className="mt-3 flex flex-wrap justify-center gap-2">
            {categories.slice(1, 7).map((cat) => {'''

# The later revenue-hook producer replaces the category row. Match the complete
# price-filter block separately so a repeated build preserves that newer row.
quick_filter_block = quick_filters_new.split('\n\n          <div className="mt-3')[0]
mobile_quick_filter_block = quick_filter_block.replace('className="inline-flex items-center',
                                                       'className="inline-flex min-h-11 items-center')
if quick_filter_block not in text and mobile_quick_filter_block not in text:
    if quick_filters_anchor not in text:
        raise SystemExit("Quick-filter insertion point changed; refusing unsafe UX patch")
    text = text.replace(quick_filters_anchor, quick_filters_new, 1)

app.write_text(text, encoding="utf-8")
print("Search UX patch applied: stable focus, richer autocomplete, quick price filters")
