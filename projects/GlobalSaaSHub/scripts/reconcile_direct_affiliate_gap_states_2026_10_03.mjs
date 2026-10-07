import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-10-03T03:05:00+09:00';

const states = {
  activepieces: {
    stale: [null, 'unclassified', 'browser_required_sales_inquiry'],
    status: 'browser_required_affiliate_application',
    checkedAt: '2026-10-07T12:22:00+09:00',
    source: 'https://market.partnerstack.com/program/activepieces',
    workflow: 'https://market.partnerstack.com/program/activepieces',
    next: 'Reuse the existing COSHUMA-owned PartnerStack session to open the official Activepieces program application. Inspect the application questions and program terms first; submit once only if no CAPTCHA, OTP, legal-consent, payment, or forced-identity gate appears. Recover and validate only the exact vendor-issued customer referral URL after approval.',
    evidence: [
      '2026-10-07 official PartnerStack marketplace recheck: the Activepieces program directory exposes an Apply to program action and PartnerStack sign-in.',
      'This verifies that a public application route exists; it does not prove COSHUMA application, approval, tracking URL, clicks, customers, commission, payout, or revenue.',
      'No application was submitted in this update and no COSHUMA-specific tracking URL is verified.',
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
    stale: [null, 'unclassified', 'application_available'],
    status: 'browser_required_application_form',
    source: 'https://hide.me/en/affiliates',
    workflow: 'https://hide.me/en/affiliates',
    next: 'Use the current official hide.me enrollment route and reconcile it with the prior COSHUMA inquiry before creating any new partner identity.',
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

console.log(`Direct affiliate gap reconciliation complete; conditional tool updates=${changes}`);
