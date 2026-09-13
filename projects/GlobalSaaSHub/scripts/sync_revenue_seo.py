"""Restore curated search metadata after generation without touching body or CTAs."""
from pathlib import Path
from html import escape
import re

PUBLIC = Path(__file__).resolve().parents[1] / "public"
page = PUBLIC / "tool/tagshop-ai.html"
title = "Tagshop AI: AI Video Ads, Features & Pricing Guide | COSHUMA"
description = (
    "Explore Tagshop AI for UGC-style video ads from product URLs or scripts. "
    "Review features, compare alternatives and check official pricing before choosing."
)
text = page.read_text(encoding="utf-8")
head, body = text.split("</head>", 1)
replacements = [
    (r"<title>.*?</title>", f"<title>{escape(title)}</title>"),
    (r'<meta name="description" content="[^"]*"\s*/?>', f'<meta name="description" content="{escape(description)}" />'),
    (r'<meta property="og:title" content="[^"]*"\s*/?>', f'<meta property="og:title" content="{escape(title)}" />'),
    (r'<meta property="og:description" content="[^"]*"\s*/?>', f'<meta property="og:description" content="{escape(description)}" />'),
]
for pattern, replacement in replacements:
    head, count = re.subn(pattern, lambda _: replacement, head, flags=re.S)
    if count != 1:
        raise ValueError(f"Expected exactly one metadata field: {pattern}")
updated = head + "</head>" + body
if updated != text:
    page.write_text(updated, encoding="utf-8")
print("Curated Tagshop AI search metadata synchronized; body and CTAs preserved.")

# Give both existing Catalister comparisons a crawlable link from the profile.
page = PUBLIC / "tool/catalister.html"
text = page.read_text(encoding="utf-8")
links = []
for other, label in (("kinsta", "Kinsta"), ("quillbot", "QuillBot")):
    href = f"/compare/catalister-vs-{other}.html"
    if f'href="{href}"' not in text:
        if not (PUBLIC / href.lstrip("/")).is_file():
            raise ValueError(f"Missing comparison: {href}")
        links.append(f'<li><a href="{href}" class="text-purple-300 underline">Catalister vs {label}</a></li>')
if links:
    if text.count("</main>") != 1:
        raise ValueError("Expected one Catalister main closing anchor")
    section = '<nav aria-label="Catalister comparisons" class="mt-8"><h2 class="text-xl font-bold">Compare Catalister</h2><ul>' + "".join(links) + '</ul></nav>\n'
    page.write_text(text.replace("</main>", section + "</main>"), encoding="utf-8")
print("Catalister comparison internal links checked.")
