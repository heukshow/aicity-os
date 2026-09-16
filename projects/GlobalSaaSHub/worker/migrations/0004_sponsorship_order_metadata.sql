-- Extend existing PayPal orders with sponsorship product metadata.
--
-- This migration is intentionally additive and must be applied only after the
-- existing 0001_orders.sql, 0002_private_ops.sql and 0003_sponsored_campaigns.sql
-- migrations already present on main.
--
-- Checkout remains disabled until the compatible Worker revision is deployed
-- and verified. No payment route is enabled by this migration alone.

ALTER TABLE orders ADD COLUMN product_id TEXT;
ALTER TABLE orders ADD COLUMN payer_name TEXT;
ALTER TABLE orders ADD COLUMN payer_email TEXT;
ALTER TABLE orders ADD COLUMN paid_at TEXT;
