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
            if updated != original:
                path.write_text(updated, encoding="utf-8")
                changed += 1
    print(f"polish_public_copy: scanned={scanned} changed={changed}")


if __name__ == "__main__":
    main()
