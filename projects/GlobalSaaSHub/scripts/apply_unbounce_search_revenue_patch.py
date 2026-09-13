"""Improve the highest-impression approved-tracking Unbounce page for pricing intent.

Evidence used:
- Live Search Console snapshot: /tool/unbounce.html had 168 impressions and 0 clicks.
- Admin snapshot query signal: "unbounce" had 82 impressions and 0 clicks.
- Verified customer tracking URL stays unchanged: https://unbounce.partnerlinks.io/5ubjnt8lluqi
- Unbounce official pricing on 2026-09-09: Starter $29 monthly / $22 yearly,
  Build $99 / $74, Experiment $149 / $112, Optimize $249 / $187;
  14-day free trial with no credit card.
- Unbounce partner program: referred customers receive 20% off first 3 months or
  35% off first annual subscription; 90-day tracking cookie.
- Unbounce Affiliate Team email 1a09606cd37312f7, received 2026-09-12, says
  referrals can connect Unbounce directly with Mailchimp, Marketo and Salesforce,
  use Zapier templates, or send captured lead data through webhooks. The email also
  reconfirms COSHUMA's exact existing referral URL.

This patch is intentionally exact-match and idempotent. It does not change the
verified referral URL or infer signups, commission, or revenue.
"""
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "unbounce.html"
html = PAGE.read_text(encoding="utf-8")
original = html

replacements = [
    (
        "<title>Unbounce Review & Pricing 2026: 14-Day Free Trial, $29 Starter + 20%/35% Discount | COSHUMA</title>",
        "<title>Unbounce Pricing 2026: $22/mo Annual, 14-Day Trial + 20%/35% Off | COSHUMA</title>",
    ),
    (
        '<meta name="description" content="Unbounce review and pricing for 2026: Starter $29/mo, 14-day free trial with no credit card, current plan limits, and COSHUMA\'s verified 20%/35% partner discount." />',
        '<meta name="description" content="Unbounce pricing for 2026: Starter $29/mo or $22/mo billed yearly. Compare Build, Experiment and Optimize, the 14-day no-card trial, and COSHUMA\'s verified 20%/35% customer offer." />',
    ),
    (
        '<meta property="og:title" content="Unbounce Review & Pricing 2026: 14-Day Free Trial + Partner Discount" />',
        '<meta property="og:title" content="Unbounce Pricing 2026: $22/mo Annual + 14-Day Trial + Partner Discount" />',
    ),
    (
        '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce Review, Pricing & Verified Partner Discount</h1>',
        '<h1 class="text-4xl md:text-5xl font-black text-white mt-1">Unbounce Pricing 2026: Monthly vs Annual + Partner Discount</h1>',
    ),
    (
        '<div class="text-2xl font-black text-emerald-400 mt-1">$29/mo</div><div class="text-xs text-slate-500 mt-2">5 pages · up to 500 traffic · 1 user</div>',
        '<div class="text-2xl font-black text-emerald-400 mt-1">$29/mo</div><div class="text-xs text-emerald-300 mt-1">$22/mo billed yearly</div><div class="text-xs text-slate-500 mt-2">5 pages · up to 500 traffic · 1 user</div>',
    ),
    (
        '<div class="text-2xl font-black text-emerald-400 mt-1">$99/mo</div><div class="text-xs text-slate-500 mt-2">Unlimited pages · up to 20k traffic</div>',
        '<div class="text-2xl font-black text-emerald-400 mt-1">$99/mo</div><div class="text-xs text-emerald-300 mt-1">$74/mo billed yearly</div><div class="text-xs text-slate-500 mt-2">Unlimited pages · up to 20k traffic</div>',
    ),
    (
        '<div class="text-2xl font-black text-emerald-400 mt-1">$149/mo</div><div class="text-xs text-slate-500 mt-2">Unlimited A/B testing · up to 30k traffic · 3 users</div>',
        '<div class="text-2xl font-black text-emerald-400 mt-1">$149/mo</div><div class="text-xs text-emerald-300 mt-1">$112/mo billed yearly</div><div class="text-xs text-slate-500 mt-2">Unlimited A/B testing · up to 30k traffic · 3 users</div>',
    ),
    (
        '<div class="text-2xl font-black text-emerald-400 mt-1">$249/mo</div><div class="text-xs text-slate-500 mt-2">Adds deeper AI optimization and Smart Traffic workflows</div>',
        '<div class="text-2xl font-black text-emerald-400 mt-1">$249/mo</div><div class="text-xs text-emerald-300 mt-1">$187/mo billed yearly</div><div class="text-xs text-slate-500 mt-2">Adds deeper AI optimization and Smart Traffic workflows</div>',
    ),
]

changed = 0
for before, after in replacements:
    if before in html:
        html = html.replace(before, after, 1)
        changed += 1

marker = '<!-- COSHUMA_UNBOUNCE_INTEGRATION_FIT_20260913 -->'
anchor = '''      <section class="rounded-3xl border border-[#262a3d] bg-[#121520] p-6 md:p-8 space-y-5">
        <div>
          <div class="text-xs uppercase tracking-widest text-purple-300 font-bold">Why the partner route matters</div>'''
integration_block = '''      <!-- COSHUMA_UNBOUNCE_INTEGRATION_FIT_20260913 -->
      <section class="rounded-3xl border border-cyan-500/20 bg-cyan-500/5 p-6 md:p-8 space-y-5">
        <div>
          <div class="text-xs uppercase tracking-widest text-cyan-300 font-bold">Fit check before you start</div>
          <h2 class="text-3xl font-black text-white mt-1">Unbounce fits best when your leads already need somewhere to go</h2>
          <p class="text-sm text-slate-300 leading-relaxed mt-3">Unbounce's Affiliate Team specifically highlighted connected marketing stacks as a retention driver for referred customers. Before starting the trial, check whether your workflow already depends on one of the integration paths below.</p>
        </div>
        <div class="grid md:grid-cols-3 gap-4">
          <div class="rounded-2xl border border-cyan-400/15 bg-black/20 p-5"><div class="text-sm font-extrabold text-white">Native integrations</div><div class="mt-2 text-sm leading-6 text-slate-300">Unbounce's partner guidance names Mailchimp, Marketo and Salesforce as examples that can connect directly from the Unbounce dashboard.</div></div>
          <div class="rounded-2xl border border-cyan-400/15 bg-black/20 p-5"><div class="text-sm font-extrabold text-white">Zapier workflows</div><div class="mt-2 text-sm leading-6 text-slate-300">Use Zapier when your captured leads need to move into other apps without building a custom integration from scratch.</div></div>
          <div class="rounded-2xl border border-cyan-400/15 bg-black/20 p-5"><div class="text-sm font-extrabold text-white">Webhooks</div><div class="mt-2 text-sm leading-6 text-slate-300">Use webhooks when you need custom lead-data routing, transformation or delivery into another system.</div></div>
        </div>
        <div class="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5 text-sm leading-6 text-slate-300">This is buyer-fit guidance from Unbounce's affiliate team, not a COSHUMA performance claim. Your actual retention and conversion results depend on your traffic, offer and implementation.</div>
        <div class="flex flex-col sm:flex-row gap-3">
          <a data-cta="affiliate" data-tool-id="unbounce" data-cta-source="tool-integration-fit" href="https://unbounce.partnerlinks.io/5ubjnt8lluqi" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-center">Start the verified 14-day Unbounce route →</a>
          <a href="/best/unbounce-discount.html" class="px-6 py-3.5 rounded-xl border border-cyan-400/20 bg-black/20 text-cyan-100 font-bold text-center hover:bg-black/30">Review the partner discount first →</a>
        </div>
      </section>

'''

if marker not in html:
    if anchor not in html:
        raise SystemExit("Unbounce partner-route section anchor changed; refusing blind integration-fit patch")
    html = html.replace(anchor, integration_block + anchor, 1)
    changed += 1

if html != original:
    PAGE.write_text(html, encoding="utf-8")

print(f"apply_unbounce_search_revenue_patch: replacements={changed}")
