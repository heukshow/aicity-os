import fs from './affiliate_state_fs.mjs';

const checkedAt = '2026-10-03T03:05:00+09:00';

const states = {
  activepieces: {
    stale: [null, 'unclassified'],
    status: 'browser_required_sales_inquiry',
    source: 'https://www.activepieces.com/',
    workflow: 'https://www.activepieces.com/',
    next: 'Use the current official Talk to sales/contact route to ask whether a public affiliate or referral program exists. Do not infer a program or tracking URL.',
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
    stale: [null, 'unclassified', 'application_not_submitted'],
    status: 'browser_required_program_enrollment',
    source: 'https://partners.dub.co/dub',
    workflow: 'https://app.dub.co/referrals',
    next: 'Reuse the existing Dub account and open Dub own referral dashboard/program enrollment. Do not create a duplicate Dub account.',
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
    stale: [null, 'unclassified', 'browser_required_country_eligibility_check'],
    status: 'application_available_account_required',
    source: 'https://workspace.google.com/intl/ko/affiliate-program/',
    workflow: 'https://public.cj.com/signup/publisher?advertiserId=5261735',
    next: 'Reuse an existing COSHUMA-owned CJ publisher account if authenticated evidence becomes available. Otherwise hold: CJ account creation, publisher-agreement consent, tax forms, and payment information are outside the current autonomous application scope. After authorized enrollment, apply to advertiser 5261735 and verify the issued customer-facing tracking URL before any CTA change.',
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
    status: 'browser_required_application_form',
    source: 'https://snov.io/affiliate-program',
    workflow: 'https://snov.io/affiliate-program',
    next: 'Use the current official Snov.io affiliate application and reconcile the prior COSHUMA inquiry before any resubmission.',
  },
};

const protectedStates = new Set(['approved_tracking','approved','approved_account','application_submitted','application_pending','pending','rejected','cooldown','closed']);

function reconcileTool(tool, rule) {
  const current = tool.affiliate_status ?? null;
  if (protectedStates.has(current) || !rule.stale.includes(current)) return false;
  tool.affiliate_url = null;
  tool.affiliate_verified = false;
  tool.affiliate_status = rule.status;
  tool.affiliate_status_checked_at = checkedAt;
  tool.affiliate_source_url = rule.source;
  if (rule.workflow) tool.affiliate_workflow_url = rule.workflow;
  tool.affiliate_next_action = rule.next;
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
