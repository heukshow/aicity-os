from pathlib import Path

root = Path(__file__).resolve().parents[1]
best_dir = root / "public" / "best"
best_dir.mkdir(parents=True, exist_ok=True)
page = best_dir / "fillout-form-builder.html"

tracking = "https://try.fillout.com/sang-kwon-an-hxwn"
html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Fillout Review & Pricing 2026: Free Forms for Leads & Payments | COSHUMA</title>
  <meta name="description" content="Use Fillout to capture leads, applications and payments with a free plan. Compare current Free, Starter, Pro and Business pricing before you choose." />
  <link rel="canonical" href="https://coshuma.com/best/fillout-form-builder.html" />
  <meta property="og:title" content="Fillout Review & Pricing 2026: Capture Leads & Payments | COSHUMA" />
  <meta property="og:description" content="A buyer-focused look at Fillout's free form builder, lead capture, payment collection and current pricing." />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>body{{background:#08090d;color:#e2e8f0;font-family:Inter,system-ui,sans-serif}}</style>
</head>
<body>
  <header class="border-b border-white/10 bg-[#08090d]/95 px-5 py-4">
    <div class="mx-auto flex max-w-5xl items-center justify-between gap-4">
      <a href="/" class="text-lg font-black text-white">COSHUMA</a>
      <a href="/" class="text-sm font-semibold text-slate-400 hover:text-white">← Explore tools</a>
    </div>
  </header>
  <main class="mx-auto max-w-5xl px-5 py-10 sm:py-16">
    <div class="max-w-3xl">
      <div class="inline-flex rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs font-bold text-emerald-200">Verified customer partner link · no extra cost to you</div>
      <h1 class="mt-5 text-4xl font-black tracking-tight text-white sm:text-6xl">Turn traffic into leads, applications and payments with Fillout.</h1>
      <p class="mt-5 text-lg leading-8 text-slate-300">Fillout is a modern form builder for lead forms, applications, surveys, scheduling and payment collection. Its free plan is unusually useful, so you can test a real workflow before paying.</p>
      <div class="mt-7 flex flex-col gap-3 sm:flex-row">
        <a data-cta="affiliate" data-tool-id="fillout" href="{tracking}" target="_blank" rel="sponsored noopener noreferrer" class="inline-flex min-h-12 items-center justify-center rounded-xl bg-violet-500 px-6 py-3 font-black text-white hover:bg-violet-400">Try Fillout free →</a>
        <a href="https://www.fillout.com/pricing" target="_blank" rel="noopener noreferrer" class="inline-flex min-h-12 items-center justify-center rounded-xl border border-white/10 bg-white/5 px-6 py-3 font-bold text-slate-200 hover:bg-white/10">Check official pricing</a>
      </div>
      <p class="mt-3 text-xs leading-5 text-slate-500">Affiliate disclosure: COSHUMA may earn a commission if you purchase after using the verified partner link. Your price is not increased by COSHUMA.</p>
    </div>

    <section class="mt-12 grid gap-4 md:grid-cols-3">
      <div class="rounded-2xl border border-white/10 bg-white/[0.035] p-5"><div class="text-xs font-bold uppercase tracking-wider text-emerald-300">Free forever</div><div class="mt-2 text-2xl font-black text-white">$0 / month</div><p class="mt-2 text-sm leading-6 text-slate-400">Unlimited forms and seats, with up to 1,000 responses per month.</p></div>
      <div class="rounded-2xl border border-white/10 bg-white/[0.035] p-5"><div class="text-xs font-bold uppercase tracking-wider text-violet-300">Starter</div><div class="mt-2 text-2xl font-black text-white">$15 / month</div><p class="mt-2 text-sm leading-6 text-slate-400">Annual-billing view. Includes 2,000 responses/month, login forms, signatures and redirects.</p></div>
      <div class="rounded-2xl border border-white/10 bg-white/[0.035] p-5"><div class="text-xs font-bold uppercase tracking-wider text-cyan-300">Scale up</div><div class="mt-2 text-2xl font-black text-white">Pro $40 · Business $75</div><p class="mt-2 text-sm leading-6 text-slate-400">Annual-billing view. Pro adds branding controls; Business adds unlimited responses, analytics and custom domains.</p></div>
    </section>

    <section class="mt-12 rounded-3xl border border-white/10 bg-[#101218] p-6 sm:p-8">
      <h2 class="text-2xl font-black text-white">Why this can matter for making money</h2>
      <p class="mt-3 leading-7 text-slate-300">A form does not create revenue by itself. It can, however, remove friction between a visitor and a revenue action: requesting a quote, becoming a lead, booking a service, submitting an application or paying you.</p>
      <div class="mt-6 grid gap-3 sm:grid-cols-2">
        <div class="rounded-xl bg-white/[0.035] p-4"><div class="font-bold text-white">Capture qualified leads</div><p class="mt-1 text-sm text-slate-400">Use conditional logic and multi-page forms to ask only the questions needed for the next sales step.</p></div>
        <div class="rounded-xl bg-white/[0.035] p-4"><div class="font-bold text-white">Collect payments</div><p class="mt-1 text-sm text-slate-400">Payment collection is included even on Fillout's free plan according to its current official pricing table.</p></div>
        <div class="rounded-xl bg-white/[0.035] p-4"><div class="font-bold text-white">Connect your workflow</div><p class="mt-1 text-sm text-slate-400">Current free-plan integrations include Airtable, Google Sheets, Notion, webhooks, HubSpot, Mailchimp and many more.</p></div>
        <div class="rounded-xl bg-white/[0.035] p-4"><div class="font-bold text-white">Start without subscription risk</div><p class="mt-1 text-sm text-slate-400">The free plan supports unlimited forms, so you can prove the workflow before upgrading.</p></div>
      </div>
    </section>

    <section class="mt-10 rounded-3xl border border-amber-400/15 bg-amber-400/[0.05] p-6 sm:p-8">
      <h2 class="text-xl font-black text-white">Who should try it first?</h2>
      <p class="mt-3 leading-7 text-slate-300">A good fit if you need a lead form, quote request, client intake, booking flow, order/payment form or application workflow and want to start free. If you only need a very basic survey and already use Google Workspace, compare the extra automation and design features before switching.</p>
    </section>

    <section class="mt-10 text-sm leading-6 text-slate-500">
      <p><strong class="text-slate-300">Pricing check:</strong> Fillout official pricing page, checked September 9, 2026. Prices and limits can change; verify the final terms before subscribing.</p>
      <p class="mt-2"><strong class="text-slate-300">Tracking verification:</strong> COSHUMA's exact customer-facing Fillout referral URL was issued in the authenticated Dub partner dashboard. A dashboard or generic homepage is not treated as a revenue link.</p>
    </section>
  </main>
  <footer class="border-t border-white/10 px-5 py-8 text-center text-xs text-slate-600">© 2026 COSHUMA · Independent AI & SaaS decision guides</footer>
</body>
</html>'''
page.write_text(html, encoding="utf-8")

# Keep the revenue page discoverable from the buyer hub without replacing existing offers.
hub = best_dir / "verified-software-free-trials-deals.html"
if hub.exists():
    text = hub.read_text(encoding="utf-8")
    marker = "<!-- COSHUMA_FILLOUT_REVENUE_PATH -->"
    if marker not in text:
        block = f'''\n<section class="mt-8 rounded-2xl border border-emerald-400/20 bg-emerald-400/5 p-6" id="fillout-leads">\n  {marker}\n  <div class="text-xs font-bold uppercase tracking-wider text-emerald-300">Lead & payment capture</div>\n  <h2 class="mt-2 text-2xl font-black text-white">Fillout: start with a real lead form for $0</h2>\n  <p class="mt-2 text-sm leading-6 text-slate-300">Use the free plan to test lead intake, applications or payment collection before deciding whether a paid tier is worth it.</p>\n  <div class="mt-4 flex flex-wrap gap-3"><a href="/best/fillout-form-builder.html" class="rounded-xl bg-white px-4 py-2.5 text-sm font-black text-slate-950">See Fillout buyer guide</a><a href="{tracking}" target="_blank" rel="sponsored noopener noreferrer" class="rounded-xl border border-emerald-400/30 bg-emerald-400/10 px-4 py-2.5 text-sm font-bold text-emerald-200">Try Fillout free</a></div>\n</section>\n'''
        close = "</main>"
        if close not in text:
            raise SystemExit("Verified offers hub structure changed; refusing unsafe Fillout insertion")
        text = text.replace(close, block + close, 1)
        hub.write_text(text, encoding="utf-8")

# Add the page to the sitemap idempotently.
sitemap = root / "public" / "sitemap.xml"
if sitemap.exists():
    text = sitemap.read_text(encoding="utf-8")
    url = "https://coshuma.com/best/fillout-form-builder.html"
    if url not in text:
        entry = f'''  <url>\n    <loc>{url}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>\n'''
        if "</urlset>" not in text:
            raise SystemExit("Sitemap structure changed; refusing unsafe Fillout insertion")
        text = text.replace("</urlset>", entry + "</urlset>", 1)
        sitemap.write_text(text, encoding="utf-8")

print("Published Fillout revenue buyer page, verified CTA, buyer-hub link and sitemap entry")
