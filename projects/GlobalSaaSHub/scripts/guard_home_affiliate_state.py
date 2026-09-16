from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "App.jsx"
text = APP.read_text(encoding="utf-8")
changes = 0


def replace_first(options, new: str, label: str, required: bool = True) -> None:
    global text, changes
    if new in text:
        return
    for old in options:
        if old in text:
            text = text.replace(old, new, 1)
            changes += 1
            return
    if required:
        raise SystemExit(f"home link guard could not find expected {label} pattern")


# Some earlier homepage passes intentionally remove vanity stats altogether.
# If the old affiliate-count stat still exists, convert it to a shopper-facing
# link count; otherwise do not recreate a stat just for affiliate operations.
customer_link_count = "const verified = toolsData.filter((t) => Boolean(getValidExternalUrl(t))).length;"
replace_first(
    [
        "const verified = toolsData.filter((t) =>\n      t.affiliate_verified === true &&\n      t.affiliate_status === 'approved_tracking' &&\n      typeof t.affiliate_url === 'string' &&\n      /^https?:\\/\\//i.test(t.affiliate_url.trim())\n    ).length;",
        "const verified = toolsData.filter((t) => t.affiliate_verified === true && t.affiliate_status === 'approved_tracking').length;",
        "const verified = toolsData.filter((t) => t.affiliate_verified === true).length;",
    ],
    customer_link_count,
    "homepage link count",
    required=False,
)

if 'Verified affiliate paths' in text:
    text = text.replace('Verified affiliate paths', 'Live vendor links', 1)
    changes += 1

strict_card = (
    "const validUrl = getValidExternalUrl(tool);\n"
    "              const isApprovedAffiliate = Boolean(\n"
    "                tool.affiliate_verified === true &&\n"
    "                tool.affiliate_status === 'approved_tracking' &&\n"
    "                typeof tool.affiliate_url === 'string' &&\n"
    "                validUrl === tool.affiliate_url.trim()\n"
    "              );"
)
replace_first(
    [
        "const isApprovedAffiliate = tool.affiliate_verified === true && tool.affiliate_status === 'approved_tracking';\n              const validUrl = getValidExternalUrl(tool);",
        "const validUrl = getValidExternalUrl(tool);",
    ],
    strict_card,
    "per-card approved affiliate predicate",
)

# Preserve tracking and sponsored-link semantics without exposing the mechanics
# in visible card copy.
legacy_pairs = [
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
        "{isApprovedAffiliate ? 'View offer' : 'Visit official site'}",
    ),
    (
        "{isApprovedAffiliate ? 'Check verified offer' : 'Visit official site'}",
        "{isApprovedAffiliate ? 'View offer' : 'Visit official site'}",
    ),
]
for old, new in legacy_pairs:
    if old in text:
        text = text.replace(old, new, 1)
        changes += 1

# Remove per-card affiliate-state commentary. The homepage keeps one concise
# general disclosure instead of repeating internal verification language.
for note in [
    '{tool.affiliate_verified === true && <div className="mt-2 flex items-center justify-center gap-1 text-[10px] text-slate-600"><CheckCircle2 className="h-3 w-3" /> Affiliate link verified in our records · disclosure applies</div>}',
    '{isApprovedAffiliate && <div className="mt-2 flex items-center justify-center gap-1 text-[10px] text-slate-600"><CheckCircle2 className="h-3 w-3" /> Affiliate link verified in our records · disclosure applies</div>}',
]:
    if note in text:
        text = text.replace(note, '', 1)
        changes += 1

plain_anchor = "<a href={validUrl} target=\"_blank\" rel={isApprovedAffiliate ? 'sponsored noopener noreferrer' : 'noopener noreferrer'} onClick={() => trackToolClick(tool.id, tool.name, validUrl, isApprovedAffiliate)} className=\"flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-indigo-500 px-4 py-3 text-sm font-black text-white shadow-lg shadow-violet-950/20 hover:from-violet-400 hover:to-indigo-400\">"
tracked_anchor = "<a data-cta={isApprovedAffiliate ? 'affiliate' : 'official'} data-tool-id={tool.id} data-cta-source=\"home-tool-card\" href={validUrl} target=\"_blank\" rel={isApprovedAffiliate ? 'sponsored noopener noreferrer' : 'noopener noreferrer'} onClick={() => trackToolClick(tool.id, tool.name, validUrl, isApprovedAffiliate)} className=\"flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-indigo-500 px-4 py-3 text-sm font-black text-white shadow-lg shadow-violet-950/20 hover:from-violet-400 hover:to-indigo-400\">"
if plain_anchor in text:
    text = text.replace(plain_anchor, tracked_anchor, 1)
    changes += 1
elif tracked_anchor not in text:
    raise SystemExit("home link guard could not find expected homepage outbound CTA")

required = [
    "tool.affiliate_status === 'approved_tracking'",
    "validUrl === tool.affiliate_url.trim()",
    "trackToolClick(tool.id, tool.name, validUrl, isApprovedAffiliate)",
    "data-cta={isApprovedAffiliate ? 'affiliate' : 'official'}",
    "{isApprovedAffiliate ? 'View offer' : 'Visit official site'}",
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"home link guard missing required marker: {marker}")

blocked_visible = [
    'Verified affiliate paths',
    'Check verified offer',
    'Affiliate link verified in our records',
]
for phrase in blocked_visible:
    if phrase in text:
        raise SystemExit(f"home link guard left internal customer copy: {phrase}")

APP.write_text(text, encoding="utf-8")
print(f"guard_home_affiliate_state: changes={changes}; tracking retained, shopper copy simplified")
