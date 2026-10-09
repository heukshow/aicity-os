// Process-replacement fixture. Real disk SQLite; payment responses are strictly synthetic.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { openTestStore } from './ad-commerce-disk-adapter.js';
import { syntheticInput, syntheticPayPal, png, TEST_ENV } from './ad-commerce-fixtures.js';
import { AD_ASSET_SPECS } from '../../src/ad-asset-specs.js';
import { validateAdAsset } from '../../src/ad-commerce-assets.js';
import { SandboxAdPayments } from '../../src/ad-commerce-sandbox-payments.js';
const [action, dbPath, providerPath, product = 'tool-primary'] = process.argv.slice(2);
if (!dbPath?.endsWith('.ad-sandbox.sqlite') || !providerPath?.endsWith('.synthetic-provider.json') || dirname(dbPath) !== dirname(providerPath)) throw new Error('Explicit paired temporary fixtures required.');
globalThis.fetch = () => { throw new Error('Actual network is forbidden in restart tests.'); };
const f = openTestStore(dbPath, { initialize: action === 'prepare' });
const provider = syntheticPayPal();
const saved = existsSync(providerPath) ? JSON.parse(readFileSync(providerPath, 'utf8')) : { records: [], responses: {}, requests: [] };
for (const [key, record] of saved.records) provider.records.set(key, record);
const persistProvider = () => writeFileSync(providerPath, JSON.stringify({ ...saved, records: [...provider.records] }));
const transport = async (url, init = {}) => {
  const path = new URL(url).pathname, method = init.method || 'GET';
  const requestId = new Headers(init.headers).get('PayPal-Request-Id');
  const key = method + ':' + path + ':' + requestId;
  if (method === 'POST' && path.startsWith('/v2/') && !requestId) throw new Error('Every simulated financial POST requires idempotency.');
  if (requestId && saved.responses[key]) return new Response(JSON.stringify(saved.responses[key]));
  const response = await provider.fetchImpl(url, init);
  saved.requests.push({ path, method });
  if (requestId && response.ok) saved.responses[key] = await response.clone().json();
  persistProvider();
  // Exit after the simulated provider committed but before our application receives success.
  // The replacement process must recover without a second financial POST.
  if (action === 'capture-crash' && method === 'POST' && path.endsWith('/capture')) process.exit(71);
  return response;
};
const payments = new SandboxAdPayments(f.store, { env: TEST_ENV, fetchImpl: transport });
const summary = async extra => {
  const order = f.native.prepare('SELECT * FROM ad_sale_orders ORDER BY created_at LIMIT 1').get();
  return { action, pid: process.pid, id: order?.id, state: order?.state,
    files: order ? (await f.store.files(order.id)).length : 0,
    holds: order ? f.native.prepare('SELECT count(*) n FROM ad_sale_holds WHERE order_id=?').get(order.id).n : 0,
    captureId: order?.capture_id, providerOrder: order?.provider_order,
    startsAt: order?.starts_at, endsAt: order?.ends_at,
    verifiedAudits: f.native.prepare("SELECT count(*) n FROM ad_sale_audit WHERE action='sandbox_payment_verified'").get().n,
    createPosts: saved.requests.filter(x => x.method === 'POST' && x.path === '/v2/checkout/orders').length,
    capturePosts: saved.requests.filter(x => x.method === 'POST' && x.path.endsWith('/capture')).length,
    ...extra };
};
try {
  await f.store.ready();
  if (action === 'prepare') {
    const slots = product === 'P2' ? ['tool-primary', 'buyer-intent-top'] : [product];
    const { order } = await f.store.createDraft(syntheticInput(product, slots));
    for (const role of ['logo', ...slots]) {
      const spec = AD_ASSET_SPECS[role], file = await validateAdAsset(role, 'image/png', png(spec.width, spec.height));
      await f.store.q('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)', crypto.randomUUID(), order.id, role, file.mime,
        file.width, file.height, file.byte_size, file.sha256, file.data).run();
    }
    await f.store.submitDraft(order.id);
    await f.store.review(order.id, { reviewer: 'synthetic-reviewer', decision: 'approve', notes: 'Generated PNG and synthetic claims only.', destinationChecked: true, claimsChecked: true });
    await f.store.reserveReviewedOrder(order.id);
  } else {
    const order = f.native.prepare('SELECT * FROM ad_sale_orders ORDER BY created_at LIMIT 1').get();
    if (action === 'checkout' || action === 'checkout-crash') {
      if (action === 'checkout-crash') f.db.batch = async () => { persistProvider(); process.exit(72); };
      await payments.checkout(order.id);
    } else if (action === 'capture' || action === 'capture-crash') {
      provider.approve(order.provider_order); persistProvider();
      await payments.capture(order.id);
    } else if (action === 'recover' || action === 'recover-after-deadline') {
      if (action === 'recover-after-deadline') f.store.clock = () => new Date(Date.parse(order.hold_until) + 60000);
      await payments.reconcile(order.id);
    } else if (action === 'expired-unpaid-capture') {
      f.store.clock = () => new Date(Date.parse(order.hold_until) + 60000);
      const before = saved.requests.length;
      let refused = false;
      try { await payments.capture(order.id); } catch { refused = true; }
      if (!refused || before !== saved.requests.length) throw new Error('Expired unpaid checkout must not contact provider.');
    } else if (action === 'expire') {
      f.store.clock = () => new Date(Date.parse(order.ends_at) + 1);
      await payments.expire();
    } else if (action !== 'status') throw new Error('Unsupported fixture phase');
  }
  persistProvider();
  console.log(JSON.stringify(await summary({ realProviderRequests: 0 })));
} finally { f.close(); }
