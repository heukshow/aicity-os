// Explicit filesystem adapter for legacy affiliate state producers.
// Non-lifecycle files use ordinary fs; canonical JSON writes preserve direct evidence.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const root = fileURLToPath(new URL('../data/', import.meta.url));
const names = new Set(['tools.json', 'tools.next.json', 'affiliate_outreach_state.json', 'browser_required_queue.json']);
const guard = fileURLToPath(new URL('./affiliate_lifecycle_guard.py', import.meta.url));

export default {
  ...fs,
  writeFileSync(file, content, options) {
    const filename = file instanceof URL ? fileURLToPath(file) : path.resolve(String(file));
    if (path.dirname(filename) === path.resolve(root) && names.has(path.basename(filename))) {
      const result = spawnSync(process.env.PYTHON || 'python', [guard, '--merge', filename], {
        input: String(content), encoding: 'utf8', maxBuffer: 16 * 1024 * 1024,
      });
      if (result.error || result.status !== 0) throw new Error(`Affiliate lifecycle guard failed: ${result.error?.message || result.stderr}`);
      return fs.writeFileSync(file, result.stdout, options);
    }
    return fs.writeFileSync(file, content, options);
  },
};
