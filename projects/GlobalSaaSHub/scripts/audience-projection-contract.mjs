import assert from 'node:assert/strict';

export const AUDIENCE_EVENTS = Object.freeze([
  'return_visit', 'saved_tool_change', 'saved_tools_view', 'saved_shortlist_share',
  'buyer_intent_stage', 'compare_open', 'compare_tool_select', 'compare_cta_view',
]);

export function expectedAudienceProjection(snapshot) {
  const source = snapshot?.audience_growth;
  assert.ok(source && typeof source === 'object', 'Fresh audience source is unavailable');
  const expected = {
    status: typeof source.status === 'string' ? source.status : 'unavailable',
    scope: 'first_party_direct_customer_asset_usage',
    events: [...AUDIENCE_EVENTS],
    ranges: {},
  };
  for (const range of ['7d', '30d']) {
    expected.ranges[range] = {};
    for (const event of AUDIENCE_EVENTS) {
      const row = source.ranges?.[range]?.[event] || {};
      expected.ranges[range][event] = {
        events: Number.isFinite(row.events) ? row.events : null,
        users: Number.isFinite(row.users) ? row.users : null,
      };
    }
  }
  if (typeof source.collected_at === 'string') expected.collected_at = source.collected_at;
  return expected;
}

export function assertAudienceProjection(actual, snapshot) {
  // Deep equality rejects any extra private field as well as missing events,
  // changed windows, guessed zeroes or a response from an older snapshot.
  assert.deepEqual(actual, expectedAudienceProjection(snapshot));
}
