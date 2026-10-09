CREATE TABLE IF NOT EXISTS ad_sandbox_runtime(key TEXT PRIMARY KEY,value TEXT NOT NULL);
INSERT OR IGNORE INTO ad_sandbox_runtime(key,value) VALUES('scope','coshuma-ads-sandbox-v1');
CREATE TABLE IF NOT EXISTS ad_sandbox_evidence(id TEXT PRIMARY KEY,kind TEXT NOT NULL,detail_json TEXT NOT NULL,instance_id TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ad_sandbox_faults(order_id TEXT NOT NULL,kind TEXT NOT NULL,created_at TEXT NOT NULL,consumed_at TEXT,PRIMARY KEY(order_id,kind),FOREIGN KEY(order_id) REFERENCES ad_sale_orders(id));
CREATE TABLE IF NOT EXISTS ad_sandbox_clocks(order_id TEXT PRIMARY KEY,offset_ms INTEGER NOT NULL CHECK(offset_ms>=0),FOREIGN KEY(order_id) REFERENCES ad_sale_orders(id));
