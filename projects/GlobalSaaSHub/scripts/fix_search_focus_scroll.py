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

if autocomplete_new not in text:
    if autocomplete_old not in text:
        raise SystemExit("Autocomplete markup changed; refusing unsafe UX patch")
    text = text.replace(autocomplete_old, autocomplete_new, 1)

app.write_text(text, encoding="utf-8")
print("Search UX patch applied: no focus auto-scroll; autocomplete shows category and pricing")
