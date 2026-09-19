from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    ROOT / "public/tool/semrush.html": {
        "needle": "/compare/semrush-vs-frase.html",
        "anchor": "<!-- Pricing & Action -->",
        "block": '''<section data-search-opportunity-link="frase-vs-semrush" class="p-5 rounded-2xl bg-purple-500/5 border border-purple-500/20 space-y-2">
<h2 class="text-lg font-bold text-white">Comparing Semrush with a content-first SEO tool?</h2>
<p class="text-sm text-slate-300">Frase focuses more tightly on research-to-brief-to-content optimization, while Semrush covers a broader SEO research stack. Compare current pricing and workflow fit side by side.</p>
<a href="/compare/semrush-vs-frase.html" class="text-sm font-bold text-purple-300 hover:text-purple-200">Frase vs Semrush pricing & workflow comparison →</a>
</section> ''',
    },
    ROOT / "public/tool/omnisend.html": {
        "needle": "/compare/privy-vs-omnisend.html",
        "anchor": "<section class=\"rounded-2xl bg-[#131520] border border-[#222538] p-6 space-y-4\"> <h2 class=\"text-2xl font-black text-white\">Compare before you upgrade</h2>",
        "block": '''<section data-search-opportunity-link="omnisend-vs-privy" class="rounded-2xl bg-emerald-500/5 border border-emerald-500/20 p-6 space-y-3">
<h2 class="text-2xl font-black text-white">Need stronger on-site pop-ups and capture?</h2>
<p class="text-sm leading-6 text-slate-300">Omnisend is the lower-risk start for a small list because it has a permanent Free plan. Privy is worth comparing when pop-ups, displays and on-site capture are the main job.</p>
<a href="/compare/privy-vs-omnisend.html" class="text-sm font-bold text-emerald-300 hover:text-emerald-200">Omnisend vs Privy: free plan, trial & pricing →</a>
</section> ''',
    },
}

changed = 0
for path, cfg in TARGETS.items():
    text = path.read_text(encoding="utf-8")
    if cfg["needle"] in text:
        continue
    if cfg["anchor"] not in text:
        raise SystemExit(f"Search-opportunity internal-link anchor missing: {path.name}")
    text = text.replace(cfg["anchor"], cfg["block"] + cfg["anchor"], 1)
    if cfg["needle"] not in text:
        raise SystemExit(f"Search-opportunity link insertion failed: {path.name}")
    path.write_text(text, encoding="utf-8")
    changed += 1

print(f"Search-opportunity reciprocal internal links strengthened: {changed}")
