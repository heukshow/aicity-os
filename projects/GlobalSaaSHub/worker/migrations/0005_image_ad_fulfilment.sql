-- Additive migration. Existing orders, payments and private dashboards are unchanged.
CREATE TABLE IF NOT EXISTS ad_sale_orders (
 id TEXT PRIMARY KEY, reference TEXT NOT NULL UNIQUE, access_hash TEXT NOT NULL,
 product TEXT NOT NULL, catalog_version TEXT NOT NULL, days INTEGER NOT NULL CHECK(days IN(7,30,90)),
 amount TEXT NOT NULL, currency TEXT NOT NULL CHECK(currency='USD'),
 quote_json TEXT NOT NULL CHECK(json_valid(quote_json)), company TEXT NOT NULL,
 product_name TEXT NOT NULL, email TEXT NOT NULL, materials_json TEXT NOT NULL CHECK(json_valid(materials_json)),
 rights_confirmed INTEGER NOT NULL CHECK(rights_confirmed=1),
 state TEXT NOT NULL DEFAULT 'draft' CHECK(state IN('draft','submitted','approved','checkout','capturing','active','ended','rejected','held','refunded','cancelled')),
 approved_by TEXT, approved_at TEXT, review_notes TEXT,
 provider_order TEXT UNIQUE, capture_id TEXT UNIQUE, merchant_id TEXT,
 payment_environment TEXT CHECK(payment_environment IN('live','sandbox')), payment_verified_at TEXT,
 hold_until TEXT, starts_at TEXT, ends_at TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ad_sale_files (
 id TEXT PRIMARY KEY, order_id TEXT NOT NULL REFERENCES ad_sale_orders(id), role TEXT NOT NULL,
 mime TEXT NOT NULL CHECK(mime IN('image/png','image/jpeg','image/webp')),
 width INTEGER NOT NULL, height INTEGER NOT NULL, byte_size INTEGER NOT NULL CHECK(byte_size>0 AND byte_size<=500000),
 sha256 TEXT NOT NULL, data BLOB NOT NULL, UNIQUE(order_id,role), CHECK(length(data)=byte_size)
);
CREATE TABLE IF NOT EXISTS ad_sale_holds (
 slot TEXT NOT NULL, lane INTEGER NOT NULL CHECK(lane BETWEEN 1 AND 3),
 order_id TEXT NOT NULL REFERENCES ad_sale_orders(id), expires_at TEXT NOT NULL,
 PRIMARY KEY(slot,lane), UNIQUE(order_id,slot)
);
CREATE TABLE IF NOT EXISTS ad_sale_events (
 environment TEXT NOT NULL CHECK(environment IN('live','sandbox')), id TEXT NOT NULL, event_type TEXT NOT NULL,
 provider_order TEXT, capture_ids_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(capture_ids_json)),
 received_at TEXT NOT NULL, processed_at TEXT, PRIMARY KEY(environment,id)
);
CREATE TABLE IF NOT EXISTS ad_sale_audit (
 id TEXT PRIMARY KEY, order_id TEXT NOT NULL REFERENCES ad_sale_orders(id), action TEXT NOT NULL,
 actor TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ad_sale_metric_events (
 nonce TEXT NOT NULL, order_id TEXT NOT NULL, slot TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN('impression','click')), expires_at TEXT NOT NULL,
 PRIMARY KEY(nonce,order_id,slot,kind)
);
CREATE TABLE IF NOT EXISTS ad_sale_metrics (
 order_id TEXT NOT NULL REFERENCES ad_sale_orders(id), slot TEXT NOT NULL, day TEXT NOT NULL,
 impressions INTEGER NOT NULL DEFAULT 0, clicks INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(order_id,slot,day)
);
CREATE INDEX IF NOT EXISTS ad_sale_live ON ad_sale_orders(state,ends_at);
CREATE INDEX IF NOT EXISTS ad_sale_files_order ON ad_sale_files(order_id,role);
CREATE INDEX IF NOT EXISTS ad_sale_holds_order ON ad_sale_holds(order_id,expires_at);
CREATE INDEX IF NOT EXISTS ad_sale_events_order ON ad_sale_events(environment,provider_order);
CREATE TRIGGER IF NOT EXISTS ad_sale_new_draft BEFORE INSERT ON ad_sale_orders WHEN NEW.state!='draft'
BEGIN SELECT RAISE(ABORT,'New orders must start as drafts'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_quote_immutable BEFORE UPDATE OF id,reference,access_hash,product,catalog_version,days,amount,currency,quote_json ON ad_sale_orders
BEGIN SELECT RAISE(ABORT,'Quoted order terms cannot change'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_material_lock BEFORE UPDATE OF materials_json,company,product_name,email ON ad_sale_orders WHEN OLD.state!='draft'
BEGIN SELECT RAISE(ABORT,'Materials are locked after submission'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_file_insert_guard BEFORE INSERT ON ad_sale_files
WHEN NOT EXISTS(SELECT 1 FROM ad_sale_orders WHERE id=NEW.order_id AND state='draft'
 AND (NEW.role='logo' OR EXISTS(SELECT 1 FROM json_each(quote_json,'$.slots') WHERE value=NEW.role)))
BEGIN SELECT RAISE(ABORT,'Files must belong to a selected draft position'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_file_update_guard BEFORE UPDATE ON ad_sale_files
WHEN OLD.id!=NEW.id OR OLD.order_id!=NEW.order_id OR OLD.role!=NEW.role
 OR NOT EXISTS(SELECT 1 FROM ad_sale_orders WHERE id=NEW.order_id AND state='draft')
BEGIN SELECT RAISE(ABORT,'Submitted files are immutable'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_file_delete_guard BEFORE DELETE ON ad_sale_files
WHEN EXISTS(SELECT 1 FROM ad_sale_orders WHERE id=OLD.order_id AND state NOT IN('draft','cancelled','rejected','ended','refunded'))
BEGIN SELECT RAISE(ABORT,'Required campaign files cannot be deleted'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_terminal BEFORE UPDATE OF state ON ad_sale_orders
WHEN OLD.state IN('refunded','rejected','cancelled') AND NEW.state!=OLD.state
BEGIN SELECT RAISE(ABORT,'Closed orders cannot be reactivated'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_approval_guard BEFORE UPDATE ON ad_sale_orders
WHEN NEW.state IN('approved','checkout','capturing','active') AND (
 julianday(NEW.approved_at) IS NULL OR length(trim(coalesce(NEW.approved_by,'')))=0
 OR (SELECT count(*) FROM ad_sale_files WHERE order_id=NEW.id)!=1+json_array_length(NEW.quote_json,'$.slots'))
BEGIN SELECT RAISE(ABORT,'Reviewed complete files are required'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_active_guard BEFORE UPDATE ON ad_sale_orders WHEN NEW.state='active'
BEGIN
 SELECT (CASE WHEN OLD.state NOT IN('capturing','active')
 OR length(trim(coalesce(NEW.capture_id,'')))=0 OR length(trim(coalesce(NEW.provider_order,'')))=0
 OR length(trim(coalesce(NEW.merchant_id,'')))=0 OR coalesce(NEW.payment_environment,'') NOT IN('live','sandbox')
 OR julianday(NEW.payment_verified_at) IS NULL OR julianday(NEW.starts_at) IS NULL OR julianday(NEW.ends_at) IS NULL
 OR abs((julianday(NEW.ends_at)-julianday(NEW.starts_at))*86400-NEW.days*86400)>0.01
 OR (SELECT count(*) FROM ad_sale_holds WHERE order_id=NEW.id AND expires_at>=NEW.ends_at)!=json_array_length(NEW.quote_json,'$.slots')
 THEN RAISE(ABORT,'Verified payment, complete files and every reserved position are required') END);
END;
CREATE TRIGGER IF NOT EXISTS ad_sale_stop_guard BEFORE UPDATE ON ad_sale_orders
WHEN NEW.state IN('capturing','active') AND EXISTS(SELECT 1 FROM ad_sale_events e
 WHERE e.environment=NEW.payment_environment
 AND (e.provider_order=NEW.provider_order OR EXISTS(SELECT 1 FROM json_each(e.capture_ids_json) WHERE value=NEW.capture_id))
 AND (e.event_type IN('PAYMENT.CAPTURE.REFUNDED','PAYMENT.CAPTURE.REVERSED','CHECKOUT.PAYMENT-APPROVAL.REVERSED') OR e.event_type LIKE 'CUSTOMER.DISPUTE.%'))
BEGIN SELECT RAISE(ABORT,'A verified stop event prevents publication'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_lane_guard BEFORE INSERT ON ad_sale_holds
WHEN NEW.slot NOT IN('tool-primary','buyer-intent-top','compare-decision-premium','buyer-hub-fixed','comparison-hub-fixed','tool-rotation','guide-rotation','compare-rotation')
 OR (NEW.slot NOT IN('tool-rotation','guide-rotation','compare-rotation') AND NEW.lane!=1)
 OR NOT EXISTS(SELECT 1 FROM ad_sale_orders o,json_each(o.quote_json,'$.slots') j WHERE o.id=NEW.order_id AND j.value=NEW.slot)
 OR EXISTS(SELECT 1 FROM sponsorship_applications a WHERE a.slot=NEW.slot AND a.publication_status='published' AND a.ends_at>strftime('%Y-%m-%dT%H:%M:%fZ','now'))
BEGIN SELECT RAISE(ABORT,'Position is unavailable or outside this order'); END;

-- Explicit transitions keep direct database writes from skipping review or capture.
CREATE TRIGGER IF NOT EXISTS ad_sale_transition_guard BEFORE UPDATE OF state ON ad_sale_orders
WHEN OLD.state!=NEW.state AND NOT (
 (OLD.state='draft' AND NEW.state IN('submitted','cancelled')) OR
 (OLD.state='submitted' AND NEW.state IN('approved','draft','rejected','cancelled')) OR
 (OLD.state='approved' AND NEW.state IN('checkout','cancelled')) OR
 (OLD.state='checkout' AND NEW.state IN('capturing','approved','held','refunded','cancelled')) OR
 (OLD.state='capturing' AND NEW.state IN('active','held','refunded')) OR
 (OLD.state='active' AND NEW.state IN('held','refunded','ended')) OR
 (OLD.state='ended' AND NEW.state IN('held','refunded')) OR
 (OLD.state='held' AND NEW.state IN('refunded','cancelled')))
BEGIN SELECT RAISE(ABORT,'Invalid order state transition'); END;
CREATE TRIGGER IF NOT EXISTS ad_sale_capture_guard BEFORE UPDATE ON ad_sale_orders WHEN NEW.state='capturing'
BEGIN
 SELECT (CASE WHEN coalesce(NEW.payment_environment,'') NOT IN('live','sandbox')
 OR length(trim(coalesce(NEW.provider_order,'')))=0 OR length(trim(coalesce(NEW.merchant_id,'')))=0
 OR (SELECT count(*) FROM ad_sale_holds WHERE order_id=NEW.id AND expires_at>strftime('%Y-%m-%dT%H:%M:%fZ','now'))!=json_array_length(NEW.quote_json,'$.slots')
 THEN RAISE(ABORT,'A provider order and every reserved position are required before capture') END);
END;
