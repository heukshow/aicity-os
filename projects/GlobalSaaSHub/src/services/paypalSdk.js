import { paymentConfig } from '../config/payment.js';

let sdkPromise;

export function loadPayPalSdk() {
  if (!paymentConfig.checkoutEnabled) {
    return Promise.reject(new Error('Checkout is not enabled'));
  }
  if (window.paypal?.Buttons) return Promise.resolve(window.paypal);
  if (sdkPromise) return sdkPromise;

  sdkPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const params = new URLSearchParams({
      'client-id': paymentConfig.paypalClientId,
      components: 'buttons',
      currency: 'USD',
      intent: 'capture',
    });
    script.src = `https://www.paypal.com/sdk/js?${params}`;
    script.async = true;
    script.onload = () => window.paypal?.Buttons
      ? resolve(window.paypal)
      : reject(new Error('PayPal checkout is unavailable'));
    script.onerror = () => reject(new Error('PayPal checkout could not be loaded'));
    document.head.appendChild(script);
  }).catch((error) => {
    sdkPromise = undefined;
    throw error;
  });

  return sdkPromise;
}
