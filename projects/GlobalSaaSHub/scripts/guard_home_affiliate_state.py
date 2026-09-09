from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "App.jsx"
text = APP.read_text(encoding="utf-8")
changes = 0


def replace_once(old: str, new: str, label: str) -> None:
    global text, changes
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"home affiliate guard could not find expected {label} pattern")
    text = text.replace(old, new, 1)
    changes += 1


replace_once(
    "const verified = toolsData.filter((t) => t.affiliate_verified === true).length;",
    "const verified = toolsData.filter((t) =>\n"
    "      t.affiliate_verified === true &&\n"
    "      t.affiliate_status === 'approved_tracking' &&\n"
    "      typeof t.affiliate_url === 'string' &&\n"
    "      /^https?:\\/\\//i.test(t.affiliate_url.trim())\n"
    "    ).length;",
    "verified-path count",
)

replace_once(
    "const validUrl = getValidExternalUrl(tool);\n              return (",
    "const validUrl = getValidExternalUrl(tool);\n"
    "              const isApprovedAffiliate = Boolean(\n"
    "                tool.affiliate_verified === true &&\n"
    "                tool.affiliate_status === 'approved_tracking' &&\n"
    "                typeof tool.affiliate_url === 'string' &&\n"
    "                validUrl === tool.affiliate_url.trim()\n"
    "              );\n"
    "              return (",
    "per-card approved affiliate predicate",
)

replace_once(
    "<a href={validUrl} target=\"_blank\" rel={tool.affiliate_verified === true ? 'sponsored noopener noreferrer' : 'noopener noreferrer'} onClick={() => trackToolClick(tool.id, tool.name, validUrl, tool.affiliate_verified === true)} className=\"flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-indigo-500 px-4 py-3 text-sm font-black text-white shadow-lg shadow-violet-950/20 hover:from-violet-400 hover:to-indigo-400\">",
    "<a data-cta={isApprovedAffiliate ? 'affiliate' : 'official'} data-tool-id={tool.id} data-cta-source=\"home-tool-card\" href={validUrl} target=\"_blank\" rel={isApprovedAffiliate ? 'sponsored noopener noreferrer' : 'noopener noreferrer'} onClick={() => trackToolClick(tool.id, tool.name, validUrl, isApprovedAffiliate)} className=\"flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-indigo-500 px-4 py-3 text-sm font-black text-white shadow-lg shadow-violet-950/20 hover:from-violet-400 hover:to-indigo-400\">",
    "homepage outbound CTA",
)

replace_once(
    "{tool.affiliate_verified === true ? 'Check verified offer' : 'Visit official site'}",
    "{isApprovedAffiliate ? 'Check verified offer' : 'Visit official site'}",
    "homepage CTA label",
)

replace_once(
    "{tool.affiliate_verified === true && <div className=\"mt-2 flex items-center justify-center gap-1 text-[10px] text-slate-600\"><CheckCircle2 className=\"h-3 w-3\" /> Affiliate link verified in our records · disclosure applies</div>}",
    "{isApprovedAffiliate && <div className=\"mt-2 flex items-center justify-center gap-1 text-[10px] text-slate-600\"><CheckCircle2 className=\"h-3 w-3\" /> Affiliate link verified in our records · disclosure applies</div>}",
    "homepage affiliate disclosure",
)

required = [
    "t.affiliate_status === 'approved_tracking'",
    "validUrl === tool.affiliate_url.trim()",
    "trackToolClick(tool.id, tool.name, validUrl, isApprovedAffiliate)",
    "data-cta={isApprovedAffiliate ? 'affiliate' : 'official'}",
    "{isApprovedAffiliate ? 'Check verified offer' : 'Visit official site'}",
    "{isApprovedAffiliate && <div",
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"home affiliate guard missing required marker: {marker}")

APP.write_text(text, encoding="utf-8")
print(f"guard_home_affiliate_state: changes={changes}; homepage affiliate status and GA4 attribution aligned")
