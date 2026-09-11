import { useEffect, useRef, useState } from 'react';
import { paymentConfig } from '../config/payment.js';
import { captureVerifiedSponsorshipOrder, createSponsorshipOrder } from '../services/paymentApi.js';
import { loadPayPalSdk } from '../services/paypalSdk.js';

export default function SponsorshipCheckout() {
  const paypalContainer = useRef(null);
  const cardContainer = useRef(null);
  const [status, setStatus] = useState({ type: 'loading', message: 'Loading secure checkout...' });
  const [cardEligible, setCardEligible] = useState(false);

  useEffect(() => {
    if (!paymentConfig.checkoutEnabled || !paypalContainer.current || !cardContainer.current) return undefined;
    let active = true;
    let paypalButtons;
    let cardButtons;

    const createOrder = async () => {
      setStatus({ type: 'loading', message: 'Preparing your $49 sponsorship...' });
      const order = await createSponsorshipOrder();
      return order.orderId;
    };

    const onApprove = async ({ orderID }) => {
      setStatus({ type: 'loading', message: 'Verifying payment securely...' });
      await captureVerifiedSponsorshipOrder(orderID);
      setStatus({ type: 'success', message: "Payment confirmed. We'll follow up about your sponsorship." });
    };

    const sharedHandlers = {
      createOrder,
      onApprove,
      onCancel: () => setStatus({ type: 'neutral', message: 'Checkout cancelled. You have not been charged.' }),
      onError: () => setStatus({ type: 'error', message: 'Checkout could not be completed. Please try again.' }),
    };

    loadPayPalSdk()
      .then(async (paypal) => {
        if (!active || !paypalContainer.current || !cardContainer.current) return;

        paypalButtons = paypal.Buttons({
          ...sharedHandlers,
          fundingSource: paypal.FUNDING.PAYPAL,
          style: { layout: 'vertical', shape: 'pill', label: 'paypal' },
        });
        if (!paypalButtons.isEligible()) throw new Error('PayPal checkout is unavailable');
        await paypalButtons.render(paypalContainer.current);

        cardButtons = paypal.Buttons({
          ...sharedHandlers,
          fundingSource: paypal.FUNDING.CARD,
          style: { layout: 'vertical', shape: 'pill', label: 'pay' },
        });

        if (cardButtons.isEligible()) {
          await cardButtons.render(cardContainer.current);
          if (active) {
            setCardEligible(true);
            setStatus({ type: 'neutral', message: 'Secure $49 payment by card or PayPal.' });
          }
        } else if (active) {
          setCardEligible(false);
          setStatus({ type: 'neutral', message: 'Secure $49 payment via PayPal. Card checkout depends on PayPal eligibility for this buyer.' });
        }
      })
      .catch(() => {
        if (active) setStatus({ type: 'error', message: 'Secure checkout is temporarily unavailable.' });
      });

    return () => {
      active = false;
      paypalButtons?.close?.();
      cardButtons?.close?.();
    };
  }, []);

  if (!paymentConfig.checkoutEnabled) return null;

  const statusColor = status.type === 'success'
    ? 'text-emerald-300'
    : status.type === 'error' ? 'text-rose-300' : 'text-slate-400';

  return (
    <div className="w-full max-w-sm" aria-live="polite">
      <div ref={cardContainer} className="min-h-0" aria-label="Credit or debit card checkout" />
      {cardEligible && <div className="my-2 text-center text-[10px] font-bold uppercase tracking-widest text-slate-600">or</div>}
      <div ref={paypalContainer} className="min-h-12" aria-label="PayPal checkout" />
      <p className={`mt-3 text-xs ${statusColor}`}>{status.message}</p>
    </div>
  );
}
