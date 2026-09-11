ALTER TABLE orders ADD COLUMN product_id TEXT;
ALTER TABLE orders ADD COLUMN payer_name TEXT;
ALTER TABLE orders ADD COLUMN payer_email TEXT;
ALTER TABLE orders ADD COLUMN paid_at TEXT;

CREATE TABLE IF NOT EXISTS campaigns (
  id TEXT PRIMARY KEY,
  order_id TEXT NOT NULL UNIQUE,
  provider_order_id TEXT NOT NULL UNIQUE,
  product_id TEXT NOT NULL,
  placement TEXT NOT NULL,
  duration_days INTEGER NOT NULL,
  price_usd TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('awaiting_payment','awaiting_assets','pending_review','ready_to_publish','published','ended','rejected','refunded')),
  advertiser_name TEXT,
  contact_email TEXT,
  intake_token TEXT NOT NULL UNIQUE,
  report_token TEXT NOT NULL UNIQUE,
  starts_at TEXT,
  ends_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(order_id) REFERENCES orders(id)
);

CREATE INDEX IF NOT EXISTS idx_campaigns_status_ends ON campaigns(status, ends_at);
CREATE INDEX IF NOT EXISTS idx_campaigns_contact ON campaigns(contact_email);

CREATE TABLE IF NOT EXISTS campaign_assets (
  campaign_id TEXT PRIMARY KEY,
  company_name TEXT NOT NULL,
  product_name TEXT NOT NULL,
  contact_email TEXT NOT NULL,
  destination_url TEXT NOT NULL,
  logo_url TEXT NOT NULL,
  headline TEXT NOT NULL,
  description TEXT NOT NULL,
  cta_text TEXT NOT NULL,
  desired_start_date TEXT,
  target_page TEXT,
  comparison_target TEXT,
  seller_attestation INTEGER NOT NULL DEFAULT 0,
  validation_status TEXT NOT NULL CHECK (validation_status IN ('pending','valid','needs_review','invalid')),
  validation_notes TEXT,
  submitted_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);

CREATE TABLE IF NOT EXISTS campaign_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  campaign_id TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type IN ('sponsored_impression','sponsored_click')),
  page TEXT,
  placement TEXT,
  destination_url TEXT,
  occurred_at TEXT NOT NULL,
  FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);

CREATE INDEX IF NOT EXISTS idx_campaign_events_campaign_type ON campaign_events(campaign_id, event_type, occurred_at);

CREATE TABLE IF NOT EXISTS campaign_reports (
  id TEXT PRIMARY KEY,
  campaign_id TEXT NOT NULL,
  report_type TEXT NOT NULL CHECK (report_type IN ('interim','renewal','final')),
  period_start TEXT NOT NULL,
  period_end TEXT NOT NULL,
  impressions INTEGER NOT NULL DEFAULT 0,
  clicks INTEGER NOT NULL DEFAULT 0,
  ctr REAL NOT NULL DEFAULT 0,
  generated_at TEXT NOT NULL,
  delivery_status TEXT NOT NULL CHECK (delivery_status IN ('queued','sent','failed')) DEFAULT 'queued',
  delivered_at TEXT,
  FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);

CREATE TABLE IF NOT EXISTS notification_outbox (
  id TEXT PRIMARY KEY,
  campaign_id TEXT,
  recipient_email TEXT NOT NULL,
  template TEXT NOT NULL,
  subject TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('queued','sent','failed')) DEFAULT 'queued',
  created_at TEXT NOT NULL,
  sent_at TEXT,
  FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);

CREATE INDEX IF NOT EXISTS idx_outbox_status_created ON notification_outbox(status, created_at);
