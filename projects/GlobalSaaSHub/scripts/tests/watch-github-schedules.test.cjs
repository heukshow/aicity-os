'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const { WATCHED, PREFIX, assessNativeSchedule, issueBody, refreshIncidentObservation, main } = require('../watch_github_schedules.cjs');
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
  assert.match(body, /A single workflow_dispatch/);
  assert.doesNotMatch(body, /confirmed successful revenue/);
});

test('open incident refresh preserves the dispatch result and operator notes', () => {
  const first = run(300);
  const latest = { ...run(190), id: 5678 };
  const body = issueBody(WATCHED[1], assessNativeSchedule(first, NOW, 180), first,
    'DISPATCH FAILED: HTTP 403') + '\n\nOperator note: retain the existing investigation.';
  const updated = refreshIncidentObservation(body, assessNativeSchedule(latest, NOW, 180),
    latest, '2026-10-12T00:00:00.000Z');
  assert.match(updated, /Latest native scheduled run age:\*\* 190 minutes/);
  assert.match(updated, /actions\/runs\/5678/);
  assert.doesNotMatch(updated, /actions\/runs\/1234/);
  assert.match(updated, /DISPATCH FAILED: HTTP 403/);
  assert.match(updated, /Operator note: retain the existing investigation/);
  assert.equal(updated.match(/\*\*Last checked at:\*\*/g).length, 1);
  assert.equal(refreshIncidentObservation(updated, assessNativeSchedule(latest, NOW, 180),
    latest, '2026-10-12T00:00:00.000Z'), updated);
});

async function withMockGithub(analyticsAgeMinutes, check) {
  const previousFetch = global.fetch;
  const previousEnv = { ...process.env };
  const writes = [];
  const createdAt = minutes => new Date(Date.now() - minutes * 60000).toISOString();
  const initial = { ...run(300), event: 'schedule' };
  const issue = {
    number: 1113, title: PREFIX + WATCHED[1].name, state: 'open',
    body: issueBody(WATCHED[1], assessNativeSchedule(initial, NOW, 180), initial,
      'GitHub accepted one workflow_dispatch request'),
  };
  process.env.GITHUB_REPOSITORY = 'heukshow/aicity-os';
  process.env.GITHUB_REF = 'refs/heads/main';
  process.env.GITHUB_TOKEN = 'test-token-never-transmitted';
  delete process.env.GITHUB_STEP_SUMMARY;
  global.fetch = async (url, request) => {
    const path = new URL(url).pathname;
    if (request.method !== 'GET') {
      writes.push({ method: request.method, path, body: JSON.parse(request.body) });
      return { ok: true, text: async () => '{}' };
    }
    let result;
    if (path.includes('/labels/')) result = {};
    else if (path.endsWith('/issues')) result = [issue];
    else if (path.includes('/actions/workflows/')) {
      const analytics = path.includes(WATCHED[1].file);
      // An unexpected manual result must never hide a native scheduling outage.
      result = { workflow_runs: [
        { id: 9999, head_branch: 'main', event: 'workflow_dispatch', status: 'completed',
          conclusion: 'success', created_at: createdAt(0) },
        { id: analytics ? 5678 : 6789, head_branch: 'main', event: 'schedule', status: 'completed',
          conclusion: 'success', created_at: createdAt(analytics ? analyticsAgeMinutes : 1) },
      ] };
    } else throw new Error('Unexpected mock read: ' + path);
    return { ok: true, text: async () => JSON.stringify(result) };
  };
  try {
    await main();
    await check(writes);
  } finally {
    global.fetch = previousFetch;
    for (const key of Object.keys(process.env)) if (!(key in previousEnv)) delete process.env[key];
    Object.assign(process.env, previousEnv);
  }
}

test('a still-overdue incident refreshes evidence without dispatching again', async () => {
  await withMockGithub(190, writes => {
    assert.equal(writes.length, 1);
    assert.equal(writes[0].method, 'PATCH');
    assert.match(writes[0].path, /issues\/1113$/);
    assert.match(writes[0].body.body, /actions\/runs\/5678/);
    assert.match(writes[0].body.body, /190 minutes/);
    assert.equal(writes[0].body.state, undefined);
  });
});

test('a native completion closes the incident using the actual native run', async () => {
  await withMockGithub(1, writes => {
    assert.equal(writes.length, 2);
    assert.equal(writes[0].method, 'POST');
    assert.match(writes[0].path, /issues\/1113\/comments$/);
    assert.match(writes[0].body.body, /actions\/runs\/5678/);
    assert.doesNotMatch(writes[0].body.body, /9999/);
    assert.equal(writes[1].method, 'PATCH');
    assert.deepEqual(writes[1].body, { state: 'closed' });
    assert.equal(writes.some(item => item.path.endsWith('/dispatches')), false);
  });
});
