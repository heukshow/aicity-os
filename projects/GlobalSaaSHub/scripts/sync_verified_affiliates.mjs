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
};

const verifiedAt = {
  unbounce: '2026-09-04T03:52:58+09:00',
  moosend: '2026-09-01T04:48:36+09:00',
};

for (const file of ['data/tools.json', 'data/tools.next.json']) {
  const tools = JSON.parse(fs.readFileSync(file, 'utf8'));
  for (const tool of tools) {
    if (verified[tool.id]) tool.affiliate_url = verified[tool.id];
    if (!tool.affiliate_url || (tool.affiliate_verified !== true && !verified[tool.id])) continue;
    tool.affiliate_verified = true;
    tool.affiliate_status = 'approved_tracking';
    tool.affiliate_verified_at ||= verifiedAt[tool.id] || '2026-09-01T00:00:00+09:00';
  }
  fs.writeFileSync(file, `${JSON.stringify(tools, null, 2)}\n`);
}
