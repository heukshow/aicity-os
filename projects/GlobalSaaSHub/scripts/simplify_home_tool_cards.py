from pathlib import Path

app = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = app.read_text(encoding="utf-8")

replacements = [
    (
        '<p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-400">{tool.description}</p>',
        '<p className="mt-4 line-clamp-2 text-sm leading-6 text-slate-400">{tool.description}</p>',
    ),
    (
        "{(tool.key_features || []).slice(0, 3).map((feature) =>",
        "{(tool.key_features || []).slice(0, 2).map((feature) =>",
    ),
    (
        '<div className="text-right"><div className="text-[10px] uppercase tracking-wider text-slate-600">Rating</div><div className="mt-0.5 inline-flex items-center gap-1 text-sm font-bold text-slate-200">{tool.rating != null && tool.rating_source_url ? <><Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" /> {tool.rating}</> : \'Source-led\'}</div></div>',
        '<div className="text-right"><div className="text-[10px] uppercase tracking-wider text-slate-600">Link</div><div className={`mt-0.5 text-sm font-bold ${tool.affiliate_verified === true ? \'text-emerald-300\' : \'text-slate-300\'}`}>{tool.affiliate_verified === true ? \'Verified partner\' : \'Official site\'}</div></div>',
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Homepage card markup changed; refusing unsafe replacement: {old[:80]}")
    text = text.replace(old, new, 1)

app.write_text(text, encoding="utf-8")
print("Homepage cards simplified for faster scanning")
