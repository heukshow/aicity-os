import { applyBrowserFollowup } from './browser_followup_evidence.mjs';
import { applyApprovedTracking } from './approved_tracking_evidence.mjs';
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
  helpdesk: 'https://www.helpdesk.com/?a=8IetMhQvR&utm_campaign=pp_helpdesk-default&utm_source=PP&d=14',
  voibe: 'https://www.getvoibe.com/?aff=G5Yr5D',
  time2book: 'https://time2book.me?aff=9TzesqKi',
  taskip: 'https://taskip.net/?atp=qnV3mw',
  clickfunnels: 'https://www.clickfunnels.com/signup-flow?aff=b57f3056884d05b842f607e32347df542821875bbe3209a214141aa32a210532',
};

const verifiedAt = {
  brand24: '2026-09-02T20:44:55+09:00',
  unbounce: '2026-09-04T03:52:58+09:00',
  moosend: '2026-09-01T04:48:36+09:00',
  chatbase: '2026-09-06T01:50:28+09:00',
  taskade: '2026-09-06T00:00:00+09:00',
  gamma: '2026-09-07T05:19:08+09:00',
  jotform: '2026-09-07T06:06:40+00:00',
  helpdesk: '2026-09-08T02:06:13+09:00',
  voibe: '2026-09-08T02:06:13+09:00',
  time2book: '2026-09-08T02:06:13+09:00',
  taskip: '2026-09-08T02:19:00+09:00',
  clickfunnels: '2026-09-08T02:19:00+09:00',
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

// Account-state evidence recovered from connected Gmail and authenticated vendor
// dashboards. These overrides prevent stale records from reopening duplicate work.
const statusOverrides = {
  writesonic: {
    affiliate_url: 'https://writesonic.com?fp_ref=sang-kwon-f5452a',
    affiliate_verified: true,
    affiliate_status: 'approved_tracking',
    affiliate_final_url: 'https://writesonic.com/',
    affiliate_verified_at: '2026-09-08T03:02:55+09:00',
    affiliate_rejection_reason: null,
    affiliate_evidence_markers: [
      'Writesonic reviewer Tanay Ahir explicitly accepted the COSHUMA application in Gmail message 1a07d09c9175ad13',
      'Writesonic welcome email 1a07d08d00c9f651 issued the exact customer-facing referral URL and states referrals are rewarded when they subscribe to a paid account',
      'https://writesonic.com?fp_ref=sang-kwon-f5452a',
      'This September 8 acceptance is newer and supersedes the stale September 1 rejected state in source tool data',
    ],
  },
  brand24: {
    affiliate_url: 'https://try.brand24.com/8xqrjxybmsbt',
    affiliate_verified: true,
    affiliate_status: 'approved_tracking',
    affiliate_final_url: 'https://try.brand24.com/8xqrjxybmsbt',
    affiliate_verified_at: '2026-09-02T20:44:55+09:00',
    affiliate_evidence_markers: [
      'Fresh Brand24 partner welcome evidence supplied the account-specific customer tracking route',
      'Merged PR #109 recorded the verified Brand24 partner URL',
      'https://try.brand24.com/8xqrjxybmsbt',
    ],
  },
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
      'Exact customer-facing tracking URL not yet issued or verified',
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
    affiliate_url: 'https://www.helpdesk.com/?a=8IetMhQvR&utm_campaign=pp_helpdesk-default&utm_source=PP&d=14',
    affiliate_verified: true,
    affiliate_status: 'approved_tracking',
    affiliate_final_url: 'https://www.helpdesk.com/',
    affiliate_verified_at: '2026-09-08T02:06:13+09:00',
    affiliate_evidence_markers: [
      'Authenticated Text Partner App shows active HelpDesk default campaign 723911',
      'Text Support confirmed Campaign links are commission-bearing customer links',
      'Exact customer-facing HelpDesk campaign URL copied from the authenticated Campaign UI',
      'https://www.helpdesk.com/?a=8IetMhQvR&utm_campaign=pp_helpdesk-default&utm_source=PP&d=14',
    ],
  },
  voibe: {
    affiliate_url: 'https://www.getvoibe.com/?aff=G5Yr5D',
    affiliate_verified: true,
    affiliate_status: 'approved_tracking',
    affiliate_final_url: 'https://www.getvoibe.com/?aff=G5Yr5D',
    affiliate_verified_at: '2026-09-08T02:06:13+09:00',
    affiliate_evidence_markers: [
      'Authenticated Lemon Squeezy affiliate hub showed Voibe program Active after one free merchant request',
      'Exact Affiliate URL copied from the active Voibe program',
      'Customer destination retained aff=G5Yr5D',
    ],
  },
  time2book: {
    affiliate_url: 'https://time2book.me?aff=9TzesqKi',
    affiliate_verified: true,
    affiliate_status: 'approved_tracking',
    affiliate_final_url: 'https://www.time2book.me/',
    affiliate_verified_at: '2026-09-08T02:06:13+09:00',
    affiliate_evidence_markers: [
      'Authenticated Time2book affiliates dashboard displays Earn 30% per referral',
      'Dashboard supplied exact Copy link https://time2book.me?aff=9TzesqKi',
      'Anonymous request sets aff cookie and resolves to the official Time2book site',
    ],
  },
  taskip: {
    affiliate_url: 'https://taskip.net/?atp=qnV3mw',
    affiliate_verified: true,
    affiliate_status: 'approved_tracking',
    affiliate_final_url: 'https://taskip.net/?atp=qnV3mw',
    affiliate_verified_at: '2026-09-08T02:19:00+09:00',
    affiliate_evidence_markers: [
      'Taskip affiliate welcome email confirmed program enrollment',
      'Authenticated Success Hub displayed the exact Promotion Link after onboarding',
      'Taskip dashboard states 30% lifetime commissions',
      'Exact customer URL retained atp=qnV3mw',
    ],
  },
  clickfunnels: {
    affiliate_url: 'https://www.clickfunnels.com/signup-flow?aff=b57f3056884d05b842f607e32347df542821875bbe3209a214141aa32a210532',
    affiliate_verified: true,
    affiliate_status: 'approved_tracking',
    affiliate_final_url: 'https://www.clickfunnels.com/signup-flow?aff=b57f3056884d05b842f607e32347df542821875bbe3209a214141aa32a210532',
    affiliate_verified_at: '2026-09-08T02:19:00+09:00',
    affiliate_evidence_markers: [
      'ClickFunnels Affiliate Agreement accepted with the user authorization recorded in the browser execution evidence',
      'Authenticated affiliate dashboard exposed the exact Free Trial campaign URL',
      'Exact aff-bearing URL loaded the official ClickFunnels signup flow',
      'Dashboard showed $0 commissions and 0 conversions at verification time',
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
  marblism: {
    affiliate_url: null,
    affiliate_verified: true,
    affiliate_status: 'rejected',
    affiliate_verified_at: '2026-08-17T17:06:26Z',
    affiliate_evidence_markers: [
      'Dub.co program status email: Your application to Marblism was not approved',
      'Marblism partner application was explicitly rejected after review',
      'Rejection email lists partners@marblism.com only for cases believed to be rejected in error',
      'Do not retry or request payout setup unless newer evidence changes this state',
    ],
  },
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  for (const tool of tools) {
    if (applyBrowserFollowup(tool)) continue;
    if (applyApprovedTracking(tool)) continue;
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
