import test from 'node:test';
import assert from 'node:assert/strict';
import { expectedAudienceProjection, assertAudienceProjection, AUDIENCE_EVENTS } from '../audience-projection-contract.mjs';
const fixture = () => ({ audience_growth: { status: 'live_connected', collected_at: '2026-10-03T17:00:00Z', ranges: { '7d': { return_visit: { events: 0, users: 0 } } } }, revenue: { private: true } });
test('exact eight-event projection preserves zero, null and both windows', () => {
  const source = fixture(); const actual = expectedAudienceProjection(source);
  assert.equal(actual.events.length, 8);
  assert.equal(actual.ranges['7d'].return_visit.events, 0);
  assert.equal(actual.ranges['30d'].return_visit.events, null);
  assert.deepEqual(Object.keys(actual.ranges['7d']), [...AUDIENCE_EVENTS]);
  assertAudienceProjection(actual, source);
});
test('extra private fields, absent events and invented zero fail closed', () => {
  const source=fixture(); const good=expectedAudienceProjection(source);
  assert.throws(()=>assertAudienceProjection({...good, revenue: {}}, source));
  assert.throws(()=>assertAudienceProjection({...good, events: good.events.slice(0,3)}, source));
  const zero=structuredClone(good); zero.ranges['30d'].return_visit.events=0;
  assert.throws(()=>assertAudienceProjection(zero, source));
});
test('unavailable source and stale observed response cannot pass', () => {
  assert.throws(()=>expectedAudienceProjection({}));
  const source=fixture(); const old=expectedAudienceProjection(source); old.collected_at='2026-09-01T00:00:00Z';
  assert.throws(()=>assertAudienceProjection(old, source));
});
