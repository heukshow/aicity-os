from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
PUBLIC_DIR = PROJECT_DIR / "public"
QUEUE_EVIDENCE_PATH = DATA_DIR / "browser_required_queue.d" / "claap-approved-link-recovery-2026-09-09.json"
OFFICIAL_URL = "https://www.claap.io/"


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
    if primary not in page or 'data-cta-source="claap_partnerstack_verified"' not in page:
        raise RuntimeError("Claap verified revenue CTA is missing from the public page")
    if "Affiliate disclosure:" not in page:
        raise RuntimeError("Claap affiliate disclosure is missing")
    if "30% off the first 2 months" not in page or "10% off the first year" not in page:
        raise RuntimeError("Claap vendor-confirmed referral discount is missing")
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
    print("Claap partner feedback guard: verified tracking preserved; no downgrade performed.")


if __name__ == "__main__":
    main()
