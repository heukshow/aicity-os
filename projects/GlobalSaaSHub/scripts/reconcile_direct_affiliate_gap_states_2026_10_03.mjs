import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-10-03T03:05:00+09:00';

const states = {
  activepieces: {
    stale: [null, 'unclassified', 'browser_required_sales_inquiry', 'browser_required_affiliate_application'],
    status: 'waiting_partnerstack_network_review',
    checkedAt: '2026-10-12T10:04:00+09:00',
    source: 'https://www.activepieces.com/',
    workflow: 'https://market.partnerstack.com/program/activepieces',
    applicationState: 'not_submitted_program_not_found',
    next: 'Wait for the pending PartnerStack Network Profile review, then recheck the authenticated marketplace and an independently verified official Activepieces partner route. Do not submit a PartnerStack request-a-program form or infer a tracking URL from the historical marketplace URL.',
    evidence: [
      '2026-10-12 authenticated PartnerStack marketplace exact search returned no programs matching Activepieces and exposed only Request a program.',
      'The historical PartnerStack program URL is not current proof that COSHUMA can apply; the PartnerStack Network Profile reapplication is pending review.',
      'No Activepieces application, approval, customer-facing tracking URL, click, signup, customer, commission, payout, or revenue is verified.',
    ],
  },
  carv: {
    stale: [null, 'unclassified', 'browser_required_application_form'],
    status: 'waiting_vendor_eligibility_clarification',
    source: 'https://www.carv.com/partner-program/referral-partner',
    workflow: 'https://www.carv.com/partner-program/referral-partner',
    next: 'Wait for Carv to confirm whether COSHUMA qualifies for the Referral Partner track; do not submit the application first.',
  },
  chatbot: {
    stale: [null, 'unclassified'],
    status: 'referral_link_requested',
    source: 'https://partners.livechat.com/app/affiliate',
    next: 'Wait for Text Partner Team to supply or identify the exact ChatBot customer-facing affiliate URL requested in Gmail 1a0fdcf2e220b96e.',
  },
  colossyan: {
    stale: [null, 'unclassified', 'program_inactive', 'browser_required_application'],
    status: 'waiting_vendor_response',
    checkedAt: '2026-10-12T10:04:00+09:00',
    source: 'https://www.colossyan.com/affiliate-program/',
    workflow: 'https://app.impact.com/campaign-promo-signup/Colossyan.brand',
    applicationState: 'not_submitted_existing_impact_access_loop',
    next: 'Wait for Colossyan to reply to Gmail message 1a12d6fc6dcddca9 with an invitation or supported route for the existing COSHUMA Impact identity. Do not create another Impact account, repeat the application loop, resend the inquiry, or infer a customer tracking URL.',
    evidence: [
      '2026-10-12 existing Impact sign-in and Google SSO both returned to the Colossyan already-signed-up/sign-in loop; the direct Impact dashboard also returned to sign-in.',
      'One routing inquiry was sent to marketing@colossyan.com in Gmail message 1a12d6fc6dcddca9 and no supplier reply was present at the latest mailbox check.',
      'No Colossyan application, approval, customer-facing tracking URL, click, signup, customer, commission, payout, or revenue is verified.',
    ],
    lifecycleOverride: {
      source_type: 'authenticated_vendor_dashboard',
      source_ref: 'github:#292-comment-6115935512',
      observed_at: '2026-10-12T10:04:00+09:00',
      reason: 'Fresh authenticated Impact UI evidence supersedes the stale 2026-09-01 program_inactive record and shows a current access loop awaiting vendor routing guidance.',
    },
  },
  docusign: {
    stale: [null, 'unclassified', 'unverified'],
    status: 'browser_required_captcha_program_form',
    source: 'https://partners.docusign.com/s/partner-program-support-form',
    workflow: 'https://partners.docusign.com/s/partner-program-support-form',
    next: 'Use the official Docusign partner support/application route to reconcile the current affiliate enrollment path. Do not infer a tracking URL.',
  },
  dub: {
    stale: [null, 'unclassified', 'application_not_submitted', 'browser_required_program_enrollment'],
    status: 'browser_required_legal_program_consent',
    checkedAt: '2026-10-05T06:18:40+09:00',
    source: 'https://partners.dub.co/dub',
    workflow: 'https://partners.dub.co/dub/apply',
    next: 'The account holder must review and accept the official Dub Affiliate Program Terms before continuing the two-step application. After consent, reuse the existing COSHUMA Dub identity if available, submit once only, and recover only the exact vendor-issued customer-facing tracking URL. Stop for CAPTCHA, OTP, payment approval or forced identity verification.',
    evidence: [
      '2026-10-05 direct official-page check: Dub states 30% per sale for one year and 20% off for referred new users for three months; these are vendor-stated terms, not independent performance evidence.',
      'The official application is Step 1 of 2 and requires name, email, website, partnership rationale, promotion plan, and affirmative acceptance of the Dub Affiliate Program Terms before Continue.',
      'No application was submitted, no program terms were accepted, no duplicate account was created, and no customer-facing tracking URL is verified.',
    ],
  },
  expandi: {
    stale: [null, 'unclassified', 'browser_required_application_form'],
    status: 'waiting_vendor_requirement',
    source: 'https://expandi.io/affiliate-program/',
    workflow: 'https://expandi.io/affiliate-program/',
    next: 'Do not submit until the required 14 days of active Expandi use is evidenced or Expandi explicitly clarifies the requirement.',
  },
  featureshark: {
    stale: [null, 'unclassified'],
    status: 'waiting_vendor_response',
    source: 'https://www.featureshark.com/help-center',
    next: 'Wait for FeatureShark support response to Gmail 1a0fdd2503fc6b9e. Do not send duplicate inquiries or construct a referral link.',
  },
  'flowgent-ai': {
    stale: [null, 'unclassified', 'program_signup_inactive_conflict'],
    status: 'program_inactive',
    source: 'https://flowgent.ai/affiliate',
    workflow: 'https://flowgent-ai.getrewardful.com/',
    next: 'Do not apply or publish an affiliate URL while the vendor-linked Rewardful enrollment route reports the program inactive.',
  },
  'google-workspace': {
    stale: [null, 'unclassified', 'browser_required_country_eligibility_check', 'application_available_account_required'],
    status: 'browser_required_legal_program_consent',
    checkedAt: '2026-10-07T22:18:35Z',
    source: 'https://workspace.google.com/affiliate-program/',
    workflow: 'https://public.cj.com/signup/publisher?advertiserId=5261735',
    next: 'The account holder must review and accept the Google Workspace Affiliate Program terms and the required CJ publisher agreement before enrollment. Reuse only an existing COSHUMA-owned CJ publisher identity if available; complete required tax and bank/payment setup only through the authorized normal process. Stop for CAPTCHA, OTP, payment approval, or forced identity verification. After authorized enrollment, apply once to advertiser 5261735 and recover only the exact vendor-issued customer-facing tracking URL.',
    evidence: [
      '2026-10-08 official Google Workspace Affiliate Program recheck: applications are free and handled through CJ Affiliate after program review.',
      'Google\'s official Affiliate Supported Countries PDF lists South Korea in the Asia Pacific region.',
      'Google\'s official affiliate terms require acceptance of the program terms and a business/residence address, valid tax identifier, and valid bank account in the supported territory; CJ publisher terms also apply.',
      'No legal terms were accepted, no application was submitted, no duplicate identity was created, and no COSHUMA-specific customer tracking URL was observed.',
    ],
  },
  'hide-me': {
    stale: [null, 'unclassified', 'application_available', 'browser_required_application_form', 'waiting_vendor_response'],
    status: 'browser_required_legal_program_consent',
    checkedAt: '2026-10-12T17:27:44+09:00',
    source: 'https://hide.me/en/affiliates',
    workflow: 'https://affiliates.hide.me/affiliates/signup.php#SignupForm',
    applicationState: 'not_submitted_legal_terms_unaccepted',
    next: "The account holder must review and explicitly approve the required hide.me affiliate agreement before submission. The form requires acceptance of material indemnification, Malaysian-law/Kuala Lumpur arbitration, prevailing-party attorney-fee and cost reimbursement, class-action waiver, and jury-trial waiver terms. If approved, reuse the existing COSHUMA identity, submit once only, and recover only the exact vendor-issued customer-facing tracking URL. Stop for CAPTCHA, OTP, payment approval, or forced identity verification.",
    evidence: [
          "Gmail message 1a12f13773e18e88 in thread 1a07b04c92ac440b from affiliate@eventure.my (cc affiliate@hide.me), received 2026-10-12T16:46:04+09:00, directs COSHUMA to the official Post Affiliate Pro signup form and says the application will be reviewed after submission.",
          "The official signup form was opened through the supported browser route and requires affirmative acceptance of the affiliate agreement; no application was submitted and no terms were accepted.",
          "The required agreement includes affiliate indemnification and defense obligations, Malaysian law and Kuala Lumpur arbitration, reimbursement of the prevailing party's attorney fees and costs, a class-action waiver, and a jury-trial waiver.",
          "No approval, customer-facing tracking URL, click, signup, paid customer, commission, payout, or revenue is verified."
    ],
    lifecycleOverride: {
      source_type: 'vendor_email_and_official_program_form',
      source_ref: 'gmail:1a12f13773e18e88',
      observed_at: '2026-10-12T17:27:44+09:00',
      reason: 'Fresh vendor direction and the required legal agreement supersede the waiting-for-response state; the application remains unsubmitted pending explicit legal consent.',
    },
  },
  'snov-io': {
    stale: [null, 'unclassified', 'application_available'],
    status: 'browser_required_legal_program_consent',
    source: 'https://snov.io/affiliate-program',
    workflow: 'https://snov.io/affiliate-program',
    next: 'Reconcile the prior COSHUMA inquiry before any resubmission. The official application requires Affiliate Program Terms and Conditions consent; do not submit or create a tracking URL until that legal-consent gate is completed through the normal supported process.',
  },
};

const protectedStates = new Set(['approved_tracking','approved','approved_account','application_submitted','application_pending','pending','rejected','cooldown','closed']);

function reconcileTool(tool, rule) {
  const current = tool.affiliate_status ?? null;
  if (protectedStates.has(current) || !rule.stale.includes(current)) return false;
  tool.affiliate_url = null;
  tool.affiliate_verified = false;
  tool.affiliate_status = rule.status;
  tool.affiliate_status_checked_at = rule.checkedAt ?? checkedAt;
  tool.affiliate_source_url = rule.source;
  if (rule.workflow) tool.affiliate_workflow_url = rule.workflow;
  if (rule.applicationState) tool.application_state = rule.applicationState;
  if (rule.lifecycleOverride) tool.affiliate_lifecycle_override = rule.lifecycleOverride;
  if (tool.affiliate_verified_at && !tool.affiliate_verified) delete tool.affiliate_verified_at;
  tool.affiliate_next_action = rule.next;
  if (rule.evidence) tool.affiliate_evidence_markers = rule.evidence;
  return true;
}

let changes = 0;
for (const file of ['data/tools.json','data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  for (const [id, rule] of Object.entries(states)) {
    const tool = tools.find((row) => row.id === id);
    if (!tool) throw new Error(`Missing affiliate-gap tool: ${id}`);
    changes += Number(reconcileTool(tool, rule));
  }
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}

const currentEvidenceAt = '2026-10-12T10:04:00+09:00';
const hideMeEvidenceAt = '2026-10-12T17:27:44+09:00';

const outreachPath = 'data/affiliate_outreach_state.json';
const outreach = JSON.parse(fs.readFileSync(outreachPath, 'utf8'));
outreach.updated_at = currentEvidenceAt;
outreach.programs ||= {};
outreach.programs.activepieces = {
  status: 'waiting_partnerstack_network_review',
  tracking_url: null,
  application_state: 'not_submitted_program_not_found',
  account: 'support@coshuma.com',
  checked_at: currentEvidenceAt,
  official_program_url: null,
  historical_marketplace_url: 'https://market.partnerstack.com/program/activepieces',
  next_action: states.activepieces.next,
  note: states.activepieces.evidence.join(' '),
  user_action_required: false,
};
outreach.programs.colossyan = {
  status: 'waiting_vendor_response',
  tracking_url: null,
  application_state: 'not_submitted_existing_impact_access_loop',
  account: 'support@coshuma.com',
  checked_at: currentEvidenceAt,
  official_program_url: 'https://www.colossyan.com/affiliate-program/',
  workflow_url: 'https://app.impact.com/campaign-promo-signup/Colossyan.brand',
  outbound_message_id: '1a12d6fc6dcddca9',
  do_not_repeat_outreach: true,
  next_action: states.colossyan.next,
  note: states.colossyan.evidence.join(' '),
  user_action_required: false,
};
outreach.programs['hide-me'] = {
  status: 'browser_required_legal_program_consent',
  tracking_url: null,
  application_state: 'not_submitted_legal_terms_unaccepted',
  account: 'personal Gmail thread 1a07b04c92ac440b',
  checked_at: hideMeEvidenceAt,
  official_program_url: 'https://hide.me/en/affiliates',
  workflow_url: 'https://affiliates.hide.me/affiliates/signup.php#SignupForm',
  inbound_message_id: '1a12f13773e18e88',
  thread_id: '1a07b04c92ac440b',
  sent_message_id: '1a12a460802a7bfc',
  do_not_repeat_outreach: true,
  next_action: states['hide-me'].next,
  note: states['hide-me'].evidence.join(' '),
  user_action_required: true,
};
outreach.updated_at = hideMeEvidenceAt;
fs.writeFileSync(outreachPath, `${JSON.stringify(outreach, null, 2)}\n`);

const queuePath = 'data/browser_required_queue.json';
const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
const upsertQueue = (id, toolId, patch) => {
  const existing = queue.find((item) => item.id === id || item.tool_id === toolId);
  if (existing) Object.assign(existing, patch);
  else queue.push({ id, tool_id: toolId, ...patch });
};
upsertQueue('activepieces-affiliate-reconcile-20261003', 'activepieces', {
  priority: 'high',
  status: 'waiting_partnerstack_network_review',
  affiliate_status: 'waiting_partnerstack_network_review',
  application_state: 'not_submitted_program_not_found',
  cost: 0,
  exact_tracking_url: null,
  user_action_required: false,
  blocker: 'The authenticated marketplace does not currently expose an Activepieces program, and the PartnerStack Network Profile is pending review.',
  reason: states.activepieces.evidence.join(' '),
  next_action: states.activepieces.next,
  verified_at: currentEvidenceAt,
});
upsertQueue('colossyan-impact-access-20261012', 'colossyan', {
  priority: 'high',
  status: 'waiting_vendor_response',
  affiliate_status: 'waiting_vendor_response',
  application_state: 'not_submitted_existing_impact_access_loop',
  cost: 0,
  exact_tracking_url: null,
  user_action_required: false,
  blocker: 'The existing COSHUMA Impact identity is caught in the vendor signup/sign-in loop; Colossyan routing guidance is pending.',
  reason: states.colossyan.evidence.join(' '),
  official_program_url: 'https://www.colossyan.com/affiliate-program/',
  next_action: states.colossyan.next,
  verified_at: currentEvidenceAt,
  outbound_message_id: '1a12d6fc6dcddca9',
  do_not_reapply: true,
});
upsertQueue('partnerstack-network-profile-reapplication-20261012', 'partnerstack-network-profile', {
  priority: 'high',
  status: 'application_submitted_pending_review',
  affiliate_status: 'application_submitted_pending_review',
  application_state: 'submitted',
  cost: 0,
  exact_tracking_url: null,
  user_action_required: false,
  blocker: 'PartnerStack Network Profile review is pending.',
  reason: 'The authenticated existing COSHUMA account confirmed that the Network Profile reapplication was sent for review on 2026-10-12. This is not program approval and does not issue a customer-facing tracking URL.',
  next_action: 'Wait for the PartnerStack Network Profile decision. Do not reapply. After a decision, reconcile each vendor program separately and use only vendor-issued customer-facing tracking URLs.',
  verified_at: currentEvidenceAt,
  github_issue: 292,
  github_comment_id: 6115935512,
  do_not_reapply: true,
});
upsertQueue('hide-me-affiliate-legal-consent-20261012', 'hide-me', {
  priority: 'high',
  status: 'browser_required_legal_program_consent',
  affiliate_status: 'browser_required_legal_program_consent',
  application_state: 'not_submitted_legal_terms_unaccepted',
  cost: 0,
  exact_tracking_url: null,
  user_action_required: true,
  blocker: 'The required affiliate agreement contains material indemnity, arbitration, attorney-fee/cost, class-action-waiver, and jury-waiver provisions that need explicit account-holder legal review and consent.',
  reason: states['hide-me'].evidence.join(' '),
  official_program_url: 'https://hide.me/en/affiliates',
  application_url: 'https://affiliates.hide.me/affiliates/signup.php#SignupForm',
  next_action: states['hide-me'].next,
  verified_at: hideMeEvidenceAt,
  inbound_message_id: '1a12f13773e18e88',
  thread_id: '1a07b04c92ac440b',
  sent_message_id: '1a12a460802a7bfc',
  do_not_reapply: true,
});
fs.writeFileSync(queuePath, `${JSON.stringify(queue, null, 2)}\n`);

console.log(`Direct affiliate gap reconciliation complete; conditional tool updates=${changes}`);
