from pathlib import Path

root = Path(__file__).resolve().parents[1]
best_dir = root / "public" / "best"
best_dir.mkdir(parents=True, exist_ok=True)
page = best_dir / "fillout-form-builder.html"
tracking = "https://try.fillout.com/sang-kwon-an-hxwn"

# Preserve the curated buyer page instead of regenerating a lower-fidelity copy.
# Only enforce the verified revenue URL and attribution wiring.
if not page.exists():
    raise SystemExit("Fillout buyer page is missing; refusing to generate an unreviewed replacement")

text = page.read_text(encoding="utf-8")
if "Try Fillout free" not in text:
    raise SystemExit("Fillout buyer CTA changed; refusing unsafe patch")

# Normalize the primary CTA to the exact Dub-issued customer URL and attribution metadata.
import re
primary_pattern = re.compile(
    r'<a\s+[^>]*href="[^"]*"[^>]*>Try Fillout free →</a>',
    re.IGNORECASE,
)
primary_replacement = (
    f'<a data-cta="affiliate" data-tool-id="fillout" '
    f'data-cta-source="fillout_buyer_guide_primary" href="{tracking}" '
    'target="_blank" rel="sponsored noopener noreferrer" '
    'class="inline-flex min-h-12 items-center justify-center rounded-xl bg-violet-500 px-6 py-3 font-black text-white hover:bg-violet-400">'
    'Try Fillout free →</a>'
)
text, replacements = primary_pattern.subn(primary_replacement, text, count=1)
if replacements != 1:
    raise SystemExit("Could not normalize the Fillout primary CTA exactly once")

if '/affiliate-attribution.js' not in text:
    if "</body>" not in text:
        raise SystemExit("Fillout page body structure changed; refusing attribution injection")
    text = text.replace("</body>", '  <script defer src="/affiliate-attribution.js"></script>\n</body>', 1)

page.write_text(text, encoding="utf-8")

# Keep the revenue page discoverable from the buyer hub without replacing existing offers.
hub = best_dir / "verified-software-free-trials-deals.html"
if hub.exists():
    text = hub.read_text(encoding="utf-8")
    marker = "<!-- COSHUMA_FILLOUT_REVENUE_PATH -->"
    block = f'''\n<section class="mt-8 rounded-2xl border border-emerald-400/20 bg-emerald-400/5 p-6" id="fillout-leads">\n  {marker}\n  <div class="text-xs font-bold uppercase tracking-wider text-emerald-300">Lead & payment capture</div>\n  <h2 class="mt-2 text-2xl font-black text-white">Fillout: start with a real lead form for $0</h2>\n  <p class="mt-2 text-sm leading-6 text-slate-300">Use the free plan to test lead intake, applications or payment collection before deciding whether a paid tier is worth it.</p>\n  <div class="mt-4 flex flex-wrap gap-3"><a href="/best/fillout-form-builder.html" class="rounded-xl bg-white px-4 py-2.5 text-sm font-black text-slate-950">See Fillout buyer guide</a><a data-cta="affiliate" data-tool-id="fillout" data-cta-source="verified_offers_fillout" href="{tracking}" target="_blank" rel="sponsored noopener noreferrer" class="rounded-xl border border-emerald-400/30 bg-emerald-400/10 px-4 py-2.5 text-sm font-bold text-emerald-200">Try Fillout free</a></div>\n</section>\n'''
    if marker not in text:
        close = "</main>"
        if close not in text:
            raise SystemExit("Verified offers hub structure changed; refusing unsafe Fillout insertion")
        text = text.replace(close, block + close, 1)
    else:
        # Existing generated block must already have attribution metadata; fail instead of silently shipping an untracked CTA.
        if 'data-cta-source="verified_offers_fillout"' not in text:
            raise SystemExit("Existing Fillout buyer-hub block is missing attribution metadata")
    hub.write_text(text, encoding="utf-8")

# Add the page to the sitemap idempotently.
sitemap = root / "public" / "sitemap.xml"
if sitemap.exists():
    text = sitemap.read_text(encoding="utf-8")
    url = "https://coshuma.com/best/fillout-form-builder.html"
    if url not in text:
        entry = f'''  <url>\n    <loc>{url}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n'''
        if "</urlset>" not in text:
            raise SystemExit("Sitemap structure changed; refusing unsafe Fillout insertion")
        text = text.replace("</urlset>", entry + "</urlset>", 1)
        sitemap.write_text(text, encoding="utf-8")

# Fail fast if a future edit drops click attribution from either revenue surface.
rendered = page.read_text(encoding="utf-8")
if tracking not in rendered or '/affiliate-attribution.js' not in rendered or 'data-cta-source="fillout_buyer_guide_primary"' not in rendered:
    raise SystemExit("Fillout buyer-page revenue attribution wiring is missing")
if hub.exists():
    hub_text = hub.read_text(encoding="utf-8")
    if marker in hub_text and 'data-cta-source="verified_offers_fillout"' not in hub_text:
        raise SystemExit("Fillout buyer-hub affiliate CTA attribution wiring is missing")

print("Preserved Fillout buyer page and verified tracked revenue CTAs")
