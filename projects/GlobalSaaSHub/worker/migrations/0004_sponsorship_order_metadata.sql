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
  product_id TEXT NOT NULL CHECK (product_id IN (
    'tool_page_7','tool_page_30','tool_page_90',
    'buyer_intent_7','buyer_intent_30','buyer_intent_90',
    'comparison_7','comparison_30','comparison_90'
  )),
  amount TEXT NOT NULL CHECK (
    (product_id = 'tool_page_7' AND amount = '19.00') OR
    (product_id = 'tool_page_30' AND amount = '49.00') OR
    (product_id = 'tool_page_90' AND amount = '129.00') OR
    (product_id = 'buyer_intent_7' AND amount = '39.00') OR
    (product_id = 'buyer_intent_30' AND amount = '99.00') OR
    (product_id = 'buyer_intent_90' AND amount = '269.00') OR
    (product_id = 'comparison_7' AND amount = '59.00') OR
    (product_id = 'comparison_30' AND amount = '149.00') OR
    (product_id = 'comparison_90' AND amount = '399.00')
  ),
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

-- A verified PayPal refund/reversal changes sponsorship_orders.status through
-- the existing webhook path. Stop any associated campaign in the same D1
-- transaction boundary so refunded inventory cannot continue to render.
CREATE TRIGGER IF NOT EXISTS trg_sponsorship_order_refund_campaign
AFTER UPDATE OF status ON sponsorship_orders
WHEN NEW.status = 'refunded'
BEGIN
  UPDATE campaigns
  SET status = 'refunded', updated_at = NEW.updated_at
  WHERE provider_order_id = NEW.provider_order_id
    AND status IN ('awaiting_assets','pending_review','ready_to_publish','published');
END;
