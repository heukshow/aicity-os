from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
AFFILIATE_URL = "https://pictory.ai?fpr=sangkwon-an23"

# Pictory's official signup page currently states that the free trial requires no credit card.
# Partner-side FirstPromoter totals confirmed on 2026-09-10 show 6 clicks but 0 signups,
# so this patch reduces perceived payment commitment without changing the verified tracking URL.

replacements = {
    "Use COSHUMA20 at Pictory →": "Start 14-day free trial — no card required →",
    "Start Pictory — use COSHUMA20 for 20% off →": "Open Pictory → Start 14-day trial — no card →",
    "Try Pictory — remember COSHUMA20 →": "Open Pictory → Start 14-day trial — no card →",
    "Start 14-day free trial — no card required →": "Open Pictory → Start 14-day trial — no card →",
    "Start Pictory via COSHUMA →": "Open Pictory → Start 14-day trial — no card →",
    "Start the Pictory free trial →": "Start 14-day free trial — no card required →",
    "Explore Pictory →": "Start 14-day free trial →",
}

text_replacements = {
    "Its pricing FAQ says the trial lets you create 3 video projects.":
        "The current pricing comparison lists 15 video minutes, a 5-minute maximum video length and 50 AI credits for the free trial.",
    "<div class=\"text-xs font-black uppercase tracking-wider text-purple-300\">Video projects</div><div class=\"mt-2 text-2xl font-black text-white\">3 projects</div>":
        "<div class=\"text-xs font-black uppercase tracking-wider text-purple-300\">Trial allowance</div><div class=\"mt-2 text-2xl font-black text-white\">15 video minutes</div>",
    "Its live pricing page currently offers Starter, Professional, Team and Enterprise plans, and advertises a 14-day free trial.":
        "Its live pricing page currently offers Starter, Professional, Team and Enterprise plans and advertises a 14-day free trial. Pictory's official signup page says the trial requires no credit card.",
    "Pictory's official pricing page currently lists a <strong class=\"text-white\">14-day free trial</strong>. The trial is designed to let you test the workflow before committing, and Pictory says it includes <strong class=\"text-white\">3 video projects</strong>.":
        "Pictory's official pricing page currently lists a <strong class=\"text-white\">14-day free trial</strong>, and its official signup page says <strong class=\"text-white\">no credit card is required</strong>. The current pricing comparison lists <strong class=\"text-white\">15 video minutes</strong>, a <strong class=\"text-white\">5-minute maximum video length</strong> and <strong class=\"text-white\">50 AI credits</strong> for the trial.",
    "Pictory offers a 14-day free trial with 3 video projects. Compare current Starter, Professional and Team pricing, then check the current offer and COSHUMA20 at checkout.":
        "Pictory offers a 14-day free trial with 15 video minutes, a 5-minute maximum video length and 50 AI credits, with no credit card required at signup. Compare current pricing, then check COSHUMA20 if you upgrade.",
    "Pictory's official pricing page currently advertises a 14-day free trial; verify current eligibility, limits and billing terms before starting.":
        "Pictory's official pricing page currently advertises a 14-day free trial, and its official signup page says no credit card is required; verify current eligibility and limits before starting.",
}

changed = []
for path in sorted(PUBLIC.rglob("*.html")):
    html = path.read_text(encoding="utf-8")
    if AFFILIATE_URL not in html:
        continue

    original = html
    for old, new in replacements.items():
        html = html.replace(old, new)
    for old, new in text_replacements.items():
        html = html.replace(old, new)

    if html != original:
        path.write_text(html, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

if not changed:
    raise RuntimeError("Pictory trial-conversion patch changed no monetized page; refusing a silent no-op")

# Guard the two highest-intent pages and the verified URL.
for rel in ("public/tool/pictory.html", "public/best/pictory-free-trial-pricing.html"):
    path = ROOT / rel
    html = path.read_text(encoding="utf-8")
    if AFFILIATE_URL not in html:
        raise RuntimeError(f"Verified Pictory affiliate URL missing after conversion patch: {rel}")
    if "no card required" not in html.lower() and "no credit card is required" not in html.lower():
        raise RuntimeError(f"No-card trial message missing after conversion patch: {rel}")
    if "COSHUMA20" not in html:
        raise RuntimeError(f"Verified Pictory promo code missing after conversion patch: {rel}")

# Surface the current official free-trial allowance on the main Pictory buyer page.
pictory_path = ROOT / "public/tool/pictory.html"
pictory_tool = pictory_path.read_text(encoding="utf-8")
trial_marker = 'data-pictory-trial-current="2026-09-19"'
if trial_marker not in pictory_tool:
    plan_heading = '<div class="grid grid-cols-1 md:grid-cols-3 gap-3">'
    if plan_heading not in pictory_tool:
        raise RuntimeError("Pictory plan-grid anchor missing; refusing speculative trial snapshot insertion")
    trial_block = '''<div data-pictory-trial-current="2026-09-19" class="rounded-2xl border border-emerald-400/25 bg-emerald-400/[0.06] p-5">
  <div class="text-xs font-black uppercase tracking-[0.16em] text-emerald-300">14-day free trial · no card</div>
  <div class="mt-3 grid grid-cols-2 gap-3 text-sm">
    <div><div class="text-slate-500">Video allowance</div><div class="font-black text-white">15 minutes</div></div>
    <div><div class="text-slate-500">Max video</div><div class="font-black text-white">5 minutes</div></div>
    <div><div class="text-slate-500">AI credits</div><div class="font-black text-white">50</div></div>
    <div><div class="text-slate-500">Max export</div><div class="font-black text-white">720p</div></div>
  </div>
  <p class="mt-3 text-xs leading-5 text-slate-400">Use the trial on one real script, URL or long-form asset before choosing a paid plan. Current limits can change, so confirm them on Pictory before upgrading.</p>
</div> '''
    pictory_tool = pictory_tool.replace(plan_heading, trial_block + plan_heading, 1)
    pictory_path.write_text(pictory_tool, encoding="utf-8")

pictory_tool = (ROOT / "public/tool/pictory.html").read_text(encoding="utf-8")
if "Explore Pictory →" in pictory_tool:
    raise RuntimeError("Generic Pictory buyer-box CTA survived trial-conversion patch")
if "Open Pictory → Start 14-day trial — no card →" not in pictory_tool and "Start 14-day free trial →" not in pictory_tool:
    raise RuntimeError("Pictory buyer-box trial CTA missing after conversion patch")
if 'data-pictory-trial-current="2026-09-19"' not in pictory_tool:
    raise RuntimeError("Pictory current trial allowance block missing after conversion patch")
if "3 video projects" in pictory_tool.lower():
    raise RuntimeError("Stale Pictory 3-video-project trial copy remains on the tool page")

print(f"Optimized Pictory trial conversion copy on {len(changed)} monetized pages")
for rel in changed:
    print(f" - {rel}")
