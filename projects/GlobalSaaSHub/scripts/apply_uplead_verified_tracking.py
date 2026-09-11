from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARE_PAGE = ROOT / "public" / "best" / "b2b-email-list-providers.html"
TRIAL_PAGE = ROOT / "public" / "best" / "uplead-free-trial-pricing.html"
DEALS_PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"

HOME_TRACKING_URL = "https://www.uplead.com?fp_ref=sangkwon-3af7dc"
PRICING_TRACKING_URL = "https://www.uplead.com/pricing/?fp_ref=sangkwon-3af7dc"
TRIAL_TRACKING_URL = "https://app.uplead.com/trial-signup?fp_ref=sangkwon-3af7dc"
BUYER_GUIDE = "/best/uplead-free-trial-pricing.html"
BUYER_GUIDE_URL = f"https://coshuma.com{BUYER_GUIDE}"
ATTRIBUTION_SCRIPT = '<script defer src="/affiliate-attribution.js"></script>'

# Vendor evidence:
# - Welcome email to support@coshuma.com (Gmail 1a08b7419d47b773) issued HOME_TRACKING_URL.
# - Human reply from Will Cannon / UpLead (Gmail 1a08d9736524831d) explicitly issued
#   PRICING_TRACKING_URL and TRIAL_TRACKING_URL for COSHUMA and separately directed
#   account statistics to https://affiliates.uplead.com/login.
# These two deep links are therefore vendor-approved customer-facing tracking routes,
# not guessed URLs. Never publish the affiliate dashboard/login URL as a buyer CTA.

html = COMPARE_PAGE.read_text(encoding="utf-8")

# Ensure affiliate clicks on this buyer-intent comparison are actually collected by
# COSHUMA's first-party attribution script. The page already uses data-cta metadata.
if ATTRIBUTION_SCRIPT not in html:
    html = html.replace('</head>', f'  {ATTRIBUTION_SCRIPT}\n</head>', 1)

# UpLead summary card: route trial intent directly to the vendor-issued trial signup.
top_marker = '<div class="mt-4 text-sm font-bold text-white">7-day trial · 5 credits · Essentials from $99/mo monthly</div>'
top_cta = top_marker + f'\n        <a data-cta="affiliate" data-tool-id="uplead" data-cta-source="best_b2b_email_list_providers_top_uplead" href="{TRIAL_TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer" class="mt-4 inline-flex rounded-lg bg-slate-700 px-4 py-2.5 text-sm font-black text-white hover:bg-slate-600">Start 7-Day UpLead Trial — 5 Credits →</a>\n        <div class="mt-2 text-xs leading-5 text-slate-400">UpLead support currently says payment details are required for full trial activation and billing begins after Day 7 unless cancelled.</div>'
if top_marker in html and 'best_b2b_email_list_providers_top_uplead' not in html:
    html = html.replace(top_marker, top_cta, 1)

# If an earlier build already inserted the homepage tracking route, upgrade it to the
# exact vendor-issued trial deep link rather than constructing a URL ourselves.
html = html.replace(
    f'data-cta-source="best_b2b_email_list_providers_top_uplead" href="{HOME_TRACKING_URL}"',
    f'data-cta-source="best_b2b_email_list_providers_top_uplead" href="{TRIAL_TRACKING_URL}"',
)
html = html.replace(
    f'data-cta-source="best_b2b_email_list_providers_uplead" href="{HOME_TRACKING_URL}"',
    f'data-cta-source="best_b2b_email_list_providers_uplead" href="{TRIAL_TRACKING_URL}"',
)
html = html.replace(
    f'data-cta-source="best_b2b_email_list_providers_table_uplead" class="font-bold text-slate-300" href="{HOME_TRACKING_URL}"',
    f'data-cta-source="best_b2b_email_list_providers_table_uplead" class="font-bold text-slate-300" href="{PRICING_TRACKING_URL}"',
)

old_detail = '<a href="https://www.uplead.com/pricing/" target="_blank" rel="noopener noreferrer" class="block rounded-xl bg-slate-700 px-5 py-4 text-center font-black text-white hover:bg-slate-600">Check UpLead pricing →</a>'
new_detail = f'<a data-cta="affiliate" data-tool-id="uplead" data-cta-source="best_b2b_email_list_providers_uplead" href="{TRIAL_TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer" class="block rounded-xl bg-slate-700 px-5 py-4 text-center font-black text-white hover:bg-slate-600">Start 7-Day UpLead Trial — 5 Credits →</a>\n            <div class="rounded-lg border border-amber-400/15 bg-amber-400/[0.04] px-4 py-3 text-xs leading-5 text-amber-100/80">Full trial activation currently requires payment details according to UpLead support. Confirm the live checkout terms and cancel before the trial ends if you do not want the selected paid plan to begin.</div>\n            <a href="{BUYER_GUIDE}" class="block rounded-xl border border-emerald-400/20 bg-emerald-400/[0.05] px-5 py-3 text-center text-sm font-bold text-emerald-200 hover:bg-emerald-400/10">Read UpLead free-trial & pricing guide</a>\n            <a data-cta="affiliate" data-tool-id="uplead" data-cta-source="best_b2b_email_list_providers_pricing_uplead" href="{PRICING_TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer" class="block rounded-xl border border-white/10 px-5 py-3 text-center text-sm font-bold text-slate-300 hover:bg-white/5">Check UpLead pricing →</a>'
if old_detail in html:
    html = html.replace(old_detail, new_detail, 1)

# Upgrade an already-patched untracked pricing link to the vendor-approved tracked one.
html = html.replace(
    '<a href="https://www.uplead.com/pricing/" target="_blank" rel="noopener noreferrer" class="block rounded-xl border border-white/10 px-5 py-3 text-center text-sm font-bold text-slate-300 hover:bg-white/5">Check official pricing</a>',
    f'<a data-cta="affiliate" data-tool-id="uplead" data-cta-source="best_b2b_email_list_providers_pricing_uplead" href="{PRICING_TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer" class="block rounded-xl border border-white/10 px-5 py-3 text-center text-sm font-bold text-slate-300 hover:bg-white/5">Check UpLead pricing →</a>',
)

table_old = '<a class="font-bold text-slate-300" href="https://www.uplead.com/pricing/" target="_blank" rel="noopener noreferrer">Official pricing →</a>'
table_new = f'<a data-cta="affiliate" data-tool-id="uplead" data-cta-source="best_b2b_email_list_providers_table_uplead" class="font-bold text-slate-300" href="{PRICING_TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer">UpLead pricing →</a>'
if table_old in html:
    html = html.replace(table_old, table_new, 1)

disclosure_old = 'COSHUMA may earn a commission if you use the Bookyourdata partner link on this page, at no extra cost to you. That relationship does not guarantee a positive recommendation or affect the other providers\' placement.'
disclosure_new = 'COSHUMA may earn a commission if you use the Bookyourdata or UpLead partner links on this page, at no extra cost to you. Those relationships do not guarantee a positive recommendation or affect the providers\' placement.'
if disclosure_old in html:
    html = html.replace(disclosure_old, disclosure_new, 1)

required = [
    TRIAL_TRACKING_URL,
    PRICING_TRACKING_URL,
    BUYER_GUIDE,
    ATTRIBUTION_SCRIPT,
    'best_b2b_email_list_providers_top_uplead',
    'best_b2b_email_list_providers_uplead',
    'best_b2b_email_list_providers_table_uplead',
    'Bookyourdata or UpLead partner links',
    'Start 7-Day UpLead Trial — 5 Credits',
    'payment details are required',
]
missing = [item for item in required if item not in html]
if missing:
    raise SystemExit(f"UpLead verified tracking patch incomplete: {missing}")
if 'affiliates.uplead.com/login' in html:
    raise SystemExit('UpLead affiliate dashboard URL leaked into public buyer page')

COMPARE_PAGE.write_text(html, encoding="utf-8")

# Dedicated UpLead trial/pricing guide: use the vendor-issued destination that matches
# each CTA's intent, while keeping the trial billing warning visible.
trial = TRIAL_PAGE.read_text(encoding="utf-8")
trial = trial.replace(
    f'data-cta-source="uplead_free_trial_hero" href="{HOME_TRACKING_URL}"',
    f'data-cta-source="uplead_free_trial_hero" href="{TRIAL_TRACKING_URL}"',
)
trial = trial.replace(
    f'data-cta-source="uplead_free_trial_bottom" href="{HOME_TRACKING_URL}"',
    f'data-cta-source="uplead_free_trial_bottom" href="{TRIAL_TRACKING_URL}"',
)
trial = trial.replace(
    '<a href="https://www.uplead.com/pricing/" target="_blank" rel="noopener noreferrer" class="flex-1 rounded-xl border border-white/10 bg-white/[0.03] px-6 py-4 text-center text-sm font-bold text-slate-200 hover:bg-white/[0.06]">Check official pricing →</a>',
    f'<a data-cta="affiliate" data-tool-id="uplead" data-cta-source="uplead_pricing_hero" href="{PRICING_TRACKING_URL}" target="_blank" rel="sponsored noopener noreferrer" class="flex-1 rounded-xl border border-white/10 bg-white/[0.03] px-6 py-4 text-center text-sm font-bold text-slate-200 hover:bg-white/[0.06]">Check UpLead pricing →</a>',
)
trial = trial.replace(
    'Affiliate disclosure: the green button uses the exact customer referral URL UpLead issued to COSHUMA.',
    'Affiliate disclosure: the trial and pricing buttons use the exact customer tracking URLs UpLead issued to COSHUMA.',
)
trial = trial.replace(
    "and UpLead's vendor-issued welcome email to COSHUMA for the exact referral URL. The dashboard/login URL is not used as a customer CTA.",
    "and UpLead's vendor emails to COSHUMA for the exact homepage, pricing and trial tracking URLs. The dashboard/login URL is not used as a customer CTA.",
)

trial_required = [
    TRIAL_TRACKING_URL,
    PRICING_TRACKING_URL,
    'uplead_free_trial_hero',
    'uplead_free_trial_bottom',
    'uplead_pricing_hero',
    'payment details',
]
trial_missing = [item for item in trial_required if item not in trial]
if trial_missing:
    raise SystemExit(f"UpLead trial/pricing guide tracking patch incomplete: {trial_missing}")
if 'affiliates.uplead.com/login' in trial:
    raise SystemExit('UpLead affiliate dashboard URL leaked into public trial/pricing guide')

TRIAL_PAGE.write_text(trial, encoding="utf-8")

# The verified-offers hub previously pointed its structured UpLead entity to
# /tool/uplead.html, which does not exist. Keep Google and buyers on the dedicated
# revenue page instead, and add a visible crawlable internal link from the hub.
deals = DEALS_PAGE.read_text(encoding="utf-8")
deals = deals.replace('https://coshuma.com/tool/uplead.html', BUYER_GUIDE_URL)
if ATTRIBUTION_SCRIPT not in deals:
    deals = deals.replace('</head>', f'  {ATTRIBUTION_SCRIPT}\n</head>', 1)

uplead_copy = """          <p class="text-sm leading-6 text-slate-300">UpLead's Will Cannon confirmed COSHUMA's exact tracked 7-day trial destination and a separate tracked pricing destination for the existing affiliate account. These links are used exactly as supplied; no referral parameter has been invented.</p>"""
uplead_guide_link = f"""
          <a data-cta-source="verified-deals-uplead-guide" href="{BUYER_GUIDE}" class="inline-flex text-sm font-bold text-cyan-200 hover:text-cyan-100">Read the full UpLead trial & pricing guide →</a>"""
if 'verified-deals-uplead-guide' not in deals:
    if uplead_copy not in deals:
        raise SystemExit('UpLead verified-offers card copy not found for internal-link patch')
    deals = deals.replace(uplead_copy, uplead_copy + uplead_guide_link, 1)

deals_required = [
    BUYER_GUIDE_URL,
    f'href="{BUYER_GUIDE}"',
    'verified-deals-uplead-guide',
    TRIAL_TRACKING_URL,
    PRICING_TRACKING_URL,
    ATTRIBUTION_SCRIPT,
    'Affiliate disclosure',
]
deals_missing = [item for item in deals_required if item not in deals]
if deals_missing:
    raise SystemExit(f"UpLead verified-offers SEO patch incomplete: {deals_missing}")
if 'https://coshuma.com/tool/uplead.html' in deals:
    raise SystemExit('Nonexistent UpLead tool URL survived verified-offers structured-data patch')

DEALS_PAGE.write_text(deals, encoding="utf-8")
print('uplead-approved-vendor-deeplinks-v5')