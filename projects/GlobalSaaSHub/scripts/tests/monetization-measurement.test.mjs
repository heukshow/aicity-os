import { test } from 'node:test';
import assert from 'node:assert/strict';
import { releaseWindows, normalizeReport, collectMonetization, reportRequest } from '../monetization-measurement.mjs';

const headers = [{ name: 'eventCount' }, { name: 'activeUsers' }];
const registry = { active_queue: [{ task_key: 'GAMMA-DECISION-MEASUREMENT-20260927', lifecycle: 'production_verified', completed_at: '2026-09-26T18:02:06Z' }] };
test('fixed full-day windows exclude release day and wait for reporting latency in property timezone', () => {
  const windows = releaseWindows('2026-09-26T18:02:06Z', new Date('2026-10-05T15:00:00Z'), 'Asia/Seoul', 7);
  assert.deepEqual(windows.baseline, { start: '2026-09-20', end: '2026-09-26' });
  assert.deepEqual(windows.post, { start: '2026-09-28', end: '2026-10-04' });
  assert.equal(windows.mature, false);
  assert.equal(windows.available_on, '2026-10-07');
  assert.equal(releaseWindows('2026-09-26T18:02:06Z', new Date('2026-10-07T01:00:00Z'), 'Asia/Seoul', 7).mature, true);
});
test('an authoritative empty complete report is 0, malformed or truncated reports are never 0', () => {
  assert.deepEqual(normalizeReport({ metricHeaders: headers }, ['affiliate_click']).affiliate_click, { status: 'current', events: 0, users: 0 });
  for (const bad of [{}, { metricHeaders: headers, rowCount: 1 }, { metricHeaders: headers, metadata: { subjectToThresholding: true } },
    { metricHeaders: headers, rows: [{ dimensionValues: [{ value: 'affiliate_click' }], metricValues: [{ value: 'unknown' }, { value: '0' }] }] }]) {
    assert.throws(() => normalizeReport(bad, ['affiliate_click']));
  }
});
test('premature post-release and uninstrumented baseline metrics remain null', async () => {
  const calls = [];
  const data = await collectMonetization({ registry, now: new Date('2026-09-27T12:00:00Z'), zone: 'UTC', query: async body => { calls.push(body); return { metricHeaders: headers }; } });
  const gamma = data.experiments[0];
  assert.equal(calls.length, 2);
  assert.equal(gamma.ranges['7d'].post.metrics.affiliate_click.events, null);
  assert.equal(gamma.ranges['7d'].baseline.metrics.affiliate_cta_view.events, null);
  assert.equal(gamma.ranges['7d'].baseline.metrics.page_view.events, 0);
  assert.equal(gamma.network_funnel.paid.events, null);
  assert.equal(data.experiments[2].status, 'awaiting_production_verification');
});
test('failed baseline is isolated and mature post collection still runs', async () => {
  let calls = 0;
  const data = await collectMonetization({ registry, now: new Date('2026-11-01T00:00:00Z'), zone: 'UTC', query: async () => {
    if (++calls === 1) throw Error('upstream');
    return { metricHeaders: headers };
  } });
  assert.equal(calls, 4);
  assert.equal(data.experiments[0].ranges['7d'].baseline.metrics.page_view.events, null);
  assert.equal(data.experiments[0].ranges['7d'].post.metrics.page_view.events, 0);
});
test('queries restrict exact page, event family and known QA URL markers', () => {
  const expressions = reportRequest('/', ['affiliate_click'], { start: '2026-09-01', end: '2026-09-07' }).dimensionFilter.andGroup.expressions;
  const pattern = new RegExp(expressions[2].notExpression.filter.stringFilter.value, 'i');
  for (const query of ['?coshuma_qa=1', '?verify=release', '?x=1&utm_medium=qa&v=1']) assert.ok(pattern.test(`https://coshuma.com/${query}`));
  assert.ok(!pattern.test('https://coshuma.com/?coshuma_qa=0'));
  assert.equal(expressions[0].filter.stringFilter.value, '/');
});
