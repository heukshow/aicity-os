from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "tool" / "boldsign.html"

AUTO_BOX = '''<!-- buyer-box:start -->
<section data-buyer-decision-box="boldsign" class="rounded-2xl border border-purple-400/40 bg-slate-900 p-6 my-6 space-y-4" aria-label="Buyer decision box">
<h2 class="text-2xl font-bold">Is BoldSign right for you?</h2>
<div class="grid md:grid-cols-2 gap-5"><div><h3 class="font-bold">Best for</h3><ul class="list-disc pl-5 space-y-1"><li>Freelancers and teams replacing print-sign-scan workflows</li><li>HR, sales and operations teams that want signatures with less back-and-forth</li></ul></div><div><h3 class="font-bold">Compare first if</h3><ul class="list-disc pl-5 space-y-1"><li>Your procurement process requires a specific incumbent e-signature vendor</li><li>You need specialized regional compliance, identity verification or integration requirements</li></ul></div></div>
<h3 class="font-bold">Why consider it?</h3><ul class="list-disc pl-5 space-y-1"><li>Ongoing Essential free plan with 25 envelopes per month</li><li>30-day free trial currently advertised with no credit card required</li><li>Business tier currently advertises unlimited envelopes and templates</li></ul>
<div class="grid md:grid-cols-2 gap-4"><div><h3 class="font-bold">Starting price / free option</h3><p>Essential $0. Growth starts from $5/month/user in the lower-cost billing view; verify the selected billing cycle before checkout.</p></div><div><h3 class="font-bold">Relevant nearby alternative</h3><p><a class="underline" href="/tool/fill-esignature.html">Fill eSignature</a></p></div></div>
<dl><dt class="font-bold">Free plan</dt><dd>Essential currently includes 25 envelopes/month and 2 templates at $0.</dd><dt class="font-bold">Free trial</dt><dd>BoldSign currently advertises a 30-day free trial with no credit card required.</dd></dl>
<p>Test one real signing workflow first. Then compare envelope volume, users, templates, add-ons and the current billing-cycle price before paying.</p>
<p class="text-sm text-slate-400">Official/public source: <a data-cta-source="buyer-box-source" href="https://www.boldsign.com/electronic-signature-pricing/" target="_blank" rel="noopener noreferrer" class="underline">check current BoldSign pricing and trial details</a>. Editorial fit guidance, not a hands-on performance benchmark.</p>
<p data-affiliate-disclosure="buyer-box" class="text-sm text-slate-300">COSHUMA may earn a commission on qualifying purchases through this partner link, at no extra cost to you.</p>
<div class="flex flex-wrap gap-3"><a data-cta="affiliate" data-cta-source="buyer-box-primary" data-tool-id="boldsign" href="https://boldsign.com?via=sangkwon" target="_blank" rel="sponsored noopener noreferrer" class="rounded-xl bg-purple-600 px-5 py-3 font-bold">Start 30-Day BoldSign Trial — No Card →</a><a data-cta="official" data-cta-source="buyer-box-official" href="https://www.boldsign.com/electronic-signature-pricing/" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-slate-500 px-5 py-3">Official pricing</a></div>
<p>Compare alternative: <a data-cta-source="buyer-box-alternative" class="underline" href="/tool/fill-esignature.html">Fill eSignature</a></p>
</section>
<!-- buyer-box:end -->'''

text = PAGE.read_text(encoding="utf-8")
start_marker = "<!-- buyer-box:start -->"
end_marker = "<!-- buyer-box:end -->"
start = text.find(start_marker)
end = text.find(end_marker)
if start < 0 or end < start:
    raise SystemExit("BoldSign generated buyer box markers missing; refusing unsafe patch")
end += len(end_marker)
text = text[:start] + AUTO_BOX + text[end:]

# Remove the temporary hand-written box if it is present. The generated box above
# is the single source of buyer-decision truth in the production document.
manual_marker = ">LOW-RISK TEST<"
idx = text.find(manual_marker)
if idx >= 0:
    section_start = text.rfind("<section", 0, idx)
    section_end = text.find("</section>", idx)
    if section_start < 0 or section_end < 0:
        raise SystemExit("BoldSign manual buyer box boundaries changed; refusing unsafe patch")
    section_end += len("</section>")
    text = text[:section_start] + text[section_end:]

if text.count('data-buyer-decision-box="boldsign"') != 1:
    raise SystemExit("BoldSign must have exactly one buyer decision box")
if "Free-plan and trial availability are not confirmed here" in text:
    raise SystemExit("Stale BoldSign free/trial uncertainty survived buyer-box patch")
if "/tool/notion-ai.html" in text[text.find(start_marker):text.find(end_marker) + len(end_marker)]:
    raise SystemExit("Irrelevant Notion AI alternative survived BoldSign buyer-box patch")
if "https://boldsign.com?via=sangkwon" not in text:
    raise SystemExit("Verified BoldSign affiliate URL missing")
if "/affiliate-attribution.js" not in text:
    raise SystemExit("BoldSign attribution script missing")

PAGE.write_text(text, encoding="utf-8")
print("boldsign-buyer-box-current-v1")
