from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
PUBLIC_DIR = PROJECT_DIR / "public"
EVIDENCE_PATH = DATA_DIR / "claap-teachable-tracking-update-2026-09-09.json"
TEACHABLE_QUEUE_PATH = DATA_DIR / "browser_required_queue.d" / "teachable-approved-tracking-recovery-2026-09-09.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reconcile_tools(evidence: dict) -> None:
    claap_e = evidence["claap"]
    teachable_e = evidence["teachable"]
    primary = claap_e["primary_tracking_url"]
    alternate = claap_e["alternate_tracking_url"]
    teachable_url = teachable_e["tracking_url"]

    for name in ("tools.json", "tools.next.json"):
        path = DATA_DIR / name
        tools = load_json(path)

        claap = next((item for item in tools if item.get("id") == "claap"), None)
        teachable = next((item for item in tools if item.get("id") == "teachable"), None)
        if not claap or not teachable:
            raise RuntimeError(f"claap or teachable missing from {name}")

        claap.update(
            {
                "affiliate_url": primary,
                "affiliate_final_url": primary,
                "affiliate_verified": True,
                "affiliate_status": "approved_tracking",
                "affiliate_verified_at": claap_e["received_at_utc"],
                "affiliate_status_checked_at": claap_e["received_at_utc"],
                "affiliate_status_evidence_url": f"gmail:{claap_e['gmail_message_id']}",
                "affiliate_tracking_url_verified": True,
                "affiliate_tracking_attribution_currently_verified": False,
                "affiliate_alternate_verified_urls": [alternate],
                "affiliate_dashboard_status": "Approved; two exact PartnerStack affiliate URLs supplied directly by Claap manager",
                "affiliate_next_action": "Keep the first vendor-issued URL as the default tracked CTA. Await Lamia's destination/custom-label mapping for both issued URLs before using the second for destination-specific routing. Do not reapply.",
                "affiliate_evidence_markers": [
                    "Claap PartnerStack welcome email 1a08009379826dfd verifies COSHUMA program acceptance.",
                    f"Claap affiliate manager Lamia Karmaly copied the exact customer-facing PartnerStack URLs into Gmail message {claap_e['gmail_message_id']}.",
                    f"Primary verified tracking URL: {primary}",
                    f"Alternate verified tracking URL: {alternate}",
                    "The first vendor-issued URL is used as the default revenue CTA until the manager identifies the intended destination/custom label of each link.",
                    "Exact tracking route is verified; no actual click, signup, commission, or revenue is inferred from URL issuance alone.",
                ],
            }
        )

        teachable.update(
            {
                "affiliate_url": teachable_url,
                "affiliate_final_url": teachable_url,
                "affiliate_verified": True,
                "affiliate_status": "approved_tracking",
                "affiliate_verified_at": teachable_e["received_at_utc"],
                "affiliate_status_checked_at": teachable_e["received_at_utc"],
                "affiliate_status_evidence_url": f"gmail:{teachable_e['tracking_reply_gmail_message_id']}",
                "affiliate_tracking_url_verified": True,
                "affiliate_tracking_attribution_currently_verified": False,
                "affiliate_dashboard_status": "Approved; exact unique PartnerStack customer tracking URL supplied directly by Teachable manager",
                "affiliate_next_action": "Use the exact vendor-supplied PartnerStack URL as the default Teachable revenue CTA. Await the vendor-supplied tracked 30-day extended-trial URL before adding a trial-specific deeplink. Do not reapply or guess a wrapper.",
                "affiliate_evidence_markers": [
                    f"Teachable welcome email {teachable_e['approval_gmail_message_id']} confirms COSHUMA is approved for the Teachable Affiliate Program.",
                    f"Teachable manager Camila Gouveia pasted COSHUMA's exact unique customer-facing PartnerStack URL into Gmail message {teachable_e['tracking_reply_gmail_message_id']}.",
                    f"Primary verified tracking URL: {teachable_url}",
                    "The affiliate-only 30-day extended-trial landing page still requires an exact tracked vendor-issued URL before it can be used as an affiliate CTA.",
                    f"COSHUMA requested that exact trial URL from support@coshuma.com in sent Gmail message {teachable_e['extended_trial_followup_sent_message_id']}.",
                    "Do not use the generic partners page, PartnerStack dashboard/login, unwrapped partner30 page, onboarding URL, or guessed tracking wrapper as an affiliate CTA.",
                    "Exact tracking route is verified; no actual click, signup, commission, or revenue is inferred from URL issuance alone.",
                ],
            }
        )
        write_json(path, tools)


def reconcile_outreach(evidence: dict) -> None:
    path = DATA_DIR / "affiliate_outreach_state.json"
    if not path.exists():
        return
    state = load_json(path)
    if not isinstance(state, dict):
        raise RuntimeError("affiliate_outreach_state.json must be an object")
    programs = state.setdefault("programs", {})
    if not isinstance(programs, dict):
        raise RuntimeError("affiliate_outreach_state.json programs must be an object")

    claap_e = evidence["claap"]
    teachable_e = evidence["teachable"]
    claap = programs.setdefault("claap", {})
    claap.update(
        {
            "status": "approved_tracking",
            "tracking_url": claap_e["primary_tracking_url"],
            "sender": "support@coshuma.com",
            "updated_at": claap_e["received_at_utc"],
            "note": "Approved Claap account now has exact manager-supplied PartnerStack URLs. Use the first issued URL as the default tracked CTA; do not reapply. Actual click/revenue remains unverified.",
        }
    )

    teachable = programs.setdefault("teachable", {})
    teachable.update(
        {
            "status": "approved_tracking",
            "tracking_url": teachable_e["tracking_url"],
            "sender": "support@coshuma.com",
            "gmail_message_id": teachable_e["tracking_reply_gmail_message_id"],
            "updated_at": teachable_e["received_at_utc"],
            "note": "Teachable manager supplied COSHUMA's exact unique PartnerStack URL by email. Use it as the default tracked CTA. Tracked 30-day trial deeplink remains pending vendor confirmation; do not reapply or guess a wrapper.",
        }
    )
    write_json(path, state)


def reconcile_browser_queue(evidence: dict) -> None:
    path = DATA_DIR / "browser_required_queue.json"
    if not path.exists():
        return
    queue = load_json(path)
    if not isinstance(queue, list):
        raise RuntimeError("browser_required_queue.json must be a list")

    remove_ids = {
        "claap-affiliate-batch-20260908-0650",
        "claap-approved-link-recovery-2026-09-09",
        "claap-approved-tracking-2026-09-09",
        "teachable-affiliate-application-2026-09-09",
        "teachable-approved-tracking-recovery-2026-09-09",
    }
    queue = [item for item in queue if item.get("id") not in remove_ids]
    claap_e = evidence["claap"]
    queue.append(
        {
            "id": "claap-approved-tracking-2026-09-09",
            "tool_id": "claap",
            "priority": "resolved",
            "status": "resolved",
            "affiliate_status": "approved_tracking",
            "exact_tracking_url": claap_e["primary_tracking_url"],
            "alternate_verified_urls": [claap_e["alternate_tracking_url"]],
            "cost": 0,
            "blocker": None,
            "user_action_required": False,
            "next_action": "Use the first exact vendor-issued Claap URL as the default tracked CTA; await destination/custom-label mapping before destination-specific use of the second URL. Do not reapply.",
            "evidence": f"Gmail {claap_e['gmail_message_id']}: Lamia Karmaly copied both URLs from COSHUMA's PartnerStack dashboard.",
        }
    )
    teachable_queue = load_json(TEACHABLE_QUEUE_PATH)
    queue.append(teachable_queue)
    write_json(path, queue)


def patch_claap_page(evidence: dict) -> None:
    path = PUBLIC_DIR / "tool" / "claap.html"
    if not path.exists():
        raise RuntimeError("Claap public page missing")
    primary = evidence["claap"]["primary_tracking_url"]
    html = path.read_text(encoding="utf-8")

    old_top = '<a data-cta="official" data-tool-id="claap" href="https://www.claap.io/" target="_blank" rel="noopener noreferrer" class="flex-1 px-6 py-4 rounded-xl font-extrabold text-sm bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-center hover:brightness-110">Try Claap on the official site →</a>'
    new_top = f'<a data-cta="affiliate" data-tool-id="claap" data-cta-source="claap_partnerstack_verified" href="{primary}" target="_blank" rel="sponsored noopener noreferrer" class="flex-1 px-6 py-4 rounded-xl font-extrabold text-sm bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-center hover:brightness-110">Start Claap with partner discount →</a>'
    html = html.replace(old_top, new_top)

    old_status = "Affiliate status: COSHUMA's Claap partnership is approved, but the exact customer-facing PartnerStack referral URL has not yet been independently verified. These buttons intentionally remain official, non-affiliate links until the issued tracking URL is recovered; COSHUMA will not guess a referral parameter."
    new_status = "Affiliate status: verified. Claap affiliate manager Lamia Karmaly supplied COSHUMA's exact customer-facing PartnerStack URLs directly by email on Sep 9, 2026. The primary Try Claap buttons use the first issued tracking URL; the pricing button remains the official live pricing page until the intended destination of the second issued URL is clarified. Link issuance does not imply a signup, commission, or sale."
    html = html.replace(old_status, new_status)

    # Claap's first-party affiliate page, rechecked 2026-09-10, states that
    # referrals who use an affiliate link receive 30% off the first two months on
    # a monthly plan or 10% off the first year on an annual plan. Surface that
    # customer benefit next to the verified CTA without inventing a deeper URL.
    offer_marker = "Claap referral discount:"
    if offer_marker not in html:
        offer_note = '<div class="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-sm text-slate-300 leading-relaxed"><strong class="text-emerald-300">Claap referral discount:</strong> Claap currently says referrals using an affiliate link get <strong class="text-white">30% off the first 2 months</strong> on a monthly plan or <strong class="text-white">10% off the first year</strong> on a yearly plan. Final eligibility and checkout terms are controlled by Claap.</div>'
        status_anchor = f'<p class="text-[11px] text-slate-500 leading-relaxed">{new_status}</p>'
        if status_anchor in html:
            html = html.replace(status_anchor, status_anchor + "\n    " + offer_note, 1)
        else:
            raise RuntimeError("Could not locate verified Claap status paragraph for referral-discount placement")

    old_bottom = '<a data-cta="official" data-tool-id="claap" href="https://www.claap.io/" target="_blank" rel="noopener noreferrer" class="inline-flex px-7 py-4 rounded-xl font-extrabold text-sm bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:brightness-110">Test Claap on the official site →</a>'
    new_bottom = f'<a data-cta="affiliate" data-tool-id="claap" data-cta-source="claap_partnerstack_verified" href="{primary}" target="_blank" rel="sponsored noopener noreferrer" class="inline-flex px-7 py-4 rounded-xl font-extrabold text-sm bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:brightness-110">Try Claap with referral discount →</a>'
    html = html.replace(old_bottom, new_bottom)

    if "Affiliate disclosure:" not in html:
        disclosure = '<p class="text-[11px] text-slate-500 leading-relaxed"><strong class="text-slate-300">Affiliate disclosure:</strong> COSHUMA may earn a commission if you purchase through a verified Claap affiliate link, at no extra cost to you. This does not affect our editorial assessment.</p>'
        anchor = '<p class="text-[11px] text-slate-500 leading-relaxed">Affiliate status:'
        pos = html.find(anchor)
        if pos != -1:
            end = html.find('</p>', pos)
            if end != -1:
                end += 4
                html = html[:end] + "\n    " + disclosure + html[end:]
        else:
            html = html.replace('</main>', f'  {disclosure}\n</main>', 1)

    marker = "<!-- claap-partner-feedback-v6 -->"
    html = html.replace(marker, "<!-- claap-partner-feedback-v6 --><!-- claap-approved-tracking-v2 -->")
    path.write_text(html, encoding="utf-8")


def validate(evidence: dict) -> None:
    primary = evidence["claap"]["primary_tracking_url"]
    alternate = evidence["claap"]["alternate_tracking_url"]
    teachable_url = evidence["teachable"]["tracking_url"]
    if not primary.startswith("https://get.claap.io/") or not alternate.startswith("https://get.claap.io/"):
        raise RuntimeError("Claap URLs are not the manager-supplied get.claap.io routes")
    if not teachable_url.startswith("https://partnerstack.teachable.com/"):
        raise RuntimeError("Teachable URL is not the manager-supplied PartnerStack customer route")

    tools = load_json(DATA_DIR / "tools.json")
    claap = next(item for item in tools if item.get("id") == "claap")
    teachable = next(item for item in tools if item.get("id") == "teachable")
    if claap.get("affiliate_status") != "approved_tracking" or claap.get("affiliate_url") != primary or claap.get("affiliate_verified") is not True:
        raise RuntimeError("Claap approved tracking state was not preserved")
    if teachable.get("affiliate_status") != "approved_tracking" or teachable.get("affiliate_url") != teachable_url or teachable.get("affiliate_verified") is not True:
        raise RuntimeError("Teachable approved tracking state was not preserved")

    page = (PUBLIC_DIR / "tool" / "claap.html").read_text(encoding="utf-8")
    if page.count(primary) < 2 or 'data-cta-source="claap_partnerstack_verified"' not in page:
        raise RuntimeError("Claap verified tracking CTA was not activated")
    if 'data-cta="affiliate" data-tool-id="claap" href="https://www.claap.io/' in page:
        raise RuntimeError("Generic Claap official URL was incorrectly marked as affiliate")
    if "Affiliate disclosure:" not in page:
        raise RuntimeError("Claap affiliate disclosure is missing")
    if "Claap referral discount:" not in page or "30% off the first 2 months" not in page or "10% off the first year" not in page:
        raise RuntimeError("Claap referral discount buyer-benefit note is missing")


def main() -> None:
    evidence = load_json(EVIDENCE_PATH)
    reconcile_tools(evidence)
    reconcile_outreach(evidence)
    reconcile_browser_queue(evidence)
    patch_claap_page(evidence)
    validate(evidence)
    print("Claap and Teachable exact tracking states activated; browser recovery is no longer required for either default CTA.")


if __name__ == "__main__":
    main()
