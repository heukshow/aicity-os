from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEST_DIR = ROOT / "public" / "best"
INDEX = BEST_DIR / "index.html"
START = "<!-- COSHUMA_BEST_DISCOVERY_LINKS_START -->"
END = "<!-- COSHUMA_BEST_DISCOVERY_LINKS_END -->"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")


def text(value: str) -> str:
    return html.unescape(TAG_RE.sub("", value)).strip()


def page_title(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    match = TITLE_RE.search(source) or H1_RE.search(source)
    if not match:
        return path.stem.replace("-", " ").title()
    title = text(match.group(1))
    title = re.sub(r"\s*\|\s*COSHUMA\s*$", "", title, flags=re.I)
    return title


def main() -> None:
    if not INDEX.exists():
        raise SystemExit("best/index.html is missing")

    source = INDEX.read_text(encoding="utf-8")
    # Remove the previously generated discovery block so each build is deterministic.
    source = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        "",
        source,
        flags=re.S,
    )

    already_linked = set(
        re.findall(r'href=["\'](/best/[^"\'#?]+\.html)["\']', source)
    )
    candidates = []
    for path in sorted(BEST_DIR.glob("*.html")):
        if path.name == "index.html":
            continue
        href = f"/best/{path.name}"
        if href in already_linked:
            continue
        candidates.append((page_title(path), href))

    candidates.sort(key=lambda item: item[0].lower())
    if not candidates:
        INDEX.write_text(source, encoding="utf-8")
        print("BEST INTERNAL LINKS: PASS (no orphan buyer guides)")
        return

    links = "".join(
        f'<a href="{html.escape(href, quote=True)}" class="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm font-bold text-slate-200 hover:border-purple-400/50 hover:text-white">{html.escape(title)}</a>'
        for title, href in candidates
    )
    block = f'''\n      {START}\n      <section class="space-y-4" aria-labelledby="more-buyer-guides">\n        <div>\n          <h2 id="more-buyer-guides" class="text-2xl md:text-3xl font-black text-white">More specialized buyer guides</h2>\n          <p class="text-sm text-slate-400 mt-2">Additional pricing, coupon and purchase-intent guides are linked here so buyers and search engines can discover them from the main buyer-guide hub.</p>\n        </div>\n        <nav aria-label="More COSHUMA buyer guides" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">{links}</nav>\n      </section>\n      {END}\n'''

    if "</main>" not in source:
        raise SystemExit("best/index.html has no </main> insertion point")
    source = source.replace("</main>", block + "    </main>", 1)
    INDEX.write_text(source, encoding="utf-8")
    print(f"BEST INTERNAL LINKS: PASS ({len(candidates)} orphan buyer guides linked)")


if __name__ == "__main__":
    main()
