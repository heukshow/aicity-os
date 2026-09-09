import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { dashboardClient, decorateOpsHtml } from '../src/ops-dashboard-view.js';

test('connected Google snapshot replaces placeholder rows and renders actual query fields and zero clicks', async () => {
  const nodes = new Map();
  const get = id => { if (!nodes.has(id)) nodes.set(id, { textContent: '', innerHTML: '', style: {}, className: '' }); return nodes.get(id); };
  const data = { status: 'live_google_connected', measurement_status: 'live_connected', generated_at: 'fixture',
    connections: { ga4: '연결됨 · property fixture', search_console: '연결됨 · site fixture' },
    metrics: { affiliate_clicks_30d: 3 }, ranges: { today: { users: 2, sessions: 2, affiliate_clicks: 0, verified_revenue: null } },
    top_queries: [{ name: 'fixture search query', value: 21 }], search_pages: [{ name: '/fixture-page', value: 21, note: 'CTR 1%' }],
    affiliate_links: [{ name: 'https://fixture.example/', value: 3 }], snapshot: [] };
  vm.runInNewContext(`(${dashboardClient.toString()})();`, { document: { getElementById: get, querySelectorAll: () => [] }, fetch: async url => ({ ok: true, json: async () => url.includes('partnerstack') ? { connected: true, rewardCount: 0, partnershipCount: 2 } : data }) });
  await new Promise(resolve => setImmediate(resolve));
  assert.match(get('opportunities').innerHTML, /실데이터 연결됨/);
  assert.doesNotMatch(get('opportunities').innerHTML, /실데이터 집계 미연결/);
  assert.match(get('opportunities').innerHTML, /fixture-page/);
  assert.match(get('queries').innerHTML, /fixture search query/);
  assert.match(get('queries').innerHTML, /21/);
  assert.equal(get('affiliateCtr').textContent, '0.0%');
  assert.equal(get('gaApiDot').className, 'ok');
  assert.match(get('partnerState').textContent, /PartnerStack 연결됨/);
  assert.equal(get('revenue').textContent, '—');
});

test('dashboard transformation replaces obsolete initial instructions, and fails closed on incompatible HTML', () => {
  const output = decorateOpsHtml('<tbody id="opportunities"><tr>실데이터 집계 미연결</tr></tbody><script>(()=>{})();</script>');
  assert.doesNotMatch(output, /실데이터 집계 미연결/);
  assert.match(output, /partnerstack-summary.json/);
  assert.throws(() => decorateOpsHtml('<html>unexpected template</html>'));
});
