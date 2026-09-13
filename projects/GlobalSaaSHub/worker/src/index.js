import { handlePrivateOps, handleSnapshotUpload } from './private-ops.js';
import { captureIsVerifiedPaid, providerOrderIdFromWebhook, validatePaidWebhook, webhookTarget } from './domain.js';
import { capturePayPalOrder, createPayPalOrder, getPayPalOrder, verifyPayPalWebhook } from './paypal.js';
import { D1OrderRepository } from './repository.js';
import { handleAdminRequest, isAdminPath } from './admin.js';

const SECURITY_HEADERS = {
  'cache-control': 'no-store',
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'no-referrer',
  'x-frame-options': 'DENY',
  'cross-origin-resource-policy': 'same-origin',
  'permissions-policy': 'camera=(), microphone=(), geolocation=(), payment=()',
  'content-security-policy': "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
};

const json = (body, status = 200, extra = {}) => new Response(JSON.stringify(body), {
  status,
  headers: { 'content-type': 'application/json; charset=utf-8', ...SECURITY_HEADERS, ...extra },
});

function corsHeaders(request, env) {
  const origin = request.headers.get('origin');
  if (!origin || origin !== env.ALLOWED_ORIGIN) return {};
  return { 'access-control-allow-origin': origin, vary: 'Origin' };
}

function isAllowedBrowserRequest(request, env) {
  return Boolean(env.ALLOWED_ORIGIN && request.headers.get('origin') === env.ALLOWED_ORIGIN);
}

function hasSafeJsonBody(request) {
  const contentType = request.headers.get('content-type') || '';
  const contentLength = Number(request.headers.get('content-length') || 0);
  return contentType.toLowerCase().startsWith('application/json')
    && Number.isFinite(contentLength)
    && contentLength >= 0
    && contentLength <= 4096;
}

function configured(env) {
  return env.CHECKOUT_ENABLED === 'true'
    && Boolean(env.ORDERS && env.ALLOWED_ORIGIN && env.PAYPAL_CLIENT_ID && env.PAYPAL_CLIENT_SECRET && env.PAYPAL_WEBHOOK_ID);
}

async function createOrder(request, env, repo) {
  if (!isAllowedBrowserRequest(request, env)) return json({ error: 'Forbidden' }, 403);
  if (!hasSafeJsonBody(request)) return json({ error: 'Invalid request' }, 415, corsHeaders(request, env));
  // The request body is intentionally ignored: price and currency are server-owned constants.
  await request.json().catch(() => ({}));
  const internalId = crypto.randomUUID();
  const provider = await createPayPalOrder(env, `create-${internalId}`);
  await repo.create({ id: internalId, providerOrderId: provider.id, now: new Date().toISOString() });
  await repo.transition(provider.id, provider.status === 'CREATED' ? 'pending' : 'created', new Date().toISOString());
  return json({ orderId: provider.id, status: 'pending' }, 201, corsHeaders(request, env));
}

async function captureOrder(request, env, repo) {
  if (!isAllowedBrowserRequest(request, env)) return json({ error: 'Forbidden' }, 403);
  if (!hasSafeJsonBody(request)) return json({ error: 'Invalid request' }, 415, corsHeaders(request, env));
  const { orderId } = await request.json();
  if (typeof orderId !== 'string' || !orderId || orderId.length > 128) return json({ error: 'orderId is required' }, 400, corsHeaders(request, env));
  const local = await repo.getByProviderOrderId(orderId);
  if (!local) return json({ error: 'Order not found' }, 404, corsHeaders(request, env));
  await capturePayPalOrder(env, orderId, `capture-${local.id}`);
  const verified = await getPayPalOrder(env, orderId);
  if (!captureIsVerifiedPaid(verified)) {
    return json({ orderId, status: local.status, verified: false }, 409, corsHeaders(request, env));
  }
  const updated = await repo.transition(orderId, 'paid', new Date().toISOString());
  return json({ orderId, status: updated.status, verified: true }, 200, corsHeaders(request, env));
}

async function webhook(request, env, repo) {
  if (!hasSafeJsonBody(request)) return json({ error: 'Invalid request' }, 415);
  const event = await request.json();
  if (!event?.id) return json({ error: 'Invalid webhook event' }, 400);
  const verification = await verifyPayPalWebhook(env, request.headers, event);
  if (verification.verification_status !== 'SUCCESS') return json({ error: 'Webhook signature verification failed' }, 401);
  validatePaidWebhook(event);

  const claimed = await repo.claimWebhook(event.id, event.event_type, new Date().toISOString());
  if (!claimed) return json({ accepted: true, duplicate: true });
  try {
    const target = webhookTarget(event);
    const providerOrderId = providerOrderIdFromWebhook(event);
    if (target && providerOrderId) await repo.transition(providerOrderId, target, new Date().toISOString());
    await repo.completeWebhook(event.id, new Date().toISOString());
    return json({ accepted: true, duplicate: false });
  } catch (error) {
    await repo.releaseWebhook(event.id);
    throw error;
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/internal/analytics-snapshot') return handleSnapshotUpload(request, env);
    if (url.pathname === '/ops' || url.pathname.startsWith('/ops/')) return handlePrivateOps(request, env);
    if (isAdminPath(url, env)) return handleAdminRequest(request, env);
    if (url.pathname === '/robots.txt') {
      const privatePath = String(env.ADMIN_PATH || '/ops-private').replace(/\/$/, '');
      return new Response(`User-agent: *\nDisallow: ${privatePath}/\n`, {
        headers: { 'content-type': 'text/plain; charset=utf-8', 'x-robots-tag': 'noindex, nofollow', ...SECURITY_HEADERS },
      });
    }
    if (request.method === 'OPTIONS') {
      if (!isAllowedBrowserRequest(request, env)) return new Response(null, { status: 403, headers: SECURITY_HEADERS });
      return new Response(null, { status: 204, headers: {
        ...SECURITY_HEADERS,
        ...corsHeaders(request, env),
        'access-control-allow-methods': 'POST, OPTIONS',
        'access-control-allow-headers': 'content-type',
        'access-control-max-age': '600',
      } });
    }
    if (url.pathname === '/health') return json({ ok: true });
    if (!configured(env)) return json({ error: 'Checkout is unavailable' }, 503, corsHeaders(request, env));
    const repo = new D1OrderRepository(env.ORDERS);
    try {
      if (request.method === 'POST' && url.pathname === '/v1/orders') return await createOrder(request, env, repo);
      if (request.method === 'POST' && url.pathname === '/v1/orders/capture') return await captureOrder(request, env, repo);
      if (request.method === 'POST' && url.pathname === '/v1/webhooks/paypal') return await webhook(request, env, repo);
      return json({ error: 'Not found' }, 404, corsHeaders(request, env));
    } catch (error) {
      console.error('Payment request failed safely', error?.name || 'Error');
      return json({ error: 'Payment request failed safely' }, 502, corsHeaders(request, env));
    }
  },
};
