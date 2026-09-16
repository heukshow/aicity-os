import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import test from 'node:test';

function migration(name) {
  return readFileSync(new URL(`../migrations/${name}`, import.meta.url), 'utf8');
}

test('0004 adds variable-price sponsorship orders without mutating legacy fixed-price data', () => {
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
    ) VALUES (?, ?, 'paypal', 'created', ?, ?, 'USD', ?, ?)
  `).run('new-19', 'PAYPAL-NEW-19', 'tool_page_7', '19.00', '2026-09-17T00:00:00.000Z', '2026-09-17T00:00:00.000Z');

  const newOrder = db.prepare('SELECT product_id, amount FROM sponsorship_orders WHERE id = ?').get('new-19');
  assert.deepEqual({ ...newOrder }, { product_id: 'tool_page_7', amount: '19.00' });

  assert.throws(() => {
    db.prepare(`
      INSERT INTO orders (id, provider_order_id, provider, status, amount, currency, created_at, updated_at)
      VALUES (?, ?, 'paypal', 'created', '19.00', 'USD', ?, ?)
    `).run('legacy-bad', 'PAYPAL-LEGACY-BAD', '2026-09-17T00:00:00.000Z', '2026-09-17T00:00:00.000Z');
  });

  db.close();
});
