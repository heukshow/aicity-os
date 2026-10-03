import { orderCreatePayload } from './domain.js';

function apiBase(env) {
  return env.PAYPAL_ENVIRONMENT === 'live'
    ? 'https://api-m.paypal.com'
    : 'https://api-m.sandbox.paypal.com';
}

async function accessToken(env, fetchImpl = fetch) {
  const encoded = btoa(`${env.PAYPAL_CLIENT_ID}:${env.PAYPAL_CLIENT_SECRET}`);
  const response = await fetchImpl(`${apiBase(env)}/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${encoded}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
  });
  if (!response.ok) throw new Error('PayPal authentication failed');
  return (await response.json()).access_token;
}

async function paypalRequest(env, path, options = {}, fetchImpl = fetch) {
  const token = await accessToken(env, fetchImpl);
  const response = await fetchImpl(`${apiBase(env)}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
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

export async function checkPayPalReadiness(env, expectedWebhookUrl, fetchImpl) {
  if (env.PAYPAL_ENVIRONMENT !== 'live' || !env.PAYPAL_CLIENT_ID || !env.PAYPAL_CLIENT_SECRET || !env.PAYPAL_WEBHOOK_ID) {
    return { providerAuthenticationVerified: false, webhookUrlVerified: false, requiredEventsVerified: false, merchantIdentityVerified: false, configurationOnly: true };
  }
  // Authenticated GET only: this cannot create an order, charge, refund or register an app.
  const webhook = await paypalRequest(env, `/v1/notifications/webhooks/${encodeURIComponent(env.PAYPAL_WEBHOOK_ID)}`, {}, fetchImpl);
  const events = new Set((webhook.event_types || []).map((event) => event.name));
  const required = ['PAYMENT.CAPTURE.COMPLETED', 'PAYMENT.CAPTURE.PENDING', 'PAYMENT.CAPTURE.REFUNDED', 'PAYMENT.CAPTURE.REVERSED', 'CUSTOMER.DISPUTE.CREATED', 'CUSTOMER.DISPUTE.UPDATED', 'CUSTOMER.DISPUTE.RESOLVED'];
  // Some live-app subscription UIs do not offer this pre-capture legacy event.
  // Its absence does not weaken completed-capture verification or ad-stop events.
  const optional = ['CHECKOUT.PAYMENT-APPROVAL.REVERSED'];
  const missingRequiredEvents = events.has('*') ? [] : required.filter((name) => !events.has(name));
  const missingOptionalEvents = events.has('*') ? [] : optional.filter((name) => !events.has(name));
  if (!events.has('*') && !events.has('PAYMENT.CAPTURE.DENIED') && !events.has('PAYMENT.CAPTURE.DECLINED')) missingRequiredEvents.push('PAYMENT.CAPTURE.DENIED or PAYMENT.CAPTURE.DECLINED');
  return {
    providerAuthenticationVerified: true,
    webhookUrlVerified: webhook.url === expectedWebhookUrl,
    requiredEventsVerified: missingRequiredEvents.length === 0,
    missingRequiredEvents,
    missingOptionalEvents,
    // An OAuth token and registered webhook do not independently establish merchant identity.
    merchantIdentityVerified: false,
    configurationOnly: true,
  };
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
