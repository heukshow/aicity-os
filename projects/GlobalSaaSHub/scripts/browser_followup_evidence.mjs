import fs from 'node:fs';
import { approvedTracking } from './approved_tracking_evidence.mjs';

export const browserEvidencePath = 'data/affiliate-browser-followup-wave3-2026-09-08.json';
export const browserFollowups = new Map(JSON.parse(fs.readFileSync(
  new URL('../' + browserEvidencePath, import.meta.url), 'utf8',
)).results.map(item => [item.id, item]));
const submissionEvidencePath = 'data/affiliate-submission-batch-2026-09-08.json';
for (const item of JSON.parse(fs.readFileSync(new URL('../' + submissionEvidencePath, import.meta.url), 'utf8')).results) {
  browserFollowups.set(item.id, {...item, evidence_path: submissionEvidencePath});
}

// This browser snapshot preserves existing approvals, never infers a new one
// from a successful public landing, and keeps account access separate from CTAs.
export function applyBrowserFollowup(tool) {
  const item = browserFollowups.get(tool.id);
  if (!item) return false;
  const approved = item.status === 'approved_tracking';
  if (approved) {
    const url = new URL(item.affiliate_url);
    const existing = url.searchParams.get('ref') &&
      item.status_origin === 'existing_remote_record_preserved_not_new_approval';
    const emailIssued = item.status_origin === 'authenticated_approval_email_issued_tracking' &&
      item.approval_email_confirmed === true && item.approval_email_recipient === 'support@coshuma.com' &&
      item.approval_email_sender === 'noreply-affiliates@tapfiliate.com';
    // Native eProfessor referrals carry the issued account identifier in the path.
    // Keep this narrow: a generic /invite or a dashboard must never pass this gate.
    const accountPath = item.id === 'eprofessor' &&
      item.customer_tracking_kind === 'account_specific_referral_path' &&
      url.hostname === 'eprofessor.com' && /^\/invite\/[a-z0-9-]+$/i.test(url.pathname);
    const issued = (item.status_origin === 'authenticated_portal_issued_tracking' || emailIssued) &&
      item.portal_enrollment_confirmed === true && item.customer_landing_verified === true &&
      approvedTracking.get(item.id)?.exact_tracking_url === item.affiliate_url &&
      (accountPath || [...url.searchParams.values()].some(value => value.trim()));
    if (url.protocol !== 'https:' || (!existing && !issued)) {
      throw new Error(`Missing exact existing referral evidence: ${item.id}`);
    }
  }
  Object.assign(tool, {
    affiliate_status: item.status,
    affiliate_url: approved ? item.affiliate_url : null,
    affiliate_verified: approved,
    affiliate_final_url: approved ? item.affiliate_url : null,
    affiliate_evidence_markers: [item.evidence, item.next_action, item.evidence_path || browserEvidencePath],
    affiliate_status_checked_at: item.checked_at || '2026-09-08',
    affiliate_status_evidence_url: item.portal_enrollment_confirmed ? item.workflow_url : item.official_program_url || item.workflow_url,
    affiliate_workflow_url: item.workflow_url,
    affiliate_next_action: item.next_action,
  });
  if (approved && item.checked_at) tool.affiliate_verified_at = item.checked_at;
  if (item.supersedes_unavailable_route === true) {
    tool.affiliate_source_url = item.official_program_url;
    delete tool.affiliate_rejection_reason;
  }
  if (typeof item.payout_setup_complete === 'boolean') {
    tool.payout_setup_status = item.payout_setup_complete ? 'complete' : 'incomplete';
  }
  if (item.current_dashboard_status) {
    tool.affiliate_dashboard_status = item.current_dashboard_status;
    tool.affiliate_tracking_attribution_currently_verified = false;
  }
  return true;
}
