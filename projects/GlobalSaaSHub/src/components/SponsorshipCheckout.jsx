import { useEffect, useRef, useState } from 'react';
import { paymentConfig } from '../config/payment.js';
import { captureVerifiedSponsorshipOrder, createSponsorshipOrder } from '../services/paymentApi.js';
import { loadPayPalSdk } from '../services/paypalSdk.js';

export default function SponsorshipCheckout() {
  const buttonContainer = useRef(null);
  const [status, setStatus] = useState({ type: 'loading', message: 'Loading secure checkout...' });

  useEffect(() => {
    if (!paymentConfig.checkoutEnabled || !buttonContainer.current) return undefined;
    let active = true;
    let buttons;

    loadPayPalSdk()
      .then((paypal) => {
        if (!active || !buttonContainer.current) return;
        buttons = paypal.Buttons({
          style: { layout: 'vertical', shape: 'pill', label: 'paypal' },
          createOrder: async () => {
            setStatus({ type: 'loading', message: 'Preparing your $49 sponsorship...' });
            const order = await createSponsorshipOrder();
            return order.orderId;
          },
          onApprove: async ({ orderID }) => {
            setStatus({ type: 'loading', message: 'Verifying payment securely...' });
            await captureVerifiedSponsorshipOrder(orderID);
            setStatus({ type: 'success', message: "Payment confirmed. We'll follow up about your sponsorship." });
          },
          onCancel: () => setStatus({ type: 'neutral', message: 'Checkout cancelled. You have not been charged.' }),
          onError: () => setStatus({ type: 'error', message: 'Checkout could not be completed. Please try again.' }),
        });
        if (!buttons.isEligible()) throw new Error('PayPal checkout is unavailable');
        return buttons.render(buttonContainer.current).then(() => {
          if (active) setStatus({ type: 'neutral', message: 'Secure $49 sponsorship payment via PayPal.' });
        });
      })
      .catch(() => {
        if (active) setStatus({ type: 'error', message: 'Secure checkout is temporarily unavailable.' });
      });

    return () => {
      active = false;
      buttons?.close?.();
    };
  }, []);

  if (!paymentConfig.checkoutEnabled) return null;

  const statusColor = status.type === 'success'
    ? 'text-emerald-300'
    : status.type === 'error' ? 'text-rose-300' : 'text-slate-400';

  return (
    <div className="w-full max-w-sm" aria-live="polite">
      <div ref={buttonContainer} className="min-h-12" />
      <p className={`mt-3 text-xs ${statusColor}`}>{status.message}</p>
    </div>
  );
}
