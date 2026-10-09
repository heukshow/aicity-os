import { SponsorshipError } from './sponsorship-domain.js';

const encoder = new TextEncoder();
const decoder = new TextDecoder();
const DAY = 86400000;
const SLOT_LABELS = Object.freeze({
  'tool-primary': 'Tool Page Sponsored',
  'buyer-intent-top': 'Featured Buyer Guide Placement',
  'compare-decision-premium': 'Comparison Premium',
});

const safeText = (value) => String(value ?? '').replace(/[\u0000-\u001f\u007f]/g, ' ').trim();
const escapeHtml = (value) => safeText(value).replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));

function b64url(bytes) {
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function fromB64url(value) {
  if (typeof value !== 'string' || !/^[A-Za-z0-9_-]+$/.test(value)) throw new SponsorshipError('Invalid application return link', 401);
  const padded = value.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - value.length % 4) % 4);
  try {
    const binary = atob(padded);
    return Uint8Array.from(binary, (character) => character.charCodeAt(0));
  } catch {
    throw new SponsorshipError('Invalid application return link', 401);
  }
}

async function signingKey(env) {
  const secret = String(env.AD_RESUME_LINK_SECRET || '');
  if (secret.length < 32) throw new SponsorshipError('Advertising return links are not configured', 503);
  return crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
}

export function approvalEmailConfigured(env) {
  return typeof env.RESEND_API_KEY === 'string' && env.RESEND_API_KEY.length >= 20
    && typeof env.AD_RESUME_LINK_SECRET === 'string' && env.AD_RESUME_LINK_SECRET.length >= 32;
}

export async function issueResumeToken(application, env, now = Date.now(), ttlMs = 7 * DAY) {
  if (!application?.id || !/^[a-f0-9-]{36}$/.test(application.id)) throw new SponsorshipError('Application return link cannot be issued', 409);
  if (!Number.isFinite(now) || !Number.isFinite(ttlMs) || ttlMs < 60000 || ttlMs > 30 * DAY) throw new SponsorshipError('Application return link lifetime is invalid', 500);
  const payload = b64url(encoder.encode(JSON.stringify({
    v: 1,
    applicationId: application.id,
    exp: Math.floor((now + ttlMs) / 1000),
  })));
  const signature = new Uint8Array(await crypto.subtle.sign('HMAC', await signingKey(env), encoder.encode(payload)));
  return `r1.${payload}.${b64url(signature)}`;
}

export async function verifyResumeToken(token, env, now = Date.now()) {
  if (typeof token !== 'string' || token.length < 40 || token.length > 700) throw new SponsorshipError('Invalid application return link', 401);
  const parts = token.split('.');
  if (parts.length !== 3 || parts[0] !== 'r1') throw new SponsorshipError('Invalid application return link', 401);
  const [_, payload, signatureText] = parts;
  const verified = await crypto.subtle.verify(
    'HMAC',
    await signingKey(env),
    fromB64url(signatureText),
    encoder.encode(payload),
  );
  if (!verified) throw new SponsorshipError('Invalid application return link', 401);
  let data;
  try { data = JSON.parse(decoder.decode(fromB64url(payload))); }
  catch { throw new SponsorshipError('Invalid application return link', 401); }
  if (data?.v !== 1 || typeof data.applicationId !== 'string' || !/^[a-f0-9-]{36}$/.test(data.applicationId)
      || !Number.isInteger(data.exp) || data.exp * 1000 <= now) {
    throw new SponsorshipError(data?.exp * 1000 <= now ? 'Application return link has expired' : 'Invalid application return link', 401);
  }
  return { applicationId: data.applicationId, expiresAt: new Date(data.exp * 1000).toISOString() };
}

export function approvalEmail(application, resumeUrl, reservationUntil) {
  const label = SLOT_LABELS[application.slot] || 'Sponsored placement';
  const amount = /^\d+(?:\.\d{1,2})?$/.test(String(application.amount || '')) ? Number(application.amount).toFixed(2) : null;
  if (!amount || application.currency !== 'USD' || !/^https:\/\/coshuma\.com\/advertise\.html#resume=/.test(resumeUrl)
      || !Number.isFinite(Date.parse(reservationUntil))) {
    throw new SponsorshipError('Approval email cannot be prepared from the saved application', 409);
  }
  const subject = `COSHUMA ad approved — complete payment · ${safeText(application.reference)}`;
  const rows = [
    ['Order reference', application.reference],
    ['Company', application.company_name],
    ['Product', application.tool_name],
    ['Placement', label],
    ['Period', `${application.duration_days} days`],
    ['Total', `USD ${amount}`],
    ['Reserved until', reservationUntil],
  ];
  const text = [
    'Your COSHUMA advertising materials have been approved and the selected position is reserved.',
    '',
    ...rows.map(([key, value]) => `${key}: ${safeText(value)}`),
    '',
    'Complete payment:',
    resumeUrl,
    '',
    'The paid campaign period starts when the approved advertisement actually goes live, not when payment is submitted.',
    'If the reservation has expired when you return, COSHUMA will check whether the position can be reserved again before offering payment.',
    'Do not send a separate PayPal transfer. Use the payment flow linked to this order so the payment can be matched automatically.',
    '',
    'Questions: support@coshuma.com',
  ].join('\n');
  const table = rows.map(([key, value]) => `<tr><th align="left" style="padding:6px 12px 6px 0;color:#60656f;font-weight:600">${escapeHtml(key)}</th><td style="padding:6px 0;color:#111827">${escapeHtml(value)}</td></tr>`).join('');
  const html = `<!doctype html><html><body style="margin:0;background:#f5f7fa;font-family:Arial,Helvetica,sans-serif;color:#111827">
  <div style="max-width:640px;margin:0 auto;padding:28px 18px"><div style="background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:26px">
    <div style="font-size:13px;letter-spacing:.08em;font-weight:700;color:#475569">COSHUMA · ADVERTISING</div>
    <h1 style="font-size:24px;line-height:1.25;margin:12px 0 10px">Your advertising materials are approved.</h1>
    <p style="line-height:1.6;margin:0 0 18px;color:#374151">The selected position is reserved. Review the order details below, then continue to the verified PayPal checkout for this application.</p>
    <table role="presentation" style="border-collapse:collapse;width:100%;font-size:14px;margin:6px 0 22px">${table}</table>
    <p style="margin:0 0 22px"><a href="${escapeHtml(resumeUrl)}" style="display:inline-block;background:#111827;color:#fff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:9px">Complete payment</a></p>
    <p style="font-size:13px;line-height:1.6;color:#4b5563;margin:0 0 8px">Your paid period begins only when the approved advertisement goes live. If this reservation has expired, the return link checks current availability again before payment.</p>
    <p style="font-size:13px;line-height:1.6;color:#4b5563;margin:0">Do not send a separate PayPal transfer. For help, reply to this email or contact <a href="mailto:support@coshuma.com">support@coshuma.com</a>.</p>
  </div></div></body></html>`;
  return { subject, text, html };
}

export async function sendApprovalEmail(env, application, resumeUrl, reservationUntil, fetcher = fetch) {
  if (!approvalEmailConfigured(env)) throw new SponsorshipError('Approval email delivery is not configured', 503);
  const email = approvalEmail(application, resumeUrl, reservationUntil);
  let response;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    response = await fetcher('https://api.resend.com/emails', {
      method: 'POST',
      signal: controller.signal,
      headers: {
        authorization: `Bearer ${env.RESEND_API_KEY}`,
        'content-type': 'application/json',
        'idempotency-key': `coshuma-ad-approval/${application.id}`,
      },
      body: JSON.stringify({
        from: env.AD_EMAIL_FROM || 'COSHUMA Ads <support@coshuma.com>',
        to: [application.contact_email],
        reply_to: 'support@coshuma.com',
        subject: email.subject,
        text: email.text,
        html: email.html,
      }),
    });
  } catch {
    throw new SponsorshipError('Approval email delivery could not be confirmed', 502);
  } finally {
    clearTimeout(timer);
  }
  const result = await response.json().catch(() => ({}));
  if (!response.ok || typeof result.id !== 'string' || !result.id) {
    throw new SponsorshipError('Approval email delivery could not be confirmed', 502);
  }
  return { provider: 'resend', messageId: result.id };
}
