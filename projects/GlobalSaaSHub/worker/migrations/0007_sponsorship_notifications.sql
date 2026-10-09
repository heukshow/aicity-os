-- Additive transactional-notification outbox for image-ad approval emails.
-- Existing sponsorship, payment, campaign and legacy notification tables are untouched.

CREATE TABLE IF NOT EXISTS sponsorship_notifications (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL REFERENCES sponsorship_applications(id),
  template TEXT NOT NULL CHECK(template IN ('approval_payment')),
  recipient_email TEXT NOT NULL,
  provider TEXT NOT NULL CHECK(provider IN ('resend')),
  provider_message_id TEXT,
  status TEXT NOT NULL DEFAULT 'queued' CHECK(status IN ('queued','sent','failed')),
  attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts >= 0),
  last_error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  sent_at TEXT,
  UNIQUE(application_id, template)
);

CREATE INDEX IF NOT EXISTS sponsorship_notifications_delivery
  ON sponsorship_notifications(status, attempts, created_at);
