from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "public" / "best" / "index.html"

text = HUB.read_text(encoding="utf-8")

# Revenue rationale:
# - COSHUMA already has a vendor-issued, customer-facing Claap PartnerStack URL.
# - Claap's current first-party affiliate page confirms affiliate tracking and
#   commission when a referral converts, but its current English page does not
#   publish a specific buyer-discount amount. Do not advertise an unconfirmed deal.
# - COSHUMA also has a verified Moosend PartnerStack route. Existing partner-side
#   evidence records 2 clicks / 0 signups / $0, so improving discovery of the
#   already-built 30-day trial buyer page is a low-cost conversion experiment.
# - Moosend's current first-party registration/terms evidence confirms a 30-day
#   free trial and no credit card required to get started.
# - Existing tool/buyer pages remain responsible for exact affiliate CTAs; this
#   patch only improves internal discovery from the high-intent buyer hub.
# - Do not construct pricing/deep-link wrappers or infer clicks, signups or revenue.

item_marker = '          {"@type":"ListItem","position":21,"url":"https://coshuma.com/tool/murf-ai.html","name":"Murf AI Free Plan & Pricing Guide"}'
item = '          {"@type":"ListItem","position":22,"url":"https://coshuma.com/tool/claap.html","name":"Claap Pricing & Verified Partner Guide"}'

old_item_name = 'Claap Pricing & Referral Discount Guide'
if old_item_name in text:
    text = text.replace(old_item_name, 'Claap Pricing & Verified Partner Guide')

if 'https://coshuma.com/tool/claap.html\",\"name\":\"Claap Pricing & Verified Partner Guide\"' not in text:
    if item_marker not in text:
        raise SystemExit("Murf ItemList marker not found; refusing unsafe Claap buyer-hub rewrite")
    text = text.replace(item_marker, item_marker + ',\n' + item, 1)

moosend_item_marker = '          {"@type":"ListItem","position":22,"url":"https://coshuma.com/tool/claap.html","name":"Claap Pricing & Verified Partner Guide"}'
moosend_item = '          {"@type":"ListItem","position":23,"url":"https://coshuma.com/best/moosend-free-trial.html","name":"Moosend 30-Day Free Trial & Pricing Guide"}'
if 'https://coshuma.com/best/moosend-free-trial.html\",\"name\":\"Moosend 30-Day Free Trial & Pricing Guide\"' not in text:
    if moosend_item_marker not in text:
        raise SystemExit("Claap ItemList marker not found; refusing unsafe Moosend buyer-hub rewrite")
    text = text.replace(moosend_item_marker, moosend_item_marker + ',\n' + moosend_item, 1)

card_marker = '''          <a href="/best/databox-genie-ai-analyst.html" class="p-5 rounded-2xl bg-[#131520] border border-purple-500/25 hover:border-purple-400/60 transition-all">'''
claap_card_block = '''          <a href="/tool/claap.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">AI meetings · verified partner route</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Claap Pricing & Verified Partner Route</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Compare Claap's free/trial entry and plan fit, then continue through COSHUMA's vendor-verified customer tracking route if the workflow fits. Confirm final pricing and any buyer offer on Claap before purchase.</p>
          </a>
'''

old_card_start = '          <a href="/tool/claap.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">'
if old_card_start in text:
    start = text.index(old_card_start)
    end = text.index('          </a>', start) + len('          </a>\n')
    text = text[:start] + claap_card_block + text[end:]
else:
    if card_marker not in text:
        raise SystemExit("Databox buyer-hub marker not found; refusing unsafe Claap card insertion")
    text = text.replace(card_marker, claap_card_block + card_marker, 1)

moosend_card_block = '''          <a href="/best/moosend-free-trial.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">Email marketing · verified partner route</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Moosend 30-Day Free Trial</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Use the 30-day no-card trial to test a real campaign and automation, then continue through COSHUMA's verified customer referral route only if the workflow fits.</p>
          </a>
'''

# A link to the Moosend guide already exists in the lower "specialized guides"
# section, so checking only for the href can produce a false positive. Require the
# actual high-intent card heading before skipping insertion.
moosend_card_heading = '<h3 class="text-lg font-extrabold text-white mt-2">Moosend 30-Day Free Trial</h3>'
if moosend_card_heading not in text:
    if card_marker not in text:
        raise SystemExit("Databox buyer-hub marker not found; refusing unsafe Moosend card insertion")
    text = text.replace(card_marker, moosend_card_block + card_marker, 1)

required = [
    'https://coshuma.com/tool/claap.html\",\"name\":\"Claap Pricing & Verified Partner Guide\"',
    'href="/tool/claap.html"',
    'vendor-verified customer tracking route',
    'https://coshuma.com/best/moosend-free-trial.html\",\"name\":\"Moosend 30-Day Free Trial & Pricing Guide\"',
    moosend_card_heading,
    '30-day no-card trial',
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"Missing expected buyer-hub marker: {marker}")

for stale in ('30% off the first 2 months', '10% off the first year', 'Claap Pricing & Referral Discount'):
    if stale in text:
        raise SystemExit(f"Stale Claap buyer-discount claim remains in buyer hub: {stale}")

HUB.write_text(text, encoding="utf-8")
print("buyer-hub-claap-moosend-current-terms-v4")
