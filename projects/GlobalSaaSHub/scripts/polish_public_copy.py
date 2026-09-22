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

# Legacy programmatic tool pages used to embed a founder/listing administration
# panel in customer-facing HTML. Remove the whole panel rather than renaming its
# internal controls into softer public wording. The no-charge sponsorship inquiry
# below is a separate customer-facing lead path and is intentionally preserved.
LEGACY_LISTING_ADMIN_BLOCK = re.compile(
    r"\s*<!-- Claim Profile & Official Founder Badge Section -->\s*"
    r'<div class="p-6 rounded-2xl bg-\[#181a29\]/80 border border-purple-500/30 space-y-4">'
    r".*?</textarea>\s*</div>\s*</div>",
    re.S,
)
# A few hand-authored pages used a top-level section instead of the generic div.
# Limit this removal to one section with no nested section, and require both the
# exact admin marker and either the original paid profile-control CTA or the exact
# legacy normalization emitted by monetize_verified_compare_links.mjs. Ordinary
# customer-facing sponsorship inquiry sections cannot match because they do not
# contain the Founder Verification marker.
LEGACY_LISTING_ADMIN_SECTION = re.compile(
    r"\s*<section\b(?:(?!<section\b).)*?Founder\s+Verification"
    r"(?:(?!<section\b).)*?(?:Profile\s*\(\$49/yr\)|Request\s+\$49\s+sponsored\s+placement)"
    r"(?:(?!<section\b).)*?</section>",
    re.I | re.S,
)
CONTAINER_TAG = re.compile(r"<(/?)(div|section)\b[^>]*>", re.I)
FOUNDER_VERIFICATION = re.compile(r"Founder\s+Verification", re.I)
LISTING_ADMIN_SIGNAL = re.compile(
    r"Profile\s*\(\$49/yr\)"
    r"|Request\s+\$49\s+sponsored\s+placement"
    r"|Claim\s+this\s+official\s+profile"
    r"|Official\s+Embed\s+Badge\s+Code"
    r"|verified-badge\.svg"
    r"|manage\s+verified\s+business\s+information\s+and\s+badge\s+details",
    re.I,
)


def _container_spans(text: str):
    """Yield balanced div/section spans without trying to parse unrelated HTML."""
    stack: list[tuple[str, int]] = []
    for match in CONTAINER_TAG.finditer(text):
        closing, tag = match.group(1), match.group(2).lower()
        if not closing:
            stack.append((tag, match.start()))
            continue
        for index in range(len(stack) - 1, -1, -1):
            open_tag, start = stack[index]
            if open_tag != tag:
                continue
            del stack[index:]
            yield start, match.end()
            break


def remove_listing_admin_blocks(text: str) -> str:
    """Remove legacy listing-management panels, including hand-tailored variants.

    A block is removable only when one balanced div/section contains both the exact
    Founder Verification marker and a second listing-admin signal. The smallest such
    ancestor is removed, which avoids swallowing neighboring customer content.
    """
    text = LEGACY_LISTING_ADMIN_BLOCK.sub("", text)
    text = LEGACY_LISTING_ADMIN_SECTION.sub("", text)
    while True:
        marker = FOUNDER_VERIFICATION.search(text)
        if not marker:
            return text
        candidates = []
        for start, end in _container_spans(text):
            if not (start <= marker.start() < end):
                continue
            block = text[start:end]
            if FOUNDER_VERIFICATION.search(block) and LISTING_ADMIN_SIGNAL.search(block):
                candidates.append((end - start, start, end))
        if not candidates:
            return text
        _, start, end = min(candidates)
        text = text[:start] + text[end:]


TEXT_REPLACEMENTS = {
    "Global AI SaaS Decision Platform": "",
    "GlobalSaaSHub Editorial Rating": "Product information",
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
    "Global AI SaaS Decision Platform. All rights reserved.":
        "Independent AI & SaaS buyer guides. All rights reserved.",
    "Not yet editorially rated": "Product details",
    "Editorial review in progress": "Product details",
    "Review pending": "Product details",
}

# Exact verified revenue routes that may safely replace a vendor homepage in
# generated comparison CTAs. Keep this list deliberately small and evidence-based.
VERIFIED_COMPARE_LINK_REPLACEMENTS = {
    '<a href="https://unbounce.com/" target="_blank" rel="noopener noreferrer"':
        '<a data-cta="affiliate" data-tool-id="unbounce" data-cta-source="compare-generated" href="https://unbounce.partnerlinks.io/5ubjnt8lluqi" target="_blank" rel="sponsored noopener noreferrer"',
    '<a href="https://brand24.com/" target="_blank" rel="noopener noreferrer"':
        '<a data-cta="affiliate" data-tool-id="brand24" data-cta-source="compare-generated" href="https://try.brand24.com/8xqrjxybmsbt" target="_blank" rel="sponsored noopener noreferrer"',
}


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
    "ai-video-cut.html": {
        "headline": "Need a video-creation alternative now?",
        "copy": "AI Video Cut is the short-form clipping tool on this page. If you also need text-to-video creation, captions, stock-media workflows and highlight reels, compare Pictory. The Pictory offer link below can be used with promo code COSHUMA20; confirm the final price and eligibility before checkout.",
        "tool_id": "pictory",
        "source": "ai-video-cut-pictory-alternative",
        "href": "https://pictory.ai?fpr=sangkwon-an23",
        "label": "Compare Pictory + COSHUMA20 →",
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
    text = remove_listing_admin_blocks(text)

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
        r"You prioritize Product details, specialized feature set, and reliable industry workflow integration\.",
        "Its feature set looks closer to the workflow you need.",
        text,
    )
    text = re.sub(
        r"You prioritize ([^,]+), specialized feature set, and reliable industry workflow integration\.",
        r"Its feature set and published product details are the closer match for your workflow.",
        text,
    )
    text = re.sub(
        r"You want an alternative approach with ([^.]+) pricing structure and Product details\.",
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

    # Tidy whitespace left behind after conservative removals.
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    return text


def monetize_verified_compare_links(text: str) -> str:
    """Swap only exact, pre-verified vendor-homepage CTAs for revenue links."""
    for official_anchor, affiliate_anchor in VERIFIED_COMPARE_LINK_REPLACEMENTS.items():
        text = text.replace(official_anchor, affiliate_anchor)
    return text


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
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    print(f"polish_public_copy: scanned={scanned} changed={changed}")


if __name__ == "__main__":
    main()
