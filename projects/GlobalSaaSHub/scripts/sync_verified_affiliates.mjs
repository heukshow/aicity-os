import fs from 'node:fs';

const verified = {
  gohighlevel: 'https://www.gohighlevel.com/?fp_ref=sangkwon56',
  castmagic: 'https://castmagic.io?fpr=sangkwon-an54',
  descript: 'https://get.descript.com/ole5fu20j5sq',
  'fireflies-ai': 'https://fireflies.ai/?fpr=sangkwon53',
  pictory: 'https://pictory.ai?fpr=sangkwon-an23',
  vidiq: 'https://vidiq.com/coshuma',
  cartstack: 'http://www.cartstack.com/?afmc=wb',
  'customgpt-ai': 'https://customgpt.ai/?fpr=sangkwon-3b18de',
  docsbot: 'https://docsbot.ai?via=31kq9q',
  databox: 'https://databox.com?aff_id=15298659&fp_ref=sangkwon-72c9ec',
  'murf-ai': 'https://get.murf.ai/fqac0vixj0qs',
  brand24: 'https://try.brand24.com/8xqrjxybmsbt',
  shopify: 'https://shopify.pxf.io/7670642-link?sharedid=7670642',
  'vista-social': 'https://vistasocial.com?fpr=sangkwon14',
  bookyourdata: 'https://join.bookyourdata.com/swcyqmumr3s5',
  unbounce: 'https://unbounce.partnerlinks.io/5ubjnt8lluqi',
  moosend: 'https://trymoo.moosend.com/6eappdpw04pw',
  chatbase: 'https://link.chatbase.co/sang-kwon-an',
  taskade: 'https://www.taskade.com/?via=7zzjo7',
  gamma: 'https://try.gamma.app/pu20lusdpn1j',
  jotform: 'https://www.jotform.com/?partner=coshuma',
};

const verifiedAt = {
  unbounce: '2026-09-04T03:52:58+09:00',
  moosend: '2026-09-01T04:48:36+09:00',
  chatbase: '2026-09-06T01:50:28+09:00',
  taskade: '2026-09-06T00:00:00+09:00',
  gamma: '2026-09-07T05:19:08+09:00',
  jotform: '2026-09-07T06:06:40+00:00',
};

// Current official product data that must remain correct in the production build
// even when an older source record is still present in tools.json/tools.next.json.
// These fields are rechecked against the vendor's official pricing/product pages
// before being changed here.
const dataOverrides = {
  taskade: {
    description: 'AI workspace for building Taskade Genesis apps, AI agents, automations and collaborative workspaces in one environment.',
    pricing: 'Free plan; Pro $10/month in the annual-billing view (10 users included)',
    pricing_source_url: 'https://www.taskade.com/pricing',
    pricing_evidence_markers: ['$10', '10 users included', '50,000 credits/month'],
    pricing_verified: true,
    pricing_verified_at: '2026-09-06T00:00:00+09:00',
    currency: 'USD',
    billing_period: 'annual billing displayed monthly',
    evidence_source_type: 'official_pricing_page',
    key_features: [
      'Taskade Genesis AI apps',
      'Unlimited AI agents',
      'Unlimited AI automations',
      '100+ integrations',
    ],
  },
};

// Account-state evidence recovered from connected Gmail. These overrides do not
// create affiliate URLs; they only stop already-known outcomes from remaining
// "unclassified" in the production revenue audit.
const statusOverrides = {
  'synthflow-ai': {
    affiliate_url: null,
    affiliate_verified: false,
    affiliate_status: 'application_submitted',
    affiliate_source_url: 'https://synthflow.ai/partners/become-a-partner',
    affiliate_final_url: 'https://forms.default.com/166142',
    affiliate_verified_at: '2026-09-07T06:52:20Z',
    affiliate_evidence_markers: [
      'Thanks for filling out the form!',
      'A Synthflow AI Channel representative will contact you shortly',
      'Referral Partners application submitted; approval and tracking link not confirmed',
    ],
  },
  hubspot: {
    affiliate_verified: true,
    affiliate_status: 'rejected',
    affiliate_verified_at: '2026-09-02T11:28:46+09:00',
    affiliate_evidence_markers: [
      'HubSpot Affiliate Team re-review response',
      'minimum requirement of 1,000 monthly visitors',
      'reconsider once site meets the traffic criteria',
    ],
  },
  omnisend: {
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: '2026-09-01T20:00:57+09:00',
    affiliate_evidence_markers: [
      'Omnisend Affiliate Partner Program application received',
      'application will be reviewed and processed',
    ],
  },
  'socialchamp-io': {
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: '2026-09-01T19:35:42+09:00',
    affiliate_evidence_markers: [
      'Social Champ affiliate application received',
      'profile review expected in 3-5 business days',
    ],
  },
  getgabs: {
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: '2026-09-07T00:00:00+09:00',
    affiliate_evidence_markers: [
      'Getgabs official affiliate page says signup is free and provides a unique referral link',
      'COSHUMA affiliate application sent to official info@getgabs.com address',
      'Gmail message id 1a07a9eff46a2c04',
      'Exact customer-facing referral URL not yet issued or verified',
    ],
  },
  'tagshop-ai': {
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: '2026-09-07T00:00:00+09:00',
    affiliate_evidence_markers: [
      'Tagshop AI official affiliate page says joining is free and provides dashboard referral-link access',
      'Official affiliate terms show 30% recurring commission for 6 months and a 90-day cookie',
      'COSHUMA affiliate application sent to official hello@tagshop.ai address',
      'Gmail message id 1a07aa3450c58442',
      'Exact customer-facing referral URL not yet issued or verified',
    ],
  },
  veed: {
    affiliate_verified: true,
    affiliate_status: 'application_submitted',
    affiliate_verified_at: '2026-09-07T00:00:00+09:00',
    affiliate_evidence_markers: [
      'VEED official affiliate page currently advertises recurring affiliate commission',
      'Repository application route is Impact and no COSHUMA customer tracking URL is verified yet',
      'COSHUMA direct enrollment request sent to official hello@veed.io support address',
      'Gmail message id 1a07aa4c0c4a2a6d',
      'Exact customer-facing tracking URL not yet issued or verified',
    ],
  },
  jasper: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'enrollment_requested',
    affiliate_source_url: 'https://www.jasper.ai/legal/affiliates',
    affiliate_verified_at: '2026-09-07T17:40:00+09:00',
    affiliate_evidence_markers: [
      'Jasper official Marketing Affiliate Program Agreement remains published and describes application review plus an affiliate tracking tool after acceptance',
      'No prior Jasper affiliate or partner Gmail thread found before outreach',
      'COSHUMA current application route / account-specific invitation request sent to official hey@jasper.ai',
      'Gmail message id 1a07b08a71bdbf24',
      'Exact customer-facing affiliate URL not yet issued or verified',
    ],
  },
  helpdesk: {
    affiliate_verified: true,
    affiliate_status: 'approved_account_campaign_link_pending',
    affiliate_verified_at: '2026-09-07T12:15:27+09:00',
    affiliate_evidence_markers: [
      'Text Partner Program account enrolled',
      'Text Support confirms Campaign affiliate links are commission-bearing customer links',
      'Text Support permits creating a HelpDesk-specific Campaign instead of using a generic URL',
      'Exact HelpDesk Campaign customer URL still requires authenticated Partner App verification',
    ],
  },
  joiin: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'enrollment_requested',
    affiliate_source_url: 'https://www.joiin.co/affiliate-partner-programme/',
    affiliate_final_url: 'https://app.getreditus.com/marketplace/joiin',
    affiliate_verified_at: '2026-09-07T18:38:00+09:00',
    affiliate_evidence_markers: [
      'Joiin Support confirmed the official affiliate programme route',
      'Official Joiin signup CTA resolves to the Joiin Reditus programme listing',
      'COSHUMA requested direct invitation/enrollment for the existing Reditus business account',
      'Gmail sent message id 1a07b3b2652931e8',
      'Exact customer-facing referral URL not yet issued or verified',
    ],
  },
  teknikforce: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'enrollment_requested',
    affiliate_source_url: 'https://teknikforce.com/affiliates',
    affiliate_verified_at: '2026-09-07T18:47:00+09:00',
    affiliate_evidence_markers: [
      'Teknikforce official affiliate page currently lists its software products for affiliates and states 50% commissions',
      'Official affiliate page lists support@teknikforce.com for contact',
      'No prior Teknikforce affiliate or partner Gmail thread found before outreach',
      'COSHUMA enrollment/signup-path request sent to official support address',
      'Gmail sent message id 1a07b429298ef60e',
      'Exact customer-facing tracking URL not yet issued or verified',
    ],
  },
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  for (const tool of tools) {
    const dataOverride = dataOverrides[tool.id];
    if (dataOverride) Object.assign(tool, dataOverride);

    const override = statusOverrides[tool.id];
    if (override) Object.assign(tool, override);

    if (verified[tool.id]) tool.affiliate_url = verified[tool.id];
    if (!tool.affiliate_url || (tool.affiliate_verified !== true && !verified[tool.id])) continue;
    tool.affiliate_verified = true;
    tool.affiliate_status = 'approved_tracking';
    tool.affiliate_verified_at ||= verifiedAt[tool.id] || '2026-09-01T00:00:00+09:00';
  }
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}
