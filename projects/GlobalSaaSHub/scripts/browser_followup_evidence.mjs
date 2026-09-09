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
const hotfixEvidencePath = 'data/affiliate-status-hotfix-2026-09-08.json';
const statusHotfixes = JSON.parse(fs.readFileSync(new URL('../' + hotfixEvidencePath, import.meta.url), 'utf8')).results;
for (const item of statusHotfixes) {
  browserFollowups.set(item.id, {...item, evidence_path: hotfixEvidencePath});
}

// Newer authenticated Dub dashboard check supersedes the original Krater submission snapshot.
// This exact path-based URL is customer-facing tracking, not a portal/application URL.
const approvalFollowups = [
  {
    id: 'krater',
    status: 'approved_tracking',
    affiliate_url: 'https://go.krater.ai/sang-kwon-an',
    status_origin: 'authenticated_portal_issued_tracking',
    portal_enrollment_confirmed: true,
    customer_landing_verified: true,
    checked_at: '2026-09-08T14:00:00+09:00',
    workflow_url: 'https://partners.dub.co/programs/kraterai',
    official_program_url: 'https://krater.ai/',
    evidence: 'Authenticated Dub partner dashboard shows Krater Approved/Enrolled and issues the exact customer-facing link https://go.krater.ai/sang-kwon-an. The Dub partner-application URL is not treated as a customer tracking link. No reapplication was made and no referral, sale, commission, or revenue is inferred.',
    next_action: 'Preserve the issued exact customer-facing link; do not reapply. Keep customer signups, commissions and revenue at 0 without new evidence.',
    evidence_path: 'data/krater-affiliate-enrollment-evidence-2026-09-08.md',
    application_state: 'submitted',
  },
];
for (const item of approvalFollowups) browserFollowups.set(item.id, item);

// Typedesk and Omnisend now have newer human vendor-issued exact tracking URLs.
// Remove older browser/status snapshots so the authoritative approved-tracking
// evidence can apply during both sync passes instead of being masked by stale state.
browserFollowups.delete('typedesk');
browserFollowups.delete('omnisend');

// Operational approvals keep duplicate-prevention state and the browser queue current
// without requiring the browser-followup validator to reinterpret vendor-issued email links.
const operationalApprovals = [
  {
    id: 'fillout',
    status: 'approved_tracking',
    affiliate_url: 'https://try.fillout.com/sang-kwon-an-hxwn',
    checked_at: '2026-09-08T14:00:00+09:00',
    evidence: 'Authenticated Dub partner dashboard shows Fillout Approved/Enrolled and issues the exact customer-facing link https://try.fillout.com/sang-kwon-an-hxwn. No reapplication was made and no referral, sale, commission, or revenue is inferred.',
    next_action: 'Preserve the issued exact customer-facing link; do not reapply. Add a public catalog entry separately before treating this as a site CTA.',
    application_state: 'submitted',
  },
  {
    id: 'typedesk',
    status: 'approved_tracking',
    affiliate_url: 'https://www.typedesk.com?via=sangkwon',
    checked_at: '2026-09-09T10:40:59+09:00',
    evidence: 'Typedesk human reply from hennadiy@typedesk.com to support@coshuma.com explicitly supplied https://www.typedesk.com?via=sangkwon as COSHUMA\'s unique customer-facing tracking link. Rewardful login/dashboard URLs remain operational only and are not revenue links. No click, signup, commission, or revenue is inferred.',
    next_action: 'Preserve and publish the verified Typedesk tracking URL on buyer-facing COSHUMA pages; do not reapply or request another tracking account. Measure actual outbound clicks and only claim downstream revenue when separately evidenced.',
    application_state: 'submitted',
  },
  {
    id: 'omnisend',
    status: 'approved_tracking',
    affiliate_url: 'https://your.omnisend.com/4aA5k9',
    checked_at: '2026-09-09T17:50:34+09:00',
    evidence: 'Omnisend Senior Affiliate Marketing Manager Deimantė Vaitkevičiūtė replied to support@coshuma.com in Gmail message 1a0855caf8f6dee2 and explicitly instructed COSHUMA to use https://your.omnisend.com/4aA5k9 for tracking, confirming the tracking link is in Impact Assets. No click, signup, commission, payout, or revenue is inferred.',
    next_action: 'Preserve and publish the exact Omnisend-issued customer tracking URL on buyer-facing COSHUMA pages; do not reapply and do not substitute a generic Omnisend or Impact operational URL. Measure actual downstream events separately.',
    application_state: 'submitted',
  },
];

const queueMatches = (entry, id) =>
  entry.tool_id === id || entry.id === id || (typeof entry.id === 'string' && entry.id.startsWith(`${id}-`));

// Keep duplicate-prevention state and browser queue aligned with newer vendor decisions.
// A newly discovered vendor decision may refer to a program that predates the outreach
// registry. In that case create the missing operational state instead of silently skipping it.
function syncStatusHotfixes() {
  const stateUrl = new URL('../data/affiliate_outreach_state.json', import.meta.url);
  const state = JSON.parse(fs.readFileSync(stateUrl, 'utf8'));
  state.programs ||= {};
  let stateChanged = false;
  for (const item of statusHotfixes) {
    const current = state.programs[item.id] ||= {};
    Object.assign(current, {
      status: item.status,
      tracking_url: null,
      application_state: item.application_state || current.application_state || 'submitted',
      review_state: item.review_state || current.review_state,
      next_action: item.next_action,
      do_not_reapply: true,
      checked_at: item.checked_at || current.checked_at,
      evidence: item.evidence,
    });
    stateChanged = true;
  }
  for (const item of [...approvalFollowups, ...operationalApprovals]) {
    const current = state.programs?.[item.id];
    if (!current) continue;
    Object.assign(current, {
      status: item.status,
      tracking_url: item.affiliate_url,
      application_state: item.application_state || current.application_state,
      next_action: item.next_action,
      do_not_reapply: true,
      checked_at: item.checked_at,
      evidence: item.evidence,
    });
    stateChanged = true;
  }
  if (stateChanged) fs.writeFileSync(stateUrl, `${JSON.stringify(state, null, 2)}\n`);

  const queueUrl = new URL('../data/browser_required_queue.json', import.meta.url);
  const queue = JSON.parse(fs.readFileSync(queueUrl, 'utf8'));
  let queueChanged = false;
  for (const item of statusHotfixes) {
    const needsTrackingRecovery = item.status === 'approved' && !item.affiliate_url;
    let entries = queue.filter(entry => queueMatches(entry, item.id));
    if (entries.length === 0) {
      const date = (item.checked_at || 'current').slice(0, 10);
      const created = {
        id: `${item.id}-status-hotfix-${date}`,
        tool_id: item.id,
        priority: needsTrackingRecovery ? 'high' : 'medium',
        status: needsTrackingRecovery ? 'approved_account_tracking_url_required' : 'resolved',
        affiliate_status: item.status,
        cost: 0,
        exact_tracking_url: null,
        blocker: needsTrackingRecovery
          ? item.blockers?.[0] || 'Exact customer tracking URL requires authenticated partner dashboard recovery.'
          : null,
        next_action: item.next_action,
        do_not_reapply: true,
      };
      queue.push(created);
      entries = [created];
      queueChanged = true;
    }
    for (const entry of entries) {
      Object.assign(entry, {
        status: needsTrackingRecovery ? 'approved_account_tracking_url_required' : 'resolved',
        affiliate_status: item.status,
        exact_tracking_url: null,
        blocker: needsTrackingRecovery
          ? item.blockers?.[0] || 'Exact customer tracking URL requires authenticated partner dashboard recovery.'
          : null,
        next_action: item.next_action,
      });
      queueChanged = true;
    }
  }
  for (const item of [...approvalFollowups, ...operationalApprovals]) {
    for (const entry of queue.filter(entry => queueMatches(entry, item.id))) {
      Object.assign(entry, {
        status: 'resolved',
        affiliate_status: item.status,
        exact_tracking_url: item.affiliate_url,
        blocker: null,
        next_action: item.next_action,
      });
      queueChanged = true;
    }
  }
  if (queueChanged) fs.writeFileSync(queueUrl, `${JSON.stringify(queue, null, 2)}\n`);
}
syncStatusHotfixes();

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
    const approvedPath = item.id === 'krater' &&
      url.hostname === 'go.krater.ai' && /^\/[a-z0-9-]+$/i.test(url.pathname);
    const issued = (item.status_origin === 'authenticated_portal_issued_tracking' || emailIssued) &&
      item.portal_enrollment_confirmed === true && item.customer_landing_verified === true &&
      approvedTracking.get(item.id)?.exact_tracking_url === item.affiliate_url &&
      (accountPath || approvedPath || [...url.searchParams.values()].some(value => value.trim()));
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
