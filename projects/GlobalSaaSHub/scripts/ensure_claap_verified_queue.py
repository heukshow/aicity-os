from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
EVIDENCE_PATH = DATA_DIR / "claap-teachable-tracking-update-2026-09-09.json"
QUEUE_PATH = DATA_DIR / "browser_required_queue.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    evidence = load_json(EVIDENCE_PATH)["claap"]
    primary = evidence["primary_tracking_url"]
    alternate = evidence["alternate_tracking_url"]
    if not primary.startswith("https://get.claap.io/") or not alternate.startswith("https://get.claap.io/"):
        raise RuntimeError("Refusing to register non-vendor Claap tracking URLs")

    queue = load_json(QUEUE_PATH)
    if not isinstance(queue, list):
        raise RuntimeError("browser_required_queue.json must be a list")

    item_id = "claap-approved-link-recovery-2026-09-09"
    queue = [item for item in queue if item.get("id") != item_id]
    queue.append(
        {
            "id": item_id,
            "tool_id": "claap",
            "program_name": "Claap Affiliate Program",
            "priority": "high",
            "status": "resolved",
            "affiliate_status": "approved_tracking",
            "cost": 0,
            "verified_at": evidence["received_at_utc"],
            "exact_tracking_url": primary,
            "alternate_verified_url": alternate,
            "reason": "Claap affiliate manager Lamia Karmaly copied both exact customer-facing PartnerStack URLs from COSHUMA's existing dashboard into Gmail message 1a08633651c79db9.",
            "next_action": "No browser recovery is needed. Keep the first vendor-issued URL as the default Claap revenue CTA and retain the second as a verified alternate until Lamia confirms each destination/custom label.",
            "do_not": [
                "Do not reapply to Claap.",
                "Do not replace the verified URLs with PartnerStack dashboard/login, a generic Claap homepage, prototype URL, email redirect, or guessed parameter.",
                "Do not infer clicks, signups, commissions, or revenue from link issuance or CTA publication.",
            ],
            "resolved_at": evidence["received_at_utc"],
            "resolution_evidence": "Gmail message 1a08633651c79db9 from Claap affiliate manager Lamia Karmaly supplied both exact URLs; the first is the authoritative default CTA pending destination-label mapping for the second.",
        }
    )
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not any(
        item.get("tool_id") == "claap"
        and item.get("affiliate_status") == "approved_tracking"
        and item.get("exact_tracking_url") == primary
        for item in queue
    ):
        raise RuntimeError("Claap resolved queue evidence was not persisted")

    print("Claap resolved approved-tracking queue evidence preserved.")


if __name__ == "__main__":
    main()
