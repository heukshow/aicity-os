-- ISOLATED SANDBOX DB ONLY. Never apply this migration to the production ORDERS DB.
-- Apply after 0004_sponsorship_sales.sql and 0005_image_ad_fulfilment.sql in the test DB.
CREATE TABLE IF NOT EXISTS ad_sandbox_webhook_receipts (
 environment TEXT NOT NULL DEFAULT 'sandbox' CHECK(environment='sandbox'),
 id TEXT NOT NULL, webhook_id TEXT NOT NULL, merchant_id TEXT NOT NULL,
 event_type TEXT NOT NULL, provider_order TEXT, capture_ids_json TEXT NOT NULL CHECK(json_valid(capture_ids_json)),
 raw_event TEXT NOT NULL CHECK(json_valid(raw_event)), raw_sha256 TEXT NOT NULL, event_sha256 TEXT NOT NULL,
 signature_headers_json TEXT NOT NULL CHECK(json_valid(signature_headers_json)),
 verification_status TEXT NOT NULL CHECK(verification_status='SUCCESS'),
 received_at TEXT NOT NULL, verified_at TEXT NOT NULL, retry_deadline TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'pending' CHECK(state IN('pending','processing','retry','processed','failed')),
 attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts>=0),
 next_attempt_at TEXT NOT NULL, lease_token TEXT, lease_until TEXT, last_actor TEXT,
 last_error TEXT, processed_at TEXT, result_json TEXT CHECK(result_json IS NULL OR json_valid(result_json)),
 PRIMARY KEY(environment,id), FOREIGN KEY(environment,id) REFERENCES ad_sale_events(environment,id)
);
CREATE INDEX IF NOT EXISTS ad_sandbox_webhook_due
 ON ad_sandbox_webhook_receipts(merchant_id,webhook_id,state,next_attempt_at,lease_until);
CREATE TRIGGER IF NOT EXISTS ad_sandbox_webhook_identity_immutable
 BEFORE UPDATE ON ad_sandbox_webhook_receipts
 WHEN NEW.environment!=OLD.environment OR NEW.id!=OLD.id OR NEW.webhook_id!=OLD.webhook_id
 OR NEW.merchant_id!=OLD.merchant_id OR NEW.event_type!=OLD.event_type
 OR NEW.provider_order IS NOT OLD.provider_order OR NEW.capture_ids_json!=OLD.capture_ids_json
 OR NEW.raw_event!=OLD.raw_event OR NEW.raw_sha256!=OLD.raw_sha256 OR NEW.event_sha256!=OLD.event_sha256
 OR NEW.signature_headers_json!=OLD.signature_headers_json OR NEW.verification_status!=OLD.verification_status
 OR NEW.received_at!=OLD.received_at OR NEW.verified_at!=OLD.verified_at OR NEW.retry_deadline!=OLD.retry_deadline
 BEGIN SELECT RAISE(ABORT,'Verified sandbox event evidence is immutable'); END;
CREATE TABLE IF NOT EXISTS ad_sandbox_webhook_runs (
 id TEXT PRIMARY KEY, actor TEXT NOT NULL, started_at TEXT NOT NULL, completed_at TEXT,
 claimed INTEGER NOT NULL DEFAULT 0, processed INTEGER NOT NULL DEFAULT 0,
 retry INTEGER NOT NULL DEFAULT 0, failed INTEGER NOT NULL DEFAULT 0, error_code TEXT
);
