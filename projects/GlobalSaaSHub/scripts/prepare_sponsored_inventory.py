"""Prepare hidden sponsored-placement inventory without exposing ads yet.

The public runtime stays disabled by default. This script only creates reserved,
hidden containers in the highest-value buyer locations so COSHUMA can activate
specific campaigns later with one configuration switch and campaign data.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SCRIPT_TAG = '<script defer src="/sponsored-inventory.js"></script>'

SLOTS = {
    "tool": (
        "tool-primary",
        "Sponsored",
        "Sponsored option",
        "A paid promotional placement can appear here when this inventory is active.",
    ),
    "best": (
        "buyer-intent-top",
        "Sponsored",
        "Featured sponsored option",
        "A paid promotional placement can appear here when this inventory is active.",
    ),
    "compare": (
        "compare-decision-premium",
        "Sponsored",
        "Sponsored alternative",
        "A paid promotional placement can appear here when this inventory is active.",
    ),
}


def slot_html(kind: str) -> str:
    slot, label, title, body = SLOTS[kind]
    return (
        f'\n<section data-sponsored-slot="{slot}" hidden '
        'class="rounded-3xl border border-violet-500/25 bg-violet-500/5 p-6 space-y-3">\n'
        f'  <div data-sponsored-label class="text-[10px] uppercase tracking-[0.18em] font-black text-violet-300">{label}</div>\n'
        f'  <h2 data-sponsored-title class="text-xl font-extrabold text-white">{title}</h2>\n'
        f'  <p data-sponsored-body class="text-sm leading-6 text-slate-300">{body}</p>\n'
        '  <a data-sponsored-button href="#" class="inline-flex items-center justify-center rounded-xl bg-violet-600 px-5 py-3 text-sm font-extrabold text-white">Learn more →</a>\n'
        '</section>\n'
    )


def ensure_script(text: str) -> str:
    if '/sponsored-inventory.js' in text:
        return text
    if '</body>' in text:
        return text.replace('</body>', SCRIPT_TAG + '\n</body>', 1)
    return text


def insert_after_first_section(text: str, html: str) -> str:
    first = text.find('<section')
    if first < 0:
        return text
    end = text.find('</section>', first)
    if end < 0:
        return text
    end += len('</section>')
    return text[:end] + html + text[end:]


def insert_tool_slot(text: str, html: str) -> str:
    # Reserve the placement immediately after the first CTA-containing section.
    cta = text.find('data-cta=')
    if cta < 0:
        return insert_after_first_section(text, html)
    start = text.rfind('<section', 0, cta)
    if start < 0:
        return insert_after_first_section(text, html)
    end = text.find('</section>', cta)
    if end < 0:
        return insert_after_first_section(text, html)
    end += len('</section>')
    return text[:end] + html + text[end:]


def insert_compare_slot(text: str, html: str) -> str:
    # Prefer the final-decision area. Fall back to immediately before the last section.
    patterns = [
        r'<section\b[^>]*>.*?<h2\b[^>]*>\s*(?:Bottom line|Final verdict|Which should you choose|Which one should you choose)[^<]*</h2>',
        r'<section\b[^>]*>.*?<h3\b[^>]*>\s*(?:Bottom line|Final verdict)[^<]*</h3>',
    ]
    for pattern in patterns:
        matches = list(re.finditer(pattern, text, flags=re.I | re.S))
        if matches:
            pos = matches[-1].start()
            return text[:pos] + html + text[pos:]
    main_end = text.find('</main>')
    if main_end < 0:
        return text
    last_section = text.rfind('<section', 0, main_end)
    if last_section >= 0:
        return text[:last_section] + html + text[last_section:]
    return text[:main_end] + html + text[main_end:]


def prepare(path: Path, kind: str) -> bool:
    original = path.read_text(encoding='utf-8')
    if 'data-sponsored-slot=' in original:
        updated = ensure_script(original)
    else:
        html = slot_html(kind)
        if kind == 'tool':
            updated = insert_tool_slot(original, html)
        elif kind == 'best':
            updated = insert_after_first_section(original, html)
        else:
            updated = insert_compare_slot(original, html)
        updated = ensure_script(updated)
    if updated != original:
        path.write_text(updated, encoding='utf-8')
        return True
    return False


def main() -> None:
    totals = {}
    for kind in ('tool', 'best', 'compare'):
        folder = PUBLIC / kind
        changed = 0
        scanned = 0
        if folder.exists():
            for path in folder.glob('*.html'):
                scanned += 1
                if prepare(path, kind):
                    changed += 1
        totals[kind] = {'scanned': scanned, 'changed': changed}
    print(f"prepare_sponsored_inventory: {totals}; public runtime remains disabled")


if __name__ == '__main__':
    main()
