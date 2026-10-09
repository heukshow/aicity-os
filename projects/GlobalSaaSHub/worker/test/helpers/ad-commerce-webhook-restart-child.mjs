// Separate-process persistence fixture. All provider responses are synthetic.
import { readFileSync } from 'node:fs';
import { openTestStore } from './ad-commerce-disk-adapter.js';
import { SandboxAdPayments } from '../../src/ad-commerce-sandbox-payments.js';
import { SandboxAdWebhooks } from '../../src/ad-commerce-sandbox-webhooks.js';
import { TEST_ENV } from './ad-commerce-fixtures.js';
const [action, path] = process.argv.slice(2);
if (!['receive', 'drain'].includes(action) || !path?.endsWith('.ad-sandbox.sqlite')) throw new Error('Explicit test fixture required');
globalThis.fetch = () => { throw new Error('External network forbidden'); };
const f = openTestStore(path, { initialize: action === 'receive' });
let signatureRequests = 0, capturePosts = 0;
const fetchImpl = async (url, init = {}) => {
  if (new URL(url).origin !== 'https://api-m.sandbox.paypal.com') throw new Error('Unexpected host');
  if (new URL(url).pathname === '/v1/oauth2/token') return new Response('{"access_token":"SYNTHETIC"}');
  if (new URL(url).pathname === '/v1/notifications/verify-webhook-signature') {
    signatureRequests++; return new Response('{"verification_status":"SUCCESS"}');
  }
  if (init.method === 'POST' && new URL(url).pathname.endsWith('/capture')) capturePosts++;
  throw new Error('No matching order exists, so provider payment requests are forbidden');
};
try {
  if (action === 'receive') f.native.exec(readFileSync(new URL('../../sandbox-migrations/0001_webhook_retry.sql', import.meta.url), 'utf8'));
  const env = { ...TEST_ENV, PAYPAL_WEBHOOK_ID: 'SYNTHETIC-PERSISTED-WEBHOOK' };
  const existing = action === 'drain' ? f.native.prepare('SELECT next_attempt_at FROM ad_sandbox_webhook_receipts').get() : null;
  const clock = () => existing ? new Date(Date.parse(existing.next_attempt_at) + 1) : new Date();
  const payments = new SandboxAdPayments(f.store, { env, fetchImpl });
  const hooks = new SandboxAdWebhooks(f.store, payments, { env, fetchImpl, durableInbox: { clock, baseDelayMs: 1000 } });
  if (action === 'receive') {
    const headers = { 'content-type': 'application/json', 'paypal-transmission-id': 'SYNTHETIC-TX',
      'paypal-transmission-time': new Date().toISOString(), 'paypal-cert-url': 'https://api-m.sandbox.paypal.com/certs/test',
      'paypal-auth-algo': 'SHA256withRSA', 'paypal-transmission-sig': 'SYNTHETIC-SIGNATURE' };
    const event = { id: 'PERSISTED-EVENT', event_type: 'PAYMENT.CAPTURE.COMPLETED', resource: { id: 'NOT-ATTACHED-YET' } };
    const response = await hooks.handle(new Request('https://sandbox.example/webhook', { method: 'POST', headers, body: JSON.stringify(event) }));
    if (response.status !== 202) throw new Error('Expected durable unmatched event');
  } else await hooks.drain();
  const receipt = await hooks.receipt('PERSISTED-EVENT'), row = await hooks.inbox.row('PERSISTED-EVENT');
  console.log(JSON.stringify({ pid: process.pid, state: receipt.state, attempts: receipt.attempts,
    rawPersisted: JSON.parse(row.raw_event).id === 'PERSISTED-EVENT', signatureRequests, capturePosts,
    drainCompleted: (await hooks.recentRuns()).some(run => !!run.completed_at) }));
} finally { f.close(); }
