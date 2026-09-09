import fs from 'node:fs';
import path from 'node:path';

export function stripPrivateOps(root) {
  const base = path.resolve(root);
  // These are generated/publication copies only, never the private D1 records.
  for (const relative of ['ops', 'admin-affiliate-audit.json']) {
    const target = path.resolve(base, relative);
    if (!target.startsWith(base + path.sep)) throw new Error('Unsafe publication path');
    fs.rmSync(target, { recursive: true, force: true });
  }
}

export function privateOpsBuildGuard() {
  let output;
  return {
    name: 'exclude-private-operations',
    configResolved(config) { output = path.resolve(config.root, config.build.outDir); },
    closeBundle() { stripPrivateOps(output); },
  };
}
