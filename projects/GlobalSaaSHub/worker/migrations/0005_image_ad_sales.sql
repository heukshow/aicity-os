-- Versioned image-ad orders are separate from existing text-ad payment records.
CREATE TABLE ad_sales_applications (
 id TEXT PRIMARY KEY, reference TEXT NOT NULL UNIQUE, token_hash TEXT NOT NULL,
 advertiser TEXT NOT NULL, product TEXT NOT NULL, email TEXT NOT NULL, billing_name TEXT NOT NULL,
 claims TEXT NOT NULL, quote_json TEXT NOT NULL CHECK(json_valid(quote_json)),
 creative_json TEXT NOT NULL CHECK(json_valid(creative_json)),
 state TEXT NOT NULL DEFAULT 'submitted' CHECK(state IN ('submitted','approved','rejected','awaiting_payment','capturing','scheduled','paused','payment_review','refunded','cancelled')),
 review_notes TEXT, reviewed_at TEXT, reviewed_by TEXT,
 provider_order_id TEXT UNIQUE, capture_id TEXT UNIQUE, merchant_id TEXT, verified_at TEXT,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE ad_sales_assets (
 id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES ad_sales_applications(id) ON DELETE CASCADE,
 role TEXT NOT NULL, media_type TEXT NOT NULL CHECK(media_type IN ('image/png','image/jpeg','image/webp')),
 width INTEGER NOT NULL, height INTEGER NOT NULL, size INTEGER NOT NULL CHECK(size>0 AND size<=500000),
 sha256 TEXT NOT NULL, bytes BLOB NOT NULL CHECK(length(bytes)=size)
);
CREATE INDEX ad_sales_assets_application ON ad_sales_assets(application_id);
CREATE TABLE ad_sales_allocations (
 application_id TEXT NOT NULL REFERENCES ad_sales_applications(id), slot TEXT NOT NULL,
 seat INTEGER NOT NULL CHECK(seat BETWEEN 0 AND 2), start_at TEXT NOT NULL, end_at TEXT NOT NULL,
 hold_until TEXT NOT NULL, payment_lock INTEGER NOT NULL DEFAULT 0 CHECK(payment_lock IN (0,1)),
 PRIMARY KEY(application_id,slot)
);
CREATE INDEX ad_sales_capacity ON ad_sales_allocations(slot,seat,start_at,end_at,hold_until);
CREATE TABLE ad_sales_audit (id TEXT PRIMARY KEY, application_id TEXT NOT NULL, action TEXT NOT NULL, actor TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE ad_sales_readiness (id INTEGER PRIMARY KEY CHECK(id=1), checked_at TEXT NOT NULL, result_json TEXT NOT NULL CHECK(json_valid(result_json)));
CREATE TRIGGER ad_sales_terms_immutable BEFORE UPDATE OF reference,token_hash,advertiser,product,email,billing_name,claims,quote_json,creative_json ON ad_sales_applications BEGIN SELECT RAISE(ABORT,'Reviewed order terms are immutable'); END;
CREATE TRIGGER ad_sales_no_direct_publication BEFORE INSERT ON ad_sales_applications WHEN NEW.state!='submitted' BEGIN SELECT RAISE(ABORT,'An image application must start submitted'); END;
CREATE TRIGGER ad_sales_terminal_stop BEFORE UPDATE OF state ON ad_sales_applications WHEN OLD.state IN ('refunded','cancelled','rejected') AND NEW.state!=OLD.state BEGIN SELECT RAISE(ABORT,'A stopped application cannot restart'); END;
CREATE TRIGGER ad_sales_inventory_guard BEFORE INSERT ON ad_sales_allocations BEGIN
 SELECT CASE WHEN NEW.end_at<=NEW.start_at OR julianday(NEW.start_at) IS NULL OR julianday(NEW.end_at) IS NULL THEN RAISE(ABORT,'Invalid period') END;
 SELECT CASE WHEN EXISTS(SELECT 1 FROM ad_sales_allocations r WHERE r.slot=NEW.slot AND r.seat=NEW.seat AND r.application_id!=NEW.application_id AND r.start_at<NEW.end_at AND r.end_at>NEW.start_at AND (r.payment_lock=1 OR r.hold_until>strftime('%Y-%m-%dT%H:%M:%fZ','now'))) THEN RAISE(ABORT,'Inventory unavailable') END;
END;
CREATE TRIGGER ad_sales_publication_guard BEFORE UPDATE OF state ON ad_sales_applications WHEN NEW.state='scheduled' BEGIN
 SELECT CASE WHEN NEW.reviewed_at IS NULL OR length(trim(coalesce(NEW.reviewed_by,'')))=0 OR NEW.verified_at IS NULL OR length(trim(coalesce(NEW.provider_order_id,'')))=0 OR length(trim(coalesce(NEW.capture_id,'')))=0 OR length(trim(coalesce(NEW.merchant_id,'')))=0 THEN RAISE(ABORT,'Review and verified payment are required') END;
 SELECT CASE WHEN (SELECT COUNT(*) FROM ad_sales_allocations r WHERE r.application_id=NEW.id AND r.payment_lock=1 AND r.start_at=json_extract(NEW.quote_json,'$.startAt') AND r.end_at=json_extract(NEW.quote_json,'$.endAt'))!=json_array_length(NEW.quote_json,'$.slots') THEN RAISE(ABORT,'Every package position must be reserved') END;
END;

CREATE TRIGGER ad_sales_capture_guard BEFORE UPDATE OF state ON ad_sales_applications WHEN NEW.state='capturing' BEGIN
 SELECT CASE WHEN NEW.reviewed_at IS NULL OR NEW.reviewed_by IS NULL OR json_extract(NEW.quote_json,'$.startAt')<=strftime('%Y-%m-%dT%H:%M:%fZ','now') OR (SELECT COUNT(*) FROM ad_sales_allocations r WHERE r.application_id=NEW.id AND r.payment_lock=1 AND r.hold_until>strftime('%Y-%m-%dT%H:%M:%fZ','now'))!=json_array_length(NEW.quote_json,'$.slots') THEN RAISE(ABORT,'Valid reviewed payment reservations are required') END;
END;
CREATE TRIGGER ad_sales_lock_conflict BEFORE UPDATE OF payment_lock ON ad_sales_allocations WHEN NEW.payment_lock=1 BEGIN
 SELECT CASE WHEN EXISTS(SELECT 1 FROM ad_sales_allocations r WHERE r.slot=NEW.slot AND r.seat=NEW.seat AND r.application_id!=NEW.application_id AND r.start_at<NEW.end_at AND r.end_at>NEW.start_at AND (r.payment_lock=1 OR r.hold_until>strftime('%Y-%m-%dT%H:%M:%fZ','now'))) THEN RAISE(ABORT,'Inventory conflict during payment') END;
END;
