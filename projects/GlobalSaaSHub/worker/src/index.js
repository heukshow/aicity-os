import { handlePrivateOps, handleSnapshotUpload } from './private-ops.js';
import { handleSponsorshipRequest } from './sponsorship.js';
import { handleImageAdRequest, maintainImageAds } from './ad-sales.js';
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

export default {
  async scheduled(event,env,ctx){ctx.waitUntil(maintainImageAds(env));},
  async fetch(request, env) {
    const url = new URL(request.url);
    const imageAds = await handleImageAdRequest(request, env);
    if (imageAds) return imageAds;
    const sponsorship = await handleSponsorshipRequest(request, env);
    if (sponsorship) return sponsorship;
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
        'access-control-allow-methods': 'GET, POST, OPTIONS',
        'access-control-allow-headers': 'content-type',
        'access-control-max-age': '600',
      } });
    }
    if (url.pathname === '/health') return json({ ok: true });
    return json({ error: 'Not found' }, env.CHECKOUT_ENABLED === 'true' ? 404 : 503, corsHeaders(request, env));
  },
};
