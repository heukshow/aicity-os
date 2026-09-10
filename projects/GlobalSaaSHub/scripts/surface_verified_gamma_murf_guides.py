from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "public" / "best" / "index.html"

text = HUB.read_text(encoding="utf-8")

# Revenue rationale (evidence already stored in approved-tracking-2026-09-08.json):
# Gamma: vendor-issued PartnerStack route, 3 measured partner clicks / 0 signups.
# Murf AI: vendor-issued PartnerStack route, 4 measured partner clicks / 0 signups.
# Both existing tool pages already use exact verified customer-facing tracking URLs.
# This patch only improves internal discovery from the high-intent buyer-guide hub.

item_marker = '          {"@type":"ListItem","position":19,"url":"https://coshuma.com/tool/getgenie.html","name":"GetGenie Pricing & Free Plan Guide"}'
item_replacement = item_marker + ',\n' + '\n'.join([
    '          {"@type":"ListItem","position":20,"url":"https://coshuma.com/tool/gamma.html","name":"Gamma AI Free Plan & Pricing Guide"},',
    '          {"@type":"ListItem","position":21,"url":"https://coshuma.com/tool/murf-ai.html","name":"Murf AI Free Plan & Pricing Guide"}',
])

if 'https://coshuma.com/tool/gamma.html","name":"Gamma AI Free Plan & Pricing Guide"' not in text:
    if item_marker not in text:
        raise SystemExit("GetGenie ItemList marker not found; refusing unsafe buyer-hub rewrite")
    text = text.replace(item_marker, item_replacement, 1)

card_marker = '''          <a href="/best/databox-genie-ai-analyst.html" class="p-5 rounded-2xl bg-[#131520] border border-purple-500/25 hover:border-purple-400/60 transition-all">'''
card_block = '''          <a href="/tool/gamma.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">AI presentations · verified partner route</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Gamma AI Free Plan & Pricing</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Start with Gamma's no-card Free plan, compare Plus, Pro and Ultra, then use COSHUMA's verified customer referral route if the workflow fits.</p>
          </a>
          <a href="/tool/murf-ai.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">AI voice · verified partner route</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Murf AI Free Plan & Pricing</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Test Murf at $0 with no card, compare Creator and Business, then continue through COSHUMA's verified customer referral route if the voice quality fits.</p>
          </a>
'''

if 'href="/tool/gamma.html" class="p-5 rounded-2xl' not in text:
    if card_marker not in text:
        raise SystemExit("Databox buyer-hub marker not found; refusing unsafe card insertion")
    text = text.replace(card_marker, card_block + card_marker, 1)

required = [
    'https://coshuma.com/tool/gamma.html","name":"Gamma AI Free Plan & Pricing Guide"',
    'https://coshuma.com/tool/murf-ai.html","name":"Murf AI Free Plan & Pricing Guide"',
    'href="/tool/gamma.html"',
    'href="/tool/murf-ai.html"',
]
for marker in required:
    if marker not in text:
        raise SystemExit(f"Missing expected buyer-hub marker: {marker}")

HUB.write_text(text, encoding="utf-8")
print("buyer-hub-gamma-murf-v1")
