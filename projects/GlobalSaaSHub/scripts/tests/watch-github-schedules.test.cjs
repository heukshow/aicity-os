'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const { WATCHED, assessNativeSchedule, issueBody } = require('../watch_github_schedules.cjs');
const NOW = Date.parse('2026-10-12T00:00:00Z');
const run = (minutes, conclusion = 'success', status = 'completed') => ({
  id: 1234,
  created_at: new Date(NOW - minutes * 60000).toISOString(),
  conclusion, status, head_branch: 'main',
});

test('explicit approved dispatch allowlist has unique workflow files', () => {
  assert.equal(WATCHED.length, 6);
  assert.equal(new Set(WATCHED.map(item => item.file)).size, 6);
  for (const target of WATCHED) {
    assert.match(target.file, /^[a-z0-9-]+\.yml$/);
    assert.ok(target.maxAgeMinutes >= 90);
  }
});

test('fresh native successful schedule is healthy', () => {
  assert.deepEqual(assessNativeSchedule(run(70), NOW, 180),
    { healthy: true, reason: 'native_schedule_success', ageMinutes: 70 });
});

test('old successful native schedule is overdue: manual successes do not count', () => {
  assert.equal(assessNativeSchedule(run(181), NOW, 180).reason, 'native_schedule_overdue');
});

test('a failed native schedule is unhealthy even when it is recent', () => {
  assert.equal(assessNativeSchedule(run(3, 'failure'), NOW, 180).reason, 'native_schedule_failure');
});

test('an in-progress native schedule within grace does not cause an incident', () => {
  const state = assessNativeSchedule(run(5, null, 'in_progress'), NOW, 180);
  assert.equal(state.healthy, true);
  assert.equal(state.reason, 'native_run_in_progress');
});

test('an indefinitely queued run causes an incident', () => {
  assert.equal(assessNativeSchedule(run(181, null, 'queued'), NOW, 180).healthy, false);
});

test('missing run and invalid timestamps fail closed', () => {
  assert.equal(assessNativeSchedule(null, NOW, 180).reason, 'no_native_schedule_observed');
  assert.equal(assessNativeSchedule({ created_at: 'bad', status: 'completed', conclusion: 'success' }, NOW, 180).reason, 'invalid_run_timestamp');
});

test('alert never confuses dispatch with native recovery', () => {
  const state = assessNativeSchedule(run(300), NOW, 180);
  const body = issueBody(WATCHED[0], state, run(300), 'GitHub accepted one workflow_dispatch request');
  assert.match(body, /manually dispatched/);
  assert.match(body, /Only a fresh successful native scheduled run closes/);
  assert.match(body, /one-shot/);
  assert.doesNotMatch(body, /confirmed successful revenue/);
});
