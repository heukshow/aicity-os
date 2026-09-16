-- Variable-price sponsorship orders for COSHUMA checkout v2.
--
-- IMPORTANT: do not widen the legacy `orders` table in place. Its schema has
-- `CHECK (amount = '49.00')`, so reusing it for the nine product prices would
-- fail for every non-$49 package. Rebuilding that table would also create
-- unnecessary foreign-key and rollback risk.
--
-- Instead, checkout v2 writes to this additive table. The legacy `orders`
-- table remains untouched for backward compatibility while checkout stays
-- disabled during staging.

CREATE TABLE IF NOT EXISTS sponsorship_orders (
  id TEXT PRIMARY KEY,
  provider_order_id TEXT NOT NULL UNIQUE,
  provider TEXT NOT NULL CHECK (provider = 'paypal'),
  status TEXT NOT NULL CHECK (status IN ('created','pending','paid','failed','cancelled','refunded')),
  product_id TEXT NOT NULL,
  amount TEXT NOT NULL,
  currency TEXT NOT NULL CHECK (currency = 'USD'),
  payer_name TEXT,
  payer_email TEXT,
  paid_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sponsorship_orders_status_updated
  ON sponsorship_orders(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_sponsorship_orders_product
  ON sponsorship_orders(product_id, status);
