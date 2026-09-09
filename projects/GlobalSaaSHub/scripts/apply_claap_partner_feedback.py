from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
PUBLIC_DIR = PROJECT_DIR / "public"

EVIDENCE_PATH = DATA_DIR / "claap-approved-2026-09-08.json"
QUEUE_EVIDENCE_PATH = DATA_DIR / "browser_required_queue.d" / "claap-approved-link-recovery-2026-09-09.json"
OFFICIAL_URL = "https://www.claap.io/"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reconcile_data(evidence: dict, queue_evidence: dict) -> None:
    if evidence.get("tool_id") != "claap" or evidence.get("status") != "approved":
        raise RuntimeError("Claap approval evidence is missing or not approved")
    if evidence.get("tracking_url") is not None or queue_evidence.get("exact_tracking_url") is not None:
        raise RuntimeError("Claap tracking URL unexpectedly present; refuse to overwrite it")
    if evidence.get("gmail_message_id") != "1a08009379826dfd":
        raise RuntimeError("Unexpected Claap approval Gmail evidence")
    if evidence.get("latest_manager_feedback", {}).get("gmail_message_id") != "1a0854b42ac1cc9a":
        raise RuntimeError("Latest Claap manager feedback evidence is missing")

    checked_at = evidence["latest_manager_feedback"]["received_at_utc"]
    markers = [
        "Claap PartnerStack welcome email 1a08009379826dfd verifies COSHUMA program acceptance.",
        "Claap manager Lamia Karmaly reviewed the COSHUMA page in message 1a0854b42ac1cc9a.",
        "The manager explicitly confirmed the current COSHUMA Claap buttons are not affiliate-tracked yet and instructed COSHUMA to recover the issued PartnerStack link.",
        "Exact customer-facing Claap tracking URL is still unverified; do not guess or construct a referral parameter.",
        "Official product domain is claap.io, not the former claap.ai reference.",
    ]

    for name in ("tools.json", "tools.next.json"):
        path = DATA_DIR / name
        tools = load_json(path)
        tool = next((item for item in tools if item.get("id") == "claap"), None)
        if not tool:
            raise RuntimeError(f"claap missing from {name}")
        tool.update(
            {
                "official_url": OFFICIAL_URL,
                "official_evidence_url": OFFICIAL_URL,
                "affiliate_url": None,
                "affiliate_final_url": None,
                # `affiliate_verified` means an exact customer-facing tracking route
                # has been verified, not merely that the program account is approved.
                # Claap is approved, but Lamia explicitly confirmed the current CTAs
                # are not affiliate-tracked yet, so this must stay false until the
                # exact issued PartnerStack link is recovered.
                "affiliate_verified": False,
                "affiliate_status": "approved",
                "affiliate_verified_at": None,
                "affiliate_status_checked_at": checked_at,
                "affiliate_status_evidence_url": f"gmail:{evidence['gmail_message_id']}",
                "affiliate_next_action": evidence["next_action"],
                "affiliate_dashboard_status": "Approved; exact customer-facing tracking link not yet verified",
                "affiliate_tracking_attribution_currently_verified": False,
                "affiliate_evidence_markers": markers,
            }
        )
        write_json(path, tools)

    outreach_path = DATA_DIR / "affiliate_outreach_state.json"
    if outreach_path.exists():
        outreach = load_json(outreach_path)
        programs = outreach.get("programs", {}) if isinstance(outreach, dict) else {}
        claap = programs.get("claap") if isinstance(programs, dict) else None
        if isinstance(claap, dict):
            claap.update(
                {
                    "status": "approved",
                    "tracking_url": None,
                    "updated_at": checked_at,
                    "note": "Approved via PartnerStack welcome email. Latest manager review confirms COSHUMA CTAs remain non-affiliate until the exact issued PartnerStack customer-facing link is recovered. Do not reapply or send duplicate outreach.",
                }
            )
            write_json(outreach_path, outreach)

    queue_path = DATA_DIR / "browser_required_queue.json"
    queue = load_json(queue_path)
    stale_ids = {"claap-affiliate-batch-20260908-0650", queue_evidence.get("id")}
    queue = [item for item in queue if item.get("id") not in stale_ids]
    queue.append(queue_evidence)
    write_json(queue_path, queue)


def fix_public_domains() -> None:
    for path in PUBLIC_DIR.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        # Some generated pages used www/no-www and slash/no-slash variants.
        # The manager explicitly confirmed claap.io as the current official domain,
        # so normalize the hostname itself instead of relying on one exact URL form.
        updated = text.replace("claap.ai", "claap.io")
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def patch_claap_page() -> None:
    path = PUBLIC_DIR / "tool" / "claap.html"
    if not path.exists():
        raise RuntimeError("Claap public page missing")

    html = path.read_text(encoding="utf-8")

    html = html.replace(
        "<li>You need a simple asynchronous video creator rather than meeting and deal intelligence.</li>",
        "<li>Your workflow rarely involves sales calls, CRM updates, coaching, or collaborative async video review.</li>",
    )

    old_pricing = (
        '<p class="text-sm text-slate-300 leading-relaxed">Claap\'s official pricing pages currently separate lighter contributor/team use from revenue-team features such as CRM auto-complete, AI-generated emails, coaching, deal insights, Smart Tables and administrative controls. The site also shows annual billing discounts and free or trial entry paths. Because Claap is actively iterating its pricing pages, COSHUMA does not hard-code a checkout price here; confirm the live amount, currency, seat minimums and included AI credits on Claap before purchase.</p>'
    )
    new_pricing = (
        '<p class="text-sm text-slate-300 leading-relaxed">Claap\'s current plan family is Free / Pro / Business / Enterprise. Claap\'s affiliate manager supplied current US-facing list prices of Pro at $40/license/month ($32 with annual billing) and Business at $75/license/month ($60 annual), with Enterprise custom. Claap\'s own site may display localized pricing in another currency, so confirm the live currency, billing cadence, seat rules and included usage at checkout.</p>'
    )
    html = html.replace(old_pricing, new_pricing)

    html = html.replace(
        '<h3 class="font-bold text-white">Basic / entry</h3><p class="text-xs text-slate-400 mt-2">Useful for contributors who mainly need recording, transcription, summaries and collaboration.</p>',
        '<h3 class="font-bold text-white">Free</h3><p class="text-xs text-slate-400 mt-2">Entry plan for contributors and lighter recording, transcription, summaries and collaboration needs.</p>',
    )
    html = html.replace(
        '<h3 class="font-bold text-purple-300">Pro / Business</h3><p class="text-xs text-slate-300 mt-2">The practical comparison point for teams that need heavier recording, AI actions, integrations, coaching and CRM automation.</p>',
        '<h3 class="font-bold text-purple-300">Pro / Business</h3><p class="text-xs text-slate-300 mt-2">US-facing published pricing: Pro $40 monthly / $32 annual; Business $75 monthly / $60 annual per license. Verify locale at checkout.</p>',
    )

    integrations_section = '''
  <section class="p-6 rounded-3xl bg-[#131520] border border-[#222538] space-y-5">
    <h2 class="text-2xl font-black text-white">Integrations and security buyers should check</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">
      <div class="p-5 rounded-2xl bg-[#181a29] border border-[#222538]"><h3 class="font-bold text-white">Revenue-stack integrations</h3><p class="text-xs text-slate-400 mt-2 leading-relaxed">Claap's current official integrations include HubSpot, Salesforce, Pipedrive, Slack, Notion and Zapier, plus meeting and calendar tools. This matters if you want call context to flow into CRM, collaboration and automation workflows instead of living in a standalone transcript.</p></div>
      <div class="p-5 rounded-2xl bg-[#181a29] border border-[#222538]"><h3 class="font-bold text-white">Security controls</h3><p class="text-xs text-slate-400 mt-2 leading-relaxed">Claap's official security material lists SOC 2 Type II, SSO, role-based access controls, audit logs and encryption controls. Enterprise buyers should still confirm the exact controls, data residency and procurement requirements that apply to their plan.</p></div>
    </div>
  </section>
'''
    if "Integrations and security buyers should check" not in html:
        verdict_marker = '<section class="p-6 rounded-3xl bg-[#131520] border border-purple-500/30 space-y-4">\n    <h2 class="text-2xl font-black text-white">COSHUMA verdict</h2>'
        if verdict_marker in html:
            html = html.replace(verdict_marker, integrations_section + "\n  " + verdict_marker, 1)

    # Run hostname normalization again because earlier build transforms can add
    # a sources-checked block after the first pass.
    html = html.replace("claap.ai", "claap.io")
    path.write_text(html, encoding="utf-8")

    final = path.read_text(encoding="utf-8")
    if "claap.ai" in final:
        raise RuntimeError("Stale claap.ai domain remains in Claap page")
    price_tokens = ("$40", "$32", "$75", "$60")
    if not all(token in final for token in price_tokens):
        raise RuntimeError("Claap manager-supplied pricing markers are missing")
    if "SOC 2 Type 2" not in final and "SOC 2 Type II" not in final:
        raise RuntimeError("Claap security marker is missing")


def validate_data() -> None:
    tools = load_json(DATA_DIR / "tools.json")
    tool = next(item for item in tools if item.get("id") == "claap")
    if tool.get("affiliate_status") != "approved":
        raise RuntimeError("Claap did not remain approved")
    if tool.get("affiliate_verified") is not False:
        raise RuntimeError("Claap tracking must remain unverified until the exact issued link is recovered")
    if tool.get("affiliate_url") is not None or tool.get("affiliate_final_url") is not None:
        raise RuntimeError("Unverified Claap tracking URL was introduced")
    if tool.get("official_url") != OFFICIAL_URL:
        raise RuntimeError("Claap official URL was not corrected")


def main() -> None:
    evidence = load_json(EVIDENCE_PATH)
    queue_evidence = load_json(QUEUE_EVIDENCE_PATH)
    reconcile_data(evidence, queue_evidence)
    fix_public_domains()
    patch_claap_page()
    validate_data()
    print("Claap reconciled safely: approved account, exact affiliate link still pending.")


if __name__ == "__main__":
    main()
