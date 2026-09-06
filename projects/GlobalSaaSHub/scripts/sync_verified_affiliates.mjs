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
};

const verifiedAt = {
  unbounce: '2026-09-04T03:52:58+09:00',
  moosend: '2026-09-01T04:48:36+09:00',
  chatbase: '2026-09-06T01:50:28+09:00',
  taskade: '2026-09-06T00:00:00+09:00',
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
