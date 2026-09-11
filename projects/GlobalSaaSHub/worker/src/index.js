import { handlePrivateOps, handleSnapshotUpload } from './private-ops.js';
import { captureIsVerifiedPaid, getProduct, providerOrderIdFromWebhook, validatePaidWebhook, webhookTarget } from './domain.js';
import { capturePayPalOrder, createPayPalOrder, getPayPalOrder, verifyPayPalWebhook } from './paypal.js';
import { D1OrderRepository } from './repository.js';
import { handleAdminRequest, isAdminPath } from './admin.js';
import { activePlacementsForPath, publishCampaignIfEligible, runCampaignMaintenance } from './campaign-automation.js';

const PUBLIC_ADMIN_PATH = '/ops-login';
const json = (body, status = 200, extra = {}) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', ...extra } });
const html = (body, status = 200) => new Response(body, { status, headers: { 'content-type': 'text/html; charset=utf-8', 'x-robots-tag': 'noindex, nofollow' } });

function corsHeaders(request, env) {
  const origin = request.headers.get('origin');
  if (!origin || origin !== env.ALLOWED_ORIGIN) return {};
  return { 'access-control-allow-origin': origin, vary: 'Origin' };
}
function configured(env) { return Boolean(env.ORDERS && env.ALLOWED_ORIGIN && env.PAYPAL_CLIENT_ID && env.PAYPAL_CLIENT_SECRET && env.PAYPAL_WEBHOOK_ID); }
function payerName(order) { return [order?.payer?.name?.given_name, order?.payer?.name?.surname].filter(Boolean).join(' ') || null; }

function validationForAssets(asset) {
  const required = ['companyName', 'productName', 'contactEmail', 'destinationUrl', 'logoUrl', 'headline', 'description', 'ctaText', 'targetPage'];
  const missing = required.filter((key) => typeof asset?.[key] !== 'string' || !asset[key].trim());
  if (missing.length) return { status: 'invalid', notes: `Missing required fields: ${missing.join(', ')}` };
  if (!asset.sellerAttestation) return { status: 'invalid', notes: 'Seller attestation is required.' };
  if (!asset.targetPage.startsWith('/') || asset.targetPage.startsWith('//')) return { status: 'invalid', notes: 'Target page must be an exact COSHUMA path beginning with /.' };
  try {
    const destination = new URL(asset.destinationUrl); const logo = new URL(asset.logoUrl);
    if (destination.protocol !== 'https:' || logo.protocol !== 'https:') return { status: 'needs_review', notes: 'Destination and logo must use HTTPS.' };
  } catch { return { status: 'invalid', notes: 'Destination URL or logo URL is invalid.' }; }
  const risky = /(guaranteed income|guaranteed return|no risk|cure|miracle|100% guaranteed)/i;
  if (risky.test(`${asset.headline} ${asset.description}`)) return { status: 'needs_review', notes: 'Claims require manual review.' };
  if (asset.headline.length > 100 || asset.description.length > 500 || asset.ctaText.length > 50) return { status: 'needs_review', notes: 'Creative exceeds recommended length and requires review.' };
  return { status: 'valid', notes: null };
}

function intakePage(token) {
  const t = String(token || '').replace(/[^a-zA-Z0-9]/g, '');
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>COSHUMA advertiser intake</title><style>body{font-family:system-ui;background:#08090d;color:#eee;margin:0}.wrap{max-width:760px;margin:40px auto;padding:24px}.card{background:#11131a;border:1px solid #2a2d3a;border-radius:18px;padding:24px}label{display:block;margin-top:14px;font-weight:700}input,textarea{width:100%;box-sizing:border-box;margin-top:6px;padding:12px;border-radius:10px;border:1px solid #35394a;background:#0b0d12;color:#fff}button{margin-top:20px;padding:13px 18px;border:0;border-radius:12px;background:#7c3aed;color:#fff;font-weight:800}.muted{color:#9ca3af;font-size:13px}</style></head><body><div class="wrap"><div class="card"><h1>COSHUMA campaign assets</h1><p class="muted">Submit truthful campaign materials. Sponsored placement never buys an editorial rating or organic ranking.</p><form id="f"><input type="hidden" name="token" value="${t}"><label>Company name<input name="companyName" required></label><label>Product name<input name="productName" required></label><label>Contact email<input name="contactEmail" type="email" required></label><label>Destination URL<input name="destinationUrl" type="url" required placeholder="https://"></label><label>Logo URL<input name="logoUrl" type="url" required placeholder="https://"></label><label>Headline<input name="headline" maxlength="120" required></label><label>Description<textarea name="description" rows="5" maxlength="800" required></textarea></label><label>CTA text<input name="ctaText" maxlength="60" required placeholder="Learn more"></label><label>Desired start date<input name="desiredStartDate" type="date"></label><label>Exact COSHUMA target path<input name="targetPage" required placeholder="/tool/example.html"></label><label>Comparison target<input name="comparisonTarget" placeholder="Required only when relevant"></label><label><input style="width:auto" type="checkbox" name="sellerAttestation" required> I confirm these materials are accurate and I understand sponsorship does not control COSHUMA editorial ratings or organic ranking.</label><button type="submit">Submit campaign assets</button><p id="msg" class="muted"></p></form></div></div><script>const f=document.getElementById('f'),m=document.getElementById('msg');f.addEventListener('submit',async e=>{e.preventDefault();m.textContent='Submitting…';const fd=new FormData(f),body=Object.fromEntries(fd.entries());body.sellerAttestation=fd.get('sellerAttestation')==='on';const r=await fetch('/v1/advertiser/assets',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});const d=await r.json().catch(()=>({}));m.textContent=r.ok?(d.status==='published'?'Submitted. Your campaign has been scheduled automatically.':d.status==='pending_review'?'Submitted. This campaign requires review before publication.':'Submitted. Campaign status: '+d.status):(d.error||'Submission failed.');});</script></body></html>`;
}
function reportPage(token) {
  const t = String(token || '').replace(/[^a-zA-Z0-9]/g, '');
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>COSHUMA campaign report</title><style>body{font-family:system-ui;background:#08090d;color:#eee;margin:0}.wrap{max-width:760px;margin:40px auto;padding:24px}.card{background:#11131a;border:1px solid #2a2d3a;border-radius:18px;padding:24px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.metric{background:#0b0d12;border-radius:14px;padding:16px}.n{font-size:28px;font-weight:900}.muted{color:#9ca3af;font-size:13px}</style></head><body><div class="wrap"><div class="card"><h1>COSHUMA campaign report</h1><div id="content" class="muted">Loading verified campaign metrics…</div></div></div><script>fetch('/v1/advertiser/report?token=${t}').then(r=>r.json()).then(d=>{if(d.error)throw Error(d.error);document.getElementById('content').innerHTML='<p>Status: <b>'+d.status+'</b> · '+d.productId+'</p><p>'+((d.startsAt||'Not started'))+' → '+(d.endsAt||'Not scheduled')+'</p><div class="grid"><div class="metric"><div class="muted">Verified impressions</div><div class="n">'+d.metrics.impressions+'</div></div><div class="metric"><div class="muted">Verified clicks</div><div class="n">'+d.metrics.clicks+'</div></div><div class="metric"><div class="muted">CTR</div><div class="n">'+d.metrics.ctr+'%</div></div></div><p class="muted">Conversions, customer revenue and sales are not inferred unless separately verified by the advertiser or connected attribution system.</p>'}).catch(e=>document.getElementById('content').textContent=e.message);</script></body></html>`;
}

async function createOrder(request, env, repo) {
  const body = await request.json().catch(() => ({})); const product = getProduct(body.productId); const internalId = crypto.randomUUID();
  const provider = await createPayPalOrder(env, `create-${internalId}`, product.id);
  await repo.create({ id: internalId, providerOrderId: provider.id, productId: product.id, now: new Date().toISOString() });
  await repo.transition(provider.id, provider.status === 'CREATED' ? 'pending' : 'created', new Date().toISOString());
  return json({ orderId: provider.id, status: 'pending', productId: product.id, amount: product.amount, currency: 'USD' }, 201, corsHeaders(request, env));
}
async function captureOrder(request, env, repo) {
  const { orderId } = await request.json(); if (typeof orderId !== 'string' || !orderId) return json({ error: 'orderId is required' }, 400, corsHeaders(request, env));
  const local = await repo.getByProviderOrderId(orderId); if (!local) return json({ error: 'Order not found' }, 404, corsHeaders(request, env));
  await capturePayPalOrder(env, orderId, `capture-${local.id}`); const verified = await getPayPalOrder(env, orderId);
  if (!captureIsVerifiedPaid(verified, local.product_id)) return json({ orderId, status: local.status, verified: false }, 409, corsHeaders(request, env));
  const now = new Date().toISOString(); await repo.transition(orderId, 'paid', now);
  const withPayer = await repo.recordPayer(orderId, payerName(verified), verified?.payer?.email_address || null, now); const campaign = await repo.ensureCampaign(withPayer, now);
  const workerBase = new URL(request.url).origin;
  return json({ orderId, status: 'paid', verified: true, campaignId: campaign.id, intakeUrl: `${workerBase}/advertiser/intake?token=${campaign.intake_token}`, reportUrl: `${workerBase}/advertiser/report?token=${campaign.report_token}` }, 200, corsHeaders(request, env));
}
async function webhook(request, env, repo) {
  const event = await request.json(); if (!event?.id) return json({ error: 'Invalid webhook event' }, 400);
  const verification = await verifyPayPalWebhook(env, request.headers, event); if (verification.verification_status !== 'SUCCESS') return json({ error: 'Webhook signature verification failed' }, 401);
  const providerOrderId = providerOrderIdFromWebhook(event); const local = providerOrderId ? await repo.getByProviderOrderId(providerOrderId) : null; validatePaidWebhook(event, local?.product_id);
  const claimed = await repo.claimWebhook(event.id, event.event_type, new Date().toISOString()); if (!claimed) return json({ accepted: true, duplicate: true });
  try { const target = webhookTarget(event); const now = new Date().toISOString(); if (target && providerOrderId) { const updated = await repo.transition(providerOrderId, target, now); if (target === 'paid') await repo.ensureCampaign(updated, now); } await repo.completeWebhook(event.id, now); return json({ accepted: true, duplicate: false }); }
  catch (error) { await repo.releaseWebhook(event.id); throw error; }
}
async function submitAssets(request, env, repo) {
  const asset = await request.json().catch(() => ({})); const campaign = await repo.getCampaignByIntakeToken(asset.token || '');
  if (!campaign) return json({ error: 'Campaign not found' }, 404, corsHeaders(request, env));
  if (!['awaiting_assets', 'pending_review', 'ready_to_publish'].includes(campaign.status)) return json({ error: 'Campaign is not accepting asset submissions' }, 409, corsHeaders(request, env));
  const now = new Date().toISOString(); const validation = validationForAssets(asset); let updated = await repo.saveAssets(campaign.id, asset, validation.status, validation.notes, now);
  if (updated.status === 'ready_to_publish') updated = await publishCampaignIfEligible(env.ORDERS, campaign.id, now);
  return json({ campaignId: updated.id, status: updated.status, validation: validation.status }, 200, corsHeaders(request, env));
}
async function advertiserReport(request, env, repo) {
  const url = new URL(request.url); const campaign = await repo.getCampaignByReportToken(url.searchParams.get('token') || '');
  if (!campaign) return json({ error: 'Campaign not found' }, 404, corsHeaders(request, env)); const metrics = await repo.metrics(campaign.id);
  return json({ campaignId: campaign.id, productId: campaign.product_id, placement: campaign.placement, durationDays: campaign.duration_days, priceUsd: campaign.price_usd, status: campaign.status, startsAt: campaign.starts_at, endsAt: campaign.ends_at, metrics }, 200, corsHeaders(request, env));
}
async function campaignEvent(request, env, repo) {
  const body = await request.json().catch(() => ({})); if (!['sponsored_impression', 'sponsored_click'].includes(body.eventType)) return json({ error: 'Invalid event type' }, 400, corsHeaders(request, env));
  const campaign = await repo.getCampaignById(body.campaignId || ''); if (!campaign || campaign.status !== 'published') return json({ error: 'Active campaign not found' }, 404, corsHeaders(request, env));
  await repo.recordEvent(campaign.id, body.eventType, body.page, campaign.placement, body.destinationUrl, new Date().toISOString()); return json({ accepted: true }, 202, corsHeaders(request, env));
}
async function publicPlacements(request, env) {
  const url = new URL(request.url); const path = url.searchParams.get('path') || '/'; const placements = await activePlacementsForPath(env.ORDERS, path);
  return json({ placements }, 200, { ...corsHeaders(request, env), 'cache-control': 'public, max-age=60' });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/internal/analytics-snapshot') return handleSnapshotUpload(request, env);
    if (url.pathname === '/ops' || url.pathname.startsWith('/ops/')) return handlePrivateOps(request, env);
    const fixedAdminRoute = url.pathname === PUBLIC_ADMIN_PATH || url.pathname.startsWith(`${PUBLIC_ADMIN_PATH}/`); if (fixedAdminRoute) return handleAdminRequest(request, { ...env, ADMIN_PATH: PUBLIC_ADMIN_PATH });
    if (isAdminPath(url, env)) return handleAdminRequest(request, env);
    if (url.pathname === '/robots.txt') { const privatePath = String(env.ADMIN_PATH || '/ops-private').replace(/\/$/, ''); return new Response(`User-agent: *\nDisallow: ${PUBLIC_ADMIN_PATH}/\nDisallow: ${privatePath}/\nDisallow: /advertiser/\n`, { headers: { 'content-type': 'text/plain; charset=utf-8', 'x-robots-tag': 'noindex, nofollow' } }); }
    if (url.pathname === '/advertiser/intake') return html(intakePage(url.searchParams.get('token')));
    if (url.pathname === '/advertiser/report') return html(reportPage(url.searchParams.get('token')));
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: { ...corsHeaders(request, env), 'access-control-allow-methods': 'GET, POST, OPTIONS', 'access-control-allow-headers': 'content-type' } });
    if (url.pathname === '/health') return json({ ok: true, checkoutConfigured: configured(env) });
    if (!configured(env)) return json({ error: 'Checkout is not configured' }, 503, corsHeaders(request, env));
    const repo = new D1OrderRepository(env.ORDERS);
    try {
      if (request.method === 'GET' && url.pathname === '/v1/sponsored/placements') return await publicPlacements(request, env);
      if (request.method === 'POST' && url.pathname === '/v1/orders') return await createOrder(request, env, repo);
      if (request.method === 'POST' && url.pathname === '/v1/orders/capture') return await captureOrder(request, env, repo);
      if (request.method === 'POST' && url.pathname === '/v1/webhooks/paypal') return await webhook(request, env, repo);
      if (request.method === 'POST' && url.pathname === '/v1/advertiser/assets') return await submitAssets(request, env, repo);
      if (request.method === 'GET' && url.pathname === '/v1/advertiser/report') return await advertiserReport(request, env, repo);
      if (request.method === 'POST' && url.pathname === '/v1/advertiser/events') return await campaignEvent(request, env, repo);
      return json({ error: 'Not found' }, 404, corsHeaders(request, env));
    } catch (error) { console.error('Payment request failed', error?.message); return json({ error: 'Payment request failed safely' }, 502, corsHeaders(request, env)); }
  },
  async scheduled(controller, env, ctx) {
    if (!env.ORDERS) return;
    const workerBase = 'https://globalsaashub-payments.qmfforfhem.workers.dev';
    ctx.waitUntil(runCampaignMaintenance(env.ORDERS, new Date(controller.scheduledTime || Date.now()).toISOString(), `${workerBase}/advertiser/report`));
  },
};
