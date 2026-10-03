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

test('Descript prices agree across buyer pages and survive both SEO dataset producers', () => {
  const project = new URL('../../', import.meta.url);
  const pages = ['tool/descript.html', 'best/ai-video-generators.html', 'compare/descript-vs-tubebuddy.html'];
  const readPages = (root) => pages.map((file) => fs.readFileSync(path.join(root, 'public', file), 'utf8'));
  const affiliateTags = (html) => [...html.matchAll(/<a\b(?=[^>]*data-tool-id="descript")(?=[^>]*data-cta="affiliate")[^>]*>/g)].map((m) => m[0]);
  const assertPricesAgree = ([detail, shortlist, comparison]) => {
    const plans = Object.fromEntries([...detail.matchAll(/<div\b[^>]*>(Hobbyist|Creator|Business)<\/div>\s*<div\b[^>]*>\$(\d+) \/ \$(\d+)<\/div>/g)]
      .map(([, name, annual, monthly]) => [name, { annual: Number(annual), monthly: Number(monthly) }]));
    // Official Descript pricing checked on October 4, 2026. Both rates are per person/month.
    assert.deepEqual(plans, {
      Hobbyist: { annual: 16, monthly: 24 },
      Creator: { annual: 24, monthly: 35 },
      Business: { annual: 50, monthly: 65 },
    });
    const [entryName, entryPlan] = Object.entries(plans).sort((a, b) => a[1].annual - b[1].annual)[0];
    const shortlistPrices = [...shortlist.matchAll(/\b(Hobbyist|Creator|Business) \$(\d+)\/person\/mo billed yearly/g)];
    assert.equal(shortlistPrices.length, 2, 'The shortlist card and decision table must both identify the entry paid plan');
    for (const [, name, price] of shortlistPrices) {
      assert.equal(name, entryName);
      assert.equal(Number(price), entryPlan.annual);
    }
    const comparisonPrices = [...comparison.matchAll(/\b(Hobbyist|Creator|Business) \$(\d+)\/person\/mo billed annually or \$(\d+) billed monthly/g)];
    assert.equal(comparisonPrices.length, 2);
    for (const [, name, annual, monthly] of comparisonPrices) {
      assert.deepEqual({ annual: Number(annual), monthly: Number(monthly) }, plans[name]);
    }
    const schemas = [...detail.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)].map((m) => JSON.parse(m[1]));
    const pricingAnswer = schemas.flatMap((schema) => schema.mainEntity || [])
      .find((question) => question.name === 'How much does Descript cost in 2026?')?.acceptedAnswer?.text;
    assert.ok(pricingAnswer, 'The pricing FAQ must remain available after regeneration');
    const faqPrices = [...pricingAnswer.matchAll(/\b(Hobbyist|Creator|Business) at \$(\d+) per person per month billed annually or \$(\d+) billed monthly/g)];
    assert.equal(faqPrices.length, 3);
    for (const [, name, annual, monthly] of faqPrices) {
      assert.deepEqual({ annual: Number(annual), monthly: Number(monthly) }, plans[name]);
    }
    assert.equal(schemas.find((schema) => schema['@type'] === 'SoftwareApplication')?.offers?.price, '0');
    for (const html of [detail, shortlist, comparison]) {
      assert.doesNotMatch(html, /Creator (?:at )?\$12|Pro at \$24/);
    }
    assert.match(shortlist, /Pictory pricing \(pictory\.ai\/pricing\) and Fliki pricing \(fliki\.ai\/pricing\) last checked Sep 5, 2026/);
    assert.match(comparison, /TubeBuddy official sources on September 2, 2026/);
  };

  const committed = pages.map((file) => fs.readFileSync(new URL(`public/${file}`, project), 'utf8'));
  assertPricesAgree(committed);
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coshuma-descript-pricing-'));
  try {
    for (const dir of ['scripts', 'data', 'config', 'src', 'public/best']) fs.mkdirSync(path.join(root, dir), { recursive: true });
    for (const file of ['scripts/generate_seo_pages.py', 'scripts/guard_public_copy.py', 'scripts/build_search_comparisons.mjs', 'scripts/ensure_best_pages_in_sitemap.py', 'scripts/inject_tool_value_playbooks.py', 'scripts/guard_tool_trust_disclosures.py', 'scripts/build_public_tools.mjs', 'scripts/affiliate_state_fs.mjs', 'config/public_content_policy.json', 'data/tools.json', 'data/tools.next.json', 'data/standalone_tool_pages.json', 'public/methodology.html', 'src/App.jsx', 'index.html']) {
      fs.copyFileSync(new URL(file, project), path.join(root, file));
    }
    const playbooks = fs.readdirSync(new URL('data/', project)).filter((file) => /^tool_value_playbooks.*\.json$/.test(file));
    const descriptPlaybook = playbooks.map((file) => JSON.parse(fs.readFileSync(new URL(`data/${file}`, project), 'utf8')).descript).find(Boolean);
    assert.ok(descriptPlaybook);
    fs.writeFileSync(path.join(root, 'data/tool_value_playbooks.json'), JSON.stringify({ descript: descriptPlaybook }));
    fs.cpSync(new URL('scripts/public-copy-templates/', project), path.join(root, 'scripts/public-copy-templates'), { recursive: true });
    fs.writeFileSync(path.join(root, 'public/best/ai-video-generators.html'), committed[1]);
    const run = (exe, script, args = []) => {
      const result = spawnSync(exe, [path.join(root, 'scripts', script), ...args], { cwd: root, encoding: 'utf8' });
      assert.equal(result.status, 0, `${script}: ${result.stdout}\n${result.stderr}`);
    };
    // The daily generator deletes tool/compare output. Restore the researched pages
    // early, then run the existing producers; the late copy pass must retain their work.
    for (const sourceArgs of [[], ['--source', 'tools.json']]) {
      run('python', 'generate_seo_pages.py', sourceArgs);
      run('python', 'guard_public_copy.py', ['--restore-descript-guides']);
      run('node', 'build_search_comparisons.mjs');
      run('python', 'ensure_best_pages_in_sitemap.py');
      run('python', 'inject_tool_value_playbooks.py');
      run('python', 'guard_tool_trust_disclosures.py');
      run('python', 'guard_public_copy.py');
      run('node', 'build_public_tools.mjs');
      const regenerated = readPages(root);
      assertPricesAgree(regenerated);
      assert.match(regenerated[0], /COSHUMA_TRUST_BLOCK/);
      assert.match(regenerated[0], /COSHUMA_VALUE_PLAYBOOK_START/);
      assert.match(regenerated[0], /\/methodology\.html/);
      assert.match(regenerated[2], /aria-label="Evidence and methodology"/);
      regenerated.forEach((html, i) => assert.deepEqual(affiliateTags(html), affiliateTags(committed[i])));
    }
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
