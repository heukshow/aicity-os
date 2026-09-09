"""Patch the high-impression Omnisend page with the latest verified affiliate state.

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
        '<span>Review pending</span>',
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
        raise SystemExit(f"Refusing uncertain Omnisend patch; source text missing: {old[:100]}")
    text = text.replace(old, new, 1)

marker = "<!-- COSHUMA_OMNISEND_2026_BUYER_DECISION -->"
if marker not in text:
    anchor = "        <!-- Alternatives & Direct Competitors Section -->"
    if anchor not in text:
        raise SystemExit("Refusing uncertain Omnisend patch; alternatives anchor missing")
    block = '''        <!-- COSHUMA_OMNISEND_2026_BUYER_DECISION -->
        <section class="rounded-2xl border border-cyan-500/25 bg-cyan-500/5 p-6 space-y-5">
          <div>
            <div class="text-[10px] font-extrabold uppercase tracking-[0.16em] text-cyan-300">2026 buyer decision · verified against Omnisend Help Center</div>
            <h2 class="mt-2 text-2xl font-black text-white">Start with contact count and channel needs, not the plan name</h2>
            <p class="mt-2 text-sm leading-relaxed text-slate-300">Omnisend pricing changes with billable contacts. The current Free plan supports up to 250 billable contacts and 500 emails per month. Standard starts at $16/month and includes email credits equal to 12× billable contacts. Pro starts at $59/month with unlimited email; for new paid subscriptions on or after May 4, 2026, SMS is a Pro add-on with volume pricing starting at $0.007 per SMS for US/Canada recipients.</p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="rounded-xl border border-white/10 bg-[#0d1018] p-4"><div class="text-xs font-bold text-slate-400">Free</div><div class="mt-1 text-xl font-black text-white">$0</div><p class="mt-2 text-xs leading-5 text-slate-400">Up to 250 billable contacts · 500 emails/month.</p></div>
            <div class="rounded-xl border border-white/10 bg-[#0d1018] p-4"><div class="text-xs font-bold text-slate-400">Standard</div><div class="mt-1 text-xl font-black text-white">From $16/mo</div><p class="mt-2 text-xs leading-5 text-slate-400">Email-focused plan; monthly email credits scale at 12× billable contacts.</p></div>
            <div class="rounded-xl border border-white/10 bg-[#0d1018] p-4"><div class="text-xs font-bold text-slate-400">Pro</div><div class="mt-1 text-xl font-black text-white">From $59/mo</div><p class="mt-2 text-xs leading-5 text-slate-400">Unlimited email. Current SMS access for new subscribers requires Pro plus SMS credits.</p></div>
          </div>
          <div class="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-sm leading-relaxed text-slate-300"><strong class="text-white">New-subscriber offer:</strong> Omnisend currently documents 30% off the first three months when a first-time paid subscriber chooses to pay three months upfront: Standard $11.20/month or Pro $41.30/month for that initial three-month period. Verify the live checkout before relying on the offer.</div>
          <div class="flex flex-col sm:flex-row gap-3">
            <a data-cta="official" data-tool-id="omnisend" data-cta-source="omnisend_2026_pricing" href="https://www.omnisend.com/pricing/" target="_blank" rel="noopener noreferrer" class="px-5 py-3.5 rounded-xl bg-slate-800 border border-slate-600 text-white font-extrabold text-center">Check current Omnisend pricing →</a>
            <a data-cta="affiliate" data-tool-id="moosend" data-cta-source="omnisend_verified_alternative" href="https://trymoo.moosend.com/6eappdpw04pw" target="_blank" rel="sponsored noopener noreferrer" class="px-5 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-center">Prefer a 30-day trial? Compare Moosend →</a>
          </div>
          <p class="text-[11px] leading-5 text-slate-500">COSHUMA was approved for the Omnisend Affiliate Program on September 9, 2026. The approval email did not contain an account-specific customer tracking URL, so Omnisend buttons intentionally remain ordinary official links until the exact Impact-issued URL is copied and verified. The Moosend button uses COSHUMA's separately verified customer-facing partner URL; COSHUMA may earn a commission on an eligible Moosend purchase at no extra cost to you.</p>
        </section>

'''
    text = text.replace(anchor, block + anchor, 1)

PAGE.write_text(text, encoding="utf-8")
print("Omnisend approval-aware Search Console monetization patch applied")
