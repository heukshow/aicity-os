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

C04_CAMPAIGN_MARKER = 'data-campaign-asset="coshuma-one-month-growth-c04"'
C04_DECISION_ANCHOR = '<section class="p-7 rounded-3xl bg-[#131520] border border-[#222538] space-y-5"> <h2 class="text-3xl font-black text-white">Decision shortcuts</h2>'
C04_SECTION = '''<section id="jotform-upgrade-checklist" data-campaign-asset="coshuma-one-month-growth-c04" class="p-7 rounded-3xl bg-[#131520] border border-[#222538] space-y-5"> <div> <div class="text-xs uppercase tracking-widest text-emerald-300 font-bold">Upgrade worksheet</div> <h2 class="text-3xl font-black text-white mt-2">Choose a plan from your busiest month, not your average</h2> <p class="text-sm text-slate-400 mt-2">Write these numbers down privately before opening Jotform. COSHUMA does not collect or store your answers.</p> </div> <div class="overflow-x-auto"> <table class="w-full text-sm min-w-[760px]"> <thead class="text-left text-slate-400 border-b border-[#222538]"> <tr><th class="py-3 pr-4">Decision input</th><th class="py-3 pr-4">What to count</th><th class="py-3">Upgrade signal</th></tr> </thead> <tbody class="divide-y divide-[#222538] text-slate-300"> <tr><td class="py-4 pr-4 font-bold text-white">Active forms</td><td class="py-4 pr-4">Forms that must stay live at the same time</td><td class="py-4">Starter allows 5; compare the 25, 50 and 100-form paid limits when 5 is not enough.</td></tr> <tr><td class="py-4 pr-4 font-bold text-white">Peak monthly submissions</td><td class="py-4 pr-4">Completed responses across every form in your busiest recent month</td><td class="py-4">Starter allows 100. Pick the lowest tier that covers the peak with operating room.</td></tr> <tr><td class="py-4 pr-4 font-bold text-white">Payments and signatures</td><td class="py-4 pr-4">Payment submissions and signed documents, counted separately</td><td class="py-4">Starter includes 10 of each per month. Confirm the current paid-tier limits before upgrading.</td></tr> <tr><td class="py-4 pr-4 font-bold text-white">Branding</td><td class="py-4 pr-4">Whether customer-facing forms can retain Jotform branding</td><td class="py-4">A paid plan is required to remove Jotform branding.</td></tr> <tr><td class="py-4 pr-4 font-bold text-white">Compliance and team access</td><td class="py-4 pr-4">HIPAA requirements, multiple users, SSO or organization controls</td><td class="py-4">Gold and Enterprise offer optional HIPAA features; Enterprise is the multiuser plan.</td></tr> </tbody> </table> </div> <div class="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5 text-sm text-slate-300"><strong class="text-white">Selection rule:</strong> stay on Starter while every real limit fits and the branding is acceptable. Otherwise choose the lowest paid tier that clears your busiest-month form and submission needs plus any non-negotiable compliance or team requirement. AI Agent limits are separate from normal form limits.</div> <p data-affiliate-disclosure="section" class="text-[11px] leading-5 text-slate-500"><strong>Affiliate disclosure:</strong> COSHUMA may earn a commission if you upgrade through the tracked plan link, at no extra cost to you.</p> <div class="flex flex-col sm:flex-row gap-3"> <a data-cta="affiliate" data-tool-id="jotform" data-cta-source="jotform-c04-plan-checklist" href="https://www.jotform.com/pricing/?partner=coshuma" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-extrabold text-center">Check the plan that fits your numbers →</a> <a data-cta="official" href="https://www.jotform.com/help/408-understanding-your-account-usage-and-limits/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white text-sm font-extrabold text-center">Read Jotform's limit definitions →</a> </div> </section> '''

updated = []


def patch_tool_page():
    if not TOOL_PAGE.exists():
        raise SystemExit(f"Missing expected Jotform tool page: {TOOL_PAGE}")

    html = TOOL_PAGE.read_text(encoding="utf-8")
    original = html

    # Keep the exact AI Agents route for the AI-specific section, but the
    # general tool-guide hero should start from Jotform's vendor-confirmed homepage
    # route so form buyers can use Starter Free before considering an upgrade.
    html = html.replace(LEGACY_AFFILIATE_URL, AI_AGENTS_URL)
    hero_ai_pattern = re.compile(
        r'<a data-cta="affiliate"[^>]*data-cta-source="jotform-hero-(?:ai-agents|free)"[^>]*>.*?</a>',
        re.DOTALL,
    )
    hero_free = (
        f'<a data-cta="affiliate" data-tool-id="jotform" data-cta-source="jotform-hero-free" '
        f'href="{HOMEPAGE_AFFILIATE_URL}" target="_blank" rel="sponsored noopener noreferrer" '
        f'class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-purple-600 hover:bg-purple-500 text-white text-center transition-all">'
        'Open Jotform → Start Starter Free</a>'
    )
    html, hero_free_count = hero_ai_pattern.subn(hero_free, html, count=1)

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
          </div>'''
        html = html[: match.start()] + replacement + html[match.end() :]

    # Ayşe Dinçer, Jotform Team Lead / Affiliate Manager, directly supplied the
    # exact pricing destination below on 2026-09-10 and said COSHUMA can publish it
    # as provided. Convert pricing-intent CTAs only; do not synthesize deep links.
    hero_pricing_pattern = re.compile(
        r'<a data-cta="(?:official|affiliate)" (?:data-tool-id="jotform" )?'
        r'data-cta-source="jotform-hero-pricing" '
        r'href="[^"]+" target="_blank" rel="[^"]+" '
        r'class="(?P<class>[^"]+)">.*?</a>'
    )
    hero_pricing_replacement = (
        f'<a data-cta="affiliate" data-tool-id="jotform" data-cta-source="jotform-hero-pricing" '
        f'href="{PRICING_AFFILIATE_URL}" target="_blank" rel="sponsored noopener noreferrer" '
        f'class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 hover:bg-slate-700 text-white text-center border border-slate-600 transition-all">Compare Jotform plans →</a>'
    )
    html, hero_pricing_count = hero_pricing_pattern.subn(hero_pricing_replacement, html, count=1)

    bottom_pricing_pattern = re.compile(
        r'<a data-cta="(?:official|affiliate)" data-tool-id="jotform" '
        r'data-cta-source="jotform-bottom-pricing" href="[^"]+" target="_blank" rel="[^"]+" '
        r'class="(?P<class>[^"]+)">.*?</a>'
    )
    bottom_pricing_replacement = (
        f'<a data-cta="affiliate" data-tool-id="jotform" data-cta-source="jotform-bottom-pricing" '
        f'href="{PRICING_AFFILIATE_URL}" target="_blank" rel="sponsored noopener noreferrer" '
        f'class="px-6 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white text-sm font-extrabold text-center">Compare Jotform plans →</a>'
    )
    html, bottom_pricing_count = bottom_pricing_pattern.subn(bottom_pricing_replacement, html, count=1)
    if bottom_pricing_count == 0:
        bottom_pricing_pattern = re.compile(
            r'<a href="https://www\.jotform\.com/pricing/" target="_blank" rel="noopener noreferrer" '
            r'class="(?P<class>[^"]+)">Compare official Jotform plans →</a>'
        )
        html, bottom_pricing_count = bottom_pricing_pattern.subn(bottom_pricing_replacement, html, count=1)


    c04_pattern = re.compile(
        r'<section id="jotform-upgrade-checklist"[^>]*data-campaign-asset="coshuma-one-month-growth-c04"[^>]*>.*?</section> ',
        re.DOTALL,
    )
    if C04_CAMPAIGN_MARKER in html:
        html, c04_count = c04_pattern.subn(C04_SECTION, html, count=1)
        if c04_count != 1:
            raise SystemExit("Could not normalize the Jotform C04 decision worksheet")
    else:
        if C04_DECISION_ANCHOR not in html:
            raise SystemExit("Could not locate the Jotform decision-shortcuts anchor for C04")
        html = html.replace(C04_DECISION_ANCHOR, C04_SECTION + C04_DECISION_ANCHOR, 1)

    html = html.replace('"dateModified":"2026-09-07"', '"dateModified":"2026-10-04"')
    html = html.replace('Updated September 7, 2026', 'Updated October 4, 2026')
    if html.count(C04_CAMPAIGN_MARKER) != 1:
        raise SystemExit("Jotform C04 decision worksheet must appear exactly once")
    if 'data-cta-source="jotform-c04-plan-checklist"' not in html:
        raise SystemExit("Jotform C04 tracked pricing CTA missing")
    if 'href="https://www.jotform.com/help/408-understanding-your-account-usage-and-limits/"' not in html:
        raise SystemExit("Jotform official usage-limit source missing")


    if LEGACY_AFFILIATE_URL in html:
        raise SystemExit("Legacy Jotform onboarding redirect remained on the tool page")
    if AI_AGENTS_URL not in html:
        raise SystemExit("Verified Jotform AI Agents URL missing from tool page")
    if HOMEPAGE_AFFILIATE_URL not in html or 'data-cta-source="jotform-hero-free"' not in html:
        raise SystemExit("Verified Jotform free-start hero route missing from tool page")
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
