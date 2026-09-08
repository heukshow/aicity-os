from pathlib import Path

index = Path(__file__).resolve().parents[1] / "index.html"
text = index.read_text(encoding="utf-8")

replacements = [
    (
        '<title>COSHUMA | Compare AI & SaaS Pricing, Reviews & Alternatives</title>',
        '<title>COSHUMA | AI Tools You Can Use to Make Money</title>',
    ),
    (
        '<title>COSHUMA | AI & SaaS Tools to Earn, Sell & Grow</title>',
        '<title>COSHUMA | AI Tools You Can Use to Make Money</title>',
    ),
    (
        '<meta name="description" content="Compare AI and SaaS tools by pricing, trials, use cases, strengths, alternatives and verified public information before you subscribe." />',
        '<meta name="description" content="Find AI tools you can use to get leads, create content, sell online, automate work and grow traffic. Compare pricing, trials and verified offers before choosing." />',
    ),
    (
        '<meta name="description" content="Find AI and SaaS tools for getting leads, creating content, automating work and growing traffic. Compare pricing, free trials and verified offers before you choose." />',
        '<meta name="description" content="Find AI tools you can use to get leads, create content, sell online, automate work and grow traffic. Compare pricing, trials and verified offers before choosing." />',
    ),
    (
        '<meta property="og:title" content="COSHUMA | Compare AI & SaaS Pricing, Reviews & Alternatives" />',
        '<meta property="og:title" content="COSHUMA | AI Tools You Can Use to Make Money" />',
    ),
    (
        '<meta property="og:title" content="COSHUMA | AI & SaaS Tools to Earn, Sell & Grow" />',
        '<meta property="og:title" content="COSHUMA | AI Tools You Can Use to Make Money" />',
    ),
    (
        '<meta property="og:description" content="Compare AI and SaaS tools by pricing, trials, use cases, strengths, alternatives and verified public information before you subscribe." />',
        '<meta property="og:description" content="Choose AI tools for leads, content, online selling, automation and traffic growth, then compare pricing, trials and verified offers." />',
    ),
    (
        '<meta property="og:description" content="Find tools for leads, content, automation and traffic growth, then compare pricing, trials and verified offers before choosing." />',
        '<meta property="og:description" content="Choose AI tools for leads, content, online selling, automation and traffic growth, then compare pricing, trials and verified offers." />',
    ),
    (
        '"description": "Independent AI and SaaS decision guides covering pricing, trials, use cases, alternatives and verified public information."',
        '"description": "Guides to AI tools people can use for lead generation, content creation, online selling, automation and traffic growth, with pricing and offer comparisons."',
    ),
    (
        '"description": "AI and SaaS decision guides for finding tools that can support lead generation, content creation, automation and business growth."',
        '"description": "Guides to AI tools people can use for lead generation, content creation, online selling, automation and traffic growth, with pricing and offer comparisons."',
    ),
    (
        '<h1 style="font-size: 30px; font-weight: 900; color: #c4b5fd;">COSHUMA — Compare AI & SaaS Before You Subscribe</h1>',
        '<h1 style="font-size: 30px; font-weight: 900; color: #c4b5fd;">COSHUMA — Find AI Tools You Can Use to Make Money</h1>',
    ),
    (
        '<h1 style="font-size: 30px; font-weight: 900; color: #c4b5fd;">COSHUMA — Find AI & SaaS Tools to Earn, Sell & Grow</h1>',
        '<h1 style="font-size: 30px; font-weight: 900; color: #c4b5fd;">COSHUMA — Find AI Tools You Can Use to Make Money</h1>',
    ),
    (
        '<p style="font-size: 14px; color: #94a3b8; line-height: 1.7;">Independent buyer guides for AI software and business SaaS. Compare pricing, free trials, use cases, strengths, alternatives and verified public information before choosing a tool.</p>',
        '<p style="font-size: 14px; color: #94a3b8; line-height: 1.7;">Choose AI tools for getting leads, creating content, selling online, automating work and growing traffic. Compare pricing, free trials and verified offers before choosing.</p>',
    ),
    (
        '<p style="font-size: 14px; color: #94a3b8; line-height: 1.7;">Find tools for getting leads, creating content, automating work and growing traffic. Compare pricing, free trials and verified offers before choosing a tool.</p>',
        '<p style="font-size: 14px; color: #94a3b8; line-height: 1.7;">Choose AI tools for getting leads, creating content, selling online, automating work and growing traffic. Compare pricing, free trials and verified offers before choosing.</p>',
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old in text:
        text = text.replace(old, new, 1)

required = [
    'COSHUMA | AI Tools You Can Use to Make Money',
    'COSHUMA — Find AI Tools You Can Use to Make Money',
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"Homepage AI-money metadata missing after patch: {marker}")

# Give crawlers direct paths to the money-intent and lead/payment guides.
money_link = '<a href="/best/ai-tools-to-make-money.html"><strong>AI tools to make money</strong></a> ·'
fillout_link = '<a href="/best/fillout-form-builder.html">Fillout for lead & payment forms</a> ·'
marker = '<strong>Recently verified partner buyer guides:</strong><br />'
if marker not in text:
    raise SystemExit("Homepage fallback guide list changed; refusing unsafe discovery insertion")
if money_link not in text:
    text = text.replace(marker, marker + '\n          ' + money_link, 1)
if fillout_link not in text:
    text = text.replace(marker, marker + '\n          ' + fillout_link, 1)

index.write_text(text, encoding="utf-8")
print("Homepage metadata aligned to AI tools for making money, with money-intent discovery path")
