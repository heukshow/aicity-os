from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "public" / "tool" / "databox.html"
TRACKING_URL = "https://databox.com?aff_id=15298659&fp_ref=sangkwon-72c9ec"

html = PAGE.read_text(encoding="utf-8")
before_tracking = html.count(TRACKING_URL)
if before_tracking < 1:
    raise SystemExit("Databox tracking URL missing; refusing to rewrite customer copy")

replacements = {
    "plus a 14-day no-card trial through COSHUMA's verified referral link.":
        "plus a 14-day no-card trial and current plan limits.",
    "Affiliate disclosure: this button uses COSHUMA's verified Databox referral URL. COSHUMA may earn a commission if an eligible referred user becomes a customer, at no extra cost to the user.":
        "Affiliate disclosure: COSHUMA may earn a commission if an eligible referred user becomes a customer through this link, at no extra cost to the user.",
    "Databox's affiliate team recommends focusing on one real use case instead of trying to review every feature. For a clean test, use a question your current reports do not answer quickly.":
        "A useful trial starts with one real use case instead of trying to review every feature. For a clean test, use a question your current reports do not answer quickly.",
    "Use the verified COSHUMA referral route, test the question above, and add payment details only if the workflow earns its cost.":
        "Use the trial link below, test the question above, and add payment details only if the workflow earns its cost.",
    "Workflow source: Databox Affiliate Program email received by support@coshuma.com on Sep 14, 2026. Product and trial claims are cross-checked against the official Databox pages cited below.":
        "Product and trial claims are checked against the official Databox pages cited below.",
    "Databox's affiliate team highlighted three current AI workflows worth testing before you pay. COSHUMA rechecked each capability against Databox's official product and help pages on September 9, 2026.":
        "Three current AI workflows are worth testing before you pay. COSHUMA checked each capability against Databox's official product and help pages on September 17, 2026.",
    "Product sources: Databox AI Analyst, Databox MCP and Databox AI performance summaries. Affiliate disclosure: the trial button uses COSHUMA's already verified Databox referral URL.":
        "Product sources: Databox AI Analyst, Databox MCP and Databox AI performance summaries. Affiliate disclosure: COSHUMA may earn a commission from an eligible purchase through the trial button, at no extra cost to the user.",
}

changed = 0
for old, new in replacements.items():
    if old in html:
        html = html.replace(old, new)
        changed += 1

for forbidden in (
    "Databox's affiliate team",
    "Databox Affiliate Program email received by",
    "support@coshuma.com",
    "verified Databox referral URL",
    "verified COSHUMA referral route",
    "already verified Databox referral URL",
):
    if forbidden in html:
        raise SystemExit(f"Buyer-visible internal Databox wording remains: {forbidden}")

if html.count(TRACKING_URL) != before_tracking:
    raise SystemExit("Databox tracking URL count changed during customer-copy cleanup")
if "Affiliate disclosure:" not in html:
    raise SystemExit("Databox affiliate disclosure missing after customer-copy cleanup")

PAGE.write_text(html, encoding="utf-8")
print(f"Databox customer copy cleaned: replacements={changed}, tracking_urls={before_tracking}")
