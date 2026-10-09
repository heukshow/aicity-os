import { authorized } from './admin.js';
import { CATALOG, SponsorshipError, quoteFor, validateApplication, paypalPayload, verifyPayPalPayment, publicationPeriod, publicStatus, destinationUrl, captureIdFromRefundLink } from './sponsorship-domain.js';
import { SponsorshipRepository } from './sponsorship-repository.js';
import { createSponsorshipPayPalOrder, capturePayPalOrder, getPayPalOrder, getPayPalCapture, verifyPayPalWebhook, checkPayPalReadiness, repairPayPalWebhookEvents } from './paypal.js';
import { renderSponsorshipOps } from './sponsorship-ops-view.js';
import { handleLegacyPayPalEvent } from './sponsorship-legacy-webhook.js';
import { validateAdAsset } from './ad-commerce-assets.js';
import { approvalEmailConfigured, approvalResumeToken, sendApprovalEmail } from './sponsorship-email.js';

const HEADERS = {
  'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store',
  'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer',
  'x-frame-options': 'DENY', 'x-robots-tag': 'noindex, nofollow',
  'content-security-policy': "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
};
const hash = async (value) => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)))].map((byte) => byte.toString(16).padStart(2, '0')).join('');
const token = () => [...crypto.getRandomValues(new Uint8Array(32))].map((byte) => byte.toString(16).padStart(2, '0')).join('');
const same = (left, right) => {
  if (typeof left !== 'string' || typeof right !== 'string' || left.length !== right.length) return false;
  let delta = 0;
  for (let i = 0; i < left.length; i += 1) delta |= left.charCodeAt(i) ^ right.charCodeAt(i);
  return delta === 0;
};

function reply(request, env, body, status = 200) {
  const origin = request.headers.get('origin');
  const cors = env.ALLOWED_ORIGIN && origin === env.ALLOWED_ORIGIN ? { 'access-control-allow-origin': origin, vary: 'Origin' } : {};
  return new Response(JSON.stringify(body), { status, headers: { ...HEADERS, ...cors } });
}

function paymentConfiguration(env) {
  return Boolean(env.PAYPAL_ENVIRONMENT === 'live' && env.PAYPAL_CLIENT_ID && env.PAYPAL_CLIENT_SECRET
    && env.PAYPAL_WEBHOOK_ID && env.PAYPAL_MERCHANT_ID && env.ALLOWED_ORIGIN === 'https://coshuma.com');
}

function configuration(env, storageReady = true, privateView = false) {
  const intakeReady = storageReady && env.ALLOWED_ORIGIN === 'https://coshuma.com';
  const paymentReady = intakeReady && env.CHECKOUT_ENABLED === 'true' && paymentConfiguration(env);
  const result = { catalog: CATALOG, currency: 'USD', intakeReady, paymentReady };
  if (paymentReady && !privateView) result.publicClientId = env.PAYPAL_CLIENT_ID;
  if (privateView) Object.assign(result, { configurationOnly: true, checks: {
    storageReady, checkoutEnabled: env.CHECKOUT_ENABLED === 'true', liveEnvironment: env.PAYPAL_ENVIRONMENT === 'live',
    clientIdConfigured: Boolean(env.PAYPAL_CLIENT_ID), clientSecretConfigured: Boolean(env.PAYPAL_CLIENT_SECRET),
    webhookIdConfigured: Boolean(env.PAYPAL_WEBHOOK_ID), merchantIdConfigured: Boolean(env.PAYPAL_MERCHANT_ID),
    approvalEmailConfigured: approvalEmailConfigured(env),
  } });
  return result;
}

async function bodyJson(request, maxBytes = 16384, preserveRaw = false) {
  if (!(request.headers.get('content-type') || '').toLowerCase().startsWith('application/json')) throw new SponsorshipError('Send an application/json request', 415);
  const declared = Number(request.headers.get('content-length') || 0);
  if (!Number.isFinite(declared) || declared < 0 || declared > maxBytes) throw new SponsorshipError('Request body is too large', 413);
  // Do not trust Content-Length, which can be omitted by chunked requests.
  const reader = request.body?.getReader();
  const chunks = [];
  let size = 0;
  if (reader) {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > maxBytes) { await reader.cancel(); throw new SponsorshipError('Request body is too large', 413); }
      chunks.push(value);
    }
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  const rawText = new TextDecoder().decode(bytes);
  let body;
  try { body = JSON.parse(rawText); } catch { throw new SponsorshipError('Invalid JSON', 400); }
  if (!body || typeof body !== 'object' || Array.isArray(body)) throw new SponsorshipError('A JSON object is required', 400);
  return preserveRaw ? { body, rawText } : body;
}

async function bodyBytes(request, maxBytes = 500000) {
  const declared = Number(request.headers.get('content-length') || 0);
  if (!Number.isFinite(declared) || declared < 0 || declared > maxBytes) throw new SponsorshipError('Image is too large', 413);
  const reader = request.body?.getReader();
  if (!reader) throw new SponsorshipError('Image body is required', 400);
  const chunks = []; let size = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > maxBytes) { await reader.cancel(); throw new SponsorshipError('Image is too large', 413); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return bytes;
}

function publicWrite(request, env) {
  if (!env.ALLOWED_ORIGIN || request.headers.get('origin') !== env.ALLOWED_ORIGIN) throw new SponsorshipError('Forbidden', 403);
}

async function applicationAccess(request, repo, id, env) {
  const app = await repo.getApplication(id);
  const bearer = request.headers.get('authorization') || '';
  if (!app || !/^Bearer [a-f0-9]{64}$/.test(bearer)) throw new SponsorshipError('Application access is required', 401);
  const presented = bearer.slice(7);
  const originalAccess = same(await hash(presented), app.access_token_hash);
  let approvalAccess = false;
  if (!originalAccess && app.review_status === 'approved') {
    const resume = await approvalResumeToken(app, env);
    approvalAccess = Boolean(resume && same(presented, resume));
  }
  if (!originalAccess && !approvalAccess) throw new SponsorshipError('Application access is required', 401);
  return app;
}

async function statusView(application, repo, env, privateView = false) {
  const payment = await repo.getPayment(application.id);
  const view = {
    applicationId: application.id, reference: application.reference,
    companyName: application.company_name, toolName: application.tool_name,
    quote: { amount: application.amount, currency: application.currency, durationDays: application.duration_days, slot: application.slot, targetPage: application.target_page },
    status: publicStatus(application), paymentStatus: application.payment_status,
    reviewStatus: application.review_status, publicationStatus: application.publication_status,
    paymentVerified: application.payment_status === 'verified' && payment?.state === 'verified' && payment.environment === 'live'
      && Boolean(payment.capture_id && payment.provider_order_id && Number.isFinite(Date.parse(payment.verified_at)))
      && payment.amount === application.amount && payment.currency === application.currency && payment.merchant_id === env.PAYPAL_MERCHANT_ID,
    approved: application.review_status === 'approved' && Boolean(application.approved_by?.trim()) && Number.isFinite(Date.parse(application.approved_at)),
    paymentVerifiedAt: payment?.verified_at || null, lastCheckedAt: payment?.last_checked_at || null,
    startAt: application.starts_at, endAt: application.ends_at,
    paymentReady: configuration(env).paymentReady,
  };
  if (application.creative_mode === 'image') {
    const [assets, hold] = await Promise.all([repo.imageAssets(application.id), repo.imageHold(application.id)]);
    const holdActive = Boolean(hold?.expires_at && Date.parse(hold.expires_at) > Date.now());
    let imageStatus;
    if (application.review_status === 'rejected') imageStatus = 'rejected';
    else if (application.publication_status === 'published') imageStatus = publicStatus(application);
    else if (application.payment_status === 'verified') imageStatus = 'ready_to_publish';
    else if (application.review_status === 'approved') imageStatus = holdActive ? 'awaiting_payment' : 'reservation_expired';
    else if (application.submission_status === 'submitted') imageStatus = 'awaiting_review';
    else imageStatus = 'preparing_materials';
    Object.assign(view, {
      status: imageStatus, creativeMode: 'image', submissionStatus: application.submission_status,
      assets, reservationUntil: hold?.expires_at || null, reservationActive: holdActive,
    });
  }
  if (privateView) {
    const notification = await repo.approvalEmailStatus(application.id);
    Object.assign(view, {
      contactEmail: application.contact_email, reviewNotes: application.review_notes,
      destinationUrl: application.destination_url, headline: application.headline,
      description: application.description, ctaText: application.cta_text,
      desiredStartDate: application.desired_start_date,
      approvalNotification: notification ? { action: notification.action, detail: notification.detail, createdAt: notification.created_at } : null,
      paymentEvidence: payment ? { environment: payment.environment, providerOrderId: payment.provider_order_id, captureId: payment.capture_id, verificationReason: payment.verification_reason } : null,
    });
  }
  return view;
}

async function providerCall(callback) {
  try { return await callback(); } catch (error) {
    if (error instanceof SponsorshipError) throw error;
    throw new SponsorshipError('The payment provider could not be verified; no payment success is recorded', 502);
  }
}

async function notifyApprovedApplication(repo, application, env, actor) {
  if (!approvalEmailConfigured(env) || application?.creative_mode !== 'image' || application?.review_status !== 'approved') {
    return { sent: false, skipped: true };
  }
  if (await repo.approvalEmailSent(application)) return { sent: true, duplicate: true };
  const hold = await repo.imageHold(application.id);
  if (!hold?.expires_at || Date.parse(hold.expires_at) <= Date.now()) return { sent: false, skipped: true };
  try {
    const sent = await sendApprovalEmail(application, hold, env);
    await repo.recordApprovalEmailSent(application, sent.providerMessageId, actor, new Date().toISOString());
    return { sent: true, providerMessageId: sent.providerMessageId };
  } catch (error) {
    const message = error instanceof SponsorshipError ? error.message : 'Approval email delivery failed';
    await repo.recordApprovalEmailFailed(application, message, actor, new Date().toISOString());
    return { sent: false, failed: true };
  }
}

export async function retryPendingApprovalEmails(env) {
  if (!approvalEmailConfigured(env) || !env.ORDERS) return { attempted: 0, sent: 0 };
  const repo = new SponsorshipRepository(env.ORDERS);
  await repo.ready();
  await repo.imageReady();
  const rows = await repo.pendingApprovalEmailApplications(new Date().toISOString());
  let sent = 0;
  for (const application of rows) {
    const result = await notifyApprovedApplication(repo, application, env, 'approval-email-scheduler');
    if (result.sent && !result.duplicate) sent += 1;
  }
  return { attempted: rows.length, sent };
}

async function verifyExistingPayment(application, repo, env, actor) {
  if (!paymentConfiguration(env)) throw new SponsorshipError('Live payment verification is not configured', 503);
  const payment = await repo.getPayment(application.id);
  if (!payment?.provider_order_id) throw new SponsorshipError('This application has no PayPal order', 409);
  if (payment.state === 'refunded' || payment.verification_reason?.startsWith('hold:')) throw new SponsorshipError('This payment is held or reversed and cannot be activated', 409);
  const order = await providerCall(() => getPayPalOrder(env, payment.provider_order_id));
  const captures = order.purchase_units?.flatMap((unit) => unit.payments?.captures || []) || [];
  const now = new Date().toISOString();
  if (captures.length !== 1 || !captures[0].id) {
    await repo.stopPayment(application.id, 'review', 'PayPal has not returned exactly one completed capture', actor, now);
    throw new SponsorshipError('The payment has not been verified', 409);
  }
  const capture = await providerCall(() => getPayPalCapture(env, captures[0].id));
  // A signed stop event can arrive before an order/capture was linked locally.
  // Retain its minimal identifiers and reconcile it before any later verification.
  const stopEvent = await repo.blockingPaymentEvent(env.PAYPAL_ENVIRONMENT, payment.provider_order_id, capture.id);
  if (stopEvent) {
    const refunded = stopEvent.event_type.startsWith('PAYMENT.CAPTURE.');
    await repo.stopPayment(application.id, refunded ? 'refunded' : 'review', `hold:${stopEvent.event_type}`, actor, now);
    throw new SponsorshipError('A verified payment event has stopped this application', 409);
  }
  if (['REFUNDED', 'PARTIALLY_REFUNDED'].includes(capture.status)) {
    await repo.stopPayment(application.id, 'refunded', 'PayPal capture is refunded or partially refunded', actor, now);
    throw new SponsorshipError('The payment has been refunded; publication is stopped', 409);
  }
  let evidence;
  try { evidence = verifyPayPalPayment({ order, capture, application, payment, merchantId: env.PAYPAL_MERCHANT_ID, environment: env.PAYPAL_ENVIRONMENT }); }
  catch (error) {
    await repo.stopPayment(application.id, 'review', 'Order, merchant, capture or quoted gross amount did not verify', actor, now);
    throw error;
  }
  return repo.markVerified(application, evidence, actor, now);
}

async function activateVerifiedImage(application, repo, actor) {
  if (application.creative_mode !== 'image' || application.payment_status !== 'verified'
      || application.review_status !== 'approved' || application.publication_status !== 'draft') return application;
  const now = new Date();
  const nowIso = now.toISOString();
  await repo.requireImageHold(application, nowIso);
  let requested = nowIso;
  if (application.desired_start_date) {
    const candidate = new Date(application.desired_start_date + 'T00:00:00.000Z');
    if (Number.isFinite(candidate.getTime()) && candidate.getTime() > now.getTime()) requested = candidate.toISOString();
  }
  const period = publicationPeriod(application, requested, now);
  return repo.publishImage(application, period.startsAt, period.endsAt, actor, nowIso);
}

async function publicPlacements(request, env, repo) {
  const path = new URL(request.url).searchParams.get('path');
  if (!CATALOG.some((item) => item.allowedPages.includes(path))) throw new SponsorshipError('This page has no available sponsored placement', 422);
  // Display uses verified live payments, independently of whether new checkout is paused.
  if (env.PAYPAL_ENVIRONMENT !== 'live' || !env.PAYPAL_MERCHANT_ID) return reply(request, env, { ready: true, placements: [] });
  const now = new Date();
  const rows = await repo.placements(path, now.toISOString(), env.PAYPAL_MERCHANT_ID);
  const counts = new Map();
  for (const row of rows) counts.set(row.slot, (counts.get(row.slot) || 0) + 1);
  const placements = [];
  for (const row of rows) {
    try {
      const quote = quoteFor({ slot: row.slot, durationDays: row.duration_days, targetPage: row.target_page });
      const start = Date.parse(row.starts_at), end = Date.parse(row.ends_at);
      if (counts.get(row.slot) !== 1 || row.amount !== quote.amount || row.currency !== quote.currency
          || !Number.isFinite(start) || !Number.isFinite(end) || start > now.getTime() || end <= now.getTime()
          || end - start !== row.duration_days * 86400000) continue;
      const creative = { campaignId: row.id, slot: row.slot, targetPage: row.target_page,
        title: row.headline, body: row.description, button: row.cta_text, url: destinationUrl(row.destination_url),
        startAt: row.starts_at, endAt: row.ends_at, environment: 'live', paymentVerified: true, approved: true, status: 'published', label: 'Sponsored' };
      if (row.creative_mode === 'image') Object.assign(creative, {
        creativeMode: 'image',
        imageUrl: new URL('/v1/ads/assets/' + encodeURIComponent(row.id) + '/' + encodeURIComponent(row.slot), request.url).href,
        logoUrl: new URL('/v1/ads/assets/' + encodeURIComponent(row.id) + '/logo', request.url).href,
      });
      placements.push(creative);
    } catch { /* Invalid persisted material never becomes a public ad. */ }
  }
  return reply(request, env, { ready: true, placements });
}

function ownerBase(url, env) {
  if (url.pathname === '/ops/ads' || url.pathname.startsWith('/ops/ads/')) return '/ops/ads';
  const privateBase = String(env.ADMIN_PATH || '').replace(/\/$/, '');
  return privateBase && (url.pathname === `${privateBase}/ads` || url.pathname.startsWith(`${privateBase}/ads/`)) ? `${privateBase}/ads` : null;
}

async function ownerAccess(request, env, base) {
  const ops = base === '/ops/ads';
  const authEnv = ops ? { ...env, ADMIN_PATH: '/ops', ADMIN_USERNAME: 'support@coshuma.com', ADMIN_PASSWORD_SHA256: env.OPS_PASSWORD_SHA256 } : env;
  // The audience-growth publisher/OIDC permission is intentionally not accepted here.
  if (!await authorized(request, authEnv, !ops)) throw new SponsorshipError('Owner authentication is required', 401);
  if (request.method !== 'GET' && request.method !== 'HEAD'
      && request.headers.get('origin') !== new URL(request.url).origin) throw new SponsorshipError('A same-origin owner request is required', 403);
  return ops ? 'owner-ops-session' : 'owner-private-session';
}

async function ownerRequest(request, env, repo, base) {
  const actor = await ownerAccess(request, env, base);
  const suffix = new URL(request.url).pathname.slice(base.length).replace(/\/$/, '');
  if (request.method === 'GET' && suffix === '/config') return reply(request, env, configuration(env, true, true));
  if (request.method === 'POST' && suffix === '/verify-readiness') {
    await bodyJson(request);
    const result = await providerCall(() => checkPayPalReadiness(env, `${new URL(request.url).origin}/v1/webhooks/paypal`));
    return reply(request, env, { ...configuration(env, true, true), ...result, readinessVerifiedAt: new Date().toISOString() });
  }
  if (request.method === 'POST' && suffix === '/repair-webhook-events') {
    const body = await bodyJson(request);
    if (env.CHECKOUT_ENABLED !== 'false') throw new SponsorshipError('New checkout must be paused before updating webhook subscriptions', 409);
    if (Object.keys(body).length !== 1 || typeof body.expectedCandidateId !== 'string' || !/^[A-Za-z0-9_-]{1,128}$/.test(body.expectedCandidateId)) {
      throw new SponsorshipError('One expected webhook candidate ID is required', 422);
    }
    const result = await repairPayPalWebhookEvents(env, `${new URL(request.url).origin}/v1/webhooks/paypal`, body.expectedCandidateId);
    return reply(request, env, { ...configuration(env, true, true), ...result, readinessVerifiedAt: new Date().toISOString() });
  }
  if (request.method === 'GET' && ['', '/applications'].includes(suffix)) {
    const applications = await Promise.all((await repo.listApplications()).map((app) => statusView(app, repo, env, true)));
    if (suffix) return reply(request, env, { applications });
    return new Response(renderSponsorshipOps({ applications, config: configuration(env, true, true), basePath: base }), { headers: {
      ...HEADERS, 'content-type': 'text/html; charset=utf-8',
      'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    } });
  }
  const assetMatch = /^\/applications\/([a-f0-9-]{36})\/assets\/(logo|tool-primary|buyer-intent-top|compare-decision-premium)$/.exec(suffix);
  if (assetMatch && request.method === 'GET') {
    const app = await repo.getApplication(assetMatch[1]);
    if (!app || app.creative_mode !== 'image' || !['logo', app.slot].includes(assetMatch[2])) throw new SponsorshipError('Image asset not found', 404);
    const asset = await repo.getImageAsset(app.id, assetMatch[2]);
    if (!asset) throw new SponsorshipError('Image asset not found', 404);
    return new Response(asset.data, { headers: { ...HEADERS, 'content-type': asset.mime, 'cache-control': 'no-store, private' } });
  }
  const match = /^\/applications\/([a-f0-9-]{36})(?:\/(verify-payment|review|publish|pause))?$/.exec(suffix);
  if (!match) throw new SponsorshipError('Not found', 404);
  let app = await repo.getApplication(match[1]);
  if (!app) throw new SponsorshipError('Application not found', 404);
  if (request.method === 'GET' && !match[2]) return reply(request, env, await statusView(app, repo, env, true));
  if (request.method !== 'POST' || !match[2]) throw new SponsorshipError('Method not allowed', 405);
  const body = await bodyJson(request);
  const now = new Date();
  if (match[2] === 'verify-payment') {
    app = await verifyExistingPayment(app, repo, env, actor);
    app = await activateVerifiedImage(app, repo, actor);
  }
  if (match[2] === 'review') {
    if (!['approve', 'reject'].includes(body.decision) || typeof body.notes !== 'string' || !body.notes.trim() || body.notes.length > 1000) throw new SponsorshipError('A review decision and notes are required');
    if (body.decision === 'approve' && (body.destinationChecked !== true || body.claimsChecked !== true)) throw new SponsorshipError('Check the destination and claims before approving');
    quoteFor({ slot: app.slot, durationDays: app.duration_days, targetPage: app.target_page });
    destinationUrl(app.destination_url);
    app = await repo.review(app, body.decision === 'approve', body.notes.trim(), actor, now.toISOString());
    if (body.decision === 'approve' && app.creative_mode === 'image') {
      await repo.reserveImagePlacement(app, now.toISOString());
      app = await repo.getApplication(app.id);
      await notifyApprovedApplication(repo, app, env, actor);
    }
  }
  if (match[2] === 'publish') {
    // Refresh provider truth at the final gate; a stale local "paid" flag is insufficient.
    app = await verifyExistingPayment(app, repo, env, actor);
    if (app.review_status !== 'approved') throw new SponsorshipError('Material approval is required', 409);
    quoteFor({ slot: app.slot, durationDays: app.duration_days, targetPage: app.target_page });
    const period = publicationPeriod(app, body.startsAt, new Date());
    app = await repo.publish(app, period.startsAt, period.endsAt, actor, new Date().toISOString());
  }
  if (match[2] === 'pause') app = await repo.pause(app.id, actor, now.toISOString());
  return reply(request, env, await statusView(app, repo, env, true));
}

async function webhook(request, env, repo) {
  if (request.method !== 'POST') throw new SponsorshipError('Method not allowed', 405);
  // Webhooks continue while new checkout is paused, including refunds and disputes.
  if (env.PAYPAL_ENVIRONMENT !== 'live' || !env.PAYPAL_CLIENT_ID || !env.PAYPAL_CLIENT_SECRET || !env.PAYPAL_WEBHOOK_ID) throw new SponsorshipError('Payment event verification is unavailable', 503);
  const { body: event, rawText } = await bodyJson(request, 65536, true);
  if (typeof event.id !== 'string' || !event.id || event.id.length > 128 || typeof event.event_type !== 'string') throw new SponsorshipError('Invalid payment event', 400);
  const signature = await providerCall(() => verifyPayPalWebhook(env, request.headers, event, undefined, rawText));
  if (signature.verification_status !== 'SUCCESS') throw new SponsorshipError('Webhook signature verification failed', 401);
  const environment = env.PAYPAL_ENVIRONMENT;
  if (await repo.hasEvent(environment, event.id)) return reply(request, env, { accepted: true, duplicate: true });
  const ids = event.resource?.supplementary_data?.related_ids || {};
  const relatedOrderId = ids.order_id
    || (event.event_type === 'CHECKOUT.PAYMENT-APPROVAL.REVERSED' ? event.resource?.order_id : null)
    || (event.event_type.startsWith('CHECKOUT.ORDER.') ? event.resource?.id : null);
  const payments = new Map();
  const direct = relatedOrderId ? await repo.getPaymentByOrder(relatedOrderId, environment) : null;
  if (direct) payments.set(direct.id, direct);
  const captureIds = [...new Set([ids.capture_id, captureIdFromRefundLink(event),
    event.event_type.startsWith('PAYMENT.CAPTURE.') && !event.event_type.endsWith('.REFUNDED') ? event.resource?.id : null,
    ...(event.resource?.disputed_transactions || []).map((item) => item.seller_transaction_id),
  ].filter((id) => typeof id === 'string' && id && id.length <= 128))];
  const metadata = { ...event, environment, relatedOrderId, captureIds };
  for (const id of captureIds) {
    const payment = await repo.getPaymentByCapture(id, environment);
    if (payment) payments.set(payment.id, payment);
  }
  const now = new Date().toISOString();
  for (const payment of payments.values()) {
    const app = await repo.getApplication(payment.application_id);
    if (!app) throw new SponsorshipError('Payment application storage is inconsistent', 503);
    if (['PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED'].includes(event.event_type)) {
      await repo.stopPayment(app.id, 'refunded', event.event_type, 'verified-paypal-webhook', now);
    } else if (event.event_type.startsWith('CUSTOMER.DISPUTE.')) {
      await repo.stopPayment(app.id, 'review', `hold:${event.event_type}`, 'verified-paypal-webhook', now);
    } else if (event.event_type === 'PAYMENT.CAPTURE.COMPLETED') {
      if (payment.state !== 'refunded' && !payment.verification_reason?.startsWith('hold:')) {
        const verified = await verifyExistingPayment(app, repo, env, 'verified-paypal-webhook');
        await activateVerifiedImage(verified, repo, 'verified-paypal-webhook');
      }
    } else if (['PAYMENT.CAPTURE.PENDING', 'PAYMENT.CAPTURE.DENIED', 'PAYMENT.CAPTURE.DECLINED'].includes(event.event_type)) {
      await repo.stopPayment(app.id, 'review', event.event_type, 'verified-paypal-webhook', now);
    }
  }
  const knownCaptures = new Set();
  for (const payment of payments.values()) {
    const saved = await repo.getPayment(payment.application_id);
    if (saved?.capture_id) knownCaptures.add(saved.capture_id);
  }
  const legacy = direct && captureIds.every((id) => knownCaptures.has(id)) ? { matched: false }
    : await handleLegacyPayPalEvent(event, env, metadata, knownCaptures);
  // Commit dedupe only after every referenced advertising/legacy transaction was handled.
  await repo.recordEvent(metadata, now);
  return reply(request, env, { accepted: true, matched: payments.size > 0 || legacy.matched, legacy: legacy.matched });
}

async function paymentAction(request, env, repo, app, action) {
  if (!configuration(env).paymentReady) throw new SponsorshipError('Payment is not available; your application is saved', 503);
  const body = await bodyJson(request);
  if (app.payment_status === 'refunded' || app.review_status === 'rejected') throw new SponsorshipError('This application cannot accept payment', 409);
  if (app.creative_mode === 'image') {
    if (app.submission_status !== 'submitted' || app.review_status !== 'approved') {
      throw new SponsorshipError('Image materials must be approved before payment', 409);
    }
    await repo.requireImageHold(app, new Date().toISOString());
  } else if (publicStatus(app) !== 'awaiting_payment') {
    if (action === 'capture' && app.payment_status === 'verified') {
      const saved = await repo.getPayment(app.id);
      if (body.orderId !== saved?.provider_order_id) throw new SponsorshipError('The payment order does not match this application', 409);
      return { orderId: saved.provider_order_id, ...await statusView(app, repo, env) };
    }
    throw new SponsorshipError('This application is not awaiting payment', 409);
  }
  if (action === 'order') {
    const payment = await repo.reservePayment(app, env, new Date().toISOString());
    if (payment.state === 'verified') return { orderId: payment.provider_order_id, ...await statusView(app, repo, env) };
    if (payment.state === 'refunded' || payment.verification_reason?.startsWith('hold:')) throw new SponsorshipError('This payment requires owner review', 409);
    if (payment.provider_order_id) return { orderId: payment.provider_order_id };
    const order = await providerCall(() => createSponsorshipPayPalOrder(env, `${payment.id.replaceAll('-', '')}-c`, paypalPayload(app, env.PAYPAL_MERCHANT_ID)));
    if (!order?.id || !['CREATED', 'APPROVED', 'PAYER_ACTION_REQUIRED'].includes(order.status)) throw new SponsorshipError('PayPal did not create a usable order', 502);
    await repo.attachProviderOrder(app.id, order.id, new Date().toISOString());
    return { orderId: order.id, created: true };
  }
  const payment = await repo.getPayment(app.id);
  if (!payment?.provider_order_id || body.orderId !== payment.provider_order_id) throw new SponsorshipError('The payment order does not match this application', 409);
  if (payment.state === 'refunded' || payment.verification_reason?.startsWith('hold:')) throw new SponsorshipError('This payment cannot be captured', 409);
  const order = await providerCall(() => getPayPalOrder(env, payment.provider_order_id));
  if (order.status !== 'COMPLETED') await providerCall(() => capturePayPalOrder(env, payment.provider_order_id, `${payment.id.replaceAll('-', '')}-p`));
  app = await verifyExistingPayment(app, repo, env, 'advertiser-checkout');
  app = await activateVerifiedImage(app, repo, 'advertiser-checkout');
  return { orderId: payment.provider_order_id, ...await statusView(app, repo, env) };
}

export async function handleSponsorshipRequest(request, env) {
  const url = new URL(request.url);
  const base = ownerBase(url, env);
  const ours = base || url.pathname.startsWith('/v1/sponsorship/') || url.pathname.startsWith('/v1/ads/')
    || url.pathname === '/v1/sponsored/placements'
    || url.pathname === '/v1/webhooks/paypal' || ['/v1/orders', '/v1/orders/capture'].includes(url.pathname);
  if (!ours) return null;
  if (request.method === 'OPTIONS') {
    if (base || request.headers.get('origin') !== env.ALLOWED_ORIGIN) return reply(request, env, { error: 'Forbidden' }, 403);
    return new Response(null, { status: 204, headers: { ...HEADERS, 'access-control-allow-origin': env.ALLOWED_ORIGIN,
      'access-control-allow-methods': 'GET, POST, PUT, OPTIONS', 'access-control-allow-headers': 'content-type, authorization', vary: 'Origin' } });
  }
  try {
    // Authenticate financial reads before checking or disclosing storage readiness.
    if (base) await ownerAccess(request, env, base);
    const repo = new SponsorshipRepository(env.ORDERS);
    await repo.ready();
    if (base || url.pathname.startsWith('/v1/ads/')) await repo.imageReady();
    if (base) return await ownerRequest(request, env, repo, base);
    if (url.pathname === '/v1/webhooks/paypal') return await webhook(request, env, repo);
    if (['/v1/orders', '/v1/orders/capture'].includes(url.pathname)) throw new SponsorshipError('Use a saved sponsorship application for checkout', 410);
    if (request.method === 'GET' && url.pathname === '/v1/sponsored/placements') return await publicPlacements(request, env, repo);

    if (request.method === 'GET' && url.pathname === '/v1/ads/config') {
      return reply(request, env, { ...configuration(env), creativeMode: 'image', assetMimeTypes: ['image/png'],
        catalog: CATALOG,
        placements: CATALOG.map((item) => ({ slot: item.slot, label: item.label, prices: item.prices, targetPage: item.allowedPages[0] })) });
    }
    const publicAsset = /^\/v1\/ads\/assets\/([a-f0-9-]{36})\/(logo|tool-primary|buyer-intent-top|compare-decision-premium)$/.exec(url.pathname);
    if (request.method === 'GET' && publicAsset) {
      const app = await repo.getApplication(publicAsset[1]);
      const payment = app ? await repo.getPayment(app.id) : null;
      const now = Date.now();
      if (!app || app.creative_mode !== 'image' || !['logo', app.slot].includes(publicAsset[2])
        || app.publication_status !== 'published' || app.review_status !== 'approved' || app.payment_status !== 'verified'
        || !Number.isFinite(Date.parse(app.starts_at)) || !Number.isFinite(Date.parse(app.ends_at))
        || Date.parse(app.starts_at) > now || Date.parse(app.ends_at) <= now
        || payment?.state !== 'verified' || payment.environment !== 'live' || payment.merchant_id !== env.PAYPAL_MERCHANT_ID) {
        throw new SponsorshipError('Image asset not found', 404);
      }
      const asset = await repo.getImageAsset(app.id, publicAsset[2]);
      if (!asset) throw new SponsorshipError('Image asset not found', 404);
      return new Response(asset.data, { headers: { ...HEADERS, 'content-type': asset.mime,
        'access-control-allow-origin': env.ALLOWED_ORIGIN, vary: 'Origin' } });
    }
    if (request.method === 'POST' && url.pathname === '/v1/ads/applications') {
      publicWrite(request, env);
      if (!configuration(env).intakeReady) throw new SponsorshipError('Applications are not available', 503);
      const input = validateApplication(await bodyJson(request));
      const now = new Date().toISOString();
      await repo.rateLimit(await hash(request.headers.get('cf-connecting-ip') || 'unavailable'), now);
      const id = crypto.randomUUID(), accessToken = token();
      const reference = `COSHUMA-AD-${now.slice(0,10).replaceAll('-','')}-${id}`;
      const application = await repo.createImageApplication(id, reference, await hash(accessToken), input, now);
      return reply(request, env, { ...await statusView(application, repo, env), accessToken }, 201);
    }
    const imageMatch = /^\/v1\/ads\/applications\/([a-f0-9-]{36})(?:\/(assets\/(logo|tool-primary|buyer-intent-top|compare-decision-premium)|submit|order|capture))?$/.exec(url.pathname);
    if (imageMatch) {
      let app = await applicationAccess(request, repo, imageMatch[1], env);
      if (app.creative_mode !== 'image') throw new SponsorshipError('Image application access is required', 404);
      if (request.method === 'GET' && !imageMatch[2]) return reply(request, env, await statusView(app, repo, env));
      if (request.method === 'PUT' && imageMatch[3]) {
        publicWrite(request, env);
        const mime = request.headers.get('content-type')?.split(';')[0].trim().toLowerCase();
        if (mime !== 'image/png') throw new SponsorshipError('Only PNG image uploads are currently accepted', 415);
        const bytes = await bodyBytes(request);
        let file;
        try { file = await validateAdAsset(imageMatch[3], mime, bytes); }
        catch (error) { throw new SponsorshipError(String(error?.message || 'Invalid advertisement image'), 422); }
        const assets = await repo.saveImageAsset(app, imageMatch[3], file, new Date().toISOString());
        return reply(request, env, { applicationId: app.id, assets });
      }
      if (request.method === 'POST' && imageMatch[2] === 'submit') {
        publicWrite(request, env);
        await bodyJson(request);
        app = await repo.submitImageApplication(app, new Date().toISOString());
        return reply(request, env, await statusView(app, repo, env));
      }
      if (request.method === 'POST' && ['order','capture'].includes(imageMatch[2])) {
        publicWrite(request, env);
        const result = await paymentAction(request, env, repo, app, imageMatch[2]);
        return reply(request, env, result, result.created ? 201 : 200);
      }
      throw new SponsorshipError('Method not allowed', 405);
    }
    if (request.method === 'GET' && url.pathname === '/v1/sponsorship/config') return reply(request, env, configuration(env));
    if (request.method === 'GET' && url.pathname === '/v1/sponsorship/quote') return reply(request, env, { quote: quoteFor(Object.fromEntries(url.searchParams)), ...configuration(env) });
    if (request.method === 'POST') publicWrite(request, env);
    if (request.method === 'POST' && url.pathname === '/v1/sponsorship/applications') {
      if (!configuration(env).intakeReady) throw new SponsorshipError('Applications are not available', 503);
      const input = validateApplication(await bodyJson(request));
      const now = new Date().toISOString();
      await repo.rateLimit(await hash(request.headers.get('cf-connecting-ip') || 'unavailable'), now);
      const id = crypto.randomUUID(), accessToken = token();
      const reference = `COSHUMA-ADS-${now.slice(0, 10).replaceAll('-', '')}-${id}`;
      const application = await repo.createApplication(id, reference, await hash(accessToken), input, now);
      return reply(request, env, { ...await statusView(application, repo, env), accessToken }, 201);
    }
    const match = /^\/v1\/sponsorship\/applications\/([a-f0-9-]{36})(?:\/(order|capture))?$/.exec(url.pathname);
    if (!match) throw new SponsorshipError('Not found', 404);
    let app = await applicationAccess(request, repo, match[1], env);
    if (request.method === 'GET' && !match[2]) return reply(request, env, await statusView(app, repo, env));
    if (request.method !== 'POST' || !match[2]) throw new SponsorshipError('Method not allowed', 405);
    if (!configuration(env).paymentReady) throw new SponsorshipError('Payment is not available; your application is saved', 503);
    const body = await bodyJson(request);
    if (app.payment_status === 'refunded' || app.review_status === 'rejected') throw new SponsorshipError('This application cannot accept payment', 409);
    if (publicStatus(app) !== 'awaiting_payment') {
      if (match[2] === 'capture' && app.payment_status === 'verified') {
        const saved = await repo.getPayment(app.id);
        if (body.orderId !== saved?.provider_order_id) throw new SponsorshipError('The payment order does not match this application', 409);
        return reply(request, env, { orderId: saved.provider_order_id, ...await statusView(app, repo, env) });
      }
      throw new SponsorshipError('This application is not awaiting payment', 409);
    }
    if (match[2] === 'order') {
      const payment = await repo.reservePayment(app, env, new Date().toISOString());
      if (payment.state === 'verified') return reply(request, env, { orderId: payment.provider_order_id, ...await statusView(app, repo, env) });
      if (payment.state === 'refunded' || payment.verification_reason?.startsWith('hold:')) throw new SponsorshipError('This payment requires owner review', 409);
      if (payment.provider_order_id) return reply(request, env, { orderId: payment.provider_order_id });
      const order = await providerCall(() => createSponsorshipPayPalOrder(env, `${payment.id.replaceAll('-', '')}-c`, paypalPayload(app, env.PAYPAL_MERCHANT_ID)));
      if (!order?.id || !['CREATED', 'APPROVED', 'PAYER_ACTION_REQUIRED'].includes(order.status)) throw new SponsorshipError('PayPal did not create a usable order', 502);
      await repo.attachProviderOrder(app.id, order.id, new Date().toISOString());
      return reply(request, env, { orderId: order.id }, 201);
    }
    const payment = await repo.getPayment(app.id);
    if (!payment?.provider_order_id || body.orderId !== payment.provider_order_id) throw new SponsorshipError('The payment order does not match this application', 409);
    if (payment.state === 'refunded' || payment.verification_reason?.startsWith('hold:')) throw new SponsorshipError('This payment cannot be captured', 409);
    // Recover a previous successful capture first; stable request IDs protect a retry after timeout.
    const order = await providerCall(() => getPayPalOrder(env, payment.provider_order_id));
    if (order.status !== 'COMPLETED') await providerCall(() => capturePayPalOrder(env, payment.provider_order_id, `${payment.id.replaceAll('-', '')}-p`));
    app = await verifyExistingPayment(app, repo, env, 'advertiser-checkout');
    return reply(request, env, { orderId: payment.provider_order_id, ...await statusView(app, repo, env) });
  } catch (error) {
    const status = error instanceof SponsorshipError ? error.status : 503;
    const message = error instanceof SponsorshipError ? error.message : 'Application storage is unavailable; the action was not completed';
    const extra = status === 401 || status === 403 ? {} : url.pathname === '/v1/sponsored/placements' ? { ready: false, placements: [] }
      : url.pathname.endsWith('/config') ? configuration(env, false, Boolean(base)) : {};
    return reply(request, env, { ...extra, error: message }, status);
  }
}
