// Loopback-only browser fixture: synthetic PayPal, actual PNG bytes, memory databases.
// Run: node test/ad-commerce-browser-preview.mjs. No production config or credentials are loaded.
import { createServer } from 'node:http';
import { Readable } from 'node:stream';
import { readFileSync } from 'node:fs';
import { createAdSandboxHandler } from '../src/ad-commerce-sandbox-http.js';
import { SandboxAdPayments } from '../src/ad-commerce-sandbox-payments.js';
import { SandboxAdWebhooks } from '../src/ad-commerce-sandbox-webhooks.js';
import { AD_ASSET_SPECS } from '../src/ad-asset-specs.js';
import { memoryStore, syntheticInput, png, syntheticPayPal, TEST_REVIEW_KEY, TEST_ENV } from './helpers/ad-commerce-fixtures.js';
globalThis.fetch = async () => { throw new Error('External network is disabled in this browser fixture.'); };
const fixtures = [], stages = [], modes = new Map();
let origin, interactive;
function createFixture() {
  const f = memoryStore(), provider = syntheticPayPal();
  let shift = 0;
  f.store.clock = () => new Date(Date.now() + shift);
  f.advance = ms => { shift += ms; };
  fixtures.push(f);
  const payments = new SandboxAdPayments(f.store, { env: TEST_ENV, fetchImpl: provider.fetchImpl });
  const webhooks = new SandboxAdWebhooks(f.store, payments, { env: { ...TEST_ENV, PAYPAL_WEBHOOK_ID: 'SYNTHETIC-WEBHOOK' }, fetchImpl: provider.fetchImpl });
  const handle = createAdSandboxHandler({ store: f.store, payments, webhooks, reviewKey: TEST_REVIEW_KEY, environment: 'sandbox', origin });
  return { ...f, provider, payments, handle };
}
async function seed(mode) {
  const f = createFixture(), handle = f.handle;
  const call = async (method, path, token, body, bytes) => {
    const response = await handle(new Request(origin + '/sandbox' + path, { method,
      headers: { Origin: origin, ...(token ? { Authorization: 'Bearer ' + token } : {}),
        ...(bytes ? { 'Content-Type': 'image/png' } : body ? { 'Content-Type': 'application/json' } : {}) },
      body: bytes || (body ? JSON.stringify(body) : undefined) }));
    if (!response.ok) throw new Error('Synthetic setup failed at ' + path + ': ' + await response.text());
    return response.json();
  };
  await call('GET', '/catalog');
  const c = await call('POST', '/orders', null, syntheticInput()), id = c.order.id, token = c.accessToken;
  for (const role of ['logo', 'tool-primary']) {
    const spec = AD_ASSET_SPECS[role];
    await call('PUT', '/orders/' + id + '/assets/' + role, token, null, png(spec.width, spec.height));
  }
  await call('POST', '/orders/' + id + '/submit', token);
  await call('POST', '/admin/orders/' + id + '/review', TEST_REVIEW_KEY,
    { decision: 'approve', notes: 'Synthetic browser fixture review.', destinationChecked: true, claimsChecked: true });
  await call('POST', '/orders/' + id + '/reserve', token);
  const checkout = await call('POST', '/orders/' + id + '/checkout', token);
  f.provider.approve(checkout.order.provider_order);
  await call('POST', '/orders/' + id + '/capture', token);
  if (mode === 'demo-ended') { f.advance(30 * 86400000); await call('POST', '/admin/expire', TEST_REVIEW_KEY); }
  stages.push({ fixture: mode, source: 'synthetic handler and mock PayPal',
    state: (await f.store.get(id)).state, providerNetworkRequests: 0 });
  return f;
}
const localHeaders = { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
  'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'" };
const server = createServer(async (req, res) => {
  try {
    if (req.headers.host !== new URL(origin).host) { res.writeHead(403); res.end(); return; }
    const url = new URL(req.url, origin);
    const staticFiles = new Map([
      ['/', ['ad-commerce-sandbox-page.html', 'text/html; charset=utf-8']],
      ['/fixture-page.js', ['ad-commerce-sandbox-page.js', 'text/javascript; charset=utf-8']],
      ['/fixture-style.css', ['../../public/advertiser-showcase.css', 'text/css; charset=utf-8']],
    ]);
    if (req.method === 'GET' && staticFiles.has(url.pathname)) {
      const [file, mime] = staticFiles.get(url.pathname);
      res.writeHead(200, { ...localHeaders, 'Content-Type': mime }); res.end(readFileSync(new URL(file, import.meta.url))); return;
    }
    if (req.method === 'GET' && url.pathname === '/test-report') {
      res.writeHead(200, { ...localHeaders, 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ stages, actualPayPalSandboxVerified: false, productionModified: false }, null, 2)); return;
    }
    if (url.pathname.startsWith('/fixture/')) {
      if (req.method !== 'POST' || req.headers.origin !== origin) { res.writeHead(403); res.end(); return; }
      if (url.pathname.startsWith('/fixture/approve/')) interactive.provider.approve(decodeURIComponent(url.pathname.slice('/fixture/approve/'.length)));
      else if (url.pathname === '/fixture/expire') { interactive.advance(30 * 86400000); await interactive.payments.expire(); }
      else { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { ...localHeaders, 'Content-Type': 'application/json' }); res.end(JSON.stringify({ syntheticOnly: true, ok: true })); return;
    }
    const prefix = url.pathname.split('/')[1];
    if (prefix === 'demo-near-end' && !modes.has(prefix)) {
      const near = await seed(prefix); near.advance(30 * 86400000 - 10000); modes.set(prefix, near);
    }
    const f = modes.get(prefix);
    let path = f ? url.pathname.slice(prefix.length + 1) : url.pathname;
    if (f && path === '') path = '/sandbox/preview/tool-primary';
    const request = new Request(origin + path + url.search, { method: req.method, headers: req.headers,
      ...(!['GET', 'HEAD'].includes(req.method) ? { body: Readable.toWeb(req), duplex: 'half' } : {}) });
    const response = await (f || interactive).handle(request);
    res.writeHead(response.status, Object.fromEntries(response.headers));
    if (f && response.headers.get('content-type')?.startsWith('text/html')) {
      res.end((await response.text()).replaceAll('/sandbox/assets/', '/' + prefix + '/sandbox/assets/'));
    } else res.end(Buffer.from(await response.arrayBuffer()));
  } catch { res.writeHead(500); res.end('Local fixture failed.'); }
});
server.listen(0, '127.0.0.1', async () => {
  origin = 'http://127.0.0.1:' + server.address().port;
  try {
    interactive = createFixture();
    modes.set('demo-active', await seed('demo-active'));
    modes.set('demo-ended', await seed('demo-ended'));
    console.log('LOCAL_SYNTHETIC_PREVIEW=' + origin);
  } catch (error) { console.error(error.message); server.close(); for (const f of fixtures) f.close(); process.exitCode = 1; }
});
function close() { server.close(() => { for (const f of fixtures) f.close(); }); }
process.on('SIGINT', close); process.on('SIGTERM', close);
