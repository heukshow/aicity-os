// Separate Node processes + actual disk SQLite. All payment responses remain synthetic.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const child = fileURLToPath(new URL('./helpers/ad-commerce-restart-child.mjs', import.meta.url));
function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), 'coshuma-payment-restart-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return (action, { product = 'tool-primary', exit = 0 } = {}) => {
    const result = spawnSync(process.execPath, [child, action, join(dir, 'order.ad-sandbox.sqlite'), join(dir, 'provider.synthetic-provider.json'), product], { encoding: 'utf8', timeout: 20000 });
    assert.equal(result.status, exit, result.stderr || result.stdout);
    return exit === 0 ? JSON.parse(result.stdout) : null;
  };
}
test('actual process restart after checkout preserves validated files and reservation', t => {
  const run = fixture(t), draft = run('prepare'), checkout = run('checkout'), recovered = run('status');
  assert.notEqual(checkout.pid, recovered.pid); assert.equal(draft.id, recovered.id);
  assert.equal(recovered.state, 'checkout'); assert.equal(recovered.files, 2); assert.equal(recovered.holds, 1);
  assert.equal(recovered.createPosts, 1); assert.equal(recovered.capturePosts, 0);
});
test('process death after provider order creation reuses the same idempotent provider order', t => {
  const run = fixture(t); run('prepare'); run('checkout-crash', { exit: 72 });
  const before = run('status'); assert.equal(before.state, 'approved'); assert.equal(before.createPosts, 1);
  const retry = run('checkout'); assert.equal(retry.state, 'checkout'); assert.equal(retry.createPosts, 1);
});
test('process death after provider capture is recovered with reads and without another charge', t => {
  const run = fixture(t); run('prepare'); run('checkout'); run('capture-crash', { exit: 71 });
  const uncertain = run('status'); assert.equal(uncertain.state, 'capturing'); assert.equal(uncertain.holds, 1);
  const recovered = run('recover'); assert.notEqual(uncertain.pid, recovered.pid);
  assert.equal(recovered.state, 'active'); assert.equal(recovered.capturePosts, 1); assert.equal(recovered.verifiedAudits, 1);
  const again = run('recover'); assert.equal(again.capturePosts, 1); assert.equal(again.verifiedAudits, 1); assert.equal(again.startsAt, recovered.startsAt);
});
test('uncertain capture survives process replacement and reservation deadline', t => {
  const run = fixture(t); run('prepare'); run('checkout'); run('capture-crash', { exit: 71 });
  const recovered = run('recover-after-deadline');
  assert.equal(recovered.state, 'active'); assert.equal(recovered.holds, 1); assert.equal(recovered.capturePosts, 1);
});
test('a paid two-position package survives restart and expires atomically', t => {
  const run = fixture(t); run('prepare', { product: 'P2' }); run('checkout'); run('capture-crash', { exit: 71 });
  const recovered = run('recover'); assert.equal(recovered.state, 'active'); assert.equal(recovered.files, 3); assert.equal(recovered.holds, 2);
  const active = run('status'); assert.equal(active.startsAt, recovered.startsAt); assert.equal(active.endsAt, recovered.endsAt);
  const ended = run('expire'); assert.equal(ended.state, 'ended'); assert.equal(ended.holds, 0); assert.equal(ended.capturePosts, 1);
  assert.equal(run('status').state, 'ended');
});
test('expired unpaid checkout after restart cannot send a capture request', t => {
  const run = fixture(t); run('prepare'); run('checkout');
  const result = run('expired-unpaid-capture'); assert.equal(result.state, 'checkout'); assert.equal(result.capturePosts, 0);
});
test('verified active payment is not recaptured or restarted on later process replacement', t => {
  const run = fixture(t); run('prepare'); run('checkout'); const active = run('capture');
  const recovered = run('recover'); assert.equal(recovered.state, 'active'); assert.equal(recovered.captureId, active.captureId);
  assert.equal(recovered.startsAt, active.startsAt); assert.equal(recovered.endsAt, active.endsAt);
  assert.equal(recovered.capturePosts, 1); assert.equal(recovered.verifiedAudits, 1);
});
