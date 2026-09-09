"""Apply the authoritative Omnisend approval copy after shared CTR patches.

Search Console snapshot: /tool/omnisend.html had 114 impressions and 0 clicks in
30 days. Omnisend approved COSHUMA on 2026-09-09, but no account-issued customer
tracking URL is verified yet, so Omnisend remains official-only. A clearly disclosed
Moosend alternative uses the already verified COSHUMA tracking URL.
"""
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "omnisend.html"
text = PAGE.read_text(encoding="utf-8")

replacements = [
    (
        "<title>Omnisend Pricing, Features & Review (2026) | COSHUMA</title>",
        "<title>Omnisend Review & Pricing 2026: Free Plan, $16 Standard & $59 Pro | COSHUMA</title>",
    ),
    (
        '<meta name="description" content="An advanced e-commerce marketing automation platform, integrating email, SMS, and push notifications to drive sales and customer retention.... Discover features, pricing (See official pricing), and official links for Omnisend on COSHUMA." />',
        '<meta name="description" content="Omnisend review and pricing for 2026: Free up to 250 billable contacts, Standard from $16/mo and Pro from $59/mo. Compare current email/SMS limits, the first-upgrade discount, and a verified Moosend alternative." />',
    ),
    (
        '<meta property="og:title" content="Omnisend Review & Pricing (2026) | COSHUMA" />',
        '<meta property="og:title" content="Omnisend Review & Pricing 2026: Free, Standard & Pro | COSHUMA" />',
    ),
    (
        '<meta property="og:description" content="An advanced e-commerce marketing automation platform, integrating email, SMS, and push notifications to drive sales and customer retention.... Check rating, pricing, and features." />',
        '<meta property="og:description" content="Compare Omnisend Free, Standard and Pro pricing, current 2026 send/SMS rules, and when a 30-day Moosend trial may be worth comparing." />',
    ),
    (
        '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Omnisend</h1>',
        '<h1 class="text-3xl md:text-4xl font-black text-white tracking-tight">Omnisend Review &amp; Pricing 2026</h1>',
    ),
    (
        '<span>Affiliate application submitted · tracking link not approved yet</span>',
        '<span>Affiliate approved · exact tracking link pending verification</span>',
    ),
    (
        "    </style>\n  </head>",
        "    </style>\n    <script defer src=\"/affiliate-attribution.js\"></script>\n  </head>",
    ),
    (
        '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">See official pricing</div>',
        '<div class="text-xl font-extrabold text-emerald-400 mt-0.5">Free · Standard from $16/mo · Pro from $59/mo</div>',
    ),
    (
        '<a data-cta="official" href="https://www.omnisend.com/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>Visit Omnisend</span><span>→</span></a>',
        '<a data-cta="official" data-tool-id="omnisend" data-cta-source="omnisend_pricing_bottom" href="https://www.omnisend.com/pricing/" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-slate-800 text-white text-center border border-slate-600 hover:bg-slate-700 transition-all flex items-center justify-center gap-2"><span>View Official Omnisend Pricing</span><span>→</span></a>',
    ),
]

for old, new in replacements:
    if new in text:
        continue
    if old not in text:
        # Shared CTR patch owns some of the same metadata and may already have
        # transformed the base source. Fail only where neither safe state exists.
        raise SystemExit(f"Refusing uncertain Omnisend approval patch; source text missing: {old[:100]}")
    text = text.replace(old, new, 1)

old_note = "COSHUMA's Omnisend affiliate application is already submitted, but an account-specific Omnisend customer tracking URL is not yet approved or verified, so Omnisend links remain ordinary official links. The Moosend button uses COSHUMA's separately verified customer-facing partner URL; COSHUMA may earn a commission on an eligible Moosend purchase at no extra cost to you."
new_note = "COSHUMA was approved for the Omnisend Affiliate Program on September 9, 2026. The approval email did not contain an account-specific customer tracking URL, so Omnisend buttons intentionally remain ordinary official links until the exact Impact-issued URL is copied and verified. The Moosend button uses COSHUMA's separately verified customer-facing partner URL; COSHUMA may earn a commission on an eligible Moosend purchase at no extra cost to you."
if new_note not in text:
    if old_note not in text:
        raise SystemExit("Refusing uncertain Omnisend approval patch; buyer-decision status note missing")
    text = text.replace(old_note, new_note, 1)

marker = "<!-- COSHUMA_OMNISEND_2026_BUYER_DECISION -->"
if marker not in text:
    raise SystemExit("Refusing uncertain Omnisend approval patch; shared buyer-decision block missing")

PAGE.write_text(text, encoding="utf-8")
print("Omnisend approval copy aligned after Search Console CTR patch")
