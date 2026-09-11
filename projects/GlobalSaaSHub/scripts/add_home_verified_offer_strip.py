from pathlib import Path

app = Path(__file__).resolve().parents[1] / "src" / "App.jsx"
text = app.read_text(encoding="utf-8")

marker = 'data-revenue-surface="home-verified-offers"'
if marker in text:
    print("Homepage verified offer strip already present")
    raise SystemExit(0)

anchor = "\n      {featuredTools.length > 0 && ("
if anchor not in text:
    raise SystemExit("Featured-tools anchor changed; refusing unsafe homepage offer insertion")

section = r'''
      <section data-revenue-surface="home-verified-offers" className="relative z-10 mx-auto max-w-7xl px-4 pb-14 sm:px-6 lg:px-8">
        <div className="rounded-3xl border border-emerald-400/20 bg-gradient-to-br from-emerald-400/[0.08] via-white/[0.03] to-cyan-400/[0.06] p-5 sm:p-7">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <div className="text-xs font-black uppercase tracking-[0.18em] text-emerald-300">Verified low-friction buyer routes</div>
              <h2 className="mt-2 text-2xl font-black text-white sm:text-3xl">Start with a tracked trial or pricing page we have actually verified</h2>
              <p className="mt-3 text-sm leading-6 text-slate-400">These customer-facing destinations were supplied directly by the partner programs. COSHUMA does not invent referral parameters, and a click is never treated as a signup or sale.</p>
            </div>
            <a href="/best/verified-software-free-trials-deals.html" data-cta-source="home-verified-offers-all" className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-white/10 px-5 py-3 text-sm font-bold text-slate-200 hover:bg-white/5">See all verified offers <ArrowRight className="h-4 w-4" /></a>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <article className="rounded-2xl border border-cyan-400/20 bg-[#0d1118]/80 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-black uppercase tracking-wider text-cyan-300">B2B lead data</div>
                  <h3 className="mt-1 text-xl font-black text-white">UpLead</h3>
                </div>
                <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">7-day trial route</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-400">Use the exact tracked trial destination confirmed for COSHUMA's existing UpLead referral account.</p>
              <a data-cta="affiliate" data-tool-id="uplead" data-cta-source="home-verified-offers-uplead-trial" data-cta-page="home" href="https://app.uplead.com/trial-signup?fp_ref=sangkwon-3af7dc" target="_blank" rel="sponsored nofollow noopener noreferrer" className="mt-4 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-cyan-600 px-5 py-3 text-sm font-black text-white hover:bg-cyan-500">Start UpLead's 7-day trial <ArrowUpRight className="h-4 w-4" /></a>
            </article>

            <article className="rounded-2xl border border-amber-400/20 bg-[#0d1118]/80 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-black uppercase tracking-wider text-amber-200">Forms & workflows</div>
                  <h3 className="mt-1 text-xl font-black text-white">Jotform</h3>
                </div>
                <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-200">Exact pricing route</span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-400">Compare current Jotform plans through the partner-tagged pricing URL its affiliate team explicitly approved for COSHUMA.</p>
              <a data-cta="affiliate" data-tool-id="jotform" data-cta-source="home-verified-offers-jotform-pricing" data-cta-page="home" href="https://www.jotform.com/pricing/?partner=coshuma" target="_blank" rel="sponsored nofollow noopener noreferrer" className="mt-4 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl bg-amber-500 px-5 py-3 text-sm font-black text-slate-950 hover:bg-amber-400">Compare Jotform plans <ArrowUpRight className="h-4 w-4" /></a>
            </article>
          </div>

          <p className="mt-4 text-[11px] leading-5 text-slate-500">Affiliate disclosure: COSHUMA may earn a commission if an eligible purchase later occurs through these tracked links, at no extra cost to you. Trial eligibility, pricing and final terms are controlled by each vendor.</p>
        </div>
      </section>
'''

text = text.replace(anchor, section + anchor, 1)

required = (
    marker,
    'https://app.uplead.com/trial-signup?fp_ref=sangkwon-3af7dc',
    'https://www.jotform.com/pricing/?partner=coshuma',
    'data-cta-source="home-verified-offers-uplead-trial"',
    'data-cta-source="home-verified-offers-jotform-pricing"',
)
for value in required:
    if value not in text:
        raise SystemExit(f"Homepage verified offer safety check failed: {value}")

app.write_text(text, encoding="utf-8")
print("Homepage verified offer strip applied: UpLead trial + Jotform pricing + verified-offers hub")
