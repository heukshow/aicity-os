import { paymentConfig } from '../config/payment.js';

export default function SponsorshipCheckout() {
  if (!paymentConfig.checkoutEnabled) return null;

  // No public checkout UI is shipped while sponsorship checkout is paused.
  // Re-enabling a payment surface requires an explicit owner-directed implementation.
  return null;
}
