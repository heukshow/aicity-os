import fs from 'node:fs';

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
    if (url.protocol !== 'https:' || !url.searchParams.get('ref') ||
        item.status_origin !== 'existing_remote_record_preserved_not_new_approval') {
      throw new Error(`Missing exact existing referral evidence: ${item.id}`);
    }
  }
  Object.assign(tool, {
    affiliate_status: item.status,
    affiliate_url: approved ? item.affiliate_url : null,
    affiliate_verified: approved,
    affiliate_final_url: approved ? item.affiliate_url : null,
    affiliate_evidence_markers: [item.evidence, item.next_action, item.evidence_path || browserEvidencePath],
    affiliate_status_checked_at: '2026-09-08',
    affiliate_status_evidence_url: item.official_program_url || item.workflow_url,
    affiliate_workflow_url: item.workflow_url,
    affiliate_next_action: item.next_action,
  });
  if (item.current_dashboard_status) {
    tool.affiliate_dashboard_status = item.current_dashboard_status;
    tool.affiliate_tracking_attribution_currently_verified = false;
  }
  return true;
}
