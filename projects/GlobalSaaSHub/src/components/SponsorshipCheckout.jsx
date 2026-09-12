import { paymentConfig } from '../config/payment.js';

const CHECKOUT_MAINTENANCE = true;

export default function SponsorshipCheckout() {
  if (!paymentConfig.checkoutEnabled) return null;

  if (CHECKOUT_MAINTENANCE) {
    return (
      <div className="w-full max-w-md rounded-2xl border border-amber-400/25 bg-amber-400/10 p-5" aria-live="polite">
        <div className="text-xs font-black uppercase tracking-[0.16em] text-amber-300">Payment system update in progress</div>
        <h3 className="mt-2 text-lg font-black text-white">Sponsorship checkout is temporarily unavailable.</h3>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          We are updating COSHUMA's sponsorship checkout and campaign reporting system. Payments are temporarily paused to prevent incorrect charges while the update is completed.
        </p>
        <p className="mt-3 text-xs leading-5 text-slate-500">
          No payment can be submitted from this page during maintenance. For sponsorship questions, contact support@coshuma.com.
        </p>
      </div>
    );
  }

  return null;
}
