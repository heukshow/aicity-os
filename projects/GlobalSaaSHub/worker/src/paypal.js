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

export function verifyPayPalWebhook(env, headers, event, fetchImpl) {
  return paypalRequest(env, '/v1/notifications/verify-webhook-signature', {
    method: 'POST',
    body: JSON.stringify({
      transmission_id: headers.get('paypal-transmission-id'),
      transmission_time: headers.get('paypal-transmission-time'),
      cert_url: headers.get('paypal-cert-url'),
      auth_algo: headers.get('paypal-auth-algo'),
      transmission_sig: headers.get('paypal-transmission-sig'),
      webhook_id: env.PAYPAL_WEBHOOK_ID,
      webhook_event: event,
    }),
  }, fetchImpl);
}
