import inventory from '../../data/sponsorship-inventory.json' with { type: 'json' };

const pricesFor = (slot) => Object.fromEntries([7, 30, 90].map((days) => {
  const amount = inventory.placements[slot].pricing[`${days}_days`];
  if (!Number.isInteger(amount) || amount <= 0) throw new Error('Invalid sponsorship catalogue price');
  return [days, amount.toFixed(2)];
}));

// The server owns price, duration and the explicitly sellable page/slot pairs.
// Expanding this list requires an editorial/inventory review and a code change.
export const CATALOG = Object.freeze([
  { slot: 'tool-primary', label: 'Tool Page Sponsored', prices: pricesFor('tool-primary'), allowedPages: ['/tool/pipedrive.html'] },
  { slot: 'buyer-intent-top', label: 'Buyer-Intent Featured', prices: pricesFor('buyer-intent-top'), allowedPages: ['/best/claap-sales-follow-up-ai.html'] },
  { slot: 'compare-decision-premium', label: 'Comparison Premium', prices: pricesFor('compare-decision-premium'), allowedPages: ['/compare/semrush-vs-frase.html'] },
]);

export class SponsorshipError extends Error {
  constructor(message, status = 422) { super(message); this.name = 'SponsorshipError'; this.status = status; }
}

export function quoteFor({ slot, durationDays, targetPage } = {}) {
  const product = CATALOG.find((entry) => entry.slot === slot);
  const days = Number(durationDays);
  if (!product || !Number.isInteger(days) || ![7, 30, 90].includes(days)) throw new SponsorshipError('Choose a listed placement and duration');
  if (typeof targetPage !== 'string' || !product.allowedPages.includes(targetPage)) throw new SponsorshipError('This page is not available for this placement');
  return { slot, durationDays: days, targetPage, amount: product.prices[days], currency: 'USD' };
}

function textField(value, label, max, min = 1) {
  if (typeof value !== 'string') throw new SponsorshipError(`${label} is required`);
  const result = value.trim();
  if (result.length < min || result.length > max || /[\u0000-\u001f\u007f<>]/.test(result)) throw new SponsorshipError(`${label} must be plain text, ${min}-${max} characters`);
  return result;
}

export function destinationUrl(value) {
  let url;
  try { url = new URL(value); } catch { throw new SponsorshipError('A valid HTTPS destination is required'); }
  const hostname = url.hostname.toLowerCase();
  if (url.protocol !== 'https:' || url.username || url.password || String(value).length > 1000
      || hostname === 'localhost' || hostname.endsWith('.local') || !hostname.includes('.')
      || /^\d+(\.\d+){3}$/.test(hostname) || hostname.includes(':')) throw new SponsorshipError('Use a public HTTPS destination without credentials');
  return url.href;
}

export function validateApplication(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new SponsorshipError('An application object is required');
  if ('amount' in input || 'currency' in input || 'price' in input) throw new SponsorshipError('The server determines the price and currency');
  const quote = quoteFor(input);
  const contactEmail = textField(input.contactEmail, 'Contact email', 254);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contactEmail)) throw new SponsorshipError('A valid contact email is required');
  if (input.sellerAttestation !== true) throw new SponsorshipError('Confirm that you are authorised to submit the product and claims');
  const desiredStartDate = input.desiredStartDate || null;
  const requestedDate = desiredStartDate ? new Date(`${desiredStartDate}T00:00:00.000Z`) : null;
  if (desiredStartDate && (!/^\d{4}-\d{2}-\d{2}$/.test(desiredStartDate) || !Number.isFinite(requestedDate.getTime()) || requestedDate.toISOString().slice(0, 10) !== desiredStartDate)) throw new SponsorshipError('Use a valid requested start date');
  return {
    companyName: textField(input.companyName, 'Company name', 120),
    toolName: textField(input.toolName, 'Tool name', 120), contactEmail,
    destinationUrl: destinationUrl(input.destinationUrl),
    headline: textField(input.headline, 'Headline', 80, 5),
    description: textField(input.description, 'Description', 240, 20),
    ctaText: textField(input.ctaText, 'Button text', 30, 2),
    desiredStartDate, sellerAttestation: true, ...quote,
  };
}

export function paypalPayload(application, merchantId) {
  if (!merchantId) throw new SponsorshipError('Payment configuration is unavailable', 503);
  return {
    intent: 'CAPTURE',
    purchase_units: [{
      reference_id: application.id,
      custom_id: application.id,
      invoice_id: application.reference,
      description: `${application.company_name.slice(0, 40)} | ${application.tool_name.slice(0, 40)} | ${application.slot} ${application.duration_days} days`.slice(0, 127),
      payee: { merchant_id: merchantId },
      amount: { currency_code: application.currency, value: application.amount },
    }],
  };
}

export function verifyPayPalPayment({ order, capture, application, payment, merchantId, environment }) {
  const fail = () => { throw new SponsorshipError('PayPal payment evidence does not match this application', 409); };
  if (environment !== 'live' || payment?.environment !== 'live' || !merchantId || payment.merchant_id !== merchantId) fail();
  const expected = quoteFor({ slot: application.slot, durationDays: application.duration_days, targetPage: application.target_page });
  if (application.amount !== expected.amount || application.currency !== expected.currency) fail();
  if (!payment.provider_order_id || order?.id !== payment.provider_order_id || order.status !== 'COMPLETED') fail();
  if (!Array.isArray(order.purchase_units) || order.purchase_units.length !== 1) fail();
  const unit = order.purchase_units[0];
  if (unit.custom_id !== application.id || unit.invoice_id !== application.reference || unit.payee?.merchant_id !== merchantId) fail();
  const matchesAmount = (amount) => amount?.currency_code === application.currency && amount.value === application.amount;
  if (!matchesAmount(unit.amount)) fail();
  const captures = unit.payments?.captures;
  if (!Array.isArray(captures) || captures.length !== 1) fail();
  const item = captures[0];
  if (!item.id || item.id !== capture?.id || item.status !== 'COMPLETED' || capture.status !== 'COMPLETED') fail();
  if (!matchesAmount(item.amount) || !matchesAmount(capture.amount)) fail();
  if (capture.payee?.merchant_id !== merchantId || capture.supplementary_data?.related_ids?.order_id !== order.id) fail();
  if (capture.invoice_id && capture.invoice_id !== application.reference) fail();
  if (capture.custom_id && capture.custom_id !== application.id) fail();
  return { captureId: capture.id, providerOrderId: order.id, merchantId, amount: application.amount, currency: application.currency, environment: 'live' };
}

export function publicationPeriod(application, requestedStart, now = new Date()) {
  const start = new Date(requestedStart || now.toISOString());
  if (!Number.isFinite(start.getTime()) || start.getTime() < now.getTime() - 1000) throw new SponsorshipError('Publication must start now or in the future');
  const startsAt = new Date(Math.max(start.getTime(), now.getTime())).toISOString();
  const endsAt = new Date(Date.parse(startsAt) + application.duration_days * 86400000).toISOString();
  return { startsAt, endsAt };
}

export function publicStatus(application, now = new Date()) {
  if (application.payment_status === 'refunded') return 'payment_reversed';
  if (application.review_status === 'rejected') return 'rejected';
  if (application.publication_status === 'paused') return 'paused';
  if (application.publication_status === 'ended' || (application.ends_at && Date.parse(application.ends_at) <= now.getTime())) return 'ended';
  if (application.publication_status === 'published') return Date.parse(application.starts_at) > now.getTime() ? 'scheduled' : 'active';
  if (application.payment_status !== 'verified') return application.payment_status === 'review' ? 'payment_review' : 'awaiting_payment';
  return application.review_status === 'approved' ? 'ready_to_publish' : 'pending_review';
}

export function captureIdFromRefundLink(event) {
  const links = Array.isArray(event?.resource?.links) ? event.resource.links : [];
  for (const link of links) {
    if (link.rel !== 'up' || typeof link.href !== 'string') continue;
    try {
      const url = new URL(link.href);
      if (url.protocol !== 'https:' || !['api-m.paypal.com', 'api.paypal.com'].includes(url.hostname)
          || url.username || url.password || url.port || url.search || url.hash) continue;
      const match = /^\/v2\/payments\/captures\/([A-Za-z0-9_-]{1,128})$/.exec(url.pathname);
      if (match) return match[1];
    } catch { /* A provider link is never fetched directly. */ }
  }
  return null;
}
