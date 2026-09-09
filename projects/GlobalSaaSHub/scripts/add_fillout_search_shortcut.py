from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = APP.read_text(encoding="utf-8")

marker = "const filloutSearchTool = {"
if marker not in text:
    anchor = "import { trackPageView, trackToolClick } from './utils/analytics';\n"
    if anchor not in text:
        raise SystemExit("Analytics import changed; refusing unsafe Fillout search patch")
    block = '''import { trackPageView, trackToolClick } from './utils/analytics';\n\nconst filloutSearchTool = {\n  id: 'fillout',\n  name: 'Fillout',\n  category: 'sales_crm',\n  category_display: 'Forms & Lead Capture',\n  description: 'A form builder for capturing leads, applications and payments with a free plan available.',\n  affiliate_url: 'https://try.fillout.com/sang-kwon-an-hxwn',\n  pricing: 'Free plan available',\n  key_features: ['Lead capture forms', 'Payment collection'],\n  logo_url: 'https://www.google.com/s2/favicons?domain=fillout.com&sz=128',\n  affiliate_verified: true,\n  affiliate_status: 'approved_tracking',\n  official_url: 'https://www.fillout.com/',\n  detail_url: '/best/fillout-form-builder.html'\n};\n\nconst searchableToolsData = toolsData.some((tool) => tool.id === 'fillout') ? toolsData : [...toolsData, filloutSearchTool];\n'''
    text = text.replace(anchor, block, 1)

# Autocomplete should discover Fillout even though it is still maintained as a dedicated buyer guide.
old_auto = """    return toolsData\n      .filter((t) =>"""
new_auto = """    return searchableToolsData\n      .filter((t) =>"""
if new_auto not in text:
    if old_auto not in text:
        raise SystemExit("Autocomplete source changed; refusing unsafe Fillout search patch")
    text = text.replace(old_auto, new_auto, 1)

# Keep the normal 151-tool browse view unchanged; add Fillout only once the visitor is actually searching.
old_filtered = """    return toolsData.filter((tool) => {"""
new_filtered = """    const sourceTools = searchTerm.trim() ? searchableToolsData : toolsData;\n    return sourceTools.filter((tool) => {"""
if new_filtered not in text:
    if old_filtered not in text:
        raise SystemExit("Filtered tool source changed; refusing unsafe Fillout search patch")
    text = text.replace(old_filtered, new_filtered, 1)

# Autocomplete result uses the dedicated Fillout buyer guide when detail_url is present.
auto_old = '''<a key={tool.id} href={`/tool/${tool.id}.html`} className="flex items-center justify-between gap-4 border-b border-white/5 px-4 py-3 last:border-0 hover:bg-white/5">'''
auto_new = '''<a key={tool.id} href={tool.detail_url || `/tool/${tool.id}.html`} className="flex items-center justify-between gap-4 border-b border-white/5 px-4 py-3 last:border-0 hover:bg-white/5">'''
if auto_new not in text:
    if auto_old not in text:
        raise SystemExit("Autocomplete link markup changed; refusing unsafe Fillout search patch")
    text = text.replace(auto_old, auto_new, 1)

# Search-result cards also honor a dedicated guide URL. Leave the featured-card occurrence unchanged
# so the link-integrity regression still checks the canonical tools.json card route.
card_title_old = '''<a href={`/tool/${tool.id}.html`} className="block truncate text-lg font-black text-white hover:text-violet-200">'''
card_title_new = '''<a href={tool.detail_url || `/tool/${tool.id}.html`} className="block truncate text-lg font-black text-white hover:text-violet-200">'''
if card_title_new not in text:
    if card_title_old not in text:
        raise SystemExit("Tool title link changed; refusing unsafe Fillout search patch")
    text = text.replace(card_title_old, card_title_new, 1)

buyer_old = '''<a href={`/tool/${tool.id}.html`} className="flex min-h-11 items-center justify-center rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-xs font-bold text-slate-200 hover:bg-white/10">See buyer guide</a>'''
buyer_new = '''<a href={tool.detail_url || `/tool/${tool.id}.html`} className="flex min-h-11 items-center justify-center rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-xs font-bold text-slate-200 hover:bg-white/10">See buyer guide</a>'''
if buyer_new not in text:
    if buyer_old not in text:
        raise SystemExit("Buyer-guide link changed; refusing unsafe Fillout search patch")
    text = text.replace(buyer_old, buyer_new, 1)

APP.write_text(text, encoding="utf-8")
print("Fillout search shortcut added: searchable by name/forms/leads with verified buyer-guide route")
