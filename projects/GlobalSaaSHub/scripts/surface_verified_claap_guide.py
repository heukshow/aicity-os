from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "public" / "best" / "index.html"

text = HUB.read_text(encoding="utf-8")

# Revenue rationale:
# - COSHUMA already has a vendor-issued, customer-facing Claap PartnerStack URL.
# - Claap's current first-party affiliate page confirms affiliate tracking and
#   commission when a referral converts, but its current English page does not
#   publish a specific buyer-discount amount. Do not advertise an unconfirmed deal.
# - The existing tool page is responsible for the exact affiliate CTA; this patch
#   only improves internal discovery from the high-intent buyer hub.
# - Do not construct a pricing/deep-link wrapper or infer clicks, signups or revenue.

item_marker = '          {"@type":"ListItem","position":21,"url":"https://coshuma.com/tool/murf-ai.html","name":"Murf AI Free Plan & Pricing Guide"}'
item = '          {"@type":"ListItem","position":22,"url":"https://coshuma.com/tool/claap.html","name":"Claap Pricing & Verified Partner Guide"}'

old_item_name = 'Claap Pricing & Referral Discount Guide'
if old_item_name in text:
    text = text.replace(old_item_name, 'Claap Pricing & Verified Partner Guide')

if 'https://coshuma.com/tool/claap.html\",\"name\":\"Claap Pricing & Verified Partner Guide\"' not in text:
    if item_marker not in text:
        raise SystemExit("Murf ItemList marker not found; refusing unsafe Claap buyer-hub rewrite")
    text = text.replace(item_marker, item_marker + ',\n' + item, 1)

card_marker = '''          <a href="/best/databox-genie-ai-analyst.html" class="p-5 rounded-2xl bg-[#131520] border border-purple-500/25 hover:border-purple-400/60 transition-all">'''
card_block = '''          <a href="/tool/claap.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">AI meetings · verified partner route</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Claap Pricing & Verified Partner Route</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Compare Claap's free/trial entry and plan fit, then continue through COSHUMA's vendor-verified customer tracking route if the workflow fits. Confirm final pricing and any buyer offer on Claap before purchase.</p>
          </a>
'''

old_card_start = '          <a href="/tool/claap.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">'
if old_card_start in text:
    start = text.index(old_card_start)
    end = text.index('          </a>', start) + len('          </a>\n')
    text = text[:start] + card_block + text[end:]
else:
    if card_marker not in text:
        raise SystemExit("Databox buyer-hub marker not found; refusing unsafe Claap card insertion")
    text = text.replace(card_marker, card_block + card_marker, 1)

required = [
    'https://coshuma.com/tool/claap.html\",\"name\":\"Claap Pricing & Verified Partner Guide\"',
    'href="/tool/claap.html"',
    'vendor-verified customer tracking route',
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"Missing expected Claap buyer-hub marker: {marker}")

for stale in ('30% off the first 2 months', '10% off the first year', 'Claap Pricing & Referral Discount'):
    if stale in text:
        raise SystemExit(f"Stale Claap buyer-discount claim remains in buyer hub: {stale}")

HUB.write_text(text, encoding="utf-8")
print("buyer-hub-claap-current-terms-v2")
