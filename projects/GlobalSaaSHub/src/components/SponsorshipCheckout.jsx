import { useEffect, useMemo, useRef, useState } from 'react';
import { paymentConfig } from '../config/payment.js';
import { captureVerifiedSponsorshipOrder, createSponsorshipOrder } from '../services/paymentApi.js';
import { loadPayPalSdk } from '../services/paypalSdk.js';

// Final release gate. This stays true until Worker/D1 no-payment verification,
// frontend build checks, and sponsorship event/reporting checks all pass.
const CHECKOUT_MAINTENANCE = true;

const PRODUCTS = Object.freeze([
  { id: 'tool_page_7', group: 'Tool Page Sponsored', days: 7, price: 19 },
  { id: 'tool_page_30', group: 'Tool Page Sponsored', days: 30, price: 49 },
  { id: 'tool_page_90', group: 'Tool Page Sponsored', days: 90, price: 129 },
  { id: 'buyer_intent_7', group: 'Buyer-Intent Featured', days: 7, price: 39 },
  { id: 'buyer_intent_30', group: 'Buyer-Intent Featured', days: 30, price: 99 },
  { id: 'buyer_intent_90', group: 'Buyer-Intent Featured', days: 90, price: 269 },
  { id: 'comparison_7', group: 'Comparison Premium', days: 7, price: 59 },
  { id: 'comparison_30', group: 'Comparison Premium', days: 30, price: 149 },
  { id: 'comparison_90', group: 'Comparison Premium', days: 90, price: 399 },
]);

function MaintenanceNotice() {
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

function CampaignSetup({ fulfillment }) {
  const [form, setForm] = useState({
    companyName: '', productName: '', contactEmail: '', destinationUrl: '', logoUrl: '',
    headline: '', description: '', ctaText: 'Learn more', desiredStartDate: '',
    targetPage: '', comparisonTarget: '', sellerAttestation: false,
  });
  const [submission, setSubmission] = useState({ state: 'idle', message: '' });
  const [report, setReport] = useState(null);

  const setField = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  const submitAssets = async (event) => {
    event.preventDefault();
    setSubmission({ state: 'loading', message: 'Submitting campaign materials...' });
    try {
      const response = await fetch(`${paymentConfig.apiBaseUrl}/v1/advertiser/assets`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ ...form, token: fulfillment.intakeToken }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Campaign materials could not be submitted.');
      const message = data.status === 'published'
        ? 'Materials accepted. Your sponsored placement has been scheduled.'
        : data.status === 'pending_review'
          ? 'Materials received. This campaign requires review before publication.'
          : `Materials received. Campaign status: ${data.status}.`;
      setSubmission({ state: 'success', message });
    } catch (error) {
      setSubmission({ state: 'error', message: error.message || 'Campaign materials could not be submitted.' });
    }
  };

  const refreshReport = async () => {
    setReport({ loading: true });
    try {
      const response = await fetch(`${paymentConfig.apiBaseUrl}/v1/advertiser/report?token=${encodeURIComponent(fulfillment.reportToken)}`);
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Report could not be loaded.');
      setReport(data);
    } catch (error) {
      setReport({ error: error.message || 'Report could not be loaded.' });
    }
  };

  return (
    <div className="w-full max-w-2xl space-y-5" aria-live="polite">
      <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.06] p-5">
        <div className="text-xs font-black uppercase tracking-[0.16em] text-emerald-300">Payment verified</div>
        <h3 className="mt-2 text-xl font-black text-white">Submit your campaign materials</h3>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          Campaign {fulfillment.campaignId} was created after server-side payment verification. Publication begins only after the submitted materials pass validation or review.
        </p>
      </div>

      <form onSubmit={submitAssets} className="rounded-2xl border border-white/10 bg-white/[0.035] p-5 space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="text-sm font-bold text-slate-200">Company name<input required value={form.companyName} onChange={(e) => setField('companyName', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
          <label className="text-sm font-bold text-slate-200">Product name<input required value={form.productName} onChange={(e) => setField('productName', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
          <label className="text-sm font-bold text-slate-200">Contact email<input required type="email" value={form.contactEmail} onChange={(e) => setField('contactEmail', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
          <label className="text-sm font-bold text-slate-200">Desired start date<input type="date" value={form.desiredStartDate} onChange={(e) => setField('desiredStartDate', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
        </div>
        <label className="block text-sm font-bold text-slate-200">Official destination URL<input required type="url" placeholder="https://" value={form.destinationUrl} onChange={(e) => setField('destinationUrl', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
        <label className="block text-sm font-bold text-slate-200">Logo URL<input required type="url" placeholder="https://" value={form.logoUrl} onChange={(e) => setField('logoUrl', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
        <label className="block text-sm font-bold text-slate-200">COSHUMA target page path<input required placeholder="/tool/example.html" value={form.targetPage} onChange={(e) => setField('targetPage', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /><span className="mt-1 block text-xs font-normal text-slate-500">Use the exact COSHUMA page where the sponsored placement should appear.</span></label>
        <label className="block text-sm font-bold text-slate-200">Headline<input required maxLength={100} value={form.headline} onChange={(e) => setField('headline', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
        <label className="block text-sm font-bold text-slate-200">Description<textarea required maxLength={500} rows={4} value={form.description} onChange={(e) => setField('description', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="text-sm font-bold text-slate-200">CTA text<input required maxLength={50} value={form.ctaText} onChange={(e) => setField('ctaText', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
          <label className="text-sm font-bold text-slate-200">Comparison target <span className="font-normal text-slate-500">(when relevant)</span><input value={form.comparisonTarget} onChange={(e) => setField('comparisonTarget', e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-white" /></label>
        </div>
        <label className="flex items-start gap-3 text-sm leading-6 text-slate-300"><input required type="checkbox" checked={form.sellerAttestation} onChange={(e) => setField('sellerAttestation', e.target.checked)} className="mt-1" /><span>I confirm these materials are accurate and understand that sponsorship does not control COSHUMA editorial ratings, reviews, or organic rankings.</span></label>
        <button type="submit" disabled={submission.state === 'loading'} className="w-full rounded-xl bg-violet-500 px-4 py-3 text-sm font-black text-white hover:bg-violet-400 disabled:opacity-50">Submit campaign materials</button>
        {submission.message && <p className={`text-xs ${submission.state === 'error' ? 'text-rose-300' : 'text-slate-400'}`}>{submission.message}</p>}
      </form>

      <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-5">
        <div className="flex flex-wrap items-center justify-between gap-3"><div><div className="text-xs font-black uppercase tracking-[0.16em] text-cyan-300">Campaign report</div><p className="mt-1 text-xs text-slate-500">COSHUMA reports recorded impressions, sponsored clicks, and CTR. Signups, purchases, and advertiser revenue are not estimated.</p></div><button type="button" onClick={refreshReport} className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs font-black text-white hover:bg-white/10">Refresh report</button></div>
        {report?.loading && <p className="mt-4 text-xs text-slate-400">Loading report...</p>}
        {report?.error && <p className="mt-4 text-xs text-rose-300">{report.error}</p>}
        {report?.metrics && <div className="mt-4 grid grid-cols-3 gap-3"><div className="rounded-xl bg-black/20 p-3"><div className="text-[10px] uppercase text-slate-500">Impressions</div><div className="mt-1 text-xl font-black text-white">{report.metrics.impressions}</div></div><div className="rounded-xl bg-black/20 p-3"><div className="text-[10px] uppercase text-slate-500">Clicks</div><div className="mt-1 text-xl font-black text-white">{report.metrics.clicks}</div></div><div className="rounded-xl bg-black/20 p-3"><div className="text-[10px] uppercase text-slate-500">CTR</div><div className="mt-1 text-xl font-black text-white">{report.metrics.ctr}%</div></div></div>}
      </div>
    </div>
  );
}

function ActiveCheckout() {
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
      if (order.productId !== product.id || Number(order.amount) !== product.price || order.currency !== 'USD') {
        throw new Error('Server product verification failed.');
      }
      return order.orderId;
    };

    const onApprove = async ({ orderID }) => {
      setStatus({ type: 'loading', message: 'Verifying payment securely...' });
      const result = await captureVerifiedSponsorshipOrder(orderID);
      if (active) {
        setFulfillment(result);
        setStatus({ type: 'success', message: 'Payment confirmed and campaign created.' });
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

  if (fulfillment) return <CampaignSetup fulfillment={fulfillment} />;

  const statusColor = status.type === 'success'
    ? 'text-emerald-300'
    : status.type === 'error' ? 'text-rose-300' : 'text-slate-400';

  return (
    <div className="w-full max-w-xl" aria-live="polite">
      <div className="mb-4 rounded-2xl border border-white/10 bg-white/[0.035] p-4">
        <label className="block text-xs font-black uppercase tracking-[0.16em] text-violet-300" htmlFor="sponsorship-product">Choose placement and duration</label>
        <select id="sponsorship-product" value={productId} onChange={(event) => setProductId(event.target.value)} className="mt-3 w-full rounded-xl border border-white/10 bg-[#0b0d12] px-3 py-3 text-sm font-bold text-white outline-none focus:border-violet-400/50">
          {['Tool Page Sponsored', 'Buyer-Intent Featured', 'Comparison Premium'].map((group) => (
            <optgroup key={group} label={group}>{PRODUCTS.filter((item) => item.group === group).map((item) => <option key={item.id} value={item.id}>{item.days} days — ${item.price}</option>)}</optgroup>
          ))}
        </select>
        <div className="mt-3 flex items-center justify-between gap-3 text-sm"><span className="text-slate-400">{product.group} · {product.days} days</span><span className="text-lg font-black text-white">${product.price} USD</span></div>
        <p className="mt-2 text-xs leading-5 text-slate-500">Sponsored placement is clearly labeled and never purchases a positive review, rating, or organic ranking.</p>
      </div>
      <div ref={cardContainer} className="min-h-0" aria-label="Credit or debit card checkout" />
      {cardEligible && <div className="my-2 text-center text-[10px] font-bold uppercase tracking-widest text-slate-600">or</div>}
      <div ref={paypalContainer} className="min-h-12" aria-label="PayPal checkout" />
      <p className={`mt-3 text-xs ${statusColor}`}>{status.message}</p>
    </div>
  );
}

export default function SponsorshipCheckout() {
  if (!paymentConfig.checkoutEnabled) return null;
  if (CHECKOUT_MAINTENANCE) return <MaintenanceNotice />;
  return <ActiveCheckout />;
}
