import { applyBrowserFollowup } from './browser_followup_evidence.mjs';
import { applyApprovedTracking } from './approved_tracking_evidence.mjs';
import fs from 'node:fs';

const observedAt = '2026-09-08T03:27:00+09:00';

const states = {
  'tagshop-ai': {
    "affiliate_url": null,
    "affiliate_verified": false,
    "affiliate_status": "application_submitted",
    "affiliate_final_url": null,
    "affiliate_verified_at": "2026-09-08T05:05:00+09:00",
    "affiliate_status_checked_at": "2026-09-08T05:05:00+09:00",
    "affiliate_status_evidence_url": "https://tagshop.firstpromoter.com/login",
    "affiliate_workflow_url": "https://tagshop.firstpromoter.com/login",
    "affiliate_next_action": "Resume the existing confirmed account at the login page and verify its dashboard or a subsequent program email. Do not create another account or resubmit the application. Record only an issued customer-facing tracking URL after approval verification. No further consent request is needed. Leave CAPTCHA or forced identity verification to the user; no paid plan.",
    "affiliate_evidence_markers": [
      "User explicitly authorized the mandatory program agreement; live signup checkbox was checked and Sign Up submitted once for support@coshuma.com. FirstPromoter Team <support@firstpromoter.com> sent Confirmation instructions at 05:02 KST thanking COSHUMA for signing up to Tagshop - Partner Program. The official confirmation page displayed Email confirmed successfully. Subsequent sign-in attempts remained on the login form without a dashboard or visible error. Enrollment and email confirmation are verified; approval, pending-review status and customer tracking URL remain unconfirmed. No payment was made.",
      "data/tagshop-submission-2026-09-08.json"
    ]
  },

  'copy-ai': {
    affiliate_url: null,
    affiliate_verified: false,
    affiliate_status: 'no_affiliate_program',
    affiliate_source_url: 'https://mail.google.com/mail/u/?authuser=support%40coshuma.com#all/1a07d1d846b4d3c8',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'Official support confirmation: Gmail message id 1a07d1d846b4d3c8, Copy.ai support ticket #19902',
      'Copy.ai support ticket #19902 states there is currently no active affiliate or referral program',
      'Copy.ai support states it cannot accept new partners or provide referral links at this time',
      'Do not reapply unless Copy.ai later announces a new active program',
    ],
  },
  webflow: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a zero-cost Webflow affiliate enrollment-path request from support@coshuma.com',
      'Gmail message 1a07d11319866975 records the outreach',
      'Do not send duplicate outreach while awaiting a response or browser enrollment result',
    ],
  },
  'octo-browser': {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a zero-cost Octo Browser referral-program access request from support@coshuma.com',
      'Gmail message 1a07d11543a2ddd5 records the outreach',
      'Do not send duplicate outreach while awaiting a response or authenticated referral-link recovery',
    ],
  },
  privy: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a Privy Partner Affiliate enrollment request from support@coshuma.com',
      'Gmail message 1a07d1178d900425 records the outreach',
      'Do not duplicate enrollment outreach while Privy clarifies the applicable publisher path',
    ],
  },
  heygen: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_source_url: 'https://www.heygen.com/affiliate-program',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'HeyGen support confirmed the current public enrollment route is the HeyGen Affiliate Program page',
      'Gmail thread 1a07d11c9459f1f2 contains the current support confirmation',
      'Browser enrollment remains required; no exact customer tracking URL is verified yet',
    ],
  },
  blaze: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a Blaze affiliate enrollment request from support@coshuma.com',
      'Gmail message 1a07d15348a88345 records the outreach',
      'Do not duplicate outreach while awaiting the vendor response or Impact enrollment result',
    ],
  },
  questmate: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a Questmate partner and affiliate enrollment request from support@coshuma.com',
      'Gmail message 1a07d155181b14b5 records the outreach',
      'Do not duplicate outreach while awaiting a response or exact referral link',
    ],
  },
  reactin: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a ReactIn affiliate enrollment request from support@coshuma.com',
      'Gmail message 1a07d156944e99b9 records the outreach',
      'Do not duplicate outreach while awaiting enrollment or a customer-facing referral link',
    ],
  },
  jobhire: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_source_url: 'https://jobhire.ai/affiliate-program',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'JobHire.AI support confirmed the current affiliate enrollment path is the free Join Now flow on its affiliate page',
      'Gmail thread 1a07d1688d1ef15a contains the support confirmation',
      'Browser enrollment remains required; no exact customer tracking URL is verified yet',
    ],
  },
  aiassistworks: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'browser_required_otp',
    affiliate_source_url: 'https://www.aiassistworks.com/affiliate-program',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'The official AiAssistWorks Affonso flow was opened for support@coshuma.com',
      'AiAssistWorks sent a one-time-password login email at 2026-09-08 03:21 KST',
      'OTP/browser completion is required before an exact customer-facing affiliate URL can be recovered',
    ],
  },
  synder: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a Synder affiliate enrollment request from support@coshuma.com',
      'Gmail message 1a07d1eb47ed18d2 records the outreach',
      'Do not send duplicate outreach while awaiting Synder response',
    ],
  },
  teachable: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a Teachable Affiliate Partner enrollment request from support@coshuma.com',
      'Gmail message 1a07d1e9a83375a1 records the outreach',
      'Do not send duplicate outreach while awaiting Teachable response',
    ],
  },
  tapfiliate: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'outreach_sent',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'COSHUMA sent a Tapfiliate affiliate enrollment request from support@coshuma.com',
      'Gmail message 1a07d1ed0e6585e5 records the outreach',
      'Do not send duplicate outreach while awaiting Tapfiliate response or a browser path that can bypass the prior CAPTCHA blocker',
    ],
  },
  'gravity-forms': {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'Authenticated PartnerStack displays Gravity / Application pending',
      'Application was already submitted; do not submit another application',
      'Exact customer-facing tracking URL is not available before approval',
    ],
  },
  sendcloud: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'PartnerStack email confirms Sendcloud application received and submitted for review',
      'Authenticated PartnerStack currently displays Application pending',
      'Exact customer-facing tracking URL is not yet available',
    ],
  },
  apollo: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'rejected',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'Apollo.io decision email declined the affiliate application',
      'Authenticated PartnerStack also displays Application declined',
      'Do not reapply unless Apollo explicitly changes eligibility',
    ],
  },
  'ai-video-cut': {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'One application was submitted through the authenticated official affiliate flow',
      'Campaign 27205326 is pending',
      'No customer-facing tracking URL is displayed yet',
    ],
  },
  fillout: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'Fillout program application submitted once after recorded user authorization for Program Terms',
      'Application id pga_1M1YE0ANQP8BPWPGEW2BENNGR',
      'Submission confirmation says submitted for review',
    ],
  },
  beefree: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'PartnerStack receipt confirms Really Good Emails (RGE Studio) / Beefree application submitted for review',
      'The existing PartnerStack account was reused',
      'No exact customer-facing tracking URL is available yet',
    ],
  },
  gumloop: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: '2026-09-01T00:00:00+09:00',
    affiliate_evidence_markers: [
      'Existing repository evidence records a prior Gumloop Creator Program application submission',
      'Current application form does not establish that the earlier application disappeared',
      'Do not submit a duplicate while awaiting a decision',
    ],
  },
  pipedrive: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'pending',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'Authenticated PartnerStack displays Pipedrive / Application pending',
      'Pipedrive support moved partner support to authenticated Partner Portal chat',
      'Pending application must not be duplicated',
    ],
  },
  'monday-com': {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'pending',
    affiliate_verified_at: observedAt,
    affiliate_evidence_markers: [
      'Authenticated PartnerStack displays monday.com / Application pending',
      'PartnerStack support ticket 122275 is a receipt only and does not change the pending application state',
      'Do not submit a second application',
    ],
  },
  kittl: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'approved',
    affiliate_verified_at: '2026-09-02T00:47:00+09:00',
    affiliate_evidence_markers: [
      'Kittl Impact welcome email confirms acceptance into the Kittl Affiliate Program',
      'Account-specific customer tracking URL has not yet been recovered from Impact',
      'Do not submit another Kittl application',
    ],
  },
  'reply-io': {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'enrollment_requested',
    affiliate_source_url: 'https://reply.io/affiliates/',
    affiliate_verified_at: '2026-09-07T16:47:56+09:00',
    affiliate_evidence_markers: [
      'Merged PR #269 records COSHUMA Reply.io affiliate enrollment outreach',
      'Enrollment request was sent before the audit still showed Reply.io as unclassified',
      'Exact customer-facing PartnerStack referral URL has not yet been issued',
    ],
  },
  'reclaim-ai': {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'enrollment_requested',
    affiliate_verified_at: '2026-09-07T19:50:46+09:00',
    affiliate_evidence_markers: [
      'Merged PR #289 records a current Reclaim.ai program-specific enrollment/direct-invitation request',
      'Do not reopen the stale application_page_unavailable state while this request is unresolved',
      'Exact customer-facing tracking URL is not yet verified',
    ],
  },
  reditus: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'enrollment_requested',
    affiliate_verified_at: '2026-09-07T19:44:59+09:00',
    affiliate_evidence_markers: [
      'Merged PR #287 records a zero-cost Reditus affiliate enrollment request',
      'Existing Reditus account was reused rather than creating a duplicate account',
      'Exact customer-facing referral URL is not yet verified',
    ],
  },
  marketingblocks: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'enrollment_requested',
    affiliate_verified_at: '2026-09-07T19:48:03+09:00',
    affiliate_evidence_markers: [
      'Merged PR #288 records a zero-cost MarketingBlocks affiliate enrollment-path request',
      'Official support material confirms affiliates receive unique tracked links after approval',
      'Exact customer-facing tracking URL is not yet issued or verified',
    ],
  },
  flowgent: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'vendor-paused',
    affiliate_verified_at: '2026-09-07T19:43:49+09:00',
    affiliate_evidence_markers: [
      'Merged PR #286 records that the official Rewardful CTA currently reports Affiliate Program Inactive',
      'Do not submit or infer an application until the vendor restores a working program route',
    ],
  },
  cloudways: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'pending',
    affiliate_verified_at: '2026-09-07T19:43:49+09:00',
    affiliate_evidence_markers: [
      'Merged PR #286 records Cloudways support ticket #966456 acknowledging the enrollment request',
      'Approval and exact customer tracking URL remain unconfirmed',
      'Do not create a duplicate request while the ticket is pending',
    ],
  },
  pickaxe: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'excluded_user_request',
    affiliate_verified_at: '2026-09-07T19:50:46+09:00',
    affiliate_evidence_markers: [
      'Merged PR #289 records that Pickaxe requires an affiliate to be a paying Pickaxe user for earnings to accrue',
      'COSHUMA operating rules prohibit adding a paid subscription solely to unlock an affiliate path',
      'Exclude from zero-cost enrollment unless the vendor changes this requirement',
    ],
  },
};

for (const relativePath of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(relativePath, 'utf8'));
  let changed = 0;
  for (const tool of tools) {
    if (applyBrowserFollowup(tool)) continue;
    if (applyApprovedTracking(tool)) continue;
    const next = states[tool.id];
    if (!next) continue;
    Object.assign(tool, next);
    changed += 1;
  }
  fs.writeFileSync(relativePath, `${JSON.stringify(tools, null, 2)}\n`);
  console.log(`sync_latest_affiliate_states: ${relativePath} updated=${changed}`);
}
