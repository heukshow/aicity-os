from pathlib import Path

app = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = app.read_text(encoding="utf-8")

replacements = [
    (
        'className="relative z-10 mx-auto max-w-7xl px-4 pb-14 pt-14 sm:px-6 sm:pt-20 lg:px-8"',
        'className="relative z-10 mx-auto max-w-7xl px-4 pb-10 pt-10 sm:px-6 sm:pb-14 sm:pt-20 lg:px-8"',
    ),
    (
        'className="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-bold text-emerald-200"',
        'className="mb-5 inline-flex max-w-full items-center gap-2 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-[11px] font-bold leading-5 text-emerald-200 sm:mb-6 sm:rounded-full sm:py-1.5 sm:text-xs"',
    ),
    (
        'className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs font-semibold text-slate-300 hover:border-violet-400/30 hover:bg-violet-400/10 hover:text-white"',
        'className="inline-flex min-h-11 items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-xs font-semibold text-slate-300 hover:border-violet-400/30 hover:bg-violet-400/10 hover:text-white"',
    ),
    (
        'className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-bold text-emerald-200 hover:bg-emerald-400/20"',
        'className="inline-flex min-h-11 items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-bold text-emerald-200 hover:bg-emerald-400/20"',
    ),
    (
        'className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/20"',
        'className="inline-flex min-h-11 items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-bold text-cyan-200 hover:bg-cyan-400/20"',
    ),
    (
        'className="mb-4 flex flex-wrap gap-2"',
        'className="mb-4 -mx-1 flex gap-2 overflow-x-auto px-1 pb-2 sm:mx-0 sm:flex-wrap sm:overflow-visible sm:px-0 sm:pb-0"',
    ),
    (
        'className={`inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold transition ${active ? \'bg-white text-slate-950\' : \'border border-white/10 bg-white/[0.02] text-slate-400 hover:text-white\'}`}',
        'className={`inline-flex min-h-11 shrink-0 items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold transition ${active ? \'bg-white text-slate-950\' : \'border border-white/10 bg-white/[0.02] text-slate-400 hover:text-white\'}`}',
    ),
    (
        'className="flex flex-wrap items-center gap-2"',
        'className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1 md:mx-0 md:flex-wrap md:overflow-visible md:px-0 md:pb-0"',
    ),
    (
        'className={`rounded-lg px-3 py-1.5 text-xs font-semibold ${selectedPricing === opt.id ? \'bg-violet-500 text-white\' : \'bg-white/5 text-slate-400 hover:text-white\'}`}',
        'className={`min-h-11 shrink-0 rounded-lg px-3 py-2 text-xs font-semibold ${selectedPricing === opt.id ? \'bg-violet-500 text-white\' : \'bg-white/5 text-slate-400 hover:text-white\'}`}',
    ),
    (
        'className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold ${showBookmarksOnly ? \'bg-rose-500/20 text-rose-200\' : \'bg-white/5 text-slate-400 hover:text-white\'}`}',
        'className={`inline-flex min-h-11 shrink-0 items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-semibold ${showBookmarksOnly ? \'bg-rose-500/20 text-rose-200\' : \'bg-white/5 text-slate-400 hover:text-white\'}`}',
    ),
    (
        'className={`rounded-lg border p-2 ${bookmarkedIds.includes(tool.id) ? \'border-rose-400/30 bg-rose-400/10 text-rose-300\' : \'border-white/10 text-slate-600 hover:text-white\'}`}',
        'className={`min-h-11 min-w-11 rounded-lg border p-2 ${bookmarkedIds.includes(tool.id) ? \'border-rose-400/30 bg-rose-400/10 text-rose-300\' : \'border-white/10 text-slate-600 hover:text-white\'}`}',
    ),
    (
        'className="flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-xs font-bold text-slate-200 hover:bg-white/10"',
        'className="flex min-h-11 items-center justify-center rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-xs font-bold text-slate-200 hover:bg-white/10"',
    ),
    (
        'className="flex items-center justify-center rounded-xl border border-white/10 bg-white/5 px-3 text-slate-400 hover:text-white"',
        'className="flex min-h-11 min-w-11 items-center justify-center rounded-xl border border-white/10 bg-white/5 px-3 text-slate-400 hover:text-white"',
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Mobile homepage markup changed; refusing unsafe replacement: {old[:100]}")
    text = text.replace(old, new, 1)

app.write_text(text, encoding="utf-8")
print("Mobile homepage UX improved: swipeable filters and touch-safe controls")
