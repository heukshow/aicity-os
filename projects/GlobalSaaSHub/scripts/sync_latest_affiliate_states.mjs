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
