import { paymentConfig } from '../config/payment.js';

async function post(path, body = {}) {
  if (!paymentConfig.checkoutEnabled) throw new Error('Checkout is not enabled');
  const response = await fetch(`${paymentConfig.apiBaseUrl}${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || 'Payment request failed');
  return data;
}

export function createSponsorshipOrder() {
  return post('/v1/orders');
}

export async function captureVerifiedSponsorshipOrder(orderId) {
  const result = await post('/v1/orders/capture', { orderId });
  if (result.status !== 'paid' || result.verified !== true) {
    throw new Error('Payment has not been verified by the server');
  }
  return result;
}
