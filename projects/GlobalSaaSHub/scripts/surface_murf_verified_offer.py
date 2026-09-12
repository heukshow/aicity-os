from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "verified-software-free-trials-deals.html"
MARKER = "<!-- COSHUMA_MURF_VERIFIED_OFFER -->"
TRACKING_URL = "https://get.murf.ai/fqac0vixj0qs"
ADMIN_URLS = (
    "https://dash.partnerstack.com",
    "https://partnerstack.com/dashboard",
)

if not PAGE.exists():
    raise SystemExit(f"Missing buyer hub: {PAGE}")

html = PAGE.read_text(encoding="utf-8")

# The exact PartnerStack customer route was copied from COSHUMA's approved Murf
# program and is already preserved in approved-tracking evidence. Murf's official
# Help Center rechecked 2026-09-12 says every first-time signup is automatically
# assigned a Free Trial with no credit card required. This is not a special trial
# deep link, so do not manufacture pricing/trial parameters on the affiliate URL.
if MARKER in html:
    if TRACKING_URL not in html:
        raise SystemExit("Murf verified block exists but exact approved tracking URL is missing")
    if any(url in html for url in ADMIN_URLS):
        raise SystemExit("Murf/PartnerStack admin URL leaked into the public buyer hub")
    print("Murf verified offer already surfaced")
    raise SystemExit(0)

old_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign and Teachable. COSHUMA separates customer-facing tracking links from product claims."
)
new_meta = (
    "Compare verified SaaS free trials and partner offers from Gamma, Time2book, "
    "UpLead, Jotform, Unbounce, Pictory, Brand24, Bookyourdata, Tally, Typedesk, "
    "Tagshop AI, RGE Studio, BoldSign, Teachable and Murf AI. COSHUMA separates customer-facing tracking links from product claims."
)
if old_meta not in html:
    raise SystemExit("Buyer-hub meta description changed; refusing blind Murf patch")
html = html.replace(old_meta, new_meta, 1)

item14 = (
    '      {"@type":"ListItem","position":14,"name":"Teachable",'
    '"url":"https://coshuma.com/best/teachable-30-day-free-trial.html"}\n'
    "    ]"
)
item15 = (
    '      {"@type":"ListItem","position":14,"name":"Teachable",'
    '"url":"https://coshuma.com/best/teachable-30-day-free-trial.html"},\n'
    '      {"@type":"ListItem","position":15,"name":"Murf AI",'
    '"url":"https://coshuma.com/tool/murf-ai.html"}\n'
    "    ]"
)
if item14 not in html:
    raise SystemExit("Teachable ItemList tail missing; Murf patch requires the verified Teachable build step first")
html = html.replace(item14, item15, 1)

closing = '''    </section>\n\n    <section class="rounded-3xl border border-white/10 bg-[#11131a] p-7 md:p-9">\n      <h2 class="text-2xl font-black text-white">How this list is gated</h2>'''
if closing not in html:
    raise SystemExit("Buyer-hub final grid boundary changed; refusing blind Murf patch")

card = f'''      {MARKER}\n      <article class="rounded-3xl border border-purple-400/25 bg-[#11131a] p-7 space-y-5">\n        <div class="flex items-start justify-between gap-4"><div><div class="text-xs font-black uppercase tracking-wider text-purple-300">AI voice & voiceover</div><h2 class="mt-1 text-3xl font-black text-white">Murf AI</h2></div><span class="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Free trial · no card</span></div>\n        <p class="text-sm leading-6 text-slate-300">Murf's official Help Center currently says first-time signups are automatically assigned a <strong class="text-white">Free Trial</strong> with <strong class="text-white">no credit card required</strong>. The Studio trial includes access to 300+ voices across 33 languages, 10 minutes of voice generation and 10 minutes of transcription; downloads are not included during the trial.</p>\n        <p class="text-sm leading-6 text-slate-300">Murf's official affiliate page currently states that eligible paid referrals can earn the affiliate <strong class="text-white">20% recurring commission for up to 24 months</strong> and uses a <strong class="text-white">90-day attribution window</strong>. Murf also says it does not provide a special affiliate discount to referred users.</p>\n        <div class="grid gap-3 sm:grid-cols-2"><a data-cta="affiliate" data-tool-id="murf-ai" data-cta-source="verified-deals-murf-approved-link" data-cta-page="verified-software-free-trials-deals" href="{TRACKING_URL}" target="_blank" rel="sponsored nofollow noopener noreferrer" class="rounded-xl bg-purple-600 px-5 py-3.5 text-center text-sm font-black text-white hover:bg-purple-500">Open Murf via verified partner link →</a><a href="/tool/murf-ai.html" class="rounded-xl border border-white/10 px-5 py-3.5 text-center text-sm font-bold text-slate-200 hover:bg-white/5">Compare Murf pricing & trial</a></div>\n        <p class="text-[11px] leading-5 text-slate-500">The first button uses COSHUMA's exact approved Murf PartnerStack customer link. It is an affiliate entry route, not a guessed trial deep link. A click, free trial, signup, paid customer, commission, payout or revenue is not counted without partner-side evidence.</p>\n      </article>\n'''

html = html.replace(closing, card + closing, 1)

required = [
    TRACKING_URL,
    'data-cta-source="verified-deals-murf-approved-link"',
    "Free Trial",
    "no credit card required",
    "20% recurring commission for up to 24 months",
    "90-day attribution window",
    "not a guessed trial deep link",
    "not counted without partner-side evidence",
]
for token in required:
    if token not in html:
        raise SystemExit(f"Murf buyer-hub patch lost required token: {token}")
if any(url in html for url in ADMIN_URLS):
    raise SystemExit("Murf/PartnerStack admin URL leaked into the public buyer hub")

PAGE.write_text(html, encoding="utf-8")
print("Surfaced verified Murf partner route on buyer hub")
