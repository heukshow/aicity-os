from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "public" / "best" / "index.html"

text = HUB.read_text(encoding="utf-8")

# Revenue rationale:
# - COSHUMA already has a vendor-issued, customer-facing Claap PartnerStack URL.
# - Claap's official affiliate page confirms referrals using an affiliate link get
#   30% off the first 2 months on monthly plans or 10% off the first year annually.
# - The existing tool page is already responsible for the exact affiliate CTA;
#   this patch only improves internal discovery from the high-intent buyer hub.
# - Do not construct a pricing/deep-link wrapper or infer clicks, signups or revenue.

item_marker = '          {"@type":"ListItem","position":21,"url":"https://coshuma.com/tool/murf-ai.html","name":"Murf AI Free Plan & Pricing Guide"}'
item = '          {"@type":"ListItem","position":22,"url":"https://coshuma.com/tool/claap.html","name":"Claap Pricing & Referral Discount Guide"}'

if 'https://coshuma.com/tool/claap.html\",\"name\":\"Claap Pricing & Referral Discount Guide\"' not in text:
    if item_marker not in text:
        raise SystemExit("Murf ItemList marker not found; refusing unsafe Claap buyer-hub rewrite")
    text = text.replace(item_marker, item_marker + ',\n' + item, 1)

card_marker = '''          <a href="/best/databox-genie-ai-analyst.html" class="p-5 rounded-2xl bg-[#131520] border border-purple-500/25 hover:border-purple-400/60 transition-all">'''
card_block = '''          <a href="/tool/claap.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">AI meetings · verified partner route + referral discount</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Claap Pricing & Referral Discount</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Compare Claap's free/trial entry and plan fit, then use COSHUMA's verified referral route if it suits your workflow. Claap's official affiliate terms currently state 30% off the first 2 months on monthly plans or 10% off the first year annually.</p>
          </a>
'''

if 'href="/tool/claap.html" class="p-5 rounded-2xl' not in text:
    if card_marker not in text:
        raise SystemExit("Databox buyer-hub marker not found; refusing unsafe Claap card insertion")
    text = text.replace(card_marker, card_block + card_marker, 1)

required = [
    'https://coshuma.com/tool/claap.html\",\"name\":\"Claap Pricing & Referral Discount Guide\"',
    'href="/tool/claap.html"',
    '30% off the first 2 months',
    '10% off the first year',
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"Missing expected Claap buyer-hub marker: {marker}")

HUB.write_text(text, encoding="utf-8")
print("buyer-hub-claap-v1")
