from pathlib import Path

"""Add one verified, high-intent partner CTA to each money-path section.

The hub should answer "which AI tool can help me make money?" without forcing a
second navigation step before a visitor can try a relevant tool.  Each direct
CTA below uses an already verified customer-facing tracking URL.  The script
is intentionally idempotent and only edits the dedicated make-money hub.

No earnings, conversion, or income claim is made by this patch.
"""

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "public" / "best" / "ai-tools-to-make-money.html"
text = PAGE.read_text(encoding="utf-8")

paths = {
    "get-leads": {
        "tool_id": "fillout",
        "url": "https://try.fillout.com/sang-kwon-an-hxwn",
        "eyebrow": "Low-friction starting point",
        "headline": "Need a lead or payment form first? Start with Fillout free.",
        "body": "Use a real enquiry, application or payment form before paying for a larger sales stack.",
        "cta": "Try Fillout free →",
    },
    "create-content": {
        "tool_id": "pictory",
        "url": "https://pictory.ai?fpr=sangkwon-an23",
        "eyebrow": "Verified partner offer",
        "headline": "Want to turn scripts into videos? Try Pictory through COSHUMA.",
        "body": "COSHUMA's verified Pictory route is active. Use code COSHUMA20 where eligible and confirm the discount at checkout before relying on it.",
        "cta": "Open Pictory partner offer →",
    },
    "sell-online": {
        "tool_id": "clickfunnels",
        "url": "https://www.clickfunnels.com/signup-flow?aff=b57f3056884d05b842f607e32347df542821875bbe3209a214141aa32a210532",
        "eyebrow": "Verified funnel path",
        "headline": "Need a sales funnel rather than a general website? Test ClickFunnels.",
        "body": "Use the verified COSHUMA campaign route to evaluate whether its funnel workflow fits your offer before committing to a paid plan.",
        "cta": "Try ClickFunnels →",
    },
    "automate-work": {
        "tool_id": "make-com",
        "url": "https://www.make.com/?pc=coshuma",
        "eyebrow": "Verified automation path",
        "headline": "Need to automate repeatable client work? Start with Make.",
        "body": "Build one real multi-step workflow first, measure the time it removes, and only then decide whether scaling the automation is worth paying for.",
        "cta": "Open Make via COSHUMA →",
    },
    "grow-traffic": {
        "tool_id": "writesonic",
        "url": "https://writesonic.com?fp_ref=sang-kwon-f5452a",
        "eyebrow": "Verified SEO/content path",
        "headline": "Need search-focused content and optimisation? Compare Writesonic.",
        "body": "Use the verified COSHUMA route to test whether its content and SEO workflow fits the buyer queries you actually want to rank for.",
        "cta": "Try Writesonic →",
    },
}

for section_id, item in paths.items():
    marker = f"<!-- COSHUMA_DIRECT_REVENUE_PATH_{section_id} -->"
    if marker in text:
        continue

    start_token = f'<section id="{section_id}"'
    start = text.find(start_token)
    if start == -1:
        raise SystemExit(f"Missing expected money-path section: {section_id}")
    close = text.find("</section>", start)
    if close == -1:
        raise SystemExit(f"Missing closing section tag for: {section_id}")

    block = f'''\n      {marker}\n      <div class="mt-5 flex flex-col gap-4 rounded-2xl border border-violet-400/20 bg-violet-500/[0.07] p-5 sm:flex-row sm:items-center sm:justify-between">\n        <div class="max-w-3xl">\n          <div class="text-[10px] font-black uppercase tracking-[0.16em] text-violet-300">{item['eyebrow']}</div>\n          <div class="mt-1 font-black text-white">{item['headline']}</div>\n          <p class="mt-1 text-xs leading-5 text-slate-400">{item['body']}</p>\n        </div>\n        <a data-cta="affiliate" data-tool-id="{item['tool_id']}" data-cta-source="make_money_hub_{section_id}" href="{item['url']}" target="_blank" rel="sponsored noopener noreferrer" class="inline-flex min-h-11 shrink-0 items-center justify-center rounded-xl bg-violet-500 px-5 py-3 text-sm font-black text-white hover:bg-violet-400">{item['cta']}</a>\n      </div>\n      <p class="mt-2 text-[10px] leading-4 text-slate-600">Partner disclosure: COSHUMA may earn a commission if you purchase after using a verified partner link. Your price is not increased by COSHUMA.</p>\n'''
    text = text[:close] + block + text[close:]

PAGE.write_text(text, encoding="utf-8")
print("Make-money hub: verified direct revenue CTAs added for five buyer intents")
