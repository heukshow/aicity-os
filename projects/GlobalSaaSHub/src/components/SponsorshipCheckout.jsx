import { useEffect, useMemo, useRef, useState } from 'react';
import { paymentConfig } from '../config/payment.js';
import { captureVerifiedSponsorshipOrder, createSponsorshipOrder } from '../services/paymentApi.js';
import { loadPayPalSdk } from '../services/paypalSdk.js';

const PRODUCTS = [
  { id: 'tool_page_7', group: 'Tool Page Sponsored', days: 7, price: 19 },
  { id: 'tool_page_30', group: 'Tool Page Sponsored', days: 30, price: 49 },
  { id: 'tool_page_90', group: 'Tool Page Sponsored', days: 90, price: 129 },
  { id: 'buyer_intent_7', group: 'Buyer-Intent Featured', days: 7, price: 39 },
  { id: 'buyer_intent_30', group: 'Buyer-Intent Featured', days: 30, price: 99 },
  { id: 'buyer_intent_90', group: 'Buyer-Intent Featured', days: 90, price: 269 },
  { id: 'comparison_7', group: 'Comparison Premium', days: 7, price: 59 },
  { id: 'comparison_30', group: 'Comparison Premium', days: 30, price: 149 },
  { id: 'comparison_90', group: 'Comparison Premium', days: 90, price: 399 },
];

export default function SponsorshipCheckout() {
  const paypalContainer = useRef(null);
  const cardContainer = useRef(null);
  const [productId, setProductId] = useState('tool_page_30');
  const [status, setStatus] = useState({ type: 'loading', message: 'Loading secure checkout...' });
  const [cardEligible, setCardEligible] = useState(false);
  const [fulfillment, setFulfillment] = useState(null);
  const product = useMemo(() => PRODUCTS.find((item) => item.id === productId) || PRODUCTS[1], [productId]);

  useEffect(() => {
    if (!paymentConfig.checkoutEnabled || !paypalContainer.current || !cardContainer.current || fulfillment) return undefined;
    let active = true;
    let paypalButtons;
    let cardButtons;

    paypalContainer.current.innerHTML = '';
    cardContainer.current.innerHTML = '';
    setCardEligible(false);
    setStatus({ type: 'loading', message: `Loading secure $${product.price} checkout...` });

    const createOrder = async () => {
      setStatus({ type: 'loading', message: `Preparing ${product.group} — ${product.days} days ($${product.price})...` });
      const order = await createSponsorshipOrder(product.id);
      return order.orderId;
    };

    const onApprove = async ({ orderID }) => {
      setStatus({ type: 'loading', message: 'Verifying payment securely...' });
      const result = await captureVerifiedSponsorshipOrder(orderID);
      if (active) {
        setFulfillment(result);
        setStatus({ type: 'success', message: 'Payment confirmed. Submit your campaign assets to start fulfillment.' });
      }
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
            setStatus({ type: 'neutral', message: `Secure $${product.price} payment by card or PayPal.` });
          }
        } else if (active) {
          setCardEligible(false);
          setStatus({ type: 'neutral', message: `Secure $${product.price} payment via PayPal. Card checkout depends on PayPal eligibility for this buyer.` });
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
  }, [product.id, product.group, product.days, product.price, fulfillment]);

  if (!paymentConfig.checkoutEnabled) return null;

  const statusColor = status.type === 'success'
    ? 'text-emerald-300'
    : status.type === 'error' ? 'text-rose-300' : 'text-slate-400';

  if (fulfillment) {
    return (
      <div className="w-full max-w-xl rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.06] p-5" aria-live="polite">
        <div className="text-xs font-black uppercase tracking-[0.16em] text-emerald-300">Payment verified</div>
        <h3 className="mt-2 text-xl font-black text-white">Next: send your campaign materials</h3>
        <p className="mt-2 text-sm leading-6 text-slate-400">Your order is paid. COSHUMA created a campaign record and a private advertiser intake link. Publication starts only after the submitted materials pass validation or review.</p>
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          <a href={fulfillment.intakeUrl} target="_blank" rel="noopener noreferrer" className="rounded-xl bg-emerald-500 px-4 py-3 text-center text-sm font-black text-slate-950 hover:bg-emerald-400">Submit campaign assets</a>
          <a href={fulfillment.reportUrl} target="_blank" rel="noopener noreferrer" className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-center text-sm font-bold text-white hover:bg-white/10">Open campaign report</a>
        </div>
        <p className="mt-3 text-xs text-slate-500">Keep the report link private. It reports verified COSHUMA impressions and clicks only; sales or customer revenue are never inferred.</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-xl" aria-live="polite">
      <div className="mb-4 rounded-2xl border border-white/10 bg-white/[0.035] p-4">
        <label className="block text-xs font-black uppercase tracking-[0.16em] text-violet-300" htmlFor="sponsorship-product">Choose placement and duration</label>
        <select id="sponsorship-product" value={productId} onChange={(event) => setProductId(event.target.value)} className="mt-3 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-sm font-bold text-white outline-none focus:border-violet-400/50">
          <optgroup label="Tool Page Sponsored">
            {PRODUCTS.filter((item) => item.group === 'Tool Page Sponsored').map((item) => <option key={item.id} value={item.id}>{item.days} days — ${item.price}</option>)}
          </optgroup>
          <optgroup label="Buyer-Intent Featured">
            {PRODUCTS.filter((item) => item.group === 'Buyer-Intent Featured').map((item) => <option key={item.id} value={item.id}>{item.days} days — ${item.price}</option>)}
          </optgroup>
          <optgroup label="Comparison Premium">
            {PRODUCTS.filter((item) => item.group === 'Comparison Premium').map((item) => <option key={item.id} value={item.id}>{item.days} days — ${item.price}</option>)}
          </optgroup>
        </select>
        <div className="mt-3 flex items-center justify-between gap-3 text-sm">
          <span className="text-slate-400">{product.group} · {product.days} days</span>
          <span className="text-lg font-black text-white">${product.price} USD</span>
        </div>
        <p className="mt-2 text-xs leading-5 text-slate-500">Sponsored placement is clearly labeled and never purchases a positive review, rating or organic ranking.</p>
      </div>
      <div ref={cardContainer} className="min-h-0" aria-label="Credit or debit card checkout" />
      {cardEligible && <div className="my-2 text-center text-[10px] font-bold uppercase tracking-widest text-slate-600">or</div>}
      <div ref={paypalContainer} className="min-h-12" aria-label="PayPal checkout" />
      <p className={`mt-3 text-xs ${statusColor}`}>{status.message}</p>
    </div>
  );
}
