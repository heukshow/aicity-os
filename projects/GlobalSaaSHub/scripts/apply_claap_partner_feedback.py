from __future__ import annotations

import csv
import io
import json
import re
from html import escape
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
PUBLIC_DIR = PROJECT_DIR / "public"
QUEUE_EVIDENCE_PATH = DATA_DIR / "browser_required_queue.d" / "claap-approved-link-recovery-2026-09-09.json"
OFFICIAL_URL = "https://www.claap.io/"
BUYER_TEST_ID = "claap-3-call-checklist"
BUYER_TEST_TITLE = "A practical 3-call test before paying"
CHECKLIST_URL = "/resources/claap-3-call-coaching-checklist.csv"
# Editorial evaluation prompts, not customer statements or COSHUMA test results.
# The same five checks generate both buyer pages and the blank worksheet.
COACHING_CHECKS = (
    ("Evidence quote", "Trace each useful insight to a short, redacted quote or timestamp in the call record. Check the surrounding context before accepting the summary."),
    ("Objection", "Compare the captured concern with what the buyer actually said. Keep an unresolved objection visible instead of treating it as an agreement."),
    ("Next step", "Check that the proposed action was agreed on the call and is specific enough to act on. Mark an unstated next step as missing."),
    ("Owner and deadline", "Check who agreed to act and by when. Use a role or call label in the worksheet; record Not stated when either detail was not agreed."),
    ("CRM field", "Check the destination record, field and saved value against the approved call notes. Record any correction or plan limitation before relying on the handoff."),
)


def buyer_test_html() -> str:
    rows = "\n".join(
        f'        <tr class="border-t border-[#30344c]"><th scope="row" class="px-4 py-4 text-left align-top font-bold text-white">{escape(label)}</th><td class="px-4 py-4 align-top leading-relaxed">{escape(prompt)}</td></tr>'
        for label, prompt in COACHING_CHECKS
    )
    return f'''<section id="{BUYER_TEST_ID}" aria-labelledby="{BUYER_TEST_ID}-title" class="p-6 rounded-3xl bg-[#131520] border border-[#222538] space-y-5">
    <h2 id="{BUYER_TEST_ID}-title" class="text-2xl font-black text-white">{BUYER_TEST_TITLE}</h2>
    <p class="text-sm text-slate-300 leading-relaxed">Use one discovery, one demo and one follow-up call you are allowed to process. Compare the notes and follow-up draft with each call record, then check the actual CRM handoff on the plan you are considering.</p>
    <div class="overflow-x-auto rounded-xl border border-[#30344c]">
      <table class="w-full text-sm text-slate-300">
        <caption class="px-4 py-3 text-left text-xs text-slate-400">Repeat these five checks for each call. Fill in the blank worksheet with your own observations.</caption>
        <thead class="bg-[#181a29]"><tr><th scope="col" class="px-4 py-3 text-left text-white">Check</th><th scope="col" class="px-4 py-3 text-left text-white">What to verify</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p class="text-sm text-slate-300 leading-relaxed"><strong class="text-white">Record a result in each cell:</strong> Pass, Needs correction, Not stated, or Unavailable on this plan, followed by a short redacted note. Use Not stated for information absent from the call; use Needs correction if the output invents it. Record the correction needed before sharing the follow-up or updating CRM.</p>
    <a href="{CHECKLIST_URL}" download="claap-3-call-coaching-checklist.csv" class="inline-flex items-center px-5 py-3 rounded-xl border border-purple-400/40 bg-purple-500/10 text-sm font-bold text-purple-200 hover:bg-purple-500/20">Download the blank 3-call checklist (CSV)</a>
    <p class="text-xs text-slate-400 leading-relaxed">The worksheet has three call rows and five blank review fields per call. Fill it locally using call labels and redacted notes; keep customer details in your approved systems.</p>
    <div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 text-sm text-slate-300 leading-relaxed"><strong class="text-white">Use the results to decide:</strong> Identify repeated corrections, missing commitments and unavailable CRM features. Test configuration changes on another call, then compare the required plan and review effort with your current workflow before paying.</div>
    <p class="text-xs text-slate-400 leading-relaxed">COSHUMA evaluation worksheet. For the documented workflow and plan access, see <a href="https://www.claap.io/automatic-note-taker" target="_blank" rel="noopener noreferrer" class="text-purple-300 underline">Claap's note-taking documentation</a>. This worksheet contains no completed product test or customer results.</p>
  </section>'''


def apply_buyer_test() -> None:
    section = buyer_test_html()
    for relative in ("tool/claap.html", "best/claap-sales-follow-up-ai.html"):
        page = PUBLIC_DIR / relative
        original = page.read_text(encoding="utf-8")
        # Replace the existing test in place, including its earlier unmarked form.
        # Other sections, CTA attributes, disclosures and pricing stay untouched.
        pattern = re.compile(
            r'<section\b[^>]*>(?:(?!</section>).)*?<h2\b[^>]*>'
            + re.escape(BUYER_TEST_TITLE)
            + r'</h2>(?:(?!</section>).)*?</section>',
            re.S,
        )
        updated, count = pattern.subn(lambda _: section, original)
        if count > 1:
            raise RuntimeError(f"Duplicate Claap buyer tests in {relative}")
        if count == 0:
            marker = re.search(r'<section\b[^>]*>\s*<h2\b[^>]*>COSHUMA verdict</h2>', original)
            if not marker:
                raise RuntimeError(f"Claap buyer-test insertion point missing in {relative}")
            updated = original[:marker.start()] + section + "\n  " + original[marker.start():]
        if updated != original:
            page.write_text(updated, encoding="utf-8")

    # A call label plus the five review fields; all observation cells stay blank.
    worksheet = io.StringIO(newline="")
    writer = csv.writer(worksheet, lineterminator="\n")
    writer.writerow(("call_label", "evidence_quote_or_timestamp", "objection", "next_step", "owner_and_deadline", "crm_field_and_saved_value"))
    for number in range(1, 4):
        writer.writerow((f"Call {number}", "", "", "", "", ""))
    target = PUBLIC_DIR / CHECKLIST_URL.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.read_text(encoding="utf-8") != worksheet.getvalue():
        target.write_text(worksheet.getvalue(), encoding="utf-8")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fix_public_domains() -> None:
    for path in PUBLIC_DIR.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        updated = text.replace("claap.ai", "claap.io")
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def validate_current_tracking() -> None:
    evidence = load_json(QUEUE_EVIDENCE_PATH)
    primary = evidence.get("exact_tracking_url")
    alternate = evidence.get("alternate_verified_url")
    if evidence.get("affiliate_status") != "approved_tracking":
        raise RuntimeError("Claap resolved tracking evidence is not approved_tracking")
    if not isinstance(primary, str) or not primary.startswith("https://get.claap.io/"):
        raise RuntimeError("Claap primary vendor-issued tracking URL is missing")
    if not isinstance(alternate, str) or not alternate.startswith("https://get.claap.io/"):
        raise RuntimeError("Claap alternate vendor-issued tracking URL is missing")

    for name in ("tools.json", "tools.next.json"):
        tools = load_json(DATA_DIR / name)
        tool = next((item for item in tools if item.get("id") == "claap"), None)
        if not tool:
            raise RuntimeError(f"claap missing from {name}")
        if tool.get("affiliate_status") != "approved_tracking":
            raise RuntimeError(f"Claap status regressed in {name}: {tool.get('affiliate_status')}")
        if tool.get("affiliate_verified") is not True:
            raise RuntimeError(f"Claap tracking verification regressed in {name}")
        if tool.get("affiliate_url") != primary:
            raise RuntimeError(f"Claap primary tracking URL regressed in {name}")
        if tool.get("official_url") != OFFICIAL_URL:
            raise RuntimeError(f"Claap official URL regressed in {name}")

    page = (PUBLIC_DIR / "tool" / "claap.html").read_text(encoding="utf-8")
    if primary not in page or 'data-cta-source="claap_verified_offer"' not in page:
        raise RuntimeError("Claap verified revenue CTA is missing from the public page")
    if 'rel="sponsored noopener noreferrer"' not in page:
        raise RuntimeError("Claap affiliate CTA is missing the sponsored safety relation")
    if 'data-cta="affiliate"' in page and "Affiliate disclosure:" not in page and 'data-affiliate-disclosure=' not in page:
        raise RuntimeError("Claap affiliate CTA is missing the required customer-facing affiliate disclosure")
    unsupported_buyer_claims = ("30% off the first 2 months", "10% off the first year", "partner discount →", "referral discount →")
    for claim in unsupported_buyer_claims:
        if claim in page:
            raise RuntimeError(f"Unsupported current Claap buyer-discount claim remains: {claim}")
    if 'href="https://www.claap.io/pricing"' not in page:
        raise RuntimeError("Claap official pricing evidence link is missing")
    if "claap.ai" in page:
        raise RuntimeError("Stale claap.ai domain remains in Claap page")


def main() -> None:
    # Historical versions of this script intentionally downgraded Claap to
    # `approved` while the exact PartnerStack URL was still unknown. That is no
    # longer valid: Lamia Karmaly subsequently supplied both exact URLs, and the
    # repository now treats `approved_tracking` as authoritative. This guard is
    # deliberately non-destructive so a normal build can never reopen the solved
    # browser task or erase a verified revenue route.
    fix_public_domains()
    validate_current_tracking()
    apply_buyer_test()
    print("Claap partner feedback guard: verified tracking preserved; no downgrade performed.")


if __name__ == "__main__":
    main()
