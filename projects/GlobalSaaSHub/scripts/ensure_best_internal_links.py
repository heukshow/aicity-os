from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEST_DIR = ROOT / "public" / "best"
INDEX = BEST_DIR / "index.html"
B2B_GUIDE = BEST_DIR / "b2b-email-list-providers.html"
GAMMA_GUIDE = BEST_DIR / "gamma-free-plan-pricing.html"
BRAND24_GUIDE = BEST_DIR / "brand24-free-trial.html"
START = "<!-- COSHUMA_BEST_DISCOVERY_LINKS_START -->"
END = "<!-- COSHUMA_BEST_DISCOVERY_LINKS_END -->"
B2B_COMPARE_START = "<!-- COSHUMA_B2B_COMPARE_LINK_START -->"
B2B_COMPARE_END = "<!-- COSHUMA_B2B_COMPARE_LINK_END -->"
GAMMA_COMPARE_START = "<!-- COSHUMA_GAMMA_CANVA_COMPARE_LINK_START -->"
GAMMA_COMPARE_END = "<!-- COSHUMA_GAMMA_CANVA_COMPARE_LINK_END -->"
BRAND24_COMPARE_START = "<!-- COSHUMA_BRAND24_MENTION_COMPARE_LINK_START -->"
BRAND24_COMPARE_END = "<!-- COSHUMA_BRAND24_MENTION_COMPARE_LINK_END -->"

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


def ensure_b2b_comparison_link() -> bool:
    """Give the high-intent UpLead/Apollo comparison a contextual crawl path."""
    if not B2B_GUIDE.exists():
        return False

    source = B2B_GUIDE.read_text(encoding="utf-8")
    source = re.sub(
        re.escape(B2B_COMPARE_START) + r".*?" + re.escape(B2B_COMPARE_END),
        "",
        source,
        flags=re.S,
    )

    block = f'''\n    {B2B_COMPARE_START}\n    <section class="mt-8 rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.05] p-6 sm:p-7">\n      <div class="text-xs font-black uppercase tracking-[0.16em] text-emerald-300">Direct comparison</div>\n      <h2 class="mt-2 text-2xl font-black text-white">Choosing between UpLead and Apollo?</h2>\n      <p class="mt-3 max-w-3xl text-sm leading-7 text-slate-300">Use the dedicated comparison to check current pricing, credits, free access and the workflow difference between focused B2B contact data and a broader outbound sales platform.</p>\n      <a href="/compare/uplead-vs-apollo.html" class="mt-4 inline-flex rounded-xl border border-emerald-400/25 bg-emerald-400/10 px-5 py-3 text-sm font-black text-emerald-100 hover:bg-emerald-400/15">Compare UpLead vs Apollo →</a>\n    </section>\n    {B2B_COMPARE_END}\n'''

    fast_comparison = '<section class="mt-14 overflow-hidden'
    if fast_comparison in source:
        source = source.replace(fast_comparison, block + "\n    " + fast_comparison, 1)
    elif "</main>" in source:
        source = source.replace("</main>", block + "\n  </main>", 1)
    else:
        raise SystemExit("b2b-email-list-providers.html has no insertion point")

    B2B_GUIDE.write_text(source, encoding="utf-8")
    return True


def ensure_gamma_canva_comparison_link() -> bool:
    """Give the Gamma/Canva revenue comparison a contextual buyer-guide path."""
    if not GAMMA_GUIDE.exists():
        return False

    source = GAMMA_GUIDE.read_text(encoding="utf-8")
    source = re.sub(
        re.escape(GAMMA_COMPARE_START) + r".*?" + re.escape(GAMMA_COMPARE_END),
        "",
        source,
        flags=re.S,
    )

    block = f'''\n    {GAMMA_COMPARE_START}\n    <section class="mt-10 rounded-2xl border border-violet-400/20 bg-violet-400/[0.05] p-6 sm:p-7">\n      <div class="text-xs font-black uppercase tracking-[0.16em] text-violet-300">Compare before upgrading</div>\n      <h2 class="mt-2 text-2xl font-black text-white">Gamma or Canva for your next presentation?</h2>\n      <p class="mt-3 max-w-3xl text-sm leading-7 text-slate-300">Use the dedicated comparison to test the same presentation workflow across Gamma and Canva before paying. Gamma keeps COSHUMA's verified PartnerStack route; Canva remains an official non-affiliate comparison destination.</p>\n      <a href="/compare/gamma-vs-canva.html" class="mt-4 inline-flex rounded-xl border border-violet-400/25 bg-violet-400/10 px-5 py-3 text-sm font-black text-violet-100 hover:bg-violet-400/15">Compare Gamma vs Canva →</a>\n    </section>\n    {GAMMA_COMPARE_END}\n'''

    if "</main>" not in source:
        raise SystemExit("gamma-free-plan-pricing.html has no </main> insertion point")
    source = source.replace("</main>", block + "\n  </main>", 1)
    GAMMA_GUIDE.write_text(source, encoding="utf-8")
    return True


def ensure_brand24_mention_comparison_link() -> bool:
    """Route Brand24 trial shoppers to the new Brand24/Mention decision page."""
    if not BRAND24_GUIDE.exists():
        return False

    source = BRAND24_GUIDE.read_text(encoding="utf-8")
    source = re.sub(
        re.escape(BRAND24_COMPARE_START) + r".*?" + re.escape(BRAND24_COMPARE_END),
        "",
        source,
        flags=re.S,
    )

    block = f'''\n    {BRAND24_COMPARE_START}\n    <section class="mt-10 rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.05] p-6 sm:p-7">\n      <div class="text-xs font-black uppercase tracking-[0.16em] text-cyan-300">Compare before subscribing</div>\n      <h2 class="mt-2 text-2xl font-black text-white">Brand24 or Mention for social listening?</h2>\n      <p class="mt-3 max-w-3xl text-sm leading-7 text-slate-300">Use the dedicated comparison to check monitoring focus, trial routes and buyer fit before choosing a paid listening platform. Brand24 keeps COSHUMA's verified partner route; Mention remains an official non-affiliate destination until an exact COSHUMA tracking URL is verified.</p>\n      <a href="/compare/brand24-vs-mention.html" class="mt-4 inline-flex rounded-xl border border-cyan-400/25 bg-cyan-400/10 px-5 py-3 text-sm font-black text-cyan-100 hover:bg-cyan-400/15">Compare Brand24 vs Mention →</a>\n    </section>\n    {BRAND24_COMPARE_END}\n'''

    if "</main>" not in source:
        raise SystemExit("brand24-free-trial.html has no </main> insertion point")
    source = source.replace("</main>", block + "\n  </main>", 1)
    BRAND24_GUIDE.write_text(source, encoding="utf-8")
    return True


def main() -> None:
    if not INDEX.exists():
        raise SystemExit("best/index.html is missing")

    b2b_linked = ensure_b2b_comparison_link()
    gamma_linked = ensure_gamma_canva_comparison_link()
    brand24_linked = ensure_brand24_mention_comparison_link()

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
    status_parts = []
    if b2b_linked:
        status_parts.append("UpLead vs Apollo context link current")
    if gamma_linked:
        status_parts.append("Gamma vs Canva context link current")
    if brand24_linked:
        status_parts.append("Brand24 vs Mention context link current")
    suffix = "; " + "; ".join(status_parts) if status_parts else ""

    if not candidates:
        INDEX.write_text(source, encoding="utf-8")
        print(f"BEST INTERNAL LINKS: PASS (no orphan buyer guides{suffix})")
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
    print(f"BEST INTERNAL LINKS: PASS ({len(candidates)} orphan buyer guides linked{suffix})")


if __name__ == "__main__":
    main()
