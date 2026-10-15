#!/usr/bin/env python3
"""Preserve evidence-backed lifecycle fields at every producer boundary.


Run legacy producers with this wrapper. Product facts are never restored/changed.
A backwards transition requires a newer explicit direct-evidence override.
"""
import copy
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = ["tools.json", "tools.next.json", "affiliate_outreach_state.json", "browser_required_queue.json"]
EXTRA = {"status", "tracking_url", "exact_tracking_url", "application_state", "next_action",
         "do_not_reapply", "checked_at", "verified_at", "evidence", "blocker", "blockers",
         "user_action_required", "reason", "note"}




def protected(key):
    return key.startswith(("affiliate_", "application_")) or key in EXTRA




def rank(row):
    status = row.get("affiliate_status") or row.get("status") or ""
    application = row.get("application_state") or ""
    if status in {"rejected", "no_affiliate_program", "excluded_user_request", "program_inactive",
                  "program_closed_to_new_applicants", "program_unavailable_company_winding_down", "temporarily_closed"}:
        return 4
    if status.startswith("approved_tracking") or (not status and application == "enrolled_tracking_link_verified"):
        return 5
    if status.startswith("approved") or (not status and application == "approved"):
        return 3
    if status in {"application_submitted", "application_pending", "pending"} or (not status and application in {
        "submitted", "submitted_then_declined", "interest_form_submitted"}):
        return 2
    if status == "outreach_sent":
        return 1
    return 0




def timestamp(row):
    for key in ("affiliate_status_checked_at", "checked_at", "affiliate_verified_at", "verified_at"):
        try:
            return datetime.fromisoformat(row.get(key, "").replace("Z", "+00:00")).timestamp()
        except (ValueError, TypeError, AttributeError):
            pass
    return 0




def preserve(old, new):
    """Return merged row and whether an unproven regression was prevented."""
    if not old:
        return new, False
    evidence = new.get("affiliate_lifecycle_override", {})
    direct_override = (isinstance(evidence, dict) and evidence.get("source_type") in {
        "vendor_email", "authenticated_vendor_dashboard"} and evidence.get("source_ref")
        and evidence.get("reason") and evidence != old.get("affiliate_lifecycle_override")
        and timestamp({"checked_at": evidence.get("observed_at")}) > timestamp(old))
    lower = rank(new) < rank(old)
