-- Additive: legacy orders/campaigns and their financial records are untouched.
CREATE TABLE IF NOT EXISTS sponsorship_applications (
  id TEXT PRIMARY KEY,
  reference TEXT NOT NULL UNIQUE,
  access_token_hash TEXT NOT NULL,
  company_name TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  contact_email TEXT NOT NULL,
  slot TEXT NOT NULL CHECK(slot IN ('tool-primary','buyer-intent-top','compare-decision-premium')),
  duration_days INTEGER NOT NULL CHECK(duration_days IN (7,30,90)),
  target_page TEXT NOT NULL,
  destination_url TEXT NOT NULL,
  headline TEXT NOT NULL,
  description TEXT NOT NULL,
  cta_text TEXT NOT NULL,
  desired_start_date TEXT,
  seller_attestation INTEGER NOT NULL CHECK(seller_attestation = 1),
  amount TEXT NOT NULL,
  currency TEXT NOT NULL CHECK(currency = 'USD'),
  payment_status TEXT NOT NULL DEFAULT 'unpaid' CHECK(payment_status IN ('unpaid','pending','verified','review','refunded')),
  review_status TEXT NOT NULL DEFAULT 'pending' CHECK(review_status IN ('pending','approved','rejected')),
  publication_status TEXT NOT NULL DEFAULT 'draft' CHECK(publication_status IN ('draft','published','paused','ended')),
  review_notes TEXT,
  approved_at TEXT,
  approved_by TEXT,
  starts_at TEXT,
  ends_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sponsorship_payments (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL UNIQUE REFERENCES sponsorship_applications(id),
  environment TEXT NOT NULL CHECK(environment IN ('live','sandbox')),
  provider_order_id TEXT,
  merchant_id TEXT NOT NULL,
  capture_id TEXT,
  amount TEXT NOT NULL,
  currency TEXT NOT NULL CHECK(currency = 'USD'),
  state TEXT NOT NULL DEFAULT 'created' CHECK(state IN ('created','pending','verified','review','refunded')),
  verified_at TEXT,
  last_checked_at TEXT,
  verification_reason TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(environment, provider_order_id),
  UNIQUE(environment, capture_id)
);

CREATE TABLE IF NOT EXISTS sponsorship_webhook_events (
  environment TEXT NOT NULL,
  event_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  related_order_id TEXT,
  capture_ids_json TEXT NOT NULL DEFAULT '[]',
  processed_at TEXT NOT NULL,
  PRIMARY KEY(environment, event_id)
);

CREATE TABLE IF NOT EXISTS sponsorship_audit_log (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL REFERENCES sponsorship_applications(id),
  action TEXT NOT NULL,
  actor TEXT NOT NULL,
  detail TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sponsorship_intake_limits (
  client_hash TEXT NOT NULL,
  bucket INTEGER NOT NULL,
  attempts INTEGER NOT NULL,
  PRIMARY KEY(client_hash, bucket)
);

CREATE INDEX IF NOT EXISTS sponsorship_active_inventory
  ON sponsorship_applications(target_page, slot, publication_status, starts_at, ends_at);

-- Immutable quote/creative: a changed offer requires a fresh reviewed application.
CREATE TRIGGER IF NOT EXISTS sponsorship_application_terms_immutable
BEFORE UPDATE OF reference,company_name,tool_name,slot,duration_days,target_page,destination_url,headline,description,cta_text,amount,currency ON sponsorship_applications
BEGIN
  SELECT RAISE(ABORT, 'Application terms are immutable');
END;

-- Parenthesize CASE expressions for D1 remote trigger parsing (workers-sdk#4727).
CREATE TRIGGER IF NOT EXISTS sponsorship_publish_guard
BEFORE UPDATE ON sponsorship_applications
WHEN NEW.publication_status = 'published'
BEGIN
  SELECT (CASE WHEN NEW.payment_status != 'verified' OR NEW.review_status != 'approved'
    OR julianday(NEW.approved_at) IS NULL OR length(trim(coalesce(NEW.approved_by,''))) = 0
    OR julianday(NEW.starts_at) IS NULL OR julianday(NEW.ends_at) IS NULL
    OR abs((julianday(NEW.ends_at)-julianday(NEW.starts_at))*86400 - NEW.duration_days*86400) > 0.01
    OR NOT EXISTS(SELECT 1 FROM sponsorship_payments p WHERE p.application_id = NEW.id
      AND p.state = 'verified' AND p.environment = 'live' AND length(trim(coalesce(p.capture_id,''))) > 0
      AND length(trim(coalesce(p.provider_order_id,''))) > 0 AND julianday(p.verified_at) IS NOT NULL
      AND length(trim(p.merchant_id)) > 0
      AND p.amount = NEW.amount AND p.currency = NEW.currency)
    THEN RAISE(ABORT, 'Verified payment, approved materials and a valid period are required') END);
  SELECT (CASE WHEN EXISTS(SELECT 1 FROM sponsorship_applications other WHERE other.id != NEW.id
    AND other.target_page = NEW.target_page AND other.slot = NEW.slot AND other.publication_status = 'published'
    AND other.starts_at < NEW.ends_at AND other.ends_at > NEW.starts_at)
    THEN RAISE(ABORT, 'Placement inventory conflicts with another campaign') END);
END;

CREATE TRIGGER IF NOT EXISTS sponsorship_no_published_insert
BEFORE INSERT ON sponsorship_applications WHEN NEW.publication_status = 'published'
BEGIN
  SELECT RAISE(ABORT, 'Publish only after a saved application is verified and approved');
END;

-- A late completion notification cannot resurrect reversed/refunded money.
CREATE TRIGGER IF NOT EXISTS sponsorship_refund_is_terminal
BEFORE UPDATE OF state ON sponsorship_payments WHEN OLD.state = 'refunded' AND NEW.state != 'refunded'
BEGIN
  SELECT RAISE(ABORT, 'A reversed payment cannot be reactivated');
END;

CREATE TRIGGER IF NOT EXISTS sponsorship_payment_stop
AFTER UPDATE OF state ON sponsorship_payments WHEN NEW.state IN ('review','refunded')
BEGIN
  UPDATE sponsorship_applications SET payment_status = NEW.state,
    publication_status = (CASE WHEN publication_status = 'published' THEN 'paused' ELSE publication_status END),
    updated_at = NEW.updated_at WHERE id = NEW.application_id;
END;
