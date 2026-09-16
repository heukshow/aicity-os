import {
  publishCampaignIfEligible,
  validateCampaignAssets,
} from './campaign-automation.js';

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

function allowedBrowserRequest(request, env) {
  return Boolean(env.ALLOWED_ORIGIN && request.headers.get('origin') === env.ALLOWED_ORIGIN);
}

function safeJsonRequest(request, maxBytes = 8192) {
  const type = request.headers.get('content-type') || '';
  const raw = request.headers.get('content-length');
  const length = raw === null ? null : Number(raw);
  return type.toLowerCase().startsWith('application/json')
    && (length === null || (Number.isFinite(length) && length >= 0 && length <= maxBytes));
}

function validToken(value) {
  return typeof value === 'string' && /^[a-f0-9]{64}$/i.test(value);
}

async function submitAssets(request, env, repo) {
  if (!allowedBrowserRequest(request, env)) return json({ error: 'Forbidden' }, 403);
  if (!safeJsonRequest(request)) return json({ error: 'Invalid request' }, 415, corsHeaders(request, env));
  const asset = await request.json().catch(() => ({}));
  if (!validToken(asset.token)) return json({ error: 'Invalid campaign token' }, 400, corsHeaders(request, env));
  const campaign = await repo.getCampaignByIntakeToken(asset.token);
  if (!campaign) return json({ error: 'Campaign not found' }, 404, corsHeaders(request, env));
  if (!['awaiting_assets', 'pending_review', 'ready_to_publish'].includes(campaign.status)) {
    return json({ error: 'Campaign is not accepting asset submissions' }, 409, corsHeaders(request, env));
  }
  const now = new Date().toISOString();
  const validation = validateCampaignAssets(asset);
  let updated = await repo.saveAssets(campaign.id, asset, validation.status, validation.notes, now);
  if (updated.status === 'ready_to_publish') {
    updated = await publishCampaignIfEligible(env.ORDERS, campaign.id, now);
  }
  return json({
    campaignId: updated.id,
    status: updated.status,
    validation: validation.status,
    requiresManualReview: updated.status === 'pending_review',
  }, 200, corsHeaders(request, env));
}

async function advertiserReport(request, env, repo) {
  const url = new URL(request.url);
  const token = url.searchParams.get('token') || '';
  if (!validToken(token)) return json({ error: 'Invalid report token' }, 400, corsHeaders(request, env));
  const campaign = await repo.getCampaignByReportToken(token);
  if (!campaign) return json({ error: 'Campaign not found' }, 404, corsHeaders(request, env));
  const metrics = await repo.metrics(campaign.id);
  return json({
    campaignId: campaign.id,
    productId: campaign.product_id,
    placement: campaign.placement,
    durationDays: campaign.duration_days,
    priceUsd: campaign.price_usd,
    status: campaign.status,
    startsAt: campaign.starts_at,
    endsAt: campaign.ends_at,
    metrics,
    signups: 'not_tracked_by_coshuma',
    purchases: 'not_tracked_by_coshuma',
    advertiserRevenue: 'not_tracked_by_coshuma',
  }, 200, corsHeaders(request, env));
}

async function campaignEvent(request, env, repo) {
  if (!allowedBrowserRequest(request, env)) return json({ error: 'Forbidden' }, 403);
  if (!safeJsonRequest(request, 4096)) return json({ error: 'Invalid request' }, 415, corsHeaders(request, env));
  const body = await request.json().catch(() => ({}));
  if (!['sponsored_impression', 'sponsored_click'].includes(body.eventType)) {
    return json({ error: 'Invalid event type' }, 400, corsHeaders(request, env));
  }
  if (typeof body.campaignId !== 'string' || body.campaignId.length > 64) {
    return json({ error: 'Invalid campaign ID' }, 400, corsHeaders(request, env));
  }
  const campaign = await repo.getCampaignById(body.campaignId);
  if (!campaign || campaign.status !== 'published') {
    return json({ error: 'Active campaign not found' }, 404, corsHeaders(request, env));
  }
  const asset = await repo.getAssets(campaign.id);
  if (!asset || body.page !== asset.target_page || body.destinationUrl !== asset.destination_url) {
    return json({ error: 'Campaign event does not match published placement' }, 409, corsHeaders(request, env));
  }
  const now = new Date().toISOString();
  if (Date.parse(campaign.starts_at) > Date.parse(now) || Date.parse(campaign.ends_at) <= Date.parse(now)) {
    return json({ error: 'Campaign is outside its active flight' }, 409, corsHeaders(request, env));
  }
  await repo.recordEvent(
    campaign.id,
    body.eventType,
    body.page,
    campaign.placement,
    asset.destination_url,
    now,
  );
  return json({ accepted: true }, 202, corsHeaders(request, env));
}

export async function handleAdvertiserApi(request, env, repo) {
  const url = new URL(request.url);
  if (request.method === 'POST' && url.pathname === '/v1/advertiser/assets') {
    return submitAssets(request, env, repo);
  }
  if (request.method === 'GET' && url.pathname === '/v1/advertiser/report') {
    return advertiserReport(request, env, repo);
  }
  if (request.method === 'POST' && url.pathname === '/v1/sponsored/events') {
    return campaignEvent(request, env, repo);
  }
  return null;
}
