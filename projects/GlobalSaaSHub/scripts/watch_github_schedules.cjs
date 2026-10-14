#!/usr/bin/env node
'use strict';

// Native GitHub Actions scheduler watchdog. No new external services or credentials.
const fs = require('node:fs');

const REPO = 'heukshow/aicity-os';
const LABEL = 'coshuma-scheduler-sentinel';
const PREFIX = '[COSHUMA Scheduler Sentinel] ';
const WATCHED = Object.freeze([
  { file: 'coshuma-cloud-control-plane.yml', name: 'COSHUMA Cloud Control Plane', maxAgeMinutes: 95 },
  { file: 'coshuma-analytics-snapshot.yml', name: 'COSHUMA Analytics Snapshot', maxAgeMinutes: 180 },
  { file: 'coshuma-registry-reconciliation.yml', name: 'COSHUMA Registry Reconciliation', maxAgeMinutes: 180 },
  { file: 'coshuma-growth-loop.yml', name: 'COSHUMA Growth Loop', maxAgeMinutes: 180 },
  { file: 'coshuma-release-verification.yml', name: 'COSHUMA Release Verification', maxAgeMinutes: 180 },
  { file: 'royal-queue-reconcile.yml', name: 'Royal Queue Reconcile Status', maxAgeMinutes: 180 },
]);

function assessNativeSchedule(run, nowMs, maxAgeMinutes) {
  if (!run) return { healthy: false, reason: 'no_native_schedule_observed', ageMinutes: null };
  const ageMs = nowMs - Date.parse(run.created_at);
  if (!Number.isFinite(ageMs) || ageMs < -300000) {
    return { healthy: false, reason: 'invalid_run_timestamp', ageMinutes: null };
  }
  const ageMinutes = Math.max(0, Math.floor(ageMs / 60000));
  if (run.status === 'completed' && run.conclusion !== 'success') {
    return { healthy: false, reason: 'native_schedule_' + (run.conclusion || 'unknown'), ageMinutes };
  }
  if (ageMinutes > maxAgeMinutes) {
    return { healthy: false, reason: 'native_schedule_overdue', ageMinutes };
  }
  if (run.status !== 'completed') {
    return { healthy: true, reason: 'native_run_in_progress', ageMinutes };
  }
  return { healthy: true, reason: 'native_schedule_success', ageMinutes };
}

async function githubApi(method, path, data, token) {
  const response = await fetch('https://api.github.com' + path, {
    method,
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'coshuma-native-scheduler-sentinel',
      ...(data ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(data ? { body: JSON.stringify(data) } : {}),
    signal: AbortSignal.timeout(15000),
  });
  if (!response.ok) {
    const body = await response.text();
    const error = new Error(method + ' ' + path.split('?')[0] + ': HTTP ' +
      response.status + ' ' + body.slice(0, 160));
    error.status = response.status;
    throw error;
  }
  const body = await response.text();
  return body ? JSON.parse(body) : {};
}

function issueBody(target, result, run, dispatch) {
  const url = run && Number.isInteger(run.id) ?
    'https://github.com/' + REPO + '/actions/runs/' + run.id : 'none';
  return [
    '<!-- coshuma-native-scheduler-sentinel v1: ' + target.file + ' -->',
    '## COSHUMA native scheduled execution needs attention',
    '',
    '**Workflow:** ' + target.name,
    '**Problem:** ' + result.reason,
    '**Latest native scheduled run age:** ' +
      (result.ageMinutes === null ? 'unknown' : result.ageMinutes + ' minutes'),
    '**Latest native scheduled run:** ' + url,
    '**Automatic recovery:** ' + dispatch,
    '',
    'This check uses only GitHub Actions schedule events. A manually dispatched',
    'successful run DOES NOT prove that native scheduling has recovered.',
    'Only a fresh successful native scheduled run closes this issue.',
    'A single workflow_dispatch is attempted per new incident; repeated retries',
    'are blocked until native schedule recovery has been verified.',
    'No checkout, payment capture, account creation, or production deployment',
    'is performed directly by the sentinel.',
    '',
    '@heukshow — please review if this incident stays open.',
  ].join('\n');
}

function refreshIncidentObservation(body, result, run, checkedAt) {
  const url = run && Number.isInteger(run.id) ?
    'https://github.com/' + REPO + '/actions/runs/' + run.id : 'none';
  // Preserve the original dispatch outcome and any manually added notes. An open
  // incident must not keep presenting its first observation as the latest run.
  let updated = String(body || '')
    .replace(/^\*\*Problem:\*\* .*$/m, '**Problem:** ' + result.reason)
    .replace(/^\*\*Latest native scheduled run age:\*\* .*$/m,
      '**Latest native scheduled run age:** ' +
      (result.ageMinutes === null ? 'unknown' : result.ageMinutes + ' minutes'))
    .replace(/^\*\*Latest native scheduled run:\*\* .*$/m,
      '**Latest native scheduled run:** ' + url);
  const checkedLine = '**Last checked at:** ' + checkedAt;
  if (/^\*\*Last checked at:\*\* .*$/m.test(updated)) {
    updated = updated.replace(/^\*\*Last checked at:\*\* .*$/m, checkedLine);
  } else {
    updated = updated.replace(/^(\*\*Problem:\*\* .*\n)/m, '$1' + checkedLine + '\n');
  }
  return updated;
}

async function ensureLabel(api, root) {
  try {
    await api('GET', root + '/labels/' + encodeURIComponent(LABEL));
  } catch (error) {
    if (error.status !== 404) throw error;
    await api('POST', root + '/labels', {
      name: LABEL,
      color: 'b60205',
      description: 'Automated GitHub Actions native schedule interruptions',
    });
  }
}

async function main() {
  if (process.env.GITHUB_REPOSITORY !== REPO) {
    throw new Error('Refusing to operate outside the canonical COSHUMA repository');
  }
  if (process.env.GITHUB_REF !== 'refs/heads/main') {
    throw new Error('Refusing to operate outside main');
  }
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error('Missing built-in GitHub Actions token');
  const root = '/repos/' + REPO;
  const api = (method, path, data) => githubApi(method, path, data, token);
  await ensureLabel(api, root);
  const issueListing = await api(
    'GET', root + '/issues?state=all&labels=' + encodeURIComponent(LABEL) + '&per_page=100'
  );
  const known = new Map(
    issueListing.filter(item => !item.pull_request).map(item => [item.title, item])
  );
  const summary = ['## COSHUMA native scheduler sentinel', ''];
  let apiErrors = 0;

  for (const target of WATCHED) {
    const title = PREFIX + target.name;
    try {
      const path = root + '/actions/workflows/' + encodeURIComponent(target.file) +
        '/runs?event=schedule&per_page=5';
      const results = await api('GET', path);
      const runs = Array.isArray(results.workflow_runs) ? results.workflow_runs : [];
      const latest = runs.filter(item => item.head_branch === 'main' && item.event === 'schedule')
        .sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))[0] || null;
      const checkedAt = new Date().toISOString();
      const state = assessNativeSchedule(latest, Date.parse(checkedAt), target.maxAgeMinutes);
      const issue = known.get(title);

      if (state.healthy) {
        if (issue && issue.state === 'open' && state.reason === 'native_schedule_success') {
          await api('POST', root + '/issues/' + issue.number + '/comments', {
            body: 'Recovered: a fresh successful native scheduled run is confirmed. ' +
              'Run: https://github.com/' + REPO + '/actions/runs/' + latest.id +
              '. Closing this incident. A fallback-only run would not close it.',
          });
          await api('PATCH', root + '/issues/' + issue.number, { state: 'closed' });
          summary.push('- RECOVERED: ' + target.name + ' (incident #' + issue.number + ')');
        } else {
          summary.push('- OK: ' + target.name + ' (' + state.reason + ')');
        }
        continue;
      }

      if (issue && issue.state === 'open') {
        const body = refreshIncidentObservation(issue.body, state, latest, checkedAt);
        if (body !== issue.body) {
          await api('PATCH', root + '/issues/' + issue.number, { body });
        }
        summary.push('- STILL UNHEALTHY: ' + target.name + ' (#' + issue.number +
          '; ' + state.reason + '; latest native run ' + (latest ? latest.id : 'none') +
          '; age ' + (state.ageMinutes === null ? 'unknown' : state.ageMinutes + ' minutes') +
          '; one-shot retry already recorded)');
        continue;
      }

      const pending = issueBody(target, state, latest, 'pending one-shot fallback');
      let number;
      if (issue) {
        await api('PATCH', root + '/issues/' + issue.number, {
          state: 'open', body: pending,
        });
        number = issue.number;
      } else {
        const created = await api('POST', root + '/issues', {
          title, body: pending, labels: [LABEL],
        });
        number = created.number;
      }

      let dispatch = 'GitHub accepted one workflow_dispatch request';
      try {
        await api('POST', root + '/actions/workflows/' +
          encodeURIComponent(target.file) + '/dispatches', { ref: 'main' });
      } catch (error) {
        dispatch = 'DISPATCH FAILED: ' + error.message;
        apiErrors += 1;
      }
      await api('PATCH', root + '/issues/' + number, {
        body: issueBody(target, state, latest, dispatch),
      });
      summary.push('- INCIDENT: ' + target.name + ' (#' + number + '): ' +
        state.reason + ' / ' + dispatch);
    } catch (error) {
      apiErrors += 1;
      summary.push('- CHECK FAILED: ' + target.name + ': ' + error.message);
    }
  }

  const report = summary.join('\n') + '\n';
  console.log(report);
  if (process.env.GITHUB_STEP_SUMMARY) {
    fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, report);
  }
  if (apiErrors) process.exitCode = 1;
}

if (require.main === module) {
  main().catch(error => {
    console.error('COSHUMA sentinel failed:', error.message);
    process.exitCode = 1;
  });
}

module.exports = { REPO, WATCHED, PREFIX, assessNativeSchedule, issueBody, refreshIncidentObservation, main };
