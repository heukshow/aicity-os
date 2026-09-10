from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
TOOL_PAGE = PROJECT / "public" / "tool" / "jotform.html"
COMPARE_PAGE = PROJECT / "public" / "compare" / "unbounce-vs-jotform.html"
BEST_PRICING_PAGE = PROJECT / "public" / "best" / "jotform-pricing-free-plan.html"
AI_AGENTS_URL = "https://www.jotform.com/ai/agents/?partner=coshuma"
HOMEPAGE_AFFILIATE_URL = "https://www.jotform.com/?partner=coshuma"
PRICING_AFFILIATE_URL = "https://www.jotform.com/pricing/?partner=coshuma"
LEGACY_AFFILIATE_URL = "https://link.jotform.com/17STYVOunG?username=AnSangkwon"

updated = []


def patch_tool_page():
    if not TOOL_PAGE.exists():
        raise SystemExit(f"Missing expected Jotform tool page: {TOOL_PAGE}")

    html = TOOL_PAGE.read_text(encoding="utf-8")
    original = html

    # Jotform Affiliate Marketing Specialist Anna Scheucher directly confirmed on
    # 2026-09-07 that this is COSHUMA's customer-facing AI Agents partner link.
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

    # Ayşe Dinçer, Jotform Team Lead / Affiliate Manager, directly supplied the
    # exact pricing destination below on 2026-09-10 and said COSHUMA can publish it
    # as provided. Convert pricing-intent CTAs only; do not synthesize deep links.
    hero_pricing_pattern = re.compile(
        r'<a data-cta="official" data-cta-source="jotform-hero-pricing" '
        r'href="https://www\.jotform\.com/pricing/" target="_blank" rel="noopener noreferrer" '
        r'class="(?P<class>[^"]+)">.*?</a>'
    )
    hero_pricing_replacement = (
        f'<a data-cta="affiliate" data-tool-id="jotform" data-cta-source="jotform-hero-pricing" '
        f'href="{PRICING_AFFILIATE_URL}" target="_blank" rel="sponsored noopener noreferrer" '
        f'class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 hover:bg-slate-700 text-white text-center border border-slate-600 transition-all">Compare Jotform plans →</a>'
    )
    html, hero_pricing_count = hero_pricing_pattern.subn(hero_pricing_replacement, html, count=1)

    bottom_pricing_pattern = re.compile(
        r'<a href="https://www\.jotform\.com/pricing/" target="_blank" rel="noopener noreferrer" '
        r'class="(?P<class>[^"]+)">Compare official Jotform plans →</a>'
    )
    bottom_pricing_replacement = (
        f'<a data-cta="affiliate" data-tool-id="jotform" data-cta-source="jotform-bottom-pricing" '
        f'href="{PRICING_AFFILIATE_URL}" target="_blank" rel="sponsored noopener noreferrer" '
        f'class="px-6 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white text-sm font-extrabold text-center">Compare Jotform plans →</a>'
    )
    html, bottom_pricing_count = bottom_pricing_pattern.subn(bottom_pricing_replacement, html, count=1)

    old_disclosure = (
        "Affiliate disclosure: the Jotform AI Agents button uses a customer-facing partner link supplied in COSHUMA's Jotform affiliate onboarding. "
        "COSHUMA may earn a commission from qualifying referrals. The pricing button is a non-affiliate official Jotform link."
    )
    new_disclosure = (
        "Affiliate disclosure: the AI Agents and pricing buttons use customer-facing Jotform partner routes directly confirmed for COSHUMA. "
        "COSHUMA may earn a commission from qualifying referrals at no extra cost to you."
    )
    html = html.replace(old_disclosure, new_disclosure)
    html = html.replace("Updated September 7, 2026", "Updated September 10, 2026")
    html = html.replace("shown on Jotform's official pricing page on September 7, 2026", "shown on Jotform's official pricing page on September 10, 2026")
    html = html.replace("As of September 7, 2026, Jotform lists", "As of September 10, 2026, Jotform lists")

    if LEGACY_AFFILIATE_URL in html:
        raise SystemExit("Legacy Jotform onboarding redirect remained on the tool page")
    if AI_AGENTS_URL not in html:
        raise SystemExit("Verified Jotform AI Agents URL missing from tool page")
    if PRICING_AFFILIATE_URL not in html:
        raise SystemExit("Vendor-confirmed Jotform pricing URL missing from tool page")
    if hero_pricing_count == 0 and 'data-cta-source="jotform-hero-pricing"' not in html:
        raise SystemExit("Jotform hero pricing CTA missing after patch")
    if bottom_pricing_count == 0 and 'data-cta-source="jotform-bottom-pricing"' not in html:
        raise SystemExit("Jotform bottom pricing CTA missing after patch")

    if html != original:
        TOOL_PAGE.write_text(html, encoding="utf-8")
        updated.append(str(TOOL_PAGE.relative_to(PROJECT)))


def patch_unbounce_comparison():
    if not COMPARE_PAGE.exists():
        return

    html = COMPARE_PAGE.read_text(encoding="utf-8")
    original = html

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

    if HOMEPAGE_AFFILIATE_URL not in html:
        raise SystemExit("Verified Jotform homepage affiliate URL missing after comparison patch")
    if 'href="https://www.jotform.com/pricing/"' not in html:
        raise SystemExit("Jotform official pricing source disappeared during comparison patch")
    if bottom_source not in html:
        raise SystemExit("Jotform bottom affiliate CTA missing after comparison patch")

    if html != original:
        COMPARE_PAGE.write_text(html, encoding="utf-8")
        updated.append(str(COMPARE_PAGE.relative_to(PROJECT)))


def patch_pricing_guide():
    if not BEST_PRICING_PAGE.exists():
        raise SystemExit(f"Missing expected Jotform pricing guide: {BEST_PRICING_PAGE}")

    html = BEST_PRICING_PAGE.read_text(encoding="utf-8")
    original = html

    # Ayşe Dinçer, Jotform Team Lead / Affiliate Manager, explicitly supplied this
    # exact customer-facing tracked pricing URL to COSHUMA on 2026-09-10 and said it
    # can be published as provided. Do not construct alternate pricing deep links.
    pricing_pattern = re.compile(
        r'<a data-cta="(?:official|affiliate)" data-tool-id="jotform" '
        r'data-cta-source="best-jotform-pricing-hero-(?:official|pricing)" '
        r'href="[^"]+" target="_blank" rel="[^"]+" '
        r'class="(?P<class>[^"]+)">.*?</a>'
    )
    pricing_replacement = (
        f'<a data-cta="affiliate" data-tool-id="jotform" '
        f'data-cta-source="best-jotform-pricing-hero-pricing" '
        f'href="{PRICING_AFFILIATE_URL}" target="_blank" '
        f'rel="sponsored noopener noreferrer" class="px-7 py-4 rounded-xl bg-slate-800 border border-slate-600 text-white font-bold text-center">Compare Jotform plans →</a>'
    )
    html, count = pricing_pattern.subn(pricing_replacement, html, count=1)
    if count == 0 and PRICING_AFFILIATE_URL not in html:
        raise SystemExit("Could not locate the Jotform pricing-guide CTA; refusing to guess")

    old_disclosure = (
        "Affiliate disclosure: the AI Agents button uses COSHUMA's verified customer-facing Jotform partner path. "
        "COSHUMA may earn a commission from qualifying referrals. The normal pricing button is an official non-affiliate link."
    )
    new_disclosure = (
        "Affiliate disclosure: both buttons use customer-facing Jotform partner routes that Jotform directly confirmed for COSHUMA. "
        "COSHUMA may earn a commission from qualifying referrals at no extra cost to you."
    )
    html = html.replace(old_disclosure, new_disclosure)
    html = html.replace('"dateModified":"2026-09-09"', '"dateModified":"2026-09-10"')
    html = html.replace('Pricing buyer guide · updated September 9, 2026', 'Pricing buyer guide · updated September 10, 2026')
    html = html.replace('shown on Jotform\'s official pricing page on September 9, 2026', 'shown on Jotform\'s official pricing page on September 10, 2026')
    html = html.replace('Sources checked September 9, 2026:', 'Sources checked September 10, 2026:')

    if PRICING_AFFILIATE_URL not in html:
        raise SystemExit("Vendor-confirmed Jotform pricing affiliate URL missing after pricing-guide patch")
    if 'data-cta-source="best-jotform-pricing-hero-pricing"' not in html:
        raise SystemExit("Tracked Jotform pricing CTA source marker missing")
    if 'href="https://www.jotform.com/pricing/" target="_blank" rel="noopener noreferrer">Jotform official pricing</a>' not in html:
        raise SystemExit("Non-affiliate official pricing source citation disappeared")

    if html != original:
        BEST_PRICING_PAGE.write_text(html, encoding="utf-8")
        updated.append(str(BEST_PRICING_PAGE.relative_to(PROJECT)))


patch_tool_page()
patch_unbounce_comparison()
patch_pricing_guide()

if updated:
    print("Updated verified Jotform affiliate placements:")
    for path in updated:
        print(f" - {path}")
else:
    print("Verified Jotform affiliate placements already present")
