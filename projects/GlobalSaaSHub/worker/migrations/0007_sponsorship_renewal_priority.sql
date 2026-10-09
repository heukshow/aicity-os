-- Priority renewal path for an existing paid image advertiser.
-- A renewal is a new paid period linked to the immediately preceding campaign.
ALTER TABLE sponsorship_applications ADD COLUMN renewal_of_application_id TEXT;

CREATE INDEX IF NOT EXISTS sponsorship_renewal_parent
  ON sponsorship_applications(renewal_of_application_id);

CREATE UNIQUE INDEX IF NOT EXISTS sponsorship_one_open_renewal_per_parent
  ON sponsorship_applications(renewal_of_application_id)
  WHERE renewal_of_application_id IS NOT NULL AND publication_status IN ('draft','published');

DROP TRIGGER IF EXISTS sponsorship_hold_insert_guard;
CREATE TRIGGER sponsorship_hold_insert_guard
BEFORE INSERT ON sponsorship_holds
WHEN NOT EXISTS(
  SELECT 1 FROM sponsorship_applications a
  WHERE a.id=NEW.application_id AND a.creative_mode='image'
    AND a.submission_status='submitted' AND a.review_status='approved'
    AND a.publication_status='draft' AND a.payment_status IN('unpaid','pending')
    AND a.slot=NEW.slot
)
OR EXISTS(
  SELECT 1
  FROM sponsorship_applications other
  JOIN sponsorship_applications renewal ON renewal.id=NEW.application_id
  WHERE other.id!=NEW.application_id
    AND other.slot=NEW.slot
    AND other.publication_status='published'
    AND other.ends_at>strftime('%Y-%m-%dT%H:%M:%fZ','now')
    AND NOT (
      renewal.renewal_of_application_id=other.id
      AND renewal.target_page=other.target_page
      AND other.payment_status='verified'
      AND other.review_status='approved'
    )
)
BEGIN SELECT RAISE(ABORT,'Placement cannot be reserved for this application'); END;
