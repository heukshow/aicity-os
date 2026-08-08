CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  provider_order_id TEXT NOT NULL UNIQUE,
  provider TEXT NOT NULL CHECK (provider = 'paypal'),
  status TEXT NOT NULL CHECK (status IN ('created','pending','paid','failed','cancelled','refunded')),
  amount TEXT NOT NULL CHECK (amount = '49.00'),
  currency TEXT NOT NULL CHECK (currency = 'USD'),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_status_updated ON orders(status, updated_at);

CREATE TABLE IF NOT EXISTS webhook_events (
  event_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('processing','processed')),
  received_at TEXT NOT NULL,
  processed_at TEXT
);
