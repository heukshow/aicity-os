from pathlib import Path

app = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = app.read_text(encoding="utf-8")

marker = 'data-revenue-surface="home-verified-offers"'

# Keep the homepage customer-facing. Tracking mechanics, account state and
# partner-program verification details belong in private/admin records.
CUSTOMER_COPY_REPLACEMENTS = {
    'Verified low-friction buyer routes': 'Low-friction ways to start',
    'Start with a tracked trial, pricing page or referral benefit we have actually verified': 'Try a tool, compare pricing or claim an eligible referral benefit',
    'These customer-facing destinations were supplied directly by the partner programs. COSHUMA does not invent referral parameters, and a click is never treated as a signup or sale.': 'Use these links to open the vendor trial, pricing or referral page, then confirm current eligibility and final terms before you buy.',
    'See all verified offers': 'See more ways to start',
    '7-day trial route': '7-day trial',
    "Use the exact tracked trial destination confirmed for COSHUMA's existing UpLead referral account.": "Start with UpLead's 7-day trial, then compare current limits and pricing before upgrading.",
    'Exact pricing route': 'Pricing & plans',
    'Compare current Jotform plans through the partner-tagged pricing URL its affiliate team explicitly approved for COSHUMA.': 'Compare Jotform plans and choose the tier that fits your forms, workflows and expected usage.',
    'Personal referral': 'Referral benefit',
    "Affiliate disclosure: COSHUMA may earn a commission if an eligible purchase later occurs through these tracked links, at no extra cost to you. Tally's offer is a personal referral benefit for eligible new users, not a public sale. Trial eligibility, pricing, referral terms and final purchase terms are controlled by each vendor.": "Affiliate disclosure: COSHUMA may earn a commission from some links at no extra cost to you. Tally's 50% benefit is for eligible new users. Trial eligibility, pricing and final purchase terms are controlled by each vendor.",
}

if marker in text:
    original = text
    for old, new in CUSTOMER_COPY_REPLACEMENTS.items():
        text = text.replace(old, new)
    if text != original:
        app.write_text(text, encoding="utf-8")
        print("Homepage offer strip copy refreshed for shoppers")
    else:
        print("Homepage offer strip already customer-ready")
    raise SystemExit(0)

anchor = "\n      {featuredTools.length > 0 && ("
if anchor not in text:
    raise SystemExit("Featured-tools anchor changed; refusing unsafe homepage offer insertion")

section = r'''
      <section data-revenue-surface="home-verified-offers" className="relative z-10 mx-auto max-w-7xl px-4 pb-14 sm:px-6 lg:px-8">
        <div className="rounded-3xl border border-emerald-400/20 bg-gradient-to-br from-emerald-400/[0.08] via-white/[0.03] to-cyan-400/[0.06] p-5 sm:p-7">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <div className="text-xs font-black uppercase tracking-[0.18em] text-emerald-300">Low-friction ways to start</div>
              <h2 className="mt-2 text-2xl font-black text-white sm:text-3xl">Try a tool, compare pricing or claim an eligible referral benefit</h2>
              <p className="mt-3 text-sm leading-6 text-slate-400">Use these links to open the vendor trial, pricing or referral page, then confirm current eligibility and final terms before you buy.</p>
            </div>
            <a href="/best/verified-software-free-trials-deals.html" data-cta-source="home-verified-offers-all" className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-white/10 px-5 py-3 text-sm font-bold text-slate-200 hover:bg-white/5">See more ways to start <ArrowRight className="h-4 w-4" /></a>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <article className="rounded-2xl border border-cyan-400/20 bg-[#0d1118]/80 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-black uppercase tracking-wider text-cyan-300">B2B lead data</div>
                  <h3 className="mt-1 text-xl font-black text-white">UpLead</h3>
                </div>
                <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">7-day trial</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-400">Start with UpLead's 7-day trial, then compare current limits and pricing before upgrading.</p>
              <a data-cta="affiliate" data-tool-id="uplead" data-cta-source="home-verified-offers-uplead-trial" data-cta-page="home" href="https://app.uplead.com/trial-signup?fp_ref=sangkwon-3af7dc" target="_blank" rel="sponsored nofollow noopener noreferrer" className="mt-4 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-cyan-600 px-5 py-3 text-sm font-black text-white hover:bg-cyan-500">Start UpLead's 7-day trial <ArrowUpRight className="h-4 w-4" /></a>
            </article>

            <article className="rounded-2xl border border-amber-400/20 bg-[#0d1118]/80 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-black uppercase tracking-wider text-amber-200">Forms & workflows</div>
                  <h3 className="mt-1 text-xl font-black text-white">Jotform</h3>
                </div>
                <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Pricing & plans</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-400">Compare Jotform plans and choose the tier that fits your forms, workflows and expected usage.</p>
              <a data-cta="affiliate" data-tool-id="jotform" data-cta-source="home-verified-offers-jotform-pricing" data-cta-page="home" href="https://www.jotform.com/pricing/?partner=coshuma" target="_blank" rel="sponsored nofollow noopener noreferrer" className="mt-4 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-amber-500 px-5 py-3 text-sm font-black text-slate-950 hover:bg-amber-400">Compare Jotform plans <ArrowUpRight className="h-4 w-4" /></a>
            </article>

            <article className="rounded-2xl border border-violet-400/20 bg-[#0d1118]/80 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-black uppercase tracking-wider text-violet-300">Forms & surveys</div>
                  <h3 className="mt-1 text-xl font-black text-white">Tally</h3>
                </div>
                <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Referral benefit</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-400">Tally says eligible new users who sign up through a personal referral and later become paying customers receive 50% off their subscription for 3 months.</p>
              <a data-cta="affiliate" data-tool-id="tally" data-cta-source="home-verified-offers-tally-referral" data-cta-page="home" href="https://tally.cello.so/ub0qUbuKk2f" target="_blank" rel="sponsored nofollow noopener noreferrer" className="mt-4 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-5 py-3 text-sm font-black text-white hover:bg-violet-500">Open Tally referral benefit <ArrowUpRight className="h-4 w-4" /></a>
            </article>
          </div>

          <p className="mt-4 text-[11px] leading-5 text-slate-500">Affiliate disclosure: COSHUMA may earn a commission from some links at no extra cost to you. Tally's 50% benefit is for eligible new users. Trial eligibility, pricing and final purchase terms are controlled by each vendor.</p>
        </div>
      </section>
'''

text = text.replace(anchor, section + anchor, 1)

required = (
    marker,
    'https://app.uplead.com/trial-signup?fp_ref=sangkwon-3af7dc',
    'https://www.jotform.com/pricing/?partner=coshuma',
    'https://tally.cello.so/ub0qUbuKk2f',
    'data-cta-source="home-verified-offers-uplead-trial"',
    'data-cta-source="home-verified-offers-jotform-pricing"',
    'data-cta-source="home-verified-offers-tally-referral"',
)
for value in required:
    if value not in text:
        raise SystemExit(f"Homepage offer safety check failed: {value}")

app.write_text(text, encoding="utf-8")
print("Homepage shopper-start strip applied: UpLead trial + Jotform pricing + Tally referral benefit")
