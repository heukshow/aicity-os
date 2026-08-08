const enabled = import.meta.env.VITE_SPONSORSHIP_CHECKOUT_ENABLED === 'true';
const apiBaseUrl = String(import.meta.env.VITE_PAYMENT_API_BASE_URL || '').replace(/\/$/, '');
const paypalClientId = String(import.meta.env.VITE_PAYPAL_CLIENT_ID || '');

export const paymentConfig = Object.freeze({
  apiBaseUrl,
  paypalClientId,
  checkoutEnabled: enabled && apiBaseUrl.startsWith('https://') && paypalClientId.length > 0,
});
