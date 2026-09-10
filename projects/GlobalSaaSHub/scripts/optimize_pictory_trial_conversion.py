from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
AFFILIATE_URL = "https://pictory.ai?fpr=sangkwon-an23"

# Pictory's official signup page currently states that the free trial requires no credit card.
# Partner-side FirstPromoter totals confirmed on 2026-09-10 show 6 clicks but 0 signups,
# so this patch reduces perceived payment commitment without changing the verified tracking URL.

replacements = {
    "Use COSHUMA20 at Pictory →": "Start 14-day free trial — no card required →",
    "Start Pictory — use COSHUMA20 for 20% off →": "Start 14-day free trial — no card required →",
    "Try Pictory — remember COSHUMA20 →": "Start 14-day free trial — no card required →",
    "Start through verified partner link →": "Start 14-day free trial — no card required →",
    "Start Pictory via COSHUMA →": "Start 14-day free trial — no card required →",
    "Start the Pictory free trial →": "Start 14-day free trial — no card required →",
}

text_replacements = {
    "Its live pricing page currently offers Starter, Professional, Team and Enterprise plans, and advertises a 14-day free trial.":
        "Its live pricing page currently offers Starter, Professional, Team and Enterprise plans and advertises a 14-day free trial. Pictory's official signup page says the trial requires no credit card.",
    "Pictory's official pricing page currently lists a <strong class=\"text-white\">14-day free trial</strong>. The trial is designed to let you test the workflow before committing, and Pictory says it includes <strong class=\"text-white\">3 video projects</strong>.":
        "Pictory's official pricing page currently lists a <strong class=\"text-white\">14-day free trial</strong>, and its official signup page says <strong class=\"text-white\">no credit card is required</strong>. The trial is designed to let you test the workflow before committing, and Pictory says it includes <strong class=\"text-white\">3 video projects</strong>.",
    "Pictory offers a 14-day free trial with 3 video projects. Compare current Starter, Professional and Team pricing, then use COSHUMA's verified partner link and COSHUMA20 at checkout.":
        "Pictory offers a 14-day free trial with 3 video projects and no credit card required at signup. Compare current pricing, then use COSHUMA's verified partner link and COSHUMA20 if you upgrade.",
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

print(f"Optimized Pictory trial conversion copy on {len(changed)} monetized pages")
for rel in changed:
    print(f" - {rel}")
