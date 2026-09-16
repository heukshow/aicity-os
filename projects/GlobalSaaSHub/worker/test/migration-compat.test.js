import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';

function migration(name) {
  return readFileSync(new URL(`../migrations/${name}`, import.meta.url), 'utf8');
}

test('0004 preserves legacy orders, supports variable prices, and stops refunded campaigns', () => {
  const db = new DatabaseSync(':memory:');
  db.exec('PRAGMA foreign_keys = ON;');
  db.exec(migration('0001_orders.sql'));
  db.exec(migration('0002_private_ops.sql'));
  db.exec(migration('0003_sponsored_campaigns.sql'));

  db.prepare(`
    INSERT INTO orders (id, provider_order_id, provider, status, amount, currency, created_at, updated_at)
    VALUES (?, ?, 'paypal', 'paid', '49.00', 'USD', ?, ?)
  `).run('legacy-1', 'PAYPAL-LEGACY-1', '2026-09-01T00:00:00.000Z', '2026-09-01T00:00:00.000Z');

  db.exec(migration('0004_sponsorship_order_metadata.sql'));

  const legacy = db.prepare('SELECT id, amount, currency, status FROM orders WHERE id = ?').get('legacy-1');
  assert.deepEqual({ ...legacy }, { id: 'legacy-1', amount: '49.00', currency: 'USD', status: 'paid' });

  db.prepare(`
    INSERT INTO sponsorship_orders (
      id, provider_order_id, provider, status, product_id, amount, currency, created_at, updated_at
    ) VALUES (?, ?, 'paypal', 'paid', ?, ?, 'USD', ?, ?)
  `).run('new-19', 'PAYPAL-NEW-19', 'tool_page_7', '19.00', '2026-09-17T00:00:00.000Z', '2026-09-17T00:00:00.000Z');

  const newOrder = db.prepare('SELECT product_id, amount FROM sponsorship_orders WHERE id = ?').get('new-19');
  assert.deepEqual({ ...newOrder }, { product_id: 'tool_page_7', amount: '19.00' });

  db.prepare(`
    INSERT INTO campaigns (
      id, order_id, provider_order_id, product_id, placement, duration_days, price_usd,
      status, advertiser_name, contact_email, intake_token, report_token,
      starts_at, ends_at, created_at, updated_at
    ) VALUES (?, NULL, ?, ?, 'tool_page', 7, '19.00', 'published', ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    'campaign-refund', 'PAYPAL-NEW-19', 'tool_page_7', 'Example Co', 'ads@example.com',
    'a'.repeat(64), 'b'.repeat(64),
    '2026-09-17T00:00:00.000Z', '2026-09-24T00:00:00.000Z',
    '2026-09-17T00:00:00.000Z', '2026-09-17T00:00:00.000Z',
  );

  db.prepare(`UPDATE sponsorship_orders SET status='refunded', updated_at=? WHERE id=?`)
    .run('2026-09-18T00:00:00.000Z', 'new-19');
  const refundedCampaign = db.prepare('SELECT status FROM campaigns WHERE id=?').get('campaign-refund');
  assert.equal(refundedCampaign.status, 'refunded');

  assert.throws(() => {
    db.prepare(`
      INSERT INTO orders (id, provider_order_id, provider, status, amount, currency, created_at, updated_at)
      VALUES (?, ?, 'paypal', 'created', '19.00', 'USD', ?, ?)
    `).run('legacy-bad', 'PAYPAL-LEGACY-BAD', '2026-09-17T00:00:00.000Z', '2026-09-17T00:00:00.000Z');
  });

  db.close();
});
