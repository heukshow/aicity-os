import { authorized, loginPage, privateLogin, PRIVATE_HEADERS } from './admin.js';

const ISSUER = 'https://token.actions.githubusercontent.com';
const AUDIENCE = 'coshuma-private-analytics';
const WORKFLOW = 'heukshow/aicity-os/.github/workflows/coshuma-analytics-snapshot.yml@refs/heads/main';
let cachedKeys;
const decode = (s) => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
const parse = (s) => JSON.parse(new TextDecoder().decode(decode(s)));

export async function verifyPublisher(token, fetcher = fetch) {
  try {
    if (typeof token !== 'string' || token.length > 16000) return false;
    const parts = token.split('.');
    if (parts.length !== 3) return false;
    const [head, claim] = parts.slice(0, 2).map(parse);
    const now = Math.floor(Date.now() / 1000);
    if (head.alg !== 'RS256' || typeof head.kid !== 'string' || claim.iss !== ISSUER || claim.aud !== AUDIENCE
      || claim.sub !== 'repo:heukshow/aicity-os:ref:refs/heads/main'
      || claim.repository_id !== '1158871708' || claim.repository_owner_id !== '209299838'
      || claim.workflow_ref !== WORKFLOW || claim.ref !== 'refs/heads/main'
      || !['push', 'schedule', 'workflow_dispatch'].includes(claim.event_name)
      || !Number.isFinite(claim.exp) || claim.exp <= now || !Number.isFinite(claim.nbf) || claim.nbf > now + 30
      || !Number.isFinite(claim.iat) || claim.iat > now + 30 || now - claim.iat > 600) return false;
    if (!cachedKeys || cachedKeys.until < Date.now() || !cachedKeys.keys.some(k => k.kid === head.kid)) {
      const response = await fetcher(`${ISSUER}/.well-known/jwks`);
      if (!response.ok) return false;
      cachedKeys = { keys: (await response.json()).keys, until: Date.now() + 300000 };
    }
    const jwk = cachedKeys.keys.find(k => k.kid === head.kid && k.kty === 'RSA' && k.use === 'sig');
    if (!jwk) return false;
    const key = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
    return await crypto.subtle.verify('RSASSA-PKCS1-v1_5', key, decode(parts[2]), new TextEncoder().encode(parts.slice(0, 2).join('.')));
  } catch { return false; }
}

const response = (body, status, type = 'application/json; charset=utf-8') => new Response(body, {
  status, headers: { ...PRIVATE_HEADERS, 'content-type': type, 'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src data:; base-uri 'none'; form-action 'self'; frame-ancestors 'none'" },
});

export async function handleSnapshotUpload(request, env) {
  if (request.method !== 'PUT') return response('{"error":"Method not allowed"}', 405);
  const token = request.headers.get('authorization')?.replace(/^Bearer /, '');
  if (!await verifyPublisher(token)) return response('{"error":"Unauthorized"}', 401);
  if (!env.ORDERS) return response('{"error":"Storage unavailable"}', 503);
  // Bound request size without buffering an unbounded stream.
  const reader = request.body?.getReader();
  if (!reader) return response('{"error":"Empty body"}', 400);
  let size = 0; const chunks = [];
  while (true) {
    const { done, value } = await reader.read(); if (done) break;
    size += value.length;
    if (size > 1000000) { await reader.cancel(); return response('{"error":"Too large"}', 413); }
    chunks.push(value);
  }
  let data;
  try { data = JSON.parse(await new Blob(chunks).text()); } catch { return response('{"error":"Invalid JSON"}', 400); }
  if (data.status !== 'live_google_connected' || data.measurement_status !== 'live_connected'
    || !data.metrics || !data.ranges || !Number.isFinite(Date.parse(data.generated_at))
    || Math.abs(Date.now() - Date.parse(data.generated_at)) > 900000)
    return response('{"error":"Snapshot validation failed"}', 422);
  await env.ORDERS.prepare(`INSERT INTO private_ops_documents (name, content, content_type, updated_at)
    VALUES (?, ?, ?, ?) ON CONFLICT(name) DO UPDATE SET content=excluded.content, updated_at=excluded.updated_at
    WHERE excluded.updated_at > private_ops_documents.updated_at`)
    .bind('traffic-revenue-data.json', JSON.stringify(data), 'application/json; charset=utf-8', data.generated_at).run();
  return response('{"stored":true}', 200);
}

export async function handlePrivateOps(request, env) {
  const path = new URL(request.url).pathname;
  const authEnv = { ...env, ADMIN_PATH: '/ops', ADMIN_USERNAME: 'support@coshuma.com', ADMIN_PASSWORD_SHA256: env.OPS_PASSWORD_SHA256 };
  if (request.method === 'POST' && ['/ops', '/ops/', '/ops/traffic-revenue.html'].includes(path)) {
    if (!env.ORDERS || !env.OPS_PASSWORD_SHA256) return response('{"error":"Authentication unavailable"}', 503);
    const ip = request.headers.get('cf-connecting-ip') || 'unknown';
    const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(ip)))].map(b => b.toString(16).padStart(2, '0')).join('');
    const bucket = Math.floor(Date.now() / 600000);
    const attempt = await env.ORDERS.prepare(`INSERT INTO private_ops_login_limits (client, bucket, attempts) VALUES (?, ?, 1)
      ON CONFLICT(client) DO UPDATE SET bucket=excluded.bucket, attempts=CASE WHEN bucket=excluded.bucket THEN attempts+1 ELSE 1 END RETURNING attempts`)
      .bind(digest, bucket).first();
    if (!attempt || attempt.attempts > 10) return response('{"error":"Too many login attempts; try again later"}', 429);
    return privateLogin(request, authEnv, '/ops/traffic-revenue.html');
  }
  if (!await authorized(request, authEnv, false)) {
    return path.endsWith('.json') ? response('{"error":"Authentication required"}', 401)
      : response(loginPage(), 401, 'text/html; charset=utf-8');
  }
  if (!['GET', 'HEAD'].includes(request.method)) return response('{"error":"Method not allowed"}', 405);
  const name = ['/ops', '/ops/'].includes(path) ? 'traffic-revenue.html' : path.slice('/ops/'.length);
  if (!['traffic-revenue.html', 'traffic-revenue-data.json', 'revenue-seo-refresh.json', 'admin-affiliate-audit.json'].includes(name))
    return response('{"error":"Not found"}', 404);
  if (!env.ORDERS) return response('{"error":"Storage unavailable"}', 503);
  const doc = await env.ORDERS.prepare('SELECT content, content_type FROM private_ops_documents WHERE name = ?').bind(name).first();
  if (!doc) return response('{"error":"Not available"}', 503);
  return response(request.method === 'HEAD' ? null : doc.content, 200, doc.content_type);
}
