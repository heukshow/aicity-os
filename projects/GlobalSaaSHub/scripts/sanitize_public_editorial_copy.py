"""Final buyer-facing editorial copy pass.

Runs after the existing customer-only guards and immediately before Vite.
It removes internal affiliate/network/workflow language from public category,
methodology, buyer-hub and selected buyer-page copy without touching outbound URLs,
attribution attributes, required disclosure files, prices, trial terms or product facts.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

EXACT_HTML = {
    "This shortlist is generated from COSHUMA's existing product records. Verified partner status can affect link routing, but it does not determine editorial fit or imply a sale.":
        "This shortlist uses COSHUMA's product records to surface tools worth comparing for the use case above. Open each buyer guide to compare pricing, features and practical trade-offs.",
    "COSHUMA uses recorded product descriptions, pricing verification dates and official-source URLs from its dataset. Missing dates are shown as missing rather than guessed. Affiliate destinations are tracked separately from editorial pricing sources.":
        "COSHUMA uses recorded product descriptions, pricing check dates and official-source URLs. Missing dates are left missing rather than guessed.",
    "COSHUMA is an independent AI and SaaS buyer-guide site. Our goal is to make software decisions faster while keeping pricing evidence, affiliate tracking and editorial conclusions separate.":
        "COSHUMA is an AI and SaaS buyer-guide site. Our goal is to make software decisions faster by making pricing, product claims, trade-offs and source dates easier to check.",
    "Pages may show pricing, official-source or affiliate verification dates recorded in the dataset. COSHUMA does not backfill a date when no evidence exists.":
        "Pages may show pricing or official-source check dates when reliable evidence is available. COSHUMA does not invent a date when no evidence exists.",
    "Software pricing and partner programs change. Final terms should always be checked on the vendor site, and newer contradictory evidence should replace stale records instead of creating duplicate applications or links.":
        "Software pricing, trials and product terms change. Final terms should always be checked on the vendor site, and newer reliable evidence should replace stale information.",
    "How COSHUMA verifies pricing, public sources, affiliate links, comparisons and update dates.":
        "How COSHUMA checks pricing, public sources, comparisons and update dates.",
}

METHODOLOGY_AFFILIATE_BLOCK = re.compile(
    r'<div class="method"><h2 style="margin-top:0">3\. Affiliate-link separation</h2>'
    r'<p>.*?</p></div>',
    re.I | re.S,
)
METHODOLOGY_DISCLOSURE_BLOCK = re.compile(
    r'<section class="method"><strong>Affiliate disclosure:</strong>.*?</section>',
    re.I | re.S,
)

BUYER_HUB_META = (
    "Compare SaaS free trials, pricing and current offers across popular software "
    "tools before you pay. Check current terms, trial lengths and plan details."
)

JOTFORM_PATHS = (
    PUBLIC / 'tool' / 'jotform.html',
    PUBLIC / 'best' / 'jotform-pricing-free-plan.html',
)

JOTFORM_REPLACEMENTS = {
    "plus a verified Jotform AI Agents partner path for customer-support automation.":
        "plus Jotform AI Agents for customer-support automation.",
    "Revenue-ready partner path": "AI support use case",
    "See limits, buyer fit and verified Jotform partner paths.":
        "See limits, buyer fit and current Jotform options for forms and AI Agents.",
}


def clean_html(text: str) -> str:
    for old, new in EXACT_HTML.items():
        text = text.replace(old, new)
    text = METHODOLOGY_AFFILIATE_BLOCK.sub("", text)
    text = METHODOLOGY_DISCLOSURE_BLOCK.sub("", text)
    # Renumber the methodology cards after removing the internal affiliate card.
    text = text.replace('>4. Update dates</h2>', '>3. Update dates</h2>')
    text = text.replace('>5. Ratings and claims</h2>', '>4. Ratings and claims</h2>')
    text = text.replace('>6. Corrections</h2>', '>5. Corrections</h2>')
    return text


def clean_jotform(text: str) -> str:
    """Keep Jotform buyer pages focused on buyer decisions, not COSHUMA operations."""
    for old, new in JOTFORM_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def clean_buyer_hub(text: str) -> str:
    """Remove build/affiliate operations language after every offer injector ran."""
    text = re.sub(
        r'(<meta\s+name="description"\s+content=")[^"]*("\s*/?>)',
        lambda m: m.group(1) + BUYER_HUB_META + m.group(2),
        text,
        count=1,
        flags=re.I,
    )
    text = re.sub(
        r'(<meta\s+property="og:description"\s+content=")[^"]*("\s*/?>)',
        lambda m: m.group(1) + BUYER_HUB_META + m.group(2),
        text,
        count=1,
        flags=re.I,
    )
    text = text.replace(
        'Verified SaaS Free Trials & Partner Offers (2026) | COSHUMA',
        'SaaS Free Trials & Current Offers (2026) | COSHUMA',
    )
    text = text.replace(
        'Verified SaaS Free Trials & Partner Offers',
        'SaaS Free Trials & Current Offers',
    )
    text = text.replace(
        'Software free trials and partner offers worth testing before you pay',
        'Software free trials and current offers worth testing before you pay',
    )
    text = text.replace('How this list is gated', 'How this list is selected')
    text = text.replace('Verified customer links', 'Direct vendor links')
    text = text.replace('Direct partner confirmation · September 11', 'Trial and pricing options · September 11')
    text = text.replace('Exact partner-issued buyer routes', 'Compare before you pay')

    # Typedesk is injected after the earlier public-copy guard, so normalize its
    # buyer card here without changing the exact destination or Free-plan facts.
    text = re.sub(
        r'<p class="text-sm leading-6 text-slate-300">Typedesk\'s current official pricing page lists a Free plan for personal use with unlimited templates and up to 50 uses per week\..*?</p>',
        '<p class="text-sm leading-6 text-slate-300">Typedesk\'s current official pricing page lists a Free plan for personal use with unlimited templates and up to 50 uses per week. Compare the current plans and limits before upgrading.</p>',
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r'<p class="text-\[11px\] leading-5 text-slate-500">Typedesk told COSHUMA it currently provides no affiliate coupon code\..*?</p>',
        '<p class="text-[11px] leading-5 text-slate-500">No Typedesk coupon code is claimed on this guide. Check the current pricing page for the final plan price and terms.</p>',
        text,
        flags=re.I | re.S,
    )

    # Remove operations-only paragraphs even when they contain inline <strong>,
    # <code> or <a> tags. The tempered pattern never crosses a closing </p>, so
    # buyer-fact paragraphs next to them are preserved.
    ops_phrase = (
        r'customer-facing PartnerStack route|partner-side evidence|partner correspondence|'
        r'guessing referral parameters|existing affiliate account|'
        r"Jotform's affiliate team supplied|COSHUMA separates customer-facing tracking links"
    )
    text = re.sub(
        rf'<p\b[^>]*>(?:(?!</p>).)*(?:{ops_phrase})(?:(?!</p>).)*</p>',
        '',
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r'\s*A (?:visit|click|signup|trial)[^.]*?(?:commission|revenue|payout)[^.]*?partner-side evidence\.',
        '',
        text,
        flags=re.I,
    )
    return text


def clean_llms(text: str) -> str:
    text = re.sub(
        r'^> Independent AI and SaaS buyer guides.*$',
        '> Independent AI and SaaS buyer guides focused on pricing, trials, comparisons, buyer fit, and source-backed product information.',
        text,
        flags=re.M,
    )
    text = re.sub(
        r'^COSHUMA separates editorial product information from affiliate destinations\..*$',
        'Product prices, trial terms and product features can change. Use the linked vendor source on each guide to confirm final terms before purchase.',
        text,
        flags=re.M,
    )
    text = re.sub(
        r'^High-intent guides below prioritize concrete buying questions.*$',
        'High-intent guides below prioritize concrete buying questions such as free trials, pricing, discounts, alternatives and plan fit.',
        text,
        flags=re.M,
    )

    cleaned = []
    for raw in text.splitlines():
        line = raw
        if line.startswith('- https://'):
            # Keep buyer facts; remove internal network/routing/status explanations.
            line = re.sub(r"\s+using COSHUMA's[^\n]*$", "", line, flags=re.I)
            line = re.sub(r"\s+using COSHUMA[^\n]*$", "", line, flags=re.I)
            line = re.sub(r"\s+using the vendor-confirmed[^\n]*$", "", line, flags=re.I)
            line = re.sub(r"\s+and COSHUMA's exact issued[^\n]*$", "", line, flags=re.I)
            line = re.sub(r";\s*[^;\n]*(?:COSHUMA|PartnerStack|Cello|Impact|Dub|non-affiliate|partner route|affiliate route|referral route)[^\n]*$", "", line, flags=re.I)
            line = re.sub(r"\bverified\s+[A-Za-z0-9 ._-]{1,30}\s+partner[- ]route\s+guide\b", "buyer guide", line, flags=re.I)
            line = re.sub(r"\bverified\s+partner[- ]offer\b", "current offer", line, flags=re.I)
            line = re.sub(r"\bverified\s+COSHUMA20\s+offer\b", "COSHUMA20 offer", line, flags=re.I)
            line = re.sub(r"\bverified\s+Ambassador[- ]route\s+guide\b", "buyer guide", line, flags=re.I)
            line = re.sub(r"\bverified\s+partner[- ]route\s+guide\b", "buyer guide", line, flags=re.I)
            line = re.sub(r"\bverified\s+(?:customer\s+)?referral\s+route\b", "current offer", line, flags=re.I)
            line = re.sub(r"\bverified\s+affiliate\s+(?:ID|route|link)\b", "current vendor link", line, flags=re.I)
            line = re.sub(r"\s+and\s+(?:affiliate|partner|referral)-status\s+buyer guide\b", " buyer guide", line, flags=re.I)
            line = re.sub(r"\s+(?:and|with)\s+(?:current\s+)?(?:affiliate|partner|referral)-status\s+facts\b", "", line, flags=re.I)
            line = re.sub(r"\b(?:affiliate|partner|referral)-status\s+buyer guide\b", "buyer guide", line, flags=re.I)
            line = re.sub(r"\baffiliate-status\s+facts\b", "current product details", line, flags=re.I)
            line = line.replace(
                'How COSHUMA verifies public sources, affiliate links, pricing, and buyer-fit claims',
                'How COSHUMA checks public sources, pricing and buyer-fit claims',
            )
            line = re.sub(r"\s{2,}", " ", line).rstrip(' ;,')
        cleaned.append(line)
    return "\n".join(cleaned) + ("\n" if text.endswith("\n") else "")


def assert_customer_only(methodology: str, categories: list[str], llms: str, buyer_hub: str, jotform_pages: list[str]) -> None:
    public_editorial = " ".join([methodology, *categories])
    forbidden_html = re.compile(
        r'Affiliate-link separation|affiliate tracking|affiliate verification dates|'
        r'Verified partner status can affect link routing|Affiliate destinations are tracked separately|'
        r'duplicate applications or links',
        re.I,
    )
    forbidden_llms = re.compile(
        r'PartnerStack|Cello referral route|Impact (?:partner-)?route|Dub partner route|'
        r'verified partner route|verified affiliate route|verified customer referral route|'
        r'(?:affiliate|partner|referral)-status|non-affiliate|'
        r'signup, sale, commission or revenue event|'
        r'How COSHUMA verifies public sources, affiliate links',
        re.I,
    )
    forbidden_hub = re.compile(
        r'customer-facing PartnerStack route|partner-side evidence|partner correspondence|'
        r'guessing referral parameters|existing affiliate account|'
        r"Jotform's affiliate team supplied|COSHUMA separates customer-facing tracking links",
        re.I,
    )
    forbidden_jotform = re.compile(
        r'verified Jotform (?:AI Agents )?partner path|Revenue-ready partner path|verified Jotform partner paths',
        re.I,
    )
    if forbidden_html.search(public_editorial):
        raise RuntimeError('Internal affiliate/workflow copy remains in public editorial HTML')
    if forbidden_llms.search(llms):
        raise RuntimeError('Internal affiliate/network/status copy remains in public llms.txt')
    if forbidden_hub.search(buyer_hub):
        raise RuntimeError('Internal affiliate/network workflow copy remains in public buyer hub')
    if forbidden_jotform.search(' '.join(jotform_pages)):
        raise RuntimeError('Internal affiliate/partner copy remains in public Jotform buyer pages')


def main() -> None:
    changed = []
    category_paths = sorted((PUBLIC / 'category').glob('*.html'))
    methodology_path = PUBLIC / 'methodology.html'
    buyer_hub_path = PUBLIC / 'best' / 'verified-software-free-trials-deals.html'

    for path in [*category_paths, methodology_path]:
        if not path.exists():
            continue
        before = path.read_text(encoding='utf-8')
        after = clean_html(before)
        if after != before:
            path.write_text(after, encoding='utf-8')
            changed.append(path.relative_to(ROOT).as_posix())

    if buyer_hub_path.exists():
        before = buyer_hub_path.read_text(encoding='utf-8')
        after = clean_buyer_hub(before)
        if after != before:
            buyer_hub_path.write_text(after, encoding='utf-8')
            changed.append(buyer_hub_path.relative_to(ROOT).as_posix())

    for path in JOTFORM_PATHS:
        if not path.exists():
            continue
        before = path.read_text(encoding='utf-8')
        after = clean_jotform(before)
        if after != before:
            path.write_text(after, encoding='utf-8')
            changed.append(path.relative_to(ROOT).as_posix())

    llms_path = PUBLIC / 'llms.txt'
    if llms_path.exists():
        before = llms_path.read_text(encoding='utf-8')
        after = clean_llms(before)
        if after != before:
            llms_path.write_text(after, encoding='utf-8')
            changed.append(llms_path.relative_to(ROOT).as_posix())

    methodology = methodology_path.read_text(encoding='utf-8') if methodology_path.exists() else ''
    categories = [p.read_text(encoding='utf-8') for p in category_paths]
    buyer_hub = buyer_hub_path.read_text(encoding='utf-8') if buyer_hub_path.exists() else ''
    jotform_pages = [p.read_text(encoding='utf-8') for p in JOTFORM_PATHS if p.exists()]
    llms = llms_path.read_text(encoding='utf-8') if llms_path.exists() else ''
    assert_customer_only(methodology, categories, llms, buyer_hub, jotform_pages)
    print(f'Editorial customer-only copy: {len(changed)} files normalized')


if __name__ == '__main__':
    main()
