import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { stripPrivateOps } from '../private_ops_build_guard.mjs';

test('publication removes ops HTML/JSON and audit even when regenerated, retaining public site', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'coshuma-publication-'));
  try {
    fs.mkdirSync(path.join(root, 'ops'));
    for (const file of ['ops/traffic-revenue.html', 'ops/traffic-revenue-data.json', 'ops/revenue-seo-refresh.json', 'admin-affiliate-audit.json', 'index.html']) fs.writeFileSync(path.join(root,file),'fixture');
    stripPrivateOps(root);
    assert.deepEqual(fs.readdirSync(root), ['index.html']);
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});
