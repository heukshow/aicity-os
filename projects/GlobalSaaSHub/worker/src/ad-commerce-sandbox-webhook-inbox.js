// Private durable inbox for an explicitly configured, isolated Sandbox DB.
// Migration: sandbox-migrations/0001_webhook_retry.sql. No runtime DDL or production binding.
import { AdError } from './ad-commerce-domain.js';
const HEADERS = ['paypal-transmission-id', 'paypal-transmission-time', 'paypal-cert-url', 'paypal-auth-algo', 'paypal-transmission-sig'];
const ACTORS = new Set(['sandbox_webhook', 'sandbox_webhook_retry']);
const iso = ms => new Date(ms).toISOString();
const canonical = value => Array.isArray(value) ? '[' + value.map(canonical).join(',') + ']'
  : value && typeof value === 'object' ? '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}'
    : JSON.stringify(value);
const digest = async value => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value))),
  byte => byte.toString(16).padStart(2, '0')).join('');
const safeError = code => { const error = new AdError(code, 503); error.retryCode = code; return error; };

export class SandboxWebhookInbox {
  constructor(store, { merchantId, webhookId, maxAttempts = 8, deadlineMs = 86400000,
    baseDelayMs = 60000, leaseMs = 300000, clock = () => new Date() } = {}) {
    if (!store?.db?.batch || !merchantId || !webhookId || typeof clock !== 'function' ||
        !Number.isInteger(maxAttempts) || maxAttempts < 1 || maxAttempts > 20 ||
        !Number.isInteger(deadlineMs) || deadlineMs < 1000 || deadlineMs > 7 * 86400000 ||
        !Number.isInteger(baseDelayMs) || baseDelayMs < 1000 || baseDelayMs > 3600000 ||
        !Number.isInteger(leaseMs) || leaseMs < 1000 || leaseMs > 900000) throw safeError('INVALID_SANDBOX_INBOX_CONFIGURATION');
    Object.assign(this, { store, merchantId, webhookId, maxAttempts, deadlineMs, baseDelayMs, leaseMs, clock });
  }
  now() { return this.clock().toISOString(); }
  q(sql, ...values) { return this.store.q(sql, ...values); }
  async ready() {
    await this.q('SELECT id FROM ad_sandbox_webhook_receipts LIMIT 1').all();
    await this.q('SELECT id FROM ad_sandbox_webhook_runs LIMIT 1').all();
  }
  row(id) {
    return this.q("SELECT * FROM ad_sandbox_webhook_receipts WHERE environment='sandbox' AND id=? AND merchant_id=? AND webhook_id=?",
      id, this.merchantId, this.webhookId).first();
  }
  async receipt(id) {
    const row = await this.row(id);
    if (!row) return null;
    return { id: row.id, eventType: row.event_type, providerOrder: row.provider_order,
      captureIds: JSON.parse(row.capture_ids_json), verificationStatus: row.verification_status,
      receivedAt: row.received_at, verifiedAt: row.verified_at, state: row.state, attempts: row.attempts,
      nextAttemptAt: row.next_attempt_at, retryDeadline: row.retry_deadline, leaseUntil: row.lease_until,
      lastActor: row.last_actor, lastError: row.last_error, processedAt: row.processed_at,
      result: row.result_json ? JSON.parse(row.result_json) : null };
  }
  async receive(event, raw, headers, ids, { receivedAt = this.now(), verifiedAt = this.now() } = {}) {
    if (![receivedAt, verifiedAt].every(value => typeof value === 'string' && Number.isFinite(Date.parse(value))) ||
        Date.parse(receivedAt) > Date.parse(verifiedAt)) throw safeError('INVALID_SANDBOX_RECEIPT_TIMING');
    const at = this.now(), captures = JSON.stringify(ids.captureIds);
    const rawHash = await digest(raw), eventHash = await digest(canonical(event));
    const signatureHeaders = JSON.stringify(Object.fromEntries(HEADERS.map(name => [name, headers.get(name)])));
    const result = await this.store.db.batch([
      this.q(`INSERT INTO ad_sale_events(environment,id,event_type,provider_order,capture_ids_json,received_at)
        VALUES('sandbox',?,?,?,?,?) ON CONFLICT(environment,id) DO NOTHING`,
        event.id, event.event_type, ids.providerOrder, captures, at),
      this.q(`INSERT INTO ad_sandbox_webhook_receipts(environment,id,webhook_id,merchant_id,event_type,
        provider_order,capture_ids_json,raw_event,raw_sha256,event_sha256,signature_headers_json,
        verification_status,received_at,verified_at,retry_deadline,state,next_attempt_at,processed_at)
        SELECT 'sandbox',?,?,?,?,?,?,?,?,?,?,'SUCCESS',?,?,?,
          CASE WHEN e.processed_at IS NULL THEN 'pending' ELSE 'processed' END,?,e.processed_at
        FROM ad_sale_events e WHERE e.environment='sandbox' AND e.id=? AND e.event_type=?
          AND e.provider_order IS ? AND e.capture_ids_json=?
        ON CONFLICT(environment,id) DO NOTHING`,
        event.id, this.webhookId, this.merchantId, event.event_type, ids.providerOrder, captures,
        raw, rawHash, eventHash, signatureHeaders, receivedAt, verifiedAt, iso(Date.parse(verifiedAt) + this.deadlineMs), at,
        event.id, event.event_type, ids.providerOrder, captures),
    ]);
    const row = await this.row(event.id);
    if (!row || row.event_sha256 !== eventHash || row.event_type !== event.event_type ||
        row.provider_order !== ids.providerOrder || row.capture_ids_json !== captures) {
      throw new AdError('A stored verified sandbox event identity cannot be replaced.', 409);
    }
    return { duplicate: result[1].meta.changes === 0, receipt: await this.receipt(event.id) };
  }
  async expireExhausted() {
    const at = this.now();
    await this.store.db.batch([this.q(`UPDATE ad_sandbox_webhook_receipts SET state='failed',lease_token=NULL,
      lease_until=NULL,last_error=CASE WHEN retry_deadline<=? THEN 'retry_deadline_exceeded' ELSE 'retry_attempts_exhausted' END
      WHERE environment='sandbox' AND merchant_id=? AND webhook_id=? AND state IN('pending','retry','processing')
        AND (state!='processing' OR lease_until<=?) AND (retry_deadline<=? OR attempts>=?)`,
      at, this.merchantId, this.webhookId, at, at, this.maxAttempts)]);
  }
  async claim(id, actor) {
    if (!ACTORS.has(actor)) throw safeError('INVALID_SANDBOX_RETRY_ACTOR');
    await this.expireExhausted();
    const at = this.now(), token = crypto.randomUUID(), until = iso(Date.parse(at) + this.leaseMs);
    const result = await this.store.db.batch([this.q(`UPDATE ad_sandbox_webhook_receipts SET state='processing',
      attempts=attempts+1,lease_token=?,lease_until=?,last_actor=?
      WHERE environment='sandbox' AND id=? AND merchant_id=? AND webhook_id=? AND attempts<? AND retry_deadline>?
        AND ((state IN('pending','retry') AND next_attempt_at<=?) OR (state='processing' AND lease_until<=?))`,
      token, until, actor, id, this.merchantId, this.webhookId, this.maxAttempts, at, at, at)]);
    if (result[0].meta.changes !== 1) return null;
    const row = await this.row(id);
    return row?.lease_token === token ? row : null;
  }
  async finish(row, result) {
    const at = this.now();
    const updates = await this.store.db.batch([
      this.q(`UPDATE ad_sandbox_webhook_receipts SET state='processed',processed_at=?,last_error=NULL,
        result_json=?,lease_token=NULL,lease_until=NULL WHERE environment='sandbox' AND id=? AND merchant_id=?
        AND webhook_id=? AND state='processing' AND lease_token=?`,
        at, JSON.stringify(result), row.id, this.merchantId, this.webhookId, row.lease_token),
      this.q(`UPDATE ad_sale_events SET processed_at=? WHERE environment='sandbox' AND id=? AND processed_at IS NULL
        AND EXISTS(SELECT 1 FROM ad_sandbox_webhook_receipts r WHERE r.environment='sandbox' AND r.id=?
          AND r.merchant_id=? AND r.webhook_id=? AND r.state='processed')`,
        at, row.id, row.id, this.merchantId, this.webhookId),
    ]);
    if (updates[0].meta.changes !== 1) throw safeError('SANDBOX_INBOX_LEASE_LOST');
    return this.receipt(row.id);
  }
  async retry(row, code, { terminal = false } = {}) {
    const at = this.now(), expires = Date.parse(row.retry_deadline);
    const failed = terminal || row.attempts >= this.maxAttempts || Date.parse(at) >= expires;
    const errorCode = terminal ? code : row.attempts >= this.maxAttempts ? 'retry_attempts_exhausted'
      : Date.parse(at) >= expires ? 'retry_deadline_exceeded' : code;
    const next = iso(Math.min(expires, Date.parse(at) + Math.min(3600000, this.baseDelayMs * 2 ** Math.max(0, row.attempts - 1))));
    await this.store.db.batch([this.q(`UPDATE ad_sandbox_webhook_receipts SET state=?,last_error=?,next_attempt_at=?,
      lease_token=NULL,lease_until=NULL WHERE environment='sandbox' AND id=? AND merchant_id=? AND webhook_id=?
      AND state='processing' AND lease_token=?`,
      failed ? 'failed' : 'retry', errorCode, next, row.id, this.merchantId, this.webhookId, row.lease_token)]);
    return this.receipt(row.id);
  }
  async due(limit) {
    if (!Number.isInteger(limit) || limit < 1 || limit > 50) throw safeError('INVALID_SANDBOX_DRAIN_LIMIT');
    await this.expireExhausted();
    const at = this.now();
    return (await this.q(`SELECT id FROM ad_sandbox_webhook_receipts WHERE environment='sandbox'
      AND merchant_id=? AND webhook_id=? AND attempts<? AND retry_deadline>?
      AND ((state IN('pending','retry') AND next_attempt_at<=?) OR (state='processing' AND lease_until<=?))
      ORDER BY next_attempt_at,id LIMIT ?`, this.merchantId, this.webhookId, this.maxAttempts, at, at, at, limit).all()).results;
  }
  async startRun(actor) {
    if (!ACTORS.has(actor)) throw safeError('INVALID_SANDBOX_RETRY_ACTOR');
    const id = crypto.randomUUID();
    await this.store.db.batch([this.q('INSERT INTO ad_sandbox_webhook_runs(id,actor,started_at) VALUES(?,?,?)', id, actor, this.now())]);
    return id;
  }
  async finishRun(id, counts, error = null) {
    await this.store.db.batch([this.q(`UPDATE ad_sandbox_webhook_runs SET completed_at=?,claimed=?,processed=?,retry=?,failed=?,error_code=? WHERE id=?`,
      this.now(), counts.claimed, counts.processed, counts.retry, counts.failed, error, id)]);
  }
  async recentRuns(limit = 10) {
    if (!Number.isInteger(limit) || limit < 1 || limit > 50) throw safeError('INVALID_SANDBOX_RUN_LIMIT');
    return (await this.q('SELECT * FROM ad_sandbox_webhook_runs ORDER BY started_at DESC,id DESC LIMIT ?', limit).all()).results;
  }
}
