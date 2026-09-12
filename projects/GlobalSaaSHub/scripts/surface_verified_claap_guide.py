from pathlib import Path
import re

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
# - Brand24's last healthy Search Console snapshot recorded 163 impressions / 0
#   clicks for /tool/brand24.html, while the verified PartnerStack evidence recorded
#   7 clicks / 0 signups / $0. Its current first-party pricing page confirms a
#   14-day free trial with no credit card required. Surface that concrete trial
#   value from the buyer hub without changing Brand24's verified affiliate URL.
# - HelpDesk has an existing verified customer-facing partner route, while the
#   newly published HelpDesk vs Freshdesk comparison keeps Freshdesk on official
#   non-affiliate URLs. Current first-party pages confirm both products advertise
#   14-day no-card trials. Surface the comparison from the high-intent hub without
#   creating or guessing any Freshdesk affiliate URL.
# - Existing tool/buyer pages remain responsible for exact affiliate CTAs; this
#   patch only improves internal discovery from the high-intent buyer hub.
# - Do not construct pricing/deep-link wrappers or infer clicks, signups or revenue.


def ensure_item_after(anchor_url, target_url, target_name, error_label):
    global text
    identity = f'{target_url}\",\"name\":\"{target_name}\"'
    if identity in text:
        return

    pattern = re.compile(
        r'(?P<indent>[ \t]*)\{"@type":"ListItem","position":(?P<position>\d+),"url":"'
        + re.escape(anchor_url)
        + r'","name":"[^"]+"\}'
    )
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"{error_label} ItemList marker not found; refusing unsafe buyer-hub rewrite")

    positions = [int(value) for value in re.findall(r'"position":(\d+)', text)]
    next_position = max(positions, default=0) + 1
    item_marker = match.group(0)
    indent = match.group('indent')
    item = f'{indent}{{"@type":"ListItem","position":{next_position},"url":"{target_url}","name":"{target_name}"}}'
    text = text.replace(item_marker, item_marker + ',\n' + item, 1)


old_item_name = 'Claap Pricing & Referral Discount Guide'
if old_item_name in text:
    text = text.replace(old_item_name, 'Claap Pricing & Verified Partner Guide')

ensure_item_after(
    'https://coshuma.com/tool/murf-ai.html',
    'https://coshuma.com/tool/claap.html',
    'Claap Pricing & Verified Partner Guide',
    'Murf',
)
ensure_item_after(
    'https://coshuma.com/tool/claap.html',
    'https://coshuma.com/best/moosend-free-trial.html',
    'Moosend 30-Day Free Trial & Pricing Guide',
    'Claap',
)
ensure_item_after(
    'https://coshuma.com/best/moosend-free-trial.html',
    'https://coshuma.com/best/helpdesk-vs-freshdesk.html',
    'HelpDesk vs Freshdesk Pricing & Free Trial Comparison',
    'Moosend',
)

# Keep Brand24's existing URL/position but make the structured name match the
# concrete high-intent value already present on the destination page.
text = text.replace(
    '"url":"https://coshuma.com/best/brand24-ai-visibility.html","name":"Brand24 AI Visibility Review"',
    '"url":"https://coshuma.com/best/brand24-ai-visibility.html","name":"Brand24 14-Day Free Trial & AI Visibility Guide"',
    1,
)

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

helpdesk_card_block = '''          <a href="/best/helpdesk-vs-freshdesk.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">Customer support · verified HelpDesk route</div>
            <h3 class="text-lg font-extrabold text-white mt-2">HelpDesk vs Freshdesk</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Compare current pricing, AI allowances and 14-day no-card trials. HelpDesk uses COSHUMA's verified customer partner route; Freshdesk remains on official non-affiliate links.</p>
          </a>
'''
helpdesk_card_heading = '<h3 class="text-lg font-extrabold text-white mt-2">HelpDesk vs Freshdesk</h3>'
if helpdesk_card_heading not in text:
    if card_marker not in text:
        raise SystemExit("Databox buyer-hub marker not found; refusing unsafe HelpDesk comparison card insertion")
    text = text.replace(card_marker, helpdesk_card_block + card_marker, 1)

brand24_old_card = '''          <a href="/best/brand24-ai-visibility.html" class="p-5 rounded-2xl bg-[#131520] border border-purple-500/25 hover:border-purple-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-purple-300">AI visibility</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Brand24 AI Visibility</h3>
            <p class="text-sm text-slate-400 mt-2 leading-relaxed">A buyer-focused look at AI visibility and GEO tracking before adding it to a monitoring stack.</p>
          </a>
'''
brand24_card = '''          <a href="/best/brand24-ai-visibility.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">AI visibility · verified partner route</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Brand24 14-Day Trial & AI Visibility</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Test Brand24 for 14 days with no credit card, then evaluate AI Visibility and continue through COSHUMA's verified customer referral route only if the monitoring workflow fits.</p>
          </a>
'''
if brand24_card not in text:
    if brand24_old_card not in text:
        raise SystemExit("Brand24 buyer-hub card shape changed; refusing uncertain rewrite")
    text = text.replace(brand24_old_card, brand24_card, 1)

required = [
    'https://coshuma.com/tool/claap.html\",\"name\":\"Claap Pricing & Verified Partner Guide\"',
    'href="/tool/claap.html"',
    'vendor-verified customer tracking route',
    'https://coshuma.com/best/moosend-free-trial.html\",\"name\":\"Moosend 30-Day Free Trial & Pricing Guide\"',
    moosend_card_heading,
    '30-day no-card trial',
    'https://coshuma.com/best/helpdesk-vs-freshdesk.html\",\"name\":\"HelpDesk vs Freshdesk Pricing & Free Trial Comparison\"',
    helpdesk_card_heading,
    'HelpDesk uses COSHUMA\'s verified customer partner route; Freshdesk remains on official non-affiliate links.',
    'https://coshuma.com/best/brand24-ai-visibility.html\",\"name\":\"Brand24 14-Day Free Trial & AI Visibility Guide\"',
    '<h3 class="text-lg font-extrabold text-white mt-2">Brand24 14-Day Trial & AI Visibility</h3>',
    'Test Brand24 for 14 days with no credit card',
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"Missing expected buyer-hub marker: {marker}")

for stale in ('30% off the first 2 months', '10% off the first year', 'Claap Pricing & Referral Discount'):
    if stale in text:
        raise SystemExit(f"Stale Claap buyer-discount claim remains in buyer hub: {stale}")

HUB.write_text(text, encoding="utf-8")
print("buyer-hub-claap-moosend-brand24-helpdesk-current-terms-v7")