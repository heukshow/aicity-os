"""Polish generated public copy before production build.

This is intentionally conservative: it only rewrites known boilerplate strings and
removes a few generic claims that are not supported by product-specific evidence.
It is idempotent and leaves hand-written buyer guides untouched unless they contain
one of the exact legacy phrases below.
"""
from pathlib import Path
import re

PROJECT_DIR = Path(__file__).resolve().parents[1]
PUBLIC_DIR = PROJECT_DIR / "public"

TEXT_REPLACEMENTS = {
    "GlobalSaaSHub Editorial Rating": "COSHUMA review status",
    "GlobalSaaSHub": "COSHUMA",
    "Side-by-Side Head-to-Head Comparison": "Side-by-Side Comparison",
    "Decision Summary & Evidence": "Quick Take",
    "✓ Publicly Available Data": "Based on public vendor information",
    "Key Features & Capabilities": "Key Features",
    "Key Advantages (Pros)": "What stands out",
    "Considerations (Cons)": "Things to consider",
    "Pricing Plan": "Pricing",
    "Compare Alternatives": "See alternatives",
    "Back to All Tools": "Browse all tools",
    "Founder Verification": "Listing management",
    "Are you the founder of": "Manage the listing for",
    "Claim this official profile to update tool information, manage pricing details, and embed the verified rating badge on your website:":
        "If you represent this product, you can request listing updates and keep public product details accurate.",
    "Claiming a profile or purchasing sponsorship does not guarantee or alter editorial ratings or ranking positions.":
        "Listing management or sponsorship does not influence COSHUMA recommendations or ranking decisions.",
    "Global AI SaaS Decision Platform. All rights reserved.":
        "Independent AI & SaaS buyer guides. All rights reserved.",
    "Not yet editorially rated": "Review pending",
    "Editorial review in progress": "Review pending",
}

# Exact verified revenue routes that may safely replace a vendor homepage in
# generated comparison CTAs. Keep this list deliberately small and evidence-based.
VERIFIED_COMPARE_LINK_REPLACEMENTS = {
    '<a href="https://unbounce.com/" target="_blank" rel="noopener noreferrer"':
        '<a data-cta="affiliate" data-tool-id="unbounce" data-cta-source="compare-generated" href="https://unbounce.partnerlinks.io/5ubjnt8lluqi" target="_blank" rel="sponsored noopener noreferrer"',
    '<a href="https://brand24.com/" target="_blank" rel="noopener noreferrer"':
        '<a data-cta="affiliate" data-tool-id="brand24" data-cta-source="compare-generated" href="https://try.brand24.com/8xqrjxybmsbt" target="_blank" rel="sponsored noopener noreferrer"',
}

COMPARE_AFFILIATE_DISCLOSURE = (
    '      <p data-affiliate-disclosure="compare" class="text-[11px] leading-relaxed text-slate-500">'
    'Affiliate disclosure: Some buttons on this comparison use verified COSHUMA partner links. '
    'COSHUMA may earn a commission if you become a paying customer after using them, at no extra cost to you.'
    '</p>'
)

TOOL_SPONSORSHIP_INQUIRY = (
    '      <section data-sponsorship-inquiry="tool" class="mt-8 p-5 rounded-2xl bg-violet-500/5 border border-violet-500/20 space-y-3">\n'
    '        <div class="text-[10px] uppercase tracking-wider font-bold text-violet-300">Represent this product?</div>\n'
    '        <h2 class="text-lg font-extrabold text-white">Request a COSHUMA sponsored placement</h2>\n'
    '        <p class="text-xs text-slate-400 leading-relaxed">A one-time sponsored placement is USD 49. Sponsorship is reviewed separately from editorial coverage; payment does not guarantee acceptance, ranking, or an editorial rating.</p>\n'
    '        <a data-cta="sponsorship-inquiry" href="mailto:support@coshuma.com?subject=COSHUMA%20%2449%20sponsorship%20inquiry&amp;body=Product%20name%3A%0AWebsite%3A%0APlacement%20goal%3A%0A" class="inline-flex items-center justify-center px-5 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-extrabold transition-all">Email a sponsorship request →</a>\n'
    '        <p class="text-[10px] text-slate-500">This inquiry link does not create a charge.</p>\n'
    '      </section>'
)

# Some high-intent tool pages do not yet have a verified customer-facing affiliate
# URL for the searched vendor. In those cases, show one clearly framed, relevant
# alternative that does have a verified COSHUMA revenue route. Never substitute the
# alternative as if it were the searched vendor's own affiliate link.
TOOL_REVENUE_ALTERNATIVES = {
    "monday-com.html": {
        "headline": "Need an AI-first workspace instead?",
        "copy": "Monday.com is the work-management option on this page. If you want a lighter AI-native workspace with collaborative tasks, AI agents and automations, compare Taskade before choosing.",
        "tool_id": "taskade",
        "source": "monday-com-taskade-alternative",
        "href": "https://www.taskade.com/?via=7zzjo7",
        "label": "Compare Taskade →",
    },
    "time2book.html": {
        "headline": "Need CRM + appointment automation instead?",
        "copy": "Time2book is focused on fitness-business bookings. If you need a broader CRM with funnels, messaging and appointment workflows for an agency or service business, compare HighLevel before choosing.",
        "tool_id": "gohighlevel",
        "source": "time2book-highlevel-alternative",
        "href": "https://www.gohighlevel.com/?fp_ref=sangkwon56",
        "label": "Compare HighLevel →",
    },
}

# These lines are generic claims that can be misleading when applied to every product.
REMOVE_LINE_PATTERNS = [
    r"<li>Flexible pricing structure \([^<]*\)</li>",
    r"<li>Seamless workflow integration &amp; API support</li>",
    r"<li>Seamless workflow integration & API support</li>",
    r"<li>Requires active internet connection</li>",
    r"<li>Advanced features require premium tier subscription</li>",
]


def polish(text: str) -> str:
    for old, new in TEXT_REPLACEMENTS.items():
        text = text.replace(old, new)

    text = re.sub(
        r"Detailed breakdown of pricing, ratings, core capabilities, and decision recommendations to help you choose the best [^.]+ tool\.",
        "Compare pricing, core features, and practical fit to see which option makes more sense for your needs.",
        text,
    )

    text = re.sub(
        r"In-depth side-by-side comparison of ([^.]+)\. Compare pricing, features, ratings \([^)]*\), and find out which AI tool is best for your workflow\.",
        r"Compare \1 by pricing, core features, and practical fit to see which option better matches your workflow.",
        text,
    )

    text = re.sub(
        r"<title>([^<]+) Comparison, Pricing & Winner \(2026\) \| COSHUMA</title>",
        r"<title>\1 Comparison: Pricing, Features & Best Fit (2026) | COSHUMA</title>",
        text,
    )

    text = re.sub(
        r"<meta property=\"og:title\" content=\"([^\"]+) Comparison \(2026\) \| COSHUMA\" />",
        r'<meta property="og:title" content="\1 Comparison (2026) | COSHUMA" />',
        text,
    )

    text = re.sub(
        r"Visit ([^<]+) via Verified Affiliate Link",
        r"View \1 offer",
        text,
    )

    text = re.sub(
        r"Visit Official ([^<]+) Site",
        r"Visit \1",
        text,
    )

    text = re.sub(
        r"You prioritize Review pending, specialized feature set, and reliable industry workflow integration\.",
        "Its feature set looks closer to the workflow you need.",
        text,
    )
    text = re.sub(
        r"You prioritize ([^,]+), specialized feature set, and reliable industry workflow integration\.",
        r"Its feature set and published product details are the closer match for your workflow.",
        text,
    )
    text = re.sub(
        r"You want an alternative approach with ([^.]+) pricing structure and Review pending\.",
        r"Its pricing and workflow are the better fit for how you plan to use the product.",
        text,
    )
    text = re.sub(
        r"You want an alternative approach with ([^.]+) pricing structure and [^.]+\.",
        r"Its pricing and workflow are the better fit for how you plan to use the product.",
        text,
    )

    for pattern in REMOVE_LINE_PATTERNS:
        text = re.sub(pattern, "", text)

    text = text.replace("Official Documentation & Public Pricing Specs", "Official product and pricing pages")
    text = text.replace("Official Vendor Specifications & Benchmark Data", "Official product and pricing pages")
    text = text.replace("Official Embed Badge Code:", "Listing badge code:")
    text = text.replace("Verified on COSHUMA", "Listed on COSHUMA")
    text = text.replace("Featured on COSHUMA TOP AI", "Listed on COSHUMA")
    text = text.replace("⚡ Claim ", "Request updates for ")

    # Tidy whitespace left behind after conservative removals.
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    return text


def monetize_verified_compare_links(text: str) -> str:
    """Swap only exact, pre-verified vendor-homepage CTAs for revenue links."""
    for official_anchor, affiliate_anchor in VERIFIED_COMPARE_LINK_REPLACEMENTS.items():
        text = text.replace(official_anchor, affiliate_anchor)
    return text


def tag_existing_compare_disclosure(text: str) -> str:
    """Tag an existing human-written disclosure without rewriting its claims."""
    marker = text.find("Affiliate disclosure:")
    if marker < 0:
        return text

    candidates = [text.rfind(f"<{tag}", 0, marker) for tag in ("p", "section", "div")]
    start = max(candidates)
    if start < 0:
        return text

    end = text.find(">", start, marker)
    if end < 0:
        return text

    opening = text[start:end]
    if 'data-affiliate-disclosure="compare"' in opening:
        return text
    return text[:end] + ' data-affiliate-disclosure="compare"' + text[end:]


def ensure_compare_affiliate_disclosure(text: str) -> str:
    """Ensure every monetized comparison has one clearly tagged disclosure."""
    if 'data-cta="affiliate"' not in text:
        return text
    if 'data-affiliate-disclosure="compare"' in text:
        return text

    tagged = tag_existing_compare_disclosure(text)
    if tagged != text:
        return tagged

    # Generated pages may use different indentation; insert before the first closing main tag.
    return re.sub(
        r"(?=\s*</main>)",
        COMPARE_AFFILIATE_DISCLOSURE + "\n",
        text,
        count=1,
    )


def ensure_tool_revenue_alternative(text: str, filename: str) -> str:
    """Add one honest verified affiliate alternative to selected untracked vendor pages."""
    offer = TOOL_REVENUE_ALTERNATIVES.get(filename)
    if not offer or 'data-tool-revenue-alternative="true"' in text or "</main>" not in text:
        return text

    section = (
        '      <section data-tool-revenue-alternative="true" class="mt-8 p-5 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 space-y-3">\n'
        '        <div class="text-[10px] uppercase tracking-wider font-bold text-emerald-300">Buyer decision</div>\n'
        f'        <h2 class="text-lg font-extrabold text-white">{offer["headline"]}</h2>\n'
        f'        <p class="text-xs text-slate-300 leading-relaxed">{offer["copy"]}</p>\n'
        f'        <a data-cta="affiliate" data-tool-id="{offer["tool_id"]}" data-cta-source="{offer["source"]}" href="{offer["href"]}" target="_blank" rel="sponsored noopener noreferrer" class="inline-flex items-center justify-center px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-extrabold transition-all">{offer["label"]}</a>\n'
        '        <p class="text-[10px] text-slate-500">Affiliate disclosure: This alternative button uses a verified COSHUMA partner link. COSHUMA may earn a commission if you become a paying customer after using it, at no extra cost to you.</p>\n'
        '      </section>'
    )
    return re.sub(r"(?=\s*</main>)", section + "\n", text, count=1)


def ensure_tool_sponsorship_inquiry(text: str) -> str:
    """Keep a no-charge sponsorship lead path visible on every static tool profile."""
    if 'data-sponsorship-inquiry="tool"' in text:
        return text
    if "</main>" not in text:
        return text
    return re.sub(
        r"(?=\s*</main>)",
        TOOL_SPONSORSHIP_INQUIRY + "\n",
        text,
        count=1,
    )


def main() -> None:
    changed = 0
    scanned = 0
    for folder in (PUBLIC_DIR / "tool", PUBLIC_DIR / "compare"):
        if not folder.exists():
            continue
        for path in folder.glob("*.html"):
            scanned += 1
            original = path.read_text(encoding="utf-8")
            updated = polish(original)
            if folder.name == "tool":
                updated = ensure_tool_revenue_alternative(updated, path.name)
                updated = ensure_tool_sponsorship_inquiry(updated)
            if folder.name == "compare":
                updated = monetize_verified_compare_links(updated)
                updated = ensure_compare_affiliate_disclosure(updated)
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    print(f"polish_public_copy: scanned={scanned} changed={changed}")


if __name__ == "__main__":
    main()
