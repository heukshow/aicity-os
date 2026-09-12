from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "public" / "best" / "index.html"
TOOL = ROOT / "public" / "tool" / "kittl.html"
LLMS = ROOT / "public" / "llms.txt"
SLUG = "/best/kittl-commercial-use-license.html"

# Revenue rationale:
# - Kittl already has an authenticated, account-specific Impact tracking URL in
#   approved-tracking evidence. This patch does not create or alter that URL.
# - A dedicated Kittl commercial-use guide already exists and already contains
#   disclosed verified affiliate CTAs, but repository search found no internal
#   links to that exact guide from the buyer hub or Kittl product page.
# - Kittl first-party pricing/licensing/help pages rechecked 2026-09-10 state:
#   Free is personal-use only; Pro and Expert include commercial use up to
#   500,000 copies per design; Max removes that copy limit.
# - This patch only improves discovery of the existing high-intent guide. It does
#   not infer a click, signup, sale, commission, or revenue event.

hub = HUB.read_text(encoding="utf-8")

item_identity = 'https://coshuma.com/best/kittl-commercial-use-license.html","name":"Kittl Commercial Use & License Guide"'
if item_identity not in hub:
    helpdesk_pattern = re.compile(
        r'(?P<indent>[ \t]*)\{"@type":"ListItem","position":(?P<position>\d+),"url":"https://coshuma.com/best/helpdesk-vs-freshdesk.html","name":"HelpDesk vs Freshdesk Pricing & Free Trial Comparison"\}'
    )
    match = helpdesk_pattern.search(hub)
    if not match:
        raise SystemExit("HelpDesk ItemList marker not found; refusing unsafe Kittl buyer-hub rewrite")
    positions = [int(value) for value in re.findall(r'"position":(\d+)', hub)]
    next_position = max(positions, default=0) + 1
    item_marker = match.group(0)
    indent = match.group('indent')
    item = f'{indent}{{"@type":"ListItem","position":{next_position},"url":"https://coshuma.com/best/kittl-commercial-use-license.html","name":"Kittl Commercial Use & License Guide"}}'
    hub = hub.replace(item_marker, item_marker + ',\n' + item, 1)

card_marker = '''          <a href="/best/databox-genie-ai-analyst.html" class="p-5 rounded-2xl bg-[#131520] border border-purple-500/25 hover:border-purple-400/60 transition-all">'''
card_heading = '<h3 class="text-lg font-extrabold text-white mt-2">Kittl Commercial Use & License</h3>'
card = '''          <a href="/best/kittl-commercial-use-license.html" class="p-5 rounded-2xl bg-[#131520] border border-emerald-500/25 hover:border-emerald-400/60 transition-all">
            <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">Design licensing · verified partner route</div>
            <h3 class="text-lg font-extrabold text-white mt-2">Kittl Commercial Use & License</h3>
            <p class="text-sm text-slate-300 mt-2 leading-relaxed">Free is for personal use. Check when Pro or Expert commercial rights fit POD or client work, and when Max's no-copy-limit license is actually necessary.</p>
          </a>
'''
if card_heading not in hub:
    if card_marker not in hub:
        raise SystemExit("Databox buyer-hub marker not found; refusing unsafe Kittl card insertion")
    hub = hub.replace(card_marker, card + card_marker, 1)

for marker in (item_identity, card_heading, 'Design licensing · verified partner route'):
    if marker not in hub:
        raise SystemExit(f"Missing expected Kittl buyer-hub marker: {marker}")
HUB.write_text(hub, encoding="utf-8")

tool = TOOL.read_text(encoding="utf-8")
internal_heading = '<h2 class="text-2xl font-black text-white mt-2">Need Kittl for client work, POD or products?</h2>'
if internal_heading not in tool:
    faq_heading = '<h2 class="text-2xl font-black text-white mb-5">Kittl pricing FAQ</h2>'
    internal_block = '''  <section class="p-7 rounded-3xl border border-emerald-500/20 bg-emerald-500/[0.05]">
    <div class="text-xs uppercase tracking-wider font-bold text-emerald-300">Commercial-use decision guide</div>
    <h2 class="text-2xl font-black text-white mt-2">Need Kittl for client work, POD or products?</h2>
    <p class="text-sm text-slate-300 leading-6 mt-3">Use the dedicated licensing guide to check the current commercial-use boundary before you pay. It separates the personal-use Free plan from paid commercial rights and links back to Kittl's current licensing sources.</p>
    <a href="/best/kittl-commercial-use-license.html" class="inline-flex mt-4 font-black text-emerald-300 hover:text-emerald-200">Read the Kittl commercial-use guide →</a>
  </section>

'''
    faq_at = tool.find(faq_heading)
    if faq_at < 0:
        raise SystemExit("Kittl pricing FAQ heading not found; refusing unsafe internal-link insertion")
    section_at = tool.rfind('<section', 0, faq_at)
    if section_at < 0:
        raise SystemExit("Kittl pricing FAQ section boundary not found; refusing unsafe internal-link insertion")
    tool = tool[:section_at] + internal_block + tool[section_at:]
if SLUG not in tool or internal_heading not in tool:
    raise SystemExit("Kittl tool page missing expected commercial-guide internal link")
TOOL.write_text(tool, encoding="utf-8")

llms = LLMS.read_text(encoding="utf-8")
llms_line = '- https://coshuma.com/best/kittl-commercial-use-license.html — Kittl commercial-use, POD and client-work licensing guide'
if llms_line not in llms:
    anchor = '- https://coshuma.com/best/bookyourdata-free-trial.html — Bookyourdata free-leads buyer guide\n'
    if anchor not in llms:
        raise SystemExit("llms.txt buyer-guide anchor not found; refusing unsafe Kittl discovery insertion")
    llms = llms.replace(anchor, anchor + llms_line + '\n', 1)
if llms_line not in llms:
    raise SystemExit("llms.txt missing Kittl commercial-use guide")
LLMS.write_text(llms, encoding="utf-8")

print("buyer-hub-kittl-commercial-discovery-v3")