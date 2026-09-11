from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_generated_box(page: Path, auto_box: str, tool_id: str) -> str:
    text = page.read_text(encoding="utf-8")
    start_marker = "<!-- buyer-box:start -->"
    end_marker = "<!-- buyer-box:end -->"
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start < 0 or end < start:
        raise SystemExit(f"{tool_id} generated buyer box markers missing; refusing unsafe patch")
    end += len(end_marker)
    return text[:start] + auto_box + text[end:]


# BoldSign: keep the generated box aligned with current trial/free-plan evidence.
BOLDSIGN_PAGE = ROOT / "public" / "tool" / "boldsign.html"
BOLDSIGN_BOX = '''<!-- buyer-box:start -->
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

boldsign = replace_generated_box(BOLDSIGN_PAGE, BOLDSIGN_BOX, "BoldSign")
manual_marker = ">LOW-RISK TEST<"
idx = boldsign.find(manual_marker)
if idx >= 0:
    section_start = boldsign.rfind("<section", 0, idx)
    section_end = boldsign.find("</section>", idx)
    if section_start < 0 or section_end < 0:
        raise SystemExit("BoldSign manual buyer box boundaries changed; refusing unsafe patch")
    section_end += len("</section>")
    boldsign = boldsign[:section_start] + boldsign[section_end:]
if boldsign.count('data-buyer-decision-box="boldsign"') != 1:
    raise SystemExit("BoldSign must have exactly one buyer decision box")
if "Free-plan and trial availability are not confirmed here" in boldsign:
    raise SystemExit("Stale BoldSign free/trial uncertainty survived buyer-box patch")
if "/tool/notion-ai.html" in boldsign[boldsign.find("<!-- buyer-box:start -->"):boldsign.find("<!-- buyer-box:end -->")]:
    raise SystemExit("Irrelevant Notion AI alternative survived BoldSign buyer-box patch")
if "https://boldsign.com?via=sangkwon" not in boldsign:
    raise SystemExit("Verified BoldSign affiliate URL missing")
if "/affiliate-attribution.js" not in boldsign:
    raise SystemExit("BoldSign attribution script missing")
BOLDSIGN_PAGE.write_text(boldsign, encoding="utf-8")


# Kittl: taxonomy currently places unrelated tools in the same comparison group.
# Replace the generated box with a product-specific decision box and remove the
# hand-written duplicate. Do not present QuillBot/Kinsta as Kittl alternatives.
KITTL_PAGE = ROOT / "public" / "tool" / "kittl.html"
KITTL_BOX = '''<!-- buyer-box:start -->
<section data-buyer-decision-box="kittl" class="rounded-2xl border border-purple-400/40 bg-slate-900 p-6 my-6 space-y-4" aria-label="Buyer decision box">
<h2 class="text-2xl font-bold">Is Kittl right for you?</h2>
<div class="grid md:grid-cols-2 gap-5"><div><h3 class="font-bold">Best for</h3><ul class="list-disc pl-5 space-y-1"><li>Creators who want to learn Kittl before paying</li><li>Personal projects that can start with low-resolution PNG or JPG exports</li></ul></div><div><h3 class="font-bold">Compare first if</h3><ul class="list-disc pl-5 space-y-1"><li>You need commercial-use rights for client work or products</li><li>You need high-resolution or vector exports immediately</li></ul></div></div>
<h3 class="font-bold">Why start free?</h3><ul class="list-disc pl-5 space-y-1"><li>The Free plan is documented as free forever with no expiry</li><li>No credit card is required to start creating</li><li>You can test the editor before deciding whether commercial licensing and pro exports justify a paid plan</li></ul>
<div class="grid md:grid-cols-2 gap-4"><div><h3 class="font-bold">Free-plan boundary</h3><p>Free is for personal-use designs and low-resolution PNG/JPG exports. Kittl documents high-resolution/vector exports and commercial licensing as paid-plan benefits.</p></div><div><h3 class="font-bold">Before commercial use</h3><p><a class="underline" href="/best/kittl-commercial-use-license.html">Read the Kittl commercial-use guide</a></p></div></div>
<p>Start with one real design workflow for free. Upgrade only if your intended use requires the paid license, premium assets, higher-resolution/vector output or larger limits.</p>
<p class="text-sm text-slate-400">Official/public source: <a data-cta-source="buyer-box-source" href="https://help.kittl.com/subscription-billing/about-free-plan/" target="_blank" rel="noopener noreferrer" class="underline">check current Kittl Free-plan limits</a>. Editorial fit guidance, not a hands-on performance benchmark.</p>
<p data-affiliate-disclosure="buyer-box" class="text-sm text-slate-300">COSHUMA may earn a commission on a qualifying paid purchase through the verified partner link, at no extra cost to you. Starting the Free plan alone is not proof of commission.</p>
<div class="flex flex-wrap gap-3"><a data-cta="affiliate" data-cta-source="buyer-box-primary" data-tool-id="kittl" href="https://kittl.pxf.io/0GMrXY" target="_blank" rel="sponsored noopener noreferrer" class="rounded-xl bg-purple-600 px-5 py-3 font-bold">Start Kittl Free — No Card →</a><a data-cta="official" data-cta-source="buyer-box-official" href="https://www.kittl.com/pricing" target="_blank" rel="noopener noreferrer" class="rounded-xl border border-slate-500 px-5 py-3">Official pricing</a></div>
<p>Need commercial use? <a data-cta-source="buyer-box-guide" class="underline" href="/best/kittl-commercial-use-license.html">Check the licensing decision guide</a>.</p>
</section>
<!-- buyer-box:end -->'''

kittl = replace_generated_box(KITTL_PAGE, KITTL_BOX, "Kittl")
kittl_manual_marker = ">Buyer decision box<"
idx = kittl.find(kittl_manual_marker)
if idx >= 0:
    section_start = kittl.rfind("<section", 0, idx)
    section_end = kittl.find("</section>", idx)
    if section_start < 0 or section_end < 0:
        raise SystemExit("Kittl manual buyer box boundaries changed; refusing unsafe patch")
    section_end += len("</section>")
    kittl = kittl[:section_start] + kittl[section_end:]

if kittl.count('data-buyer-decision-box="kittl"') != 1:
    raise SystemExit("Kittl must have exactly one generated buyer decision box")
kittl_box_region = kittl[kittl.find("<!-- buyer-box:start -->"):kittl.find("<!-- buyer-box:end -->")]
for bad in ("/tool/quillbot.html", "/tool/kinsta.html"):
    if bad in kittl_box_region:
        raise SystemExit(f"Irrelevant Kittl alternative survived buyer-box patch: {bad}")
if "https://kittl.pxf.io/0GMrXY" not in kittl_box_region:
    raise SystemExit("Verified Kittl affiliate URL missing from buyer box")
if "/affiliate-attribution.js" not in kittl:
    raise SystemExit("Kittl attribution script missing")
KITTL_PAGE.write_text(kittl, encoding="utf-8")

print("buyer-box-current-v2: boldsign,kittl")
