// Repository integration only: SQLite :memory:, synthetic metadata, no HTTP or PayPal calls.
import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { readFileSync } from 'node:fs';
import { AdStore } from '../src/ad-commerce-store.js';
import { CATALOG_VERSION, IMAGE_SLOTS } from '../src/ad-commerce-catalog.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';
import { digest } from '../src/ad-commerce-domain.js';

function fixture(t) {
  const native = new DatabaseSync(':memory:');
  native.exec('PRAGMA foreign_keys=ON');
  for (const file of ['0004_sponsorship_sales.sql', '0005_image_ad_fulfilment.sql']) {
    native.exec(readFileSync(new URL('../migrations/' + file, import.meta.url), 'utf8'));
  }
  t.after(() => native.close());
  const db = {
    prepare(sql) { return { bind(...values) {
      const statement = native.prepare(sql);
      return {
        async first() { return statement.get(...values) ?? null; },
        async all() { return { results: statement.all(...values) }; },
        run() { return { success: true, meta: { changes: Number(statement.run(...values).changes) } }; },
      };
    } }; },
    async batch(statements) {
      native.exec('BEGIN IMMEDIATE');
      try { const results = statements.map(statement => statement.run()); native.exec('COMMIT'); return results; }
      catch (error) { native.exec('ROLLBACK'); throw error; }
    },
  };
  let time = Date.now();
  const store = new AdStore(db, { environment: 'sandbox', clock: () => new Date(time) });
  const advance = ms => { time += ms; };
  const count = table => native.prepare('SELECT count(*) AS n FROM ' + table).get().n;
  return { native, db, store, advance, count };
}
function input(product = 'tool-primary', slots = ['tool-primary']) {
  return { product, days: 30, rightsConfirmed: true, termsVersion: CATALOG_VERSION,
    company: 'LOCAL TEST ONLY', productName: 'Synthetic software', email: 'test@example.com',
    claims: 'Synthetic repository test, not advertiser evidence.',
    items: slots.map(slot => ({ slot, headline: 'Synthetic test placement',
      description: 'Synthetic metadata for repository tests only.', button: 'View product',
      alt: 'Synthetic placement asset', url: 'https://example.com/product' })) };
}
function addSyntheticFiles(native, id, slots) {
  // Deliberately not an image-upload test: these one-byte blobs exercise database state only.
  for (const role of ['logo', ...slots]) {
    const spec = AD_ASSET_SPECS[role];
    native.prepare('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)').run(
      crypto.randomUUID(), id, role, 'image/png', spec.width, spec.height, 1, 'b'.repeat(64), Buffer.from('x'));
  }
}
const approval = { reviewer: 'sandbox-reviewer', decision: 'approve', notes: 'Synthetic review only.',
  destinationChecked: true, claimsChecked: true };
async function approved(f, product = 'tool-primary', slots = ['tool-primary']) {
  const { order } = await f.store.createDraft(input(product, slots));
  addSyntheticFiles(f.native, order.id, slots);
  await f.store.submitDraft(order.id);
  return f.store.review(order.id, approval);
}

test('development repository rejects live or unspecified environments', t => {
  const f = fixture(t);
  assert.throws(() => new AdStore(f.db, { environment: 'live' }));
  assert.throws(() => new AdStore(f.db));
  assert.equal(f.count('ad_sale_orders'), 0);
});
test('draft persists server quote and hashed access, without a payment', async t => {
  const f = fixture(t); await f.store.ready();
  const created = await f.store.createDraft(input());
  assert.equal(created.order.amount, '49.00'); assert.equal(created.order.state, 'draft');
  assert.equal(created.order.access_hash, await digest(created.accessToken));
  assert.equal(created.order.provider_order, null); assert.equal(created.order.payment_verified_at, null);
  assert.equal(f.count('ad_sale_audit'), 1);
});
test('invalid material and client prices leave no draft or audit', async t => {
  const f = fixture(t);
  await assert.rejects(f.store.createDraft({ ...input(), amount: '0.01' }));
  await assert.rejects(f.store.createDraft({ ...input(), rightsConfirmed: false }));
  assert.equal(f.count('ad_sale_orders'), 0); assert.equal(f.count('ad_sale_audit'), 0);
});
test('missing assets cannot submit, review or reserve', async t => {
  const f = fixture(t), { order } = await f.store.createDraft(input());
  await assert.rejects(f.store.submitDraft(order.id));
  await assert.rejects(f.store.review(order.id, approval));
  await assert.rejects(f.store.reserveReviewedOrder(order.id));
  assert.equal((await f.store.get(order.id)).state, 'draft');
});
test('complete metadata submits, locks assets, receives review and reserves before payment', async t => {
  const f = fixture(t), order = await approved(f);
  assert.throws(() => f.native.prepare('UPDATE ad_sale_files SET sha256=? WHERE order_id=?').run('c'.repeat(64), order.id));
  const reserved = await f.store.reserveReviewedOrder(order.id);
  assert.equal(reserved.state, 'approved'); assert.equal(f.count('ad_sale_holds'), 1);
  assert.equal(reserved.provider_order, null); assert.equal(reserved.payment_verified_at, null);
});
test('approval requires explicit destination and claims checks', async t => {
  const f = fixture(t), { order } = await f.store.createDraft(input());
  addSyntheticFiles(f.native, order.id, ['tool-primary']); await f.store.submitDraft(order.id);
  await assert.rejects(f.store.review(order.id, { ...approval, destinationChecked: false }));
  await assert.rejects(f.store.review(order.id, { ...approval, claimsChecked: false }));
  assert.equal((await f.store.get(order.id)).state, 'submitted');
});
test('revision returns submitted material to a draft rather than approval', async t => {
  const f = fixture(t), { order } = await f.store.createDraft(input());
  addSyntheticFiles(f.native, order.id, ['tool-primary']); await f.store.submitDraft(order.id);
  const revised = await f.store.review(order.id, { ...approval, decision: 'revise' });
  assert.equal(revised.state, 'draft'); assert.equal(revised.approved_by, null);
  f.native.prepare('UPDATE ad_sale_files SET sha256=? WHERE order_id=?').run('c'.repeat(64), order.id);
});
test('unavailable bundle leaves every new bundle position unreserved', async t => {
  const f = fixture(t), first = await approved(f);
  await f.store.reserveReviewedOrder(first.id);
  const bundle = await approved(f, 'P2', ['tool-primary', 'buyer-intent-top']);
  await assert.rejects(f.store.reserveReviewedOrder(bundle.id));
  assert.equal(f.native.prepare('SELECT count(*) AS n FROM ad_sale_holds WHERE order_id=?').get(bundle.id).n, 0);
  assert.equal((await f.store.get(bundle.id)).hold_until, null);
});
test('concurrent fixed-position reservations cannot oversell', async t => {
  const f = fixture(t), left = await approved(f), right = await approved(f);
  const results = await Promise.allSettled([f.store.reserveReviewedOrder(left.id), f.store.reserveReviewedOrder(right.id)]);
  assert.equal(results.filter(result => result.status === 'fulfilled').length, 1);
  assert.equal(f.count('ad_sale_holds'), 1);
});
test('rotation accepts three reviewed orders and rejects the fourth', async t => {
  const f = fixture(t);
  for (let i = 0; i < 3; i++) await f.store.reserveReviewedOrder((await approved(f, 'tool-rotation', ['tool-rotation'])).id);
  const fourth = await approved(f, 'tool-rotation', ['tool-rotation']);
  await assert.rejects(f.store.reserveReviewedOrder(fourth.id));
  assert.equal((await f.store.availability()).find(slot => slot.id === 'tool-rotation').available, 0);
});
test('concurrent review decisions commit only one decision and one review audit', async t => {
  const f = fixture(t), { order } = await f.store.createDraft(input());
  addSyntheticFiles(f.native, order.id, ['tool-primary']); await f.store.submitDraft(order.id);
  const results = await Promise.allSettled([f.store.review(order.id, approval), f.store.review(order.id, { ...approval, decision: 'reject' })]);
  assert.equal(results.filter(result => result.status === 'fulfilled').length, 1);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE order_id=? AND action LIKE 'review_%'").get(order.id).n, 1);
});
test('reservation retry returns the existing hold without duplicating it', async t => {
  const f = fixture(t), order = await approved(f);
  const first = await f.store.reserveReviewedOrder(order.id);
  const second = await f.store.reserveReviewedOrder(order.id);
  assert.equal(second.hold_until, first.hold_until); assert.equal(f.count('ad_sale_holds'), 1);
});
test('expired uncharged reservations are reclaimed for a reviewed order', async t => {
  const f = fixture(t), first = await approved(f);
  await f.store.reserveReviewedOrder(first.id, 1); f.advance(120000);
  const second = await approved(f); await f.store.reserveReviewedOrder(second.id);
  assert.equal(f.count('ad_sale_holds'), 1);
  assert.equal(f.native.prepare('SELECT order_id FROM ad_sale_holds').get().order_id, second.id);
});


test('approval rejects missing, false, or nonboolean confirmation values without an approval audit', async t => {
  const f = fixture(t), { order } = await f.store.createDraft(input());
  addSyntheticFiles(f.native, order.id, ['tool-primary']); await f.store.submitDraft(order.id);
  const auditBefore = f.count('ad_sale_audit');
  for (const field of ['destinationChecked', 'claimsChecked']) {
    const missing = { ...approval }; delete missing[field];
    await assert.rejects(f.store.review(order.id, missing), /Confirm/);
    for (const value of [false, undefined, null, 0, 1, 'true', {}, []]) {
      await assert.rejects(f.store.review(order.id, { ...approval, [field]: value }), /Confirm/);
    }
  }
  assert.equal((await f.store.get(order.id)).state, 'submitted');
  assert.equal(f.count('ad_sale_audit'), auditBefore);
});

test('concurrent submissions leave one transition and one submission audit', async t => {
  const f = fixture(t), { order } = await f.store.createDraft(input());
  addSyntheticFiles(f.native, order.id, ['tool-primary']);
  const results = await Promise.allSettled([f.store.submitDraft(order.id), f.store.submitDraft(order.id)]);
  assert.equal(results.filter(result => result.status === 'fulfilled').length, 1);
  assert.equal((await f.store.get(order.id)).state, 'submitted');
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE order_id=? AND action='submission_requested'").get(order.id).n, 1);
});

test('same-order concurrent reservation retries both return the single committed reservation', async t => {
  const f = fixture(t), order = await approved(f);
  const results = await Promise.allSettled([
    f.store.reserveReviewedOrder(order.id), f.store.reserveReviewedOrder(order.id),
  ]);
  assert.equal(results.filter(result => result.status === 'fulfilled').length, 2);
  assert.equal(results[0].value.hold_until, results[1].value.hold_until);
  assert.equal(f.count('ad_sale_holds'), 1);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE order_id=? AND action='positions_reserved'").get(order.id).n, 1);
});

test('rotating-position reservation reuse preserves expiry and audit after clock advances', async t => {
  const f = fixture(t), order = await approved(f, 'tool-rotation', ['tool-rotation']);
  const first = await f.store.reserveReviewedOrder(order.id);
  const originalHolds = f.native.prepare('SELECT slot,lane,expires_at FROM ad_sale_holds WHERE order_id=? ORDER BY slot').all(order.id);
  f.advance(60000);
  const second = await f.store.reserveReviewedOrder(order.id, 60);
  assert.equal(second.hold_until, first.hold_until);
  assert.deepEqual(f.native.prepare('SELECT slot,lane,expires_at FROM ad_sale_holds WHERE order_id=? ORDER BY slot').all(order.id), originalHolds);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE order_id=? AND action='positions_reserved'").get(order.id).n, 1);
});

test('bundle reservation reuse preserves every original hold and the original expiry', async t => {
  const f = fixture(t), order = await approved(f, 'P2', ['tool-primary', 'buyer-intent-top']);
  const first = await f.store.reserveReviewedOrder(order.id);
  const originalHolds = f.native.prepare('SELECT slot,lane,expires_at FROM ad_sale_holds WHERE order_id=? ORDER BY slot').all(order.id);
  assert.equal(originalHolds.length, 2);
  f.advance(60000);
  const second = await f.store.reserveReviewedOrder(order.id, 60);
  assert.equal(second.hold_until, first.hold_until);
  assert.deepEqual(f.native.prepare('SELECT slot,lane,expires_at FROM ad_sale_holds WHERE order_id=? ORDER BY slot').all(order.id), originalHolds);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE order_id=? AND action='positions_reserved'").get(order.id).n, 1);
});

test('expired active holds remain unavailable until lifecycle expiry removes them', async t => {
  const f = fixture(t), order = await approved(f);
  await f.store.reserveReviewedOrder(order.id);
  const at = f.store.now(), ends = new Date(Date.parse(at) + 30 * 86400000).toISOString();
  // Synthetic, local state fixture only: no provider request or payment evidence is claimed.
  f.native.prepare("UPDATE ad_sale_orders SET state='checkout',provider_order=?,merchant_id=?,payment_environment='sandbox' WHERE id=?")
    .run('SYNTHETIC-ORDER', 'SYNTHETIC-MERCHANT', order.id);
  f.native.prepare("UPDATE ad_sale_orders SET state='capturing' WHERE id=?").run(order.id);
  f.native.prepare('UPDATE ad_sale_holds SET expires_at=? WHERE order_id=?').run(ends, order.id);
  f.native.prepare("UPDATE ad_sale_orders SET state='active',capture_id=?,payment_verified_at=?,starts_at=?,ends_at=? WHERE id=?")
    .run('SYNTHETIC-CAPTURE', at, at, ends, order.id);
  f.advance(31 * 86400000);
  assert.equal((await f.store.availability()).find(slot => slot.id === 'tool-primary').available, 0);
  const waiting = await approved(f);
  await assert.rejects(f.store.reserveReviewedOrder(waiting.id), /unavailable/);
  assert.equal(f.count('ad_sale_holds'), 1);
  // Simulate the lifecycle service's ended + hold deletion transaction; this test does not test that service.
  await f.db.batch([
    f.store.q("UPDATE ad_sale_orders SET state='ended' WHERE id=?", order.id),
    f.store.q('DELETE FROM ad_sale_holds WHERE order_id=?', order.id),
  ]);
  assert.equal((await f.store.availability()).find(slot => slot.id === 'tool-primary').available, 1);
});

test('a state change between reservation read and batch leaves no new hold or reservation audit', async t => {
  const f = fixture(t), order = await approved(f, 'P2', ['tool-primary', 'buyer-intent-top']);
  const batch = f.db.batch.bind(f.db);
  let intercepted = false;
  f.db.batch = async statements => {
    if (!intercepted) {
      intercepted = true;
      f.native.prepare("UPDATE ad_sale_orders SET state='cancelled' WHERE id=?").run(order.id);
    }
    return batch(statements);
  };
  await assert.rejects(f.store.reserveReviewedOrder(order.id));
  assert.equal(intercepted, true);
  assert.equal((await f.store.get(order.id)).state, 'cancelled');
  assert.equal((await f.store.get(order.id)).hold_until, null);
  assert.equal(f.native.prepare('SELECT count(*) AS n FROM ad_sale_holds WHERE order_id=?').get(order.id).n, 0);
  assert.equal(f.native.prepare("SELECT count(*) AS n FROM ad_sale_audit WHERE order_id=? AND action='positions_reserved'").get(order.id).n, 0);
});
