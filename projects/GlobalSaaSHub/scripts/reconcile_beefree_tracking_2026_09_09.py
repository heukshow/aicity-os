from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
PUBLIC_DIR = PROJECT_DIR / "public"
EVIDENCE_PATH = DATA_DIR / "beefree-approved-tracking-2026-09-09.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reconcile_tools(evidence: dict) -> None:
    url = evidence["exact_tracking_url"]
    checked_at = evidence["received_at_utc"]
    markers = [
        f"Vendor/PartnerStack welcome email {evidence['vendor_message_id']} to support@coshuma.com explicitly identifies {url} as COSHUMA's unique referral link to share.",
        "Beefree's official Ambassador page states ambassadors earn 20% of first-year customer revenue and referrals use a 90-day cookie.",
        "Generic Beefree/RGE Studio home, pricing, dashboard, onboarding and login URLs are not treated as affiliate links.",
        "Approval and link issuance do not prove a customer click, signup, commission, or revenue.",
        "data/beefree-approved-tracking-2026-09-09.json",
    ]
    for filename in ("tools.json", "tools.next.json"):
        path = DATA_DIR / filename
        tools = load_json(path)
        tool = next((item for item in tools if item.get("id") == "beefree"), None)
        if not tool:
            raise RuntimeError(f"beefree missing from {filename}")
        tool.update(
            {
                "affiliate_url": url,
                "affiliate_final_url": url,
                "affiliate_verified": True,
                "affiliate_status": "approved_tracking",
                "affiliate_verified_at": checked_at,
                "affiliate_status_checked_at": checked_at,
                "affiliate_status_evidence_url": f"gmail:{evidence['vendor_message_id']}",
                "affiliate_tracking_url_verified": True,
                "affiliate_tracking_attribution_currently_verified": False,
                "affiliate_dashboard_status": "Approved; vendor email supplied exact PartnerStack customer referral URL",
                "affiliate_next_action": "Use the exact vendor-issued referral URL on buyer-intent Beefree/RGE Studio CTAs. Keep official pricing links for price verification. Do not reapply or infer revenue. A destination-specific pricing referral link may be requested separately without blocking the current verified route.",
                "affiliate_evidence_markers": markers,
            }
        )
        write_json(path, tools)


def reconcile_outreach(evidence: dict) -> None:
    path = DATA_DIR / "affiliate_outreach_state.json"
    if not path.exists():
        return
    state = load_json(path)
    programs = state.get("programs", {}) if isinstance(state, dict) else {}
    program = programs.get("beefree") if isinstance(programs, dict) else None
    if isinstance(program, dict):
        program.update(
            {
                "status": "approved_tracking",
                "tracking_url": evidence["exact_tracking_url"],
                "updated_at": evidence["received_at_utc"],
                "note": "Beefree/RGE Studio Ambassador approval is verified and the vendor email supplied COSHUMA's exact PartnerStack referral URL. Do not reapply. No sale or revenue is inferred.",
            }
        )
        write_json(path, state)


def reconcile_queue(evidence: dict) -> None:
    path = DATA_DIR / "browser_required_queue.json"
    if not path.exists():
        return
    queue = load_json(path)
    if not isinstance(queue, list):
        raise RuntimeError("browser_required_queue.json must be a list")
    url = evidence["exact_tracking_url"]
    changed = False
    for item in queue:
        identity = " ".join(
            str(item.get(key, ""))
            for key in ("id", "tool_id", "name", "program", "task")
        ).lower()
        if "beefree" not in identity and "really good emails" not in identity and "rge studio" not in identity:
            continue
        item.update(
            {
                "status": "resolved",
                "affiliate_status": "approved_tracking",
                "exact_tracking_url": url,
                "tracking_url": url,
                "resolved_at": evidence["received_at_utc"],
                "resolution": "Exact customer-facing PartnerStack referral URL arrived by vendor email; no browser dashboard action or duplicate application is required.",
            }
        )
        changed = True
    if changed:
        write_json(path, queue)


def patch_tool_page(evidence: dict) -> None:
    path = PUBLIC_DIR / "tool" / "beefree.html"
    html = path.read_text(encoding="utf-8")
    url = evidence["exact_tracking_url"]

    old_hero = '<a data-cta="official" href="https://beefree.io/plans-pricing" target="_blank" rel="noopener noreferrer" class="px-6 py-3.5 rounded-xl bg-slate-800 border border-slate-600 text-white font-extrabold text-center">Check RGE Studio pricing →</a>'
    new_hero = f'<a data-cta="affiliate" data-tool-id="beefree" data-cta-source="beefree_vendor_verified_hero" href="{url}" target="_blank" rel="sponsored noopener noreferrer" class="px-6 py-3.5 rounded-xl bg-slate-800 border border-slate-600 text-white font-extrabold text-center">Try RGE Studio via COSHUMA →</a>'
    if old_hero in html:
        html = html.replace(old_hero, new_hero, 1)

    old_fit = '<a data-cta="official" href="https://beefree.io/plans-pricing" target="_blank" rel="noopener noreferrer" class="mt-6 block px-5 py-3 rounded-xl bg-slate-800 border border-slate-600 text-center font-extrabold">Start from official RGE Studio pricing →</a>'
    new_fit = f'<a data-cta="affiliate" data-tool-id="beefree" data-cta-source="beefree_vendor_verified_fit" href="{url}" target="_blank" rel="sponsored noopener noreferrer" class="mt-6 block px-5 py-3 rounded-xl bg-slate-800 border border-slate-600 text-center font-extrabold">Try RGE Studio through verified COSHUMA tracking →</a>'
    if old_fit in html:
        html = html.replace(old_fit, new_fit, 1)

    old_disclosure = "Affiliate disclosure: COSHUMA may earn a commission if you sign up for AWeber through the partner link. RGE Studio/Beefree links on this page are standard official links because COSHUMA does not currently publish a verified RGE Studio customer referral URL."
    new_disclosure = "Affiliate disclosure: COSHUMA may earn a commission if you become a paying Beefree/RGE Studio or AWeber customer after using the verified partner links. The live RGE Studio pricing link remains an ordinary official link for price verification."
    html = html.replace(old_disclosure, new_disclosure)

    old_note = "RGE Studio currently runs an official Ambassador program that advertises 20% of first-year customer revenue and a 90-day referral cookie. COSHUMA has <strong class=\"text-white\">not</strong> published an RGE Studio affiliate CTA here because we have not yet verified an account-specific customer referral URL. Until that exact tracking link is confirmed, all RGE Studio links remain ordinary official links."
    new_note = f"RGE Studio's official Ambassador program advertises 20% of first-year customer revenue and a 90-day referral cookie. COSHUMA's account-specific PartnerStack referral URL was supplied directly in the Sep 9, 2026 vendor welcome email and is now used on the Try RGE Studio buttons: <strong class=\"text-white\">{url}</strong>. Approval or link issuance alone is not counted as a customer signup, commission, or revenue."
    html = html.replace(old_note, new_note)

    html = html.replace("Verified Sep 6, 2026", "Affiliate tracking verified Sep 9, 2026", 1)

    if "/affiliate-attribution.js" not in html:
        html = html.replace("</head>", '  <script defer src="/affiliate-attribution.js"></script>\n</head>', 1)

    if url not in html:
        raise RuntimeError("Beefree referral URL was not injected into tool page")
    if 'data-tool-id="beefree"' not in html or 'data-cta="affiliate"' not in html:
        raise RuntimeError("Beefree tool page is missing attributed affiliate CTA metadata")
    path.write_text(html, encoding="utf-8")


def main() -> None:
    evidence = load_json(EVIDENCE_PATH)
    reconcile_tools(evidence)
    reconcile_outreach(evidence)
    reconcile_queue(evidence)
    patch_tool_page(evidence)
    print("reconcile_beefree_tracking_2026_09_09: approved_tracking + buyer CTAs applied")


if __name__ == "__main__":
    main()
