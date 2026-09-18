from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_TEACHABLE_OFFER_CARD -->"
LEGACY_MARKER = "<!-- COSHUMA_TEACHABLE_VERIFIED_OFFER -->"
TRIAL_URL = "https://partnerstack.teachable.com/COSHUMA"
ADMIN_URLS = (
    "https://dash.partnerstack.com",
    "https://partnerstack.com/dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# Remove the old internal-style marker if an earlier build left it behind.
html = html.replace(LEGACY_MARKER, MARKER)

def ensure_consumer_copy(document: str) -> str:
    # Keep network/approval/evidence mechanics out of the customer-facing card.
    replacements = (
        ("Vendor-issued 30-day trial", "30-day trial offer"),
        ("Open verified Teachable 30-day trial →", "Open Teachable 30-day trial →"),
        ("exact customer-facing extended-trial URL Teachable supplied to COSHUMA", "current 30-day trial offer link"),
    )
    for old, new in replacements:
        document = document.replace(old, new)
    return document

html = ensure_consumer_copy(html)

if MARKER in html:
    if TRIAL_URL not in html:
        raise SystemExit("Teachable offer card exists but the current 30-day trial URL is missing")
    if any(url in html for url in ADMIN_URLS):
        raise SystemExit("Administrative partner URL leaked into the public buyer hub")
    if "Affiliate disclosure:" not in html and 'data-affiliate-disclosure=' not in html:
        raise SystemExit("Teachable offer card is missing the required customer-facing affiliate disclosure")
    PAGE.write_text(html, encoding="utf-8")
    print("Teachable 30-day trial offer already surfaced with customer-only copy")
    raise SystemExit(0)

# Keep the page description useful without relying on a brittle exact previous string.
meta_copy = (
    "Compare SaaS free trials, pricing and current offers across popular software tools, "
    "including Teachable's current 30-day trial offer, before you pay."
)
html, meta_count = re.subn(
    r'(<meta\s+name="description"\s+content=")[^"]*("\s*/?>)',
    lambda m: m.group(1) + meta_copy + m.group(2),
    html,
    count=1,
    flags=re.I,
)
if meta_count != 1:
    raise SystemExit("Buyer-hub meta description is missing")

# Add Teachable to the structured list only when it is not already present.
if '"name":"Teachable"' not in html:
    itemlist_end = re.search(r'("itemListElement"\s*:\s*\[.*?)(\s*\]\s*\}\s*</script>)', html, flags=re.S)
    if itemlist_end:
        block = itemlist_end.group(1)
        positions = [int(v) for v in re.findall(r'"position"\s*:\s*(\d+)', block)]
        position = max(positions, default=0) + 1
        addition = (
            f', {{"@type":"ListItem","position":{position},"name":"Teachable",'
            '"url":"https://coshuma.com/best/teachable-30-day-free-trial.html"}'
        )
        html = html[:itemlist_end.start(1)] + block + addition + html[itemlist_end.end(1):]
    else:
        print("Buyer-hub ItemList layout changed; skipping optional Teachable structured-list insertion")

card = f'''      {MARKER}
      <article class="rounded-3xl border border-emerald-400/25 bg-[#11131a] p-7 space-y-5">
        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-emerald-300">Courses & digital products</div><h2 class="mt-1 text-3xl font-black text-white">Teachable</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">30-day trial offer</span></div>
        <p class="text-sm leading-6 text-slate-300">Teachable's public pricing page currently advertises a shorter standard trial. The offer link below currently provides a <strong class="text-white">30-day free trial</strong>. Offer availability can change, so confirm the trial length, eligibility and billing terms shown at the destination before signup.</p>
        <p data-affiliate-disclosure="true" class="text-[11px] leading-relaxed text-slate-500"><strong>Affiliate disclosure:</strong> COSHUMA may earn a commission if you purchase through this link, at no extra cost to you.</p>
        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="teachable" data-cta-source="current-offers-teachable-30day" data-cta-page="verified-software-free-trials-deals" href="{TRIAL_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-emerald-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-emerald-500">Open Teachable 30-day trial →</a><a href="/best/teachable-30-day-free-trial.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Teachable trial & pricing</a></div>
      </article>
'''

closing = re.search(
    r'(<section class="rounded-3xl border border-white/10 bg=\[#11131a\] p-7 md:p-9">\s*<h2 class="text-2xl font-black text-white">How this list is selected</h2>)',
    html,
)
if closing:
    html = html[:closing.start()] + card + html[closing.start():]
elif "</main>" in html:
    html = html.replace("</main>", card + "</main>", 1)
else:
    raise SystemExit("Buyer-hub main boundary missing; cannot safely place Teachable offer")

required = [
    TRIAL_URL,
    'data-cta-source="current-offers-teachable-30day"',
    "30-day free trial",
    "Affiliate disclosure:",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Teachable buyer-hub patch lost required token: {token}")
if any(url in html for url in ADMIN_URLS):
    raise SystemExit("Administrative partner URL leaked into the public buyer hub")

for forbidden in (
    "PartnerStack",
    "affiliate manager",
    "vendor-issued",
    "exact customer-facing",
    "no click, trial, signup, paid customer, commission, payout or revenue",
):
    # The allowed tracking URL itself contains the network domain, so strip URLs
    # before checking customer-facing prose.
    visible = html.replace(TRIAL_URL, "")
    if forbidden.lower() in visible.lower():
        raise SystemExit(f"Teachable buyer-hub customer copy still contains internal wording: {forbidden}")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced Teachable 30-day trial offer with customer-only disclosure")
