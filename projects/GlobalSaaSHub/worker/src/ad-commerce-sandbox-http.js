// Isolated development handler. Deliberately not imported by index.js or a deployment config.
import { AdError, digest } from './ad-commerce-domain.js';
import { CATALOG_VERSION, IMAGE_SLOTS, IMAGE_BUNDLES } from './ad-commerce-catalog.js';
import { AD_ASSET_SPECS } from './ad-asset-specs.js';
import { validateAdAsset } from './ad-commerce-assets.js';
import { inspectSandboxReturn } from './ad-commerce-checkout-return.js';
import { renderSandboxReturn } from './ad-commerce-sandbox-return-page.js';

const headers = {
  'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer',
  'Content-Security-Policy': "default-src 'none'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
};
const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { ...headers, 'Content-Type': 'application/json; charset=utf-8' },
});
const escapeHtml = value => String(value).replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

async function boundedBody(request, limit) {
  const declared = request.headers.get('content-length');
  if (declared && (!/^\d+$/.test(declared) || Number(declared) > limit)) throw new AdError('Request is too large.', 413);
  const reader = request.body?.getReader();
  if (!reader) return new Uint8Array();
  const chunks = []; let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > limit) { await reader.cancel(); throw new AdError('Request is too large.', 413); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  return bytes;
}
async function bodyJson(request) {
  if (request.headers.get('content-type')?.split(';')[0] !== 'application/json') throw new AdError('JSON is required.', 415);
  try { return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(await boundedBody(request, 32768))); }
  catch (error) {
    if (error instanceof AdError) throw error;
    throw new AdError('Invalid JSON.');
  }
}
function ownerView(order) {
  const { access_hash, email, ...safe } = order;
  return safe;
}
const bearer = request => /^Bearer ([A-Za-z0-9_-]+)$/.exec(request.headers.get('authorization') || '')?.[1];

export function createAdSandboxHandler({ store, payments, webhooks, reviewKey, environment, origin }) {
  const base = new URL(origin);
  if (environment !== 'sandbox' || !['127.0.0.1', 'localhost', '[::1]'].includes(base.hostname) ||
      base.protocol !== 'http:' || base.origin !== origin || typeof reviewKey !== 'string' || reviewKey.length < 32) {
    throw new AdError('An isolated loopback sandbox and a separate reviewer key are required.', 503);
  }
  const reviewHash = digest(reviewKey);
  async function owner(request, id) {
    const token = bearer(request), order = await store.get(id);
    if (!token || !order || await digest(token) !== order.access_hash) throw new AdError('Order access denied.', 403);
    return order;
  }
  async function admin(request) {
    const token = bearer(request);
    if (!token || await digest(token) !== await reviewHash) throw new AdError('Reviewer access denied.', 403);
  }
  async function visibleOrder(id) {
    return store.q(`SELECT * FROM ad_sale_orders WHERE id=? AND state='active'
      AND payment_environment='sandbox' AND payment_verified_at IS NOT NULL
      AND starts_at<=? AND ends_at>?
      AND NOT EXISTS (SELECT 1 FROM ad_sale_events e WHERE e.environment='sandbox'
        AND (e.provider_order=ad_sale_orders.provider_order OR EXISTS
          (SELECT 1 FROM json_each(e.capture_ids_json) WHERE value=ad_sale_orders.capture_id))
        AND (e.event_type IN('PAYMENT.CAPTURE.REFUNDED','PAYMENT.CAPTURE.REVERSED','CHECKOUT.PAYMENT-APPROVAL.REVERSED')
          OR e.event_type LIKE 'CUSTOMER.DISPUTE.%'))`, id, store.now(), store.now()).first();
  }
  async function placements(slot) {
    if (!IMAGE_SLOTS.some(item => item.id === slot)) throw new AdError('Unknown position.', 404);
    const at = store.now();
    const result = await store.q(`SELECT o.id FROM ad_sale_orders o JOIN ad_sale_holds h ON h.order_id=o.id
      WHERE h.slot=? AND h.expires_at>? AND o.state='active' ORDER BY o.id`, slot, at).all();
    const rows = [];
    for (const entry of result.results) {
      const order = await visibleOrder(entry.id);
      if (!order) continue;
      const item = JSON.parse(order.materials_json).items.find(item => item.slot === slot);
      if (!item) continue;
      rows.push({ id: order.id, slot, label: 'Sponsored — SANDBOX TEST', company: order.company,
        productName: order.product_name, ...item, environment: 'sandbox',
        imageUrl: '/sandbox/assets/' + order.id + '/' + slot,
        logoUrl: '/sandbox/assets/' + order.id + '/logo', startsAt: order.starts_at, endsAt: order.ends_at });
    }
    return rows;
  }
  return async function handle(request) {
    try {
      const url = new URL(request.url);
      if (url.origin !== origin) throw new AdError('Sandbox origin mismatch.', 403);
      if (url.pathname === '/sandbox/webhooks/paypal' && request.method === 'POST') {
        return webhooks ? webhooks.handle(request) : json({ error: 'Sandbox webhook verifier is not configured.' }, 503);
      }
      if (url.pathname === '/sandbox/checkout-return' && request.method === 'GET') {
        const order = await store.get(url.searchParams.get('order'));
        if (!order) throw new AdError('Checkout return access denied.', 403);
        const view = await inspectSandboxReturn(request, order, { origin, now: store.clock().getTime() });
        return renderSandboxReturn(view);
      }
      if (request.headers.has('origin') && request.headers.get('origin') !== origin) throw new AdError('Cross-origin access is disabled.', 403);
      if (!['GET', 'HEAD'].includes(request.method) && request.headers.get('origin') !== origin) {
        throw new AdError('A matching sandbox origin is required.', 403);
      }
      const parts = url.pathname.split('/').filter(Boolean).map(decodeURIComponent);
      if (parts[0] !== 'sandbox') return json({ error: 'Not found.' }, 404);
      if (request.method === 'GET' && url.pathname === '/sandbox/catalog') {
        await payments.expire();
        return json({ environment: 'sandbox', version: CATALOG_VERSION, availability: await store.availability(), slots: IMAGE_SLOTS,
          bundles: IMAGE_BUNDLES, assetSpecs: AD_ASSET_SPECS, supportedUploadMimes: ['image/png'] });
      }
      if (request.method === 'POST' && url.pathname === '/sandbox/orders') {
        const result = await store.createDraft(await bodyJson(request));
        return json({ order: ownerView(result.order), accessToken: result.accessToken }, 201);
      }
      if (request.method === 'POST' && url.pathname === '/sandbox/admin/expire') {
        await admin(request);
        return json({ expired: await payments.expire() });
      }
      if (parts[1] === 'admin' && parts[2] === 'orders' && request.method === 'GET') {
        await admin(request);
        const order = await store.get(parts[3]);
        if (!order) throw new AdError('Order not found.', 404);
        if (parts.length === 4) return json({ order: ownerView(order), files: await store.files(order.id) });
        if (parts.length === 6 && parts[4] === 'assets') {
          const file = await store.q('SELECT mime,data FROM ad_sale_files WHERE order_id=? AND role=?', order.id, parts[5]).first();
          if (!file) throw new AdError('File not found.', 404);
          return new Response(file.data, { headers: { ...headers, 'Content-Type': file.mime } });
        }
      }
      if (parts.length === 5 && parts[1] === 'admin' && parts[2] === 'orders' && parts[4] === 'review' && request.method === 'POST') {
        await admin(request);
        const input = await bodyJson(request);
        // Actor identity is supplied by this authenticated endpoint, never by applicant JSON.
        return json({ order: ownerView(await store.review(parts[3], { ...input, reviewer: 'sandbox-reviewer' })) });
      }
      if (parts[1] === 'orders' && parts.length >= 3) {
        const id = parts[2], order = await owner(request, id);
        if (parts.length === 3 && request.method === 'GET') return json({ order: ownerView(order), files: await store.files(id) });
        if (parts.length === 5 && parts[3] === 'assets' && request.method === 'PUT') {
          await store.requireState(id, ['draft']);
          const role = parts[4], spec = AD_ASSET_SPECS[role];
          if (!spec || !['logo', ...JSON.parse(order.quote_json).slots].includes(role)) throw new AdError('Unexpected file role.');
          const bytes = await boundedBody(request, spec.maxBytes);
          if (request.headers.get('content-type') !== 'image/png') throw new AdError('This sandbox accepts validated PNG files only.', 415);
          let file;
          try { file = await validateAdAsset(role, request.headers.get('content-type'), bytes); }
          catch { throw new AdError('The PNG file is invalid or does not match this position.', 422); }
          await store.requireState(id, ['draft']);
          await store.db.batch([store.q(`INSERT INTO ad_sale_files
            (id,order_id,role,mime,width,height,byte_size,sha256,data) VALUES(?,?,?,?,?,?,?,?,?)
            ON CONFLICT(order_id,role) DO UPDATE SET mime=excluded.mime,width=excluded.width,height=excluded.height,
              byte_size=excluded.byte_size,sha256=excluded.sha256,data=excluded.data`,
            crypto.randomUUID(), id, role, file.mime, file.width, file.height, file.byte_size, file.sha256, file.data)]);
          return json({ files: await store.files(id) });
        }
        if (parts.length === 4 && request.method === 'POST') {
          let result;
          if (parts[3] === 'submit') result = { order: await store.submitDraft(id) };
          else if (parts[3] === 'reserve') { await payments.expire(); result = { order: await store.reserveReviewedOrder(id) }; }
          else if (parts[3] === 'checkout') result = await payments.checkout(id);
          else if (parts[3] === 'capture') result = { order: await payments.capture(id) };
          else if (parts[3] === 'reconcile') result = { order: await payments.reconcile(id) };
          else return json({ error: 'Not found.' }, 404);
          return json({ ...result, order: ownerView(result.order) });
        }
      }
      if (parts.length === 3 && parts[1] === 'placements' && request.method === 'GET') {
        return json({ environment: 'sandbox', placements: await placements(parts[2]) });
      }
      if (parts.length === 4 && parts[1] === 'assets' && request.method === 'GET') {
        const order = await visibleOrder(parts[2]);
        if (!order) return json({ error: 'No active advertisement.' }, 404);
        const file = await store.q('SELECT mime,data FROM ad_sale_files WHERE order_id=? AND role=?', parts[2], parts[3]).first();
        if (!file) return json({ error: 'File not found.' }, 404);
        return new Response(file.data, { headers: { ...headers, 'Content-Type': file.mime } });
      }
      if (parts.length === 3 && parts[1] === 'preview' && request.method === 'GET') {
        const rows = await placements(parts[2]);
        const selected = rows.length ? rows[Math.floor(store.clock().getTime() / 10000) % rows.length] : null;
        const body = selected ? `<article><p>${escapeHtml(selected.label)}</p><img width="400" src="${escapeHtml(selected.imageUrl)}" alt="${escapeHtml(selected.alt)}">
          <h2>${escapeHtml(selected.headline)}</h2><p>${escapeHtml(selected.description)}</p>
          <a href="${escapeHtml(selected.url)}" rel="sponsored nofollow noopener noreferrer">${escapeHtml(selected.button)}</a></article>` :
          '<p>No active sandbox advertisement.</p>';
        const nonce = crypto.randomUUID().replaceAll('-', '');
        const timer = selected ? '<script nonce="' + nonce + '">const remainingAtRender=' + JSON.stringify(Math.max(0, Date.parse(selected.endsAt) - store.clock().getTime())) + ';const end=Date.now()+remainingAtRender' +
          ';function check(){const remaining=end-Date.now();if(remaining<=0){document.querySelector("article")?.remove();document.getElementById("status").textContent="Sandbox advertising period ended.";}else{setTimeout(check,Math.min(remaining,60000));}}check();</script>' : '';
        return new Response('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>COSHUMA sandbox verification</title><h1>Local test preview</h1><p id="status"></p>' + body + timer + '</html>',
          { headers: { ...headers, 'Content-Type': 'text/html; charset=utf-8',
            'Content-Security-Policy': headers['Content-Security-Policy'] + "; script-src 'nonce-" + nonce + "'" } });
      }
      return json({ error: 'Not found.' }, 404);
    } catch (error) {
      return json({ error: error instanceof AdError ? error.message : 'Sandbox operation failed.' },
        error instanceof AdError ? error.status : 500);
    }
  };
}
