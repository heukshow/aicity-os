from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
TOOL_PAGE = PROJECT / "public" / "tool" / "jotform.html"
COMPARE_PAGE = PROJECT / "public" / "compare" / "unbounce-vs-jotform.html"
AI_AGENTS_URL = "https://www.jotform.com/ai/agents/?partner=coshuma"
HOMEPAGE_AFFILIATE_URL = "https://www.jotform.com/?partner=coshuma"
LEGACY_AFFILIATE_URL = "https://link.jotform.com/17STYVOunG?username=AnSangkwon"

updated = []


def patch_tool_page():
    if not TOOL_PAGE.exists():
        raise SystemExit(f"Missing expected Jotform tool page: {TOOL_PAGE}")

    html = TOOL_PAGE.read_text(encoding="utf-8")
    original = html

    # Jotform Affiliate Marketing Specialist Anna Scheucher directly confirmed on
    # 2026-09-07 that this is COSHUMA's customer-facing AI Agents partner link.
    # If an older onboarding-email redirect is already present, normalize it to the
    # direct confirmed URL instead of creating a second CTA.
    html = html.replace(LEGACY_AFFILIATE_URL, AI_AGENTS_URL)

    if AI_AGENTS_URL not in html:
        pattern = re.compile(
            r'(?P<anchor><a data-cta="official" href="https://www\.jotform\.com/"[^>]*>.*?</a>)',
            re.DOTALL,
        )
        match = pattern.search(html)
        if not match:
            raise SystemExit("Could not locate the Jotform official CTA anchor; refusing to guess an insertion point")

        replacement = f'''<div class="flex flex-col sm:flex-row gap-3">
            <a data-cta="affiliate" href="{AI_AGENTS_URL}" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 text-white text-center border border-purple-500 hover:bg-purple-500 transition-all flex items-center justify-center gap-2"><span>Try Jotform AI Agents</span><span>→</span></a>
            {match.group("anchor")}
          </div>
          <p data-affiliate-disclosure="jotform-ai" class="mt-3 text-[11px] leading-relaxed text-slate-400">Affiliate disclosure: COSHUMA may earn a commission if you sign up through the Jotform AI Agents link. The standard Jotform site button remains a non-affiliate official link.</p>'''
        html = html[: match.start()] + replacement + html[match.end() :]

    if html != original:
        TOOL_PAGE.write_text(html, encoding="utf-8")
        updated.append(str(TOOL_PAGE.relative_to(PROJECT)))


def patch_unbounce_comparison():
    if not COMPARE_PAGE.exists():
        return

    html = COMPARE_PAGE.read_text(encoding="utf-8")
    original = html

    # Anna Scheucher also directly confirmed COSHUMA's customer-facing homepage
    # partner URL. Use that verified route for generic "try Jotform" purchase-intent
    # CTAs while keeping the precise pricing-source button on the official pricing URL.
    hero_pattern = re.compile(
        r'<a data-cta="(?:official|affiliate)" data-tool-id="jotform" '
        r'data-cta-source="compare-unbounce-jotform-hero-jotform" '
        r'href="[^"]+" target="_blank" rel="[^"]+" '
        r'class="(?P<class>[^"]+)">.*?</a>'
    )
    hero_replacement = (
        f'<a data-cta="affiliate" data-tool-id="jotform" '
        f'data-cta-source="compare-unbounce-jotform-hero-jotform" '
        f'href="{HOMEPAGE_AFFILIATE_URL}" target="_blank" '
        f'rel="sponsored noopener noreferrer" class="px-7 py-4 rounded-xl border border-blue-500/40 bg-blue-500/10 hover:bg-blue-500/20 font-extrabold text-blue-200 transition-all">Try Jotform free →</a>'
    )
    html, hero_count = hero_pattern.subn(hero_replacement, html, count=1)
    if hero_count == 0 and 'data-cta-source="compare-unbounce-jotform-hero-jotform"' not in html:
        raise SystemExit("Could not locate the Jotform hero CTA on Unbounce vs Jotform; refusing to guess")

    old_disclosure = (
        "Affiliate disclosure: COSHUMA may earn a commission if an eligible Unbounce purchase is attributed "
        "through the partner link, at no extra cost to you."
    )
    new_disclosure = (
        "Affiliate disclosure: COSHUMA may earn a commission if an eligible Unbounce or Jotform signup/purchase "
        "is attributed through the partner links, at no extra cost to you."
    )
    html = html.replace(old_disclosure, new_disclosure)

    bottom_source = 'data-cta-source="compare-unbounce-jotform-bottom-jotform"'
    if bottom_source not in html:
        unbounce_bottom = re.compile(
            r'(?P<anchor><a data-cta="affiliate" data-tool-id="unbounce" '
            r'data-cta-source="compare-unbounce-jotform-bottom"[^>]*>.*?</a>)'
        )
        match = unbounce_bottom.search(html)
        if not match:
            raise SystemExit("Could not locate the Unbounce bottom CTA; refusing to guess Jotform insertion point")
        jotform_bottom = (
            f'\n          <a data-cta="affiliate" data-tool-id="jotform" '
            f'data-cta-source="compare-unbounce-jotform-bottom-jotform" '
            f'href="{HOMEPAGE_AFFILIATE_URL}" target="_blank" rel="sponsored noopener noreferrer" '
            f'class="flex-1 text-center py-3.5 px-4 rounded-xl border border-blue-500/40 bg-blue-500/10 hover:bg-blue-500/20 font-extrabold text-sm text-blue-200 transition-all">Try Jotform free →</a>'
        )
        html = html[: match.end()] + jotform_bottom + html[match.end() :]

    html = html.replace('"dateModified": "2026-09-07"', '"dateModified": "2026-09-09"')
    html = html.replace(
        'Buyer guide · Updated September 7, 2026',
        'Buyer guide · Updated September 9, 2026',
    )

    # Guardrails: the official pricing source remains non-affiliate, while generic
    # conversion CTAs use only the two direct partner URLs issued by Jotform.
    if HOMEPAGE_AFFILIATE_URL not in html:
        raise SystemExit("Verified Jotform homepage affiliate URL missing after comparison patch")
    if 'href="https://www.jotform.com/pricing/"' not in html:
        raise SystemExit("Jotform official pricing source disappeared during comparison patch")
    if bottom_source not in html:
        raise SystemExit("Jotform bottom affiliate CTA missing after comparison patch")

    if html != original:
        COMPARE_PAGE.write_text(html, encoding="utf-8")
        updated.append(str(COMPARE_PAGE.relative_to(PROJECT)))


patch_tool_page()
patch_unbounce_comparison()

if updated:
    print("Updated verified Jotform affiliate placements:")
    for path in updated:
        print(f" - {path}")
else:
    print("Verified Jotform affiliate placements already present")
