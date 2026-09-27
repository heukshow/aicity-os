import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { matchesPricingFilter } from '../../src/utils/pricingFilter.mjs';

test('unknown prices remain discoverable but cannot become invented budget matches', () => {
  for (const value of [null, '', 'See official pricing', 'Contact sales', 'Varies by plan']) {
    assert.equal(matchesPricingFilter(value, 'all'), true);
    for (const filter of ['under20', 'under50', 'over50']) assert.equal(matchesPricingFilter(value, filter), false);
  }
});

test('budget boundaries retain decimal amounts and existing free/trial discovery', () => {
  assert.equal(matchesPricingFilter('$19.99/month', 'under20'), true);
  assert.equal(matchesPricingFilter('$20/month', 'under50'), true);
  assert.equal(matchesPricingFilter('$50.50/month', 'under50'), false);
  assert.equal(matchesPricingFilter('$50.50/month', 'over50'), true);
  assert.equal(matchesPricingFilter('$1,200/year', 'under20'), false);
  assert.equal(matchesPricingFilter('Free plan', 'under20'), true);
  assert.equal(matchesPricingFilter('14-day trial', 'free'), true);
  assert.equal(matchesPricingFilter('14-day trial', 'under50'), false);
});

test('producer, committed source and final artifacts reject internal values without erasing safe output', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coshuma-price-policy-'));
  const project = new URL('../../', import.meta.url);
  try {
    for (const dir of ['scripts', 'data', 'config', 'public', 'src/generated', 'dist']) fs.mkdirSync(path.join(root, dir), { recursive: true });
    for (const file of ['scripts/build_public_tools.mjs', 'scripts/affiliate_state_fs.mjs', 'scripts/guard_raw_public_source.py', 'scripts/guard_public_artifact_boundary.py', 'config/public_content_policy.json']) fs.copyFileSync(new URL(file, project), path.join(root, file));
    const run = (exe, script, args = []) => spawnSync(exe, [path.join(root, 'scripts', script), ...args], { cwd: root, encoding: 'utf8' });
    const output = path.join(root, 'src/generated/public-tools.json');
    const tool = { id: 'fixture', pricing: 'See official pricing', official_url: 'https://example.com/', affiliate_status: 'approved_tracking', affiliate_verified: true, affiliate_url: 'https://example.com/?ref=unchanged' };
    fs.writeFileSync(path.join(root, 'data/tools.json'), JSON.stringify([tool]));
    assert.equal(run('node', 'build_public_tools.mjs').status, 0);
    const safe = fs.readFileSync(output, 'utf8');
    assert.equal(JSON.parse(safe)[0].outbound_url, tool.affiliate_url);
    for (const bad of ['Not specified in snippet', 'Varies by paid referral plan']) {
      fs.writeFileSync(path.join(root, 'data/tools.json'), JSON.stringify([{ ...tool, pricing: bad }]));
      assert.notEqual(run('node', 'build_public_tools.mjs').status, 0);
      assert.equal(fs.readFileSync(output, 'utf8'), safe);
      fs.writeFileSync(path.join(root, 'public/tool.html'), `<p>${bad}</p>`);
      assert.notEqual(run('python', 'guard_raw_public_source.py').status, 0);
      fs.writeFileSync(path.join(root, 'dist/app.js'), `const pricing=${JSON.stringify(bad)};`);
      assert.notEqual(run('python', 'guard_public_artifact_boundary.py', ['dist']).status, 0);
    }
    fs.writeFileSync(path.join(root, 'dist/app.js'), safe);
    assert.equal(run('python', 'guard_public_artifact_boundary.py', ['dist']).status, 0);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
