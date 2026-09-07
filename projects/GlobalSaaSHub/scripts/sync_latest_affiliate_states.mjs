import fs from 'node:fs';

const observedAt = '2026-09-08T02:19:00+09:00';

const states = {
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
    const next = states[tool.id];
    if (!next) continue;
    Object.assign(tool, next);
    changed += 1;
  }
  fs.writeFileSync(relativePath, `${JSON.stringify(tools, null, 2)}\n`);
  console.log(`sync_latest_affiliate_states: ${relativePath} updated=${changed}`);
}
