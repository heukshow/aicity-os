-- Additive image-ad release schema. Existing sponsorship rows and payments remain valid.
ALTER TABLE sponsorship_applications ADD COLUMN creative_mode TEXT NOT NULL DEFAULT 'legacy_text'
  CHECK(creative_mode IN('legacy_text','image'));
ALTER TABLE sponsorship_applications ADD COLUMN submission_status TEXT NOT NULL DEFAULT 'draft'
  CHECK(submission_status IN('draft','submitted'));

CREATE TABLE IF NOT EXISTS sponsorship_assets (
  id TEXT PRIMARY KEY,
  application_id TEXT NOT NULL REFERENCES sponsorship_applications(id),
  role TEXT NOT NULL,
  mime TEXT NOT NULL CHECK(mime='image/png'),
  width INTEGER NOT NULL,
  height INTEGER NOT NULL,
  byte_size INTEGER NOT NULL CHECK(byte_size>0 AND byte_size<=500000),
  sha256 TEXT NOT NULL,
  data BLOB NOT NULL,
  UNIQUE(application_id,role),
  CHECK(length(data)=byte_size)
);

CREATE TABLE IF NOT EXISTS sponsorship_holds (
  slot TEXT PRIMARY KEY CHECK(slot IN('tool-primary','buyer-intent-top','compare-decision-premium')),
  application_id TEXT NOT NULL UNIQUE REFERENCES sponsorship_applications(id),
  expires_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS sponsorship_assets_application
  ON sponsorship_assets(application_id,role);
CREATE INDEX IF NOT EXISTS sponsorship_holds_expiry
  ON sponsorship_holds(expires_at);

CREATE TRIGGER IF NOT EXISTS sponsorship_asset_insert_guard
BEFORE INSERT ON sponsorship_assets
WHEN NOT EXISTS(
  SELECT 1 FROM sponsorship_applications a
  WHERE a.id=NEW.application_id AND a.creative_mode='image'
    AND a.submission_status='draft' AND a.publication_status='draft'
    AND a.review_status='pending'
    AND (NEW.role='logo' OR NEW.role=a.slot)
)
BEGIN SELECT RAISE(ABORT,'Assets require an editable image application and selected role'); END;

CREATE TRIGGER IF NOT EXISTS sponsorship_asset_update_guard
BEFORE UPDATE ON sponsorship_assets
WHEN OLD.id!=NEW.id OR OLD.application_id!=NEW.application_id OR OLD.role!=NEW.role
 OR NOT EXISTS(
  SELECT 1 FROM sponsorship_applications a
  WHERE a.id=NEW.application_id AND a.creative_mode='image'
    AND a.submission_status='draft' AND a.publication_status='draft'
    AND a.review_status='pending'
 )
BEGIN SELECT RAISE(ABORT,'Submitted image assets are immutable'); END;

CREATE TRIGGER IF NOT EXISTS sponsorship_asset_delete_guard
BEFORE DELETE ON sponsorship_assets
WHEN NOT EXISTS(
  SELECT 1 FROM sponsorship_applications a
  WHERE a.id=OLD.application_id AND a.creative_mode='image'
    AND a.submission_status='draft' AND a.publication_status='draft'
    AND a.review_status='pending'
 )
BEGIN SELECT RAISE(ABORT,'Submitted image assets cannot be deleted'); END;

CREATE TRIGGER IF NOT EXISTS sponsorship_image_review_guard
BEFORE UPDATE OF review_status ON sponsorship_applications
WHEN NEW.creative_mode='image' AND NEW.review_status='approved' AND (
  NEW.submission_status!='submitted'
  OR (SELECT count(*) FROM sponsorship_assets x WHERE x.application_id=NEW.id)!=2
  OR NOT EXISTS(SELECT 1 FROM sponsorship_assets x WHERE x.application_id=NEW.id AND x.role='logo')
  OR NOT EXISTS(SELECT 1 FROM sponsorship_assets x WHERE x.application_id=NEW.id AND x.role=NEW.slot)
)
BEGIN SELECT RAISE(ABORT,'Submitted logo and placement image are required before approval'); END;

CREATE TRIGGER IF NOT EXISTS sponsorship_image_publish_guard
BEFORE UPDATE OF publication_status ON sponsorship_applications
WHEN NEW.creative_mode='image' AND NEW.publication_status='published' AND (
  NEW.submission_status!='submitted'
  OR NEW.review_status!='approved'
  OR NEW.payment_status!='verified'
  OR (SELECT count(*) FROM sponsorship_assets x WHERE x.application_id=NEW.id)!=2
  OR NOT EXISTS(SELECT 1 FROM sponsorship_assets x WHERE x.application_id=NEW.id AND x.role='logo')
  OR NOT EXISTS(SELECT 1 FROM sponsorship_assets x WHERE x.application_id=NEW.id AND x.role=NEW.slot)
)
BEGIN SELECT RAISE(ABORT,'Verified payment and complete approved image assets are required'); END;

CREATE TRIGGER IF NOT EXISTS sponsorship_hold_insert_guard
BEFORE INSERT ON sponsorship_holds
WHEN NOT EXISTS(
  SELECT 1 FROM sponsorship_applications a
  WHERE a.id=NEW.application_id AND a.creative_mode='image'
    AND a.submission_status='submitted' AND a.review_status='approved'
    AND a.publication_status='draft' AND a.payment_status IN('unpaid','pending')
    AND a.slot=NEW.slot
)
OR EXISTS(
  SELECT 1 FROM sponsorship_applications other
  WHERE other.id!=NEW.application_id AND other.slot=NEW.slot
    AND other.publication_status='published'
    AND other.ends_at>strftime('%Y-%m-%dT%H:%M:%fZ','now')
)
BEGIN SELECT RAISE(ABORT,'Placement cannot be reserved for this application'); END;
