import { orderCreatePayload } from './domain.js';

function apiBase(env) {
  return env.PAYPAL_ENVIRONMENT === 'live'
    ? 'https://api-m.paypal.com'
    : 'https://api-m.sandbox.paypal.com';
}

// Only the authenticated readiness probe opts into these fixed, non-sensitive fields.
function probeStage(probe, stage, code, httpStatus = null) {
  if (probe) probe.diagnostic = { stage, code, httpStatus: Number.isInteger(httpStatus) && httpStatus >= 100 && httpStatus <= 599 ? httpStatus : null };
}

async function accessToken(env, fetchImpl = fetch, probe) {
  const encoded = btoa(`${env.PAYPAL_CLIENT_ID}:${env.PAYPAL_CLIENT_SECRET}`);
  probeStage(probe, 'authentication', 'network_error');
  const response = await fetchImpl(`${apiBase(env)}/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${encoded}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
  });
  probeStage(probe, 'authentication', response.ok ? 'unknown_error' : 'authentication_http_error', response.status);
  if (!response.ok) throw new Error('PayPal authentication failed');
  const token = (await response.json()).access_token;
  if (probe) {
    if (typeof token !== 'string' || !token.trim()) throw new Error('PayPal authentication response could not be verified');
    probe.providerAuthenticationVerified = true;
  }
  return token;
}

async function paypalRequest(env, path, options = {}, fetchImpl = fetch, probe, existingToken) {
  const token = existingToken ?? await accessToken(env, fetchImpl, probe);
  const stage = probe?.requestStage || 'webhook_lookup';
  probeStage(probe, stage, 'network_error');
  const response = await fetchImpl(`${apiBase(env)}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  probeStage(probe, stage, response.ok ? 'unknown_error' : 'provider_http_error', response.status);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`PayPal request failed (${response.status})`);
  return data;
}

export function createPayPalOrder(env, requestId, fetchImpl) {
  return paypalRequest(env, '/v2/checkout/orders', {
    method: 'POST',
    headers: { 'PayPal-Request-Id': requestId },
    body: JSON.stringify(orderCreatePayload()),
  }, fetchImpl);
}

export function capturePayPalOrder(env, providerOrderId, requestId, fetchImpl) {
  return paypalRequest(env, `/v2/checkout/orders/${encodeURIComponent(providerOrderId)}/capture`, {
    method: 'POST',
    headers: { 'PayPal-Request-Id': requestId },
    body: '{}',
  }, fetchImpl);
}

export function getPayPalOrder(env, providerOrderId, fetchImpl) {
  return paypalRequest(env, `/v2/checkout/orders/${encodeURIComponent(providerOrderId)}`, {}, fetchImpl);
}

export function createSponsorshipPayPalOrder(env, requestId, payload, fetchImpl) {
  return paypalRequest(env, '/v2/checkout/orders', {
    method: 'POST',
    headers: { 'PayPal-Request-Id': requestId, Prefer: 'return=representation' },
    body: JSON.stringify(payload),
  }, fetchImpl);
}

export function getPayPalCapture(env, captureId, fetchImpl) {
  return paypalRequest(env, `/v2/payments/captures/${encodeURIComponent(captureId)}`, {}, fetchImpl);
}

function webhookEventReadiness(webhook) {
  if (!Array.isArray(webhook.event_types) || webhook.event_types.some((event) => !event || typeof event.name !== 'string')) throw new Error('PayPal webhook events could not be verified');
  const events = new Set(webhook.event_types.map((event) => event.name));
  const required = ['PAYMENT.CAPTURE.COMPLETED', 'PAYMENT.CAPTURE.PENDING', 'PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED', 'CUSTOMER.DISPUTE.CREATED', 'CUSTOMER.DISPUTE.UPDATED', 'CUSTOMER.DISPUTE.RESOLVED'];
  // Some live-app subscription UIs do not offer this pre-capture legacy event.
  // Its absence does not weaken completed-capture verification or ad-stop events.
  const optional = ['CHECKOUT.PAYMENT-APPROVAL.REVERSED'];
  const missingRequiredEvents = events.has('*') ? [] : required.filter((name) => !events.has(name));
  const missingOptionalEvents = events.has('*') ? [] : optional.filter((name) => !events.has(name));
  if (!events.has('*') && !events.has('PAYMENT.CAPTURE.DENIED') && !events.has('PAYMENT.CAPTURE.DECLINED')) missingRequiredEvents.push('PAYMENT.CAPTURE.DENIED or PAYMENT.CAPTURE.DECLINED');
  return { requiredEventsVerified: missingRequiredEvents.length === 0, missingRequiredEvents, missingOptionalEvents };
}

async function discoverWebhookCandidates(env, expectedWebhookUrl, token, fetchImpl) {
  const probe = { requestStage: 'webhook_discovery', diagnostic: { stage: 'webhook_discovery', code: 'unknown_error', httpStatus: null } };
  try {
    // Default APPLICATION scope uses the same OAuth token and never reads ACCOUNT registrations.
    const result = await paypalRequest(env, '/v1/notifications/webhooks', {}, fetchImpl, probe, token);
    if (!Array.isArray(result?.webhooks)) throw new Error('PayPal webhook list could not be verified');
    const candidates = new Map();
    for (const webhook of result.webhooks) {
      if (webhook?.url !== expectedWebhookUrl) continue;
      if (typeof webhook.id !== 'string' || !/^[A-Za-z0-9_-]{1,128}$/.test(webhook.id)) throw new Error('PayPal webhook ID could not be verified');
      candidates.set(webhook.id, { id: webhook.id, ...webhookEventReadiness(webhook) });
    }
    return { status: candidates.size ? 'found' : 'none', candidates: [...candidates.values()], diagnostic: { stage: 'webhook_discovery', code: 'complete', httpStatus: probe.diagnostic.httpStatus } };
  } catch {
    return { status: 'failed', candidates: [], diagnostic: probe.diagnostic };
  }
}

export async function checkPayPalReadiness(env, expectedWebhookUrl, fetchImpl) {
  const unverified = { providerAuthenticationVerified: false, webhookUrlVerified: false, requiredEventsVerified: false, merchantIdentityVerified: false, configurationOnly: true };
  if (env.PAYPAL_ENVIRONMENT !== 'live' || !env.PAYPAL_CLIENT_ID || !env.PAYPAL_CLIENT_SECRET || !env.PAYPAL_WEBHOOK_ID) {
    return { ...unverified, diagnostic: { stage: 'configuration', code: 'configuration_incomplete', httpStatus: null } };
  }
  const probe = { providerAuthenticationVerified: false, diagnostic: { stage: 'authentication', code: 'unknown_error', httpStatus: null } };
  let token;
  try {
    // Authenticated GET only: this cannot create an order, charge, refund or register an app.
    token = await accessToken(env, fetchImpl, probe);
    const webhook = await paypalRequest(env, `/v1/notifications/webhooks/${encodeURIComponent(env.PAYPAL_WEBHOOK_ID)}`, {}, fetchImpl, probe, token);
    if (!webhook || typeof webhook.url !== 'string' || !Array.isArray(webhook.event_types)) throw new Error('PayPal webhook response could not be verified');
    return {
      providerAuthenticationVerified: true,
      webhookUrlVerified: webhook.url === expectedWebhookUrl,
      ...webhookEventReadiness(webhook),
      // An OAuth token and registered webhook do not independently establish merchant identity.
      merchantIdentityVerified: false,
      configurationOnly: true,
      diagnostic: { stage: 'complete', code: 'complete', httpStatus: probe.diagnostic.httpStatus },
    };
  } catch {
    // Never return an exception message, response body, token, configured ID or URL.
    const result = { ...unverified, providerAuthenticationVerified: probe.providerAuthenticationVerified, diagnostic: probe.diagnostic };
    if (probe.providerAuthenticationVerified && probe.diagnostic.stage === 'webhook_lookup'
        && probe.diagnostic.code === 'provider_http_error' && probe.diagnostic.httpStatus === 404) {
      // Candidate IDs are private setup evidence only; no binding or readiness flag changes.
      result.webhookDiscovery = await discoverWebhookCandidates(env, expectedWebhookUrl, token, fetchImpl);
    }
    return result;
  }
}

export function verifyPayPalWebhook(env, headers, event, fetchImpl, rawEventText) {
  const fields = {
    transmission_id: headers.get('paypal-transmission-id'),
    transmission_time: headers.get('paypal-transmission-time'),
    cert_url: headers.get('paypal-cert-url'),
    auth_algo: headers.get('paypal-auth-algo'),
    transmission_sig: headers.get('paypal-transmission-sig'),
    webhook_id: env.PAYPAL_WEBHOOK_ID,
  };
  // Preserve the verified webhook's original JSON formatting and number spelling.
  // The raw text is supplied only after the bounded request reader validated JSON.
  const verificationBody = typeof rawEventText === 'string'
    ? `${JSON.stringify(fields).slice(0, -1)},"webhook_event":${rawEventText}}`
    : JSON.stringify({ ...fields, webhook_event: event });
  return paypalRequest(env, '/v1/notifications/verify-webhook-signature', {
    method: 'POST',
    body: verificationBody,
  }, fetchImpl);
}
