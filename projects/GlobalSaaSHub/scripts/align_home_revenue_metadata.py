from pathlib import Path

index = Path(__file__).resolve().parents[1] / "index.html"
text = index.read_text(encoding="utf-8")

replacements = [
    (
        '<title>COSHUMA | Compare AI & SaaS Pricing, Reviews & Alternatives</title>',
        '<title>COSHUMA | AI & SaaS Tools to Earn, Sell & Grow</title>',
    ),
    (
        '<meta name="description" content="Compare AI and SaaS tools by pricing, trials, use cases, strengths, alternatives and verified public information before you subscribe." />',
        '<meta name="description" content="Find AI and SaaS tools for getting leads, creating content, automating work and growing traffic. Compare pricing, free trials and verified offers before you choose." />',
    ),
    (
        '<meta property="og:title" content="COSHUMA | Compare AI & SaaS Pricing, Reviews & Alternatives" />',
        '<meta property="og:title" content="COSHUMA | AI & SaaS Tools to Earn, Sell & Grow" />',
    ),
    (
        '<meta property="og:description" content="Compare AI and SaaS tools by pricing, trials, use cases, strengths, alternatives and verified public information before you subscribe." />',
        '<meta property="og:description" content="Find tools for leads, content, automation and traffic growth, then compare pricing, trials and verified offers before choosing." />',
    ),
    (
        '"description": "Independent AI and SaaS decision guides covering pricing, trials, use cases, alternatives and verified public information."',
        '"description": "AI and SaaS decision guides for finding tools that can support lead generation, content creation, automation and business growth."',
    ),
    (
        '<h1 style="font-size: 30px; font-weight: 900; color: #c4b5fd;">COSHUMA — Compare AI & SaaS Before You Subscribe</h1>',
        '<h1 style="font-size: 30px; font-weight: 900; color: #c4b5fd;">COSHUMA — Find AI & SaaS Tools to Earn, Sell & Grow</h1>',
    ),
    (
        '<p style="font-size: 14px; color: #94a3b8; line-height: 1.7;">Independent buyer guides for AI software and business SaaS. Compare pricing, free trials, use cases, strengths, alternatives and verified public information before choosing a tool.</p>',
        '<p style="font-size: 14px; color: #94a3b8; line-height: 1.7;">Find tools for getting leads, creating content, automating work and growing traffic. Compare pricing, free trials and verified offers before choosing a tool.</p>',
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Homepage metadata markup changed; refusing unsafe replacement: {old[:90]}")
    text = text.replace(old, new, 1)

# Give crawlers a direct path to the newly monetized lead/payment workflow.
fillout_link = '<a href="/best/fillout-form-builder.html">Fillout for lead & payment forms</a> ·'
if fillout_link not in text:
    marker = '<strong>Recently verified partner buyer guides:</strong><br />'
    if marker not in text:
        raise SystemExit("Homepage fallback guide list changed; refusing unsafe Fillout insertion")
    text = text.replace(marker, marker + '\n          ' + fillout_link, 1)

index.write_text(text, encoding="utf-8")
print("Homepage revenue-first metadata, fallback copy and Fillout discovery path aligned")
