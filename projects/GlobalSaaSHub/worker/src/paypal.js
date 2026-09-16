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

export function createPayPalOrder(env, requestId, productId, fetchImpl) {
  return paypalRequest(env, '/v2/checkout/orders', {
    method: 'POST',
    headers: { 'PayPal-Request-Id': requestId },
    body: JSON.stringify(orderCreatePayload(productId)),
  }, fetchImpl);
}

export async function capturePayPalOrder(env, providerOrderId, requestId, fetchImpl) {
  // Browser callbacks can be retried after a network interruption, and PayPal
  // webhooks can race the browser response. If the provider already shows a
  // completed order, do not issue a second capture request.
  try {
    const existing = await getPayPalOrder(env, providerOrderId, fetchImpl);
    if (existing?.status === 'COMPLETED') return existing;
  } catch {
    // A transient read failure must not prevent the first legitimate capture.
  }

  try {
    return await paypalRequest(env, `/v2/checkout/orders/${encodeURIComponent(providerOrderId)}/capture`, {
      method: 'POST',
      headers: { 'PayPal-Request-Id': requestId },
      body: '{}',
    }, fetchImpl);
  } catch (captureError) {
    // PayPal may have completed the capture even if the browser lost the
    // response. Recover only when a fresh provider read confirms COMPLETED;
    // amount/product verification still happens in the Worker before paid state.
    try {
      const recovered = await getPayPalOrder(env, providerOrderId, fetchImpl);
      if (recovered?.status === 'COMPLETED') return recovered;
    } catch {
      // Keep the original capture failure as the authoritative error.
    }
    throw captureError;
  }
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
