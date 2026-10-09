import { SponsorshipError } from './sponsorship-domain.js';

const SLOT_LABELS = Object.freeze({
  'tool-primary': 'Tool Page Sponsored',
  'buyer-intent-top': 'Featured Buyer Guide Placement',
  'compare-decision-premium': 'Comparison Premium',
});

const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));

const toHex = (bytes) => Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');

export function approvalResumeConfigured(env) {
  return Boolean(env?.APPROVAL_LINK_SECRET && env?.ALLOWED_ORIGIN === 'https://coshuma.com');
}

export function approvalEmailConfigured(env) {
  return Boolean(env?.RESEND_API_KEY && approvalResumeConfigured(env));
}

export async function approvalResumeToken(application, env) {
  if (!approvalResumeConfigured(env) || application?.creative_mode !== 'image'
      || application?.review_status !== 'approved' || !application?.approved_at) return null;
  const material = `${application.id}:${application.approved_at}`;
  const key = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(env.APPROVAL_LINK_SECRET),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'],
  );
  return toHex(new Uint8Array(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(material))));
}

export function approvalEmailMarkerId(application) {
  if (!application?.id || !application?.approved_at) throw new SponsorshipError('Approved application identity is incomplete', 409);
  return `approval-email:${application.id}:${application.approved_at}`;
}

function paymentReturnUrl(application, token) {
  const payload = encodeURIComponent(`${application.id}.${token}`);
  return `https://coshuma.com/advertise.html#coshuma-ad=${payload}`;
}

function emailText(application, hold, returnUrl) {
  const slot = SLOT_LABELS[application.slot] || application.slot;
  return [
    application.renewal_of_application_id ? `Your COSHUMA advertising renewal ${application.reference} is ready.` : `Your COSHUMA advertising application ${application.reference} has been approved.`,
    '',
    `Product: ${application.tool_name}`,
    `Placement: ${slot}`,
    `Price: ${application.currency} ${application.amount}`,
    `Period: ${application.duration_days} days from actual activation`,
    `Reserved until: ${hold.expires_at}`,
    '',
    'Continue to your saved application and PayPal checkout:',
    returnUrl,
    '',
    'Use this COSHUMA link to continue the existing application. Do not send a separate PayPal payment.',
    'Payment is matched to the saved COSHUMA application and order before the advertisement can go live.',
    '',
    'COSHUMA Advertising',
    'support@coshuma.com',
  ].join('\n');
}

function emailHtml(application, hold, returnUrl) {
  const slot = SLOT_LABELS[application.slot] || application.slot;
  const rows = [
    ['Order reference', application.reference],
    ['Product', application.tool_name],
    ['Placement', slot],
    ['Price', `${application.currency} ${application.amount}`],
    ['Period', `${application.duration_days} days from actual activation`],
    ['Reserved until', hold.expires_at],
  ].map(([label, value]) => `<tr><td style="padding:7px 12px 7px 0;color:#64748b">${esc(label)}</td><td style="padding:7px 0;font-weight:600;color:#0f172a">${esc(value)}</td></tr>`).join('');
  return `<!doctype html><html><body style="margin:0;background:#f8fafc;font-family:Arial,sans-serif;color:#0f172a">
  <div style="max-width:640px;margin:0 auto;padding:32px 20px">
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:28px">
      <p style="margin:0 0 8px;color:#6d28d9;font-weight:700">COSHUMA Advertising</p>
      <h1 style="font-size:24px;line-height:1.25;margin:0 0 16px">${application.renewal_of_application_id ? 'Your priority renewal is ready' : 'Your placement is approved'}</h1>
      <p style="line-height:1.6;margin:0 0 18px">Your submitted advertising materials were approved and the selected position is temporarily reserved. Continue to your saved COSHUMA application to review the total and pay with PayPal.</p>
      <table style="border-collapse:collapse;width:100%;font-size:14px;margin:0 0 22px">${rows}</table>
      <p style="margin:0 0 24px"><a href="${esc(returnUrl)}" style="display:inline-block;background:#111827;color:#fff;text-decoration:none;padding:12px 18px;border-radius:8px;font-weight:700">Continue to payment</a></p>
      <p style="font-size:13px;line-height:1.55;color:#475569;margin:0">Use this COSHUMA link to continue the existing application. Do not send a separate PayPal payment. Payment is matched to the saved COSHUMA application and order before the advertisement can go live.</p>
    </div>
    <p style="font-size:12px;color:#64748b;line-height:1.5;margin:16px 4px">COSHUMA · support@coshuma.com</p>
  </div></body></html>`;
}

export async function sendApprovalEmail(application, hold, env, fetchImpl = fetch) {
  if (!approvalEmailConfigured(env)) throw new SponsorshipError('Approval email delivery is not configured', 503);
  if (application?.creative_mode !== 'image' || application?.review_status !== 'approved'
      || application?.publication_status !== 'draft' || !['unpaid', 'pending'].includes(application?.payment_status)) {
    throw new SponsorshipError('This application is not eligible for an approval payment email', 409);
  }
  if (!hold?.expires_at || hold.application_id !== application.id || hold.slot !== application.slot
      || !Number.isFinite(Date.parse(hold.expires_at)) || Date.parse(hold.expires_at) <= Date.now()) {
    throw new SponsorshipError('An active placement reservation is required before sending approval email', 409);
  }
  const resumeToken = await approvalResumeToken(application, env);
  if (!resumeToken) throw new SponsorshipError('Approval return access is unavailable', 503);
  const returnUrl = paymentReturnUrl(application, resumeToken);
  const payload = {
    from: 'COSHUMA Advertising <support@coshuma.com>',
    to: [application.contact_email],
    reply_to: 'support@coshuma.com',
    subject: application.renewal_of_application_id ? `Your COSHUMA priority renewal is ready — ${application.reference}` : `Your COSHUMA ad placement is approved — ${application.reference}`,
    text: emailText(application, hold, returnUrl),
    html: emailHtml(application, hold, returnUrl),
  };
  const response = await fetchImpl('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      authorization: `Bearer ${env.RESEND_API_KEY}`,
      'content-type': 'application/json',
      'idempotency-key': `coshuma-approval/${application.id}/${application.approved_at}`,
    },
    body: JSON.stringify(payload),
    redirect: 'error',
  });
  let result = {};
  try { result = await response.json(); } catch { /* Provider body is optional for failure handling. */ }
  if (!response.ok || typeof result.id !== 'string' || !result.id) {
    throw new SponsorshipError(`Approval email provider rejected the request (HTTP ${response.status})`, 502);
  }
  return { providerMessageId: result.id, returnUrl };
}
