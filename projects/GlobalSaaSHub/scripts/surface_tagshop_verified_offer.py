from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TAGSHOP_VERIFIED_OFFER -->"
TRACKING_URL = "https://tagshop.ai?via=coshuma-22501e"
ADMIN_URL = "https://tagshop.firstpromoter.com/login"

def ensure_tool_partner_cta(tool_id, official_url, tracking_url, label, source):
    page = ROOT / "public" / "tool" / f"{tool_id}.html"
    if not page.exists():
        raise SystemExit(f"Missing tool page: {page}")

    page_html = page.read_text(encoding="utf-8")
    marker = f'data-cta-source="{source}"'
    partner = (
        f'<a data-cta="affiliate" data-tool-id="{tool_id}" '
        f'data-cta-source="{source}" href="{tracking_url}" target="_blank" '
        'rel="sponsored nofollow noopener noreferrer" '
        'class="px-6 py-3.5 rounded-xl font-extrabold text-sm bg-gradient-to-r '
        'from-purple-600 to-indigo-600 text-white text-center shadow-lg '
        'hover:brightness-110 transition-all flex items-center justify-center gap-2">'
        f'<span>{label}</span><span>→</span></a>'
    )
    disclosure = (
        '<p data-affiliate-disclosure="page" class="text-[11px] leading-5 text-slate-500">'
        '<strong>Affiliate disclosure:</strong> COSHUMA may earn a commission if you '
        'purchase through the partner link, at no extra cost to you.</p>'
    )
    official_link = (
        f'<a data-cta="official" href="{official_url}" target="_blank" '
        'rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl font-extrabold '
        'text-sm bg-slate-800 text-white text-center border border-slate-600 '
        'hover:bg-slate-700 transition-all flex items-center justify-center gap-2">'
        '<span>Visit official site</span><span>→</span></a>'
    )

    # Earlier and later build producers may promote the exact route, change the
    # source marker, or remove the explicit disclosure. Canonicalize the current
    # anchor on every pass so the second repeatability build repairs that drift.
    exact_partner = re.compile(
        r'(<a\b(?=[^>]*\bdata-cta="affiliate")(?=[^>]*\bhref="'
        + re.escape(tracking_url) + r'")[^>]*>.*?</a>)',
        flags=re.I | re.S,
    )
    exact_match = exact_partner.search(page_html)
    if exact_match:
        page_html = (
            page_html[:exact_match.start()] + partner + page_html[exact_match.end():]
        )
    else:
        official = re.compile(
            r'(<a\b(?=[^>]*\bdata-cta="official")(?=[^>]*\bhref="'
            + re.escape(official_url) + r'")[^>]*>.*?</a>)',
            flags=re.I | re.S,
        )
        page_html, count = official.subn(
            lambda _: partner + official_link, page_html, count=1
        )
        if count != 1:
            raise SystemExit(f"Could not place verified partner CTA on {tool_id}")

    exact_match = exact_partner.search(page_html)
    if not exact_match:
        raise SystemExit(f"Could not normalize verified partner CTA on {tool_id}")

    official = re.compile(
        r'<a\b(?=[^>]*\bdata-cta="official")(?=[^>]*\bhref="'
        + re.escape(official_url) + r'")[^>]*>.*?</a>',
        flags=re.I | re.S,
    )
    if not official.search(page_html):
        page_html = (
            page_html[:exact_match.end()] + official_link + page_html[exact_match.end():]
        )

    exact_match = exact_partner.search(page_html)
    disclosure_at = page_html.rfind(
        'data-affiliate-disclosure="page"', 0, exact_match.start()
    )
    if disclosure_at < 0:
        page_html = (
            page_html[:exact_match.start()] + disclosure + page_html[exact_match.start():]
        )

    affiliate_at = page_html.find(marker)
    disclosure_at = page_html.rfind('data-affiliate-disclosure="page"', 0, affiliate_at)
    required = [tracking_url, marker, 'data-cta="affiliate"', 'rel="sponsored']
    for token in required:
        if token not in page_html:
            raise SystemExit(f"{tool_id} tool CTA lost required token: {token}")
    if disclosure_at < 0:
        raise SystemExit(f"{tool_id} disclosure must appear before the partner CTA")

    page.write_text(page_html, encoding="utf-8")
    print(f"Verified {tool_id} partner CTA and disclosure")


ensure_tool_partner_cta(
    "tagshop-ai",
    "https://tagshop.ai/",
    TRACKING_URL,
    "Open Tagshop partner offer",
    "tagshop-tool-issued-referral",
)
ensure_tool_partner_cta(
    "tidio",
    "https://www.tidio.com/",
    "https://affiliate.tidio.com/7ow2khr31ti8",
    "Start with the Tidio partner link",
    "tidio-tool-issued-referral",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Idempotence + attribution safety: preserve the exact issued customer route.
# Consumer affiliate disclosures are allowed and required by the central public
# policy; internal admin/dashboard URLs must never be written into the page.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Tagshop buyer block exists but exact customer route is missing")
    if ADMIN_URL in html:
        raise SystemExit("Tagshop admin dashboard URL leaked into the public buyer hub")
    print("Tagshop buyer offer already surfaced")
    raise SystemExit(0)

item10 = (
    '      {"@type":"ListItem","position":10,"name":"Typedesk",'
    '"url":"https://coshuma.com/best/typedesk-pricing-free-plan.html"}\n'
    "    ]"
)
item11 = (
    '      {"@type":"ListItem","position":10,"name":"Typedesk",'
    '"url":"https://coshuma.com/best/typedesk-pricing-free-plan.html"},\n'
    '      {"@type":"ListItem","position":11,"name":"Tagshop AI",'
    '"url":"https://coshuma.com/best/tagshop-ai-free-trial-pricing.html"}\n'
    "    ]"
)
if item10 in html:
    html = html.replace(item10, item11, 1)
elif '"name":"Tagshop AI"' not in html:
    print("Buyer-hub ItemList layout changed; skipping optional Tagshop structured-list insertion")

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-fuchsia-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-fuchsia-300">AI UGC video ads</div><h2 class="mt-1 text-3xl font-black text-white">Tagshop AI</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">14-day trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">Tagshop's current official help center lists a <strong class="text-white">14-day free trial with full platform access and no credit card required</strong>. Check the current product and pricing terms before upgrading.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="tagshop-ai" data-cta-source="verified-deals-tagshop-issued-referral" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-fuchsia-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-fuchsia-500">Start Tagshop trial →</a><a href="/best/tagshop-ai-free-trial-pricing.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Read trial & pricing guide</a></div>\n      </article>\n'''

if closing in html:
    html = html.replace(closing, card + closing, 1)
elif "</main>" in html:
    print("Buyer-hub final grid boundary changed; using current main boundary for Tagshop card")
    html = html.replace("</main>", card + "</main>", 1)
else:
    raise SystemExit("Buyer-hub main boundary missing; cannot safely place Tagshop customer offer")

required = [
    TRACKING_URL,
    'data-cta-source="verified-deals-tagshop-issued-referral"',
    "14-day free trial with full platform access and no credit card required",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Tagshop buyer-hub patch lost required token: {token}")
if ADMIN_URL in html:
    raise SystemExit("Tagshop admin dashboard URL leaked into the public buyer hub")

# Keep downstream sequencing metadata customer-only. Disclosure normalization runs
# later and will guarantee one canonical disclosure before the first affiliate CTA.
HANDOFF_META = (
    "Compare current SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk and "
    "Tagshop AI. Check current product and pricing terms before choosing."
)
html = re.sub(
    r'(<meta\s+name="description"\s+content=")[^"]*("\s*/?>)',
    lambda m: m.group(1) + HANDOFF_META + m.group(2),
    html,
    count=1,
    flags=re.I,
)

PAGE.write_text(html, encoding="utf-8")
print("Surfaced Tagshop trial offer with customer-only copy")
