from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "best" / "b2b-email-list-providers.html"
TRACKING_URL = "https://www.uplead.com?fp_ref=sangkwon-3af7dc"

html = PAGE.read_text(encoding="utf-8")

# Vendor-issued evidence: UpLead's FirstPromoter welcome email to support@coshuma.com
# (Gmail message 1a08b7419d47b773) explicitly says to share this exact link and that
# COSHUMA is rewarded when a referred user subscribes to a paid account. Do not
# construct pricing deep links or reuse the affiliate dashboard URL as a buyer CTA.

top_marker = '<div class="mt-4 text-sm font-bold text-white">7-day trial · 5 credits · Essentials from $99/mo monthly</div>'
top_cta = top_marker + f'\n        <a data-cta="affiliate" data-tool-id="uplead" data-cta-source="best_b2b_email_list_providers_top_uplead" href="{TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer" class="mt-4 inline-flex rounded-lg bg-slate-700 px-4 py-2.5 text-sm font-black text-white hover:bg-slate-600">Start UpLead via COSHUMA →</a>'
if top_marker in html and 'best_b2b_email_list_providers_top_uplead' not in html:
    html = html.replace(top_marker, top_cta, 1)

old_detail = '<a href="https://www.uplead.com/pricing/" target="_blank" rel="noopener noreferrer" class="block rounded-xl bg-slate-700 px-5 py-4 text-center font-black text-white hover:bg-slate-600">Check UpLead pricing →</a>'
new_detail = f'<a data-cta="affiliate" data-tool-id="uplead" data-cta-source="best_b2b_email_list_providers_uplead" href="{TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer" class="block rounded-xl bg-slate-700 px-5 py-4 text-center font-black text-white hover:bg-slate-600">Start UpLead via COSHUMA →</a>\n            <a href="https://www.uplead.com/pricing/" target="_blank" rel="noopener noreferrer" class="block rounded-xl border border-white/10 px-5 py-3 text-center text-sm font-bold text-slate-300 hover:bg-white/5">Check official pricing</a>'
if old_detail in html:
    html = html.replace(old_detail, new_detail, 1)

table_old = '<a class="font-bold text-slate-300" href="https://www.uplead.com/pricing/" target="_blank" rel="noopener noreferrer">Official pricing →</a>'
table_new = f'<a data-cta="affiliate" data-tool-id="uplead" data-cta-source="best_b2b_email_list_providers_table_uplead" class="font-bold text-slate-300" href="{TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer">Try UpLead via COSHUMA →</a>'
if table_old in html:
    html = html.replace(table_old, table_new, 1)

disclosure_old = 'COSHUMA may earn a commission if you use the Bookyourdata partner link on this page, at no extra cost to you. That relationship does not guarantee a positive recommendation or affect the other providers\' placement.'
disclosure_new = 'COSHUMA may earn a commission if you use the Bookyourdata or UpLead partner links on this page, at no extra cost to you. Those relationships do not guarantee a positive recommendation or affect the providers\' placement.'
if disclosure_old in html:
    html = html.replace(disclosure_old, disclosure_new, 1)

required = [
    TRACKING_URL,
    'best_b2b_email_list_providers_top_uplead',
    'best_b2b_email_list_providers_uplead',
    'best_b2b_email_list_providers_table_uplead',
    'Bookyourdata or UpLead partner links',
]
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit(f"UpLead verified tracking patch incomplete: {missing}")

# The dashboard is operational-only and must never become a public revenue CTA.
if 'affiliates.uplead.com/login' in html:
    raise SystemExit('UpLead affiliate dashboard URL leaked into public buyer page')

PAGE.write_text(html, encoding="utf-8")
print('uplead-approved-tracking-v1')
