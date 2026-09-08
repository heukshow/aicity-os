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
        "const verified = toolsData.filter((t) => t.affiliate_verified === true).length;",
        "const verified = toolsData.filter((t) => t.affiliate_verified === true && t.affiliate_status === 'approved_tracking').length;",
    ),
    (
        "              const validUrl = getValidExternalUrl(tool);",
        "              const isApprovedAffiliate = tool.affiliate_verified === true && tool.affiliate_status === 'approved_tracking';\n              const validUrl = getValidExternalUrl(tool);",
    ),
    (
        '<div className="text-right"><div className="text-[10px] uppercase tracking-wider text-slate-600">Rating</div><div className="mt-0.5 inline-flex items-center gap-1 text-sm font-bold text-slate-200">{tool.rating != null && tool.rating_source_url ? <><Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" /> {tool.rating}</> : \'Source-led\'}</div></div>',
        '<div className="text-right"><div className="text-[10px] uppercase tracking-wider text-slate-600">Link</div><div className={`mt-0.5 text-sm font-bold ${isApprovedAffiliate ? \'text-emerald-300\' : \'text-slate-300\'}`}>{isApprovedAffiliate ? \'Verified partner\' : \'Official site\'}</div></div>',
    ),
    (
        "rel={tool.affiliate_verified === true ? 'sponsored noopener noreferrer' : 'noopener noreferrer'}",
        "rel={isApprovedAffiliate ? 'sponsored noopener noreferrer' : 'noopener noreferrer'}",
    ),
    (
        "onClick={() => trackToolClick(tool.id, tool.name, validUrl, tool.affiliate_verified === true)}",
        "onClick={() => trackToolClick(tool.id, tool.name, validUrl, isApprovedAffiliate)}",
    ),
    (
        "{tool.affiliate_verified === true ? 'Check verified offer' : 'Visit official site'}",
        "{isApprovedAffiliate ? 'Check verified offer' : 'Visit official site'}",
    ),
    (
        "{tool.affiliate_verified === true && <div className=\"mt-2 flex items-center justify-center gap-1 text-[10px] text-slate-600\"><CheckCircle2 className=\"h-3 w-3\" /> Affiliate link verified in our records · disclosure applies</div>}",
        "{isApprovedAffiliate && <div className=\"mt-2 flex items-center justify-center gap-1 text-[10px] text-slate-600\"><CheckCircle2 className=\"h-3 w-3\" /> Affiliate link verified in our records · disclosure applies</div>}",
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Homepage card markup changed; refusing unsafe replacement: {old[:80]}")
    text = text.replace(old, new, 1)

app.write_text(text, encoding="utf-8")
print("Homepage cards simplified and affiliate routing limited to approved tracking")
