import { canTransition, ORDER_STATES, SPONSORSHIP_AMOUNT, SPONSORSHIP_CURRENCY } from './domain.js';

export class D1OrderRepository {
  constructor(db) { this.db = db; }

  async create(order) {
    await this.db.prepare(`
      INSERT INTO orders (id, provider_order_id, provider, status, amount, currency, created_at, updated_at)
      VALUES (?, ?, 'paypal', 'created', ?, ?, ?, ?)
    `).bind(order.id, order.providerOrderId, SPONSORSHIP_AMOUNT, SPONSORSHIP_CURRENCY, order.now, order.now).run();
    return this.getByProviderOrderId(order.providerOrderId);
  }

  async getByProviderOrderId(providerOrderId) {
    return this.db.prepare('SELECT * FROM orders WHERE provider_order_id = ?')
      .bind(providerOrderId).first();
  }

  async transition(providerOrderId, nextStatus, now) {
    if (!ORDER_STATES.includes(nextStatus)) throw new Error('Invalid order state');
    const current = await this.getByProviderOrderId(providerOrderId);
    if (!current) throw new Error('Order not found');
    if (!canTransition(current.status, nextStatus)) throw new Error('Invalid order state transition');
    if (current.status !== nextStatus) {
      await this.db.prepare('UPDATE orders SET status = ?, updated_at = ? WHERE provider_order_id = ? AND status = ?')
        .bind(nextStatus, now, providerOrderId, current.status).run();
    }
    return this.getByProviderOrderId(providerOrderId);
  }

  async claimWebhook(eventId, eventType, now) {
    const result = await this.db.prepare(`
      INSERT INTO webhook_events (event_id, event_type, status, received_at)
      VALUES (?, ?, 'processing', ?) ON CONFLICT(event_id) DO NOTHING
    `).bind(eventId, eventType, now).run();
    return result.meta?.changes === 1;
  }

  async completeWebhook(eventId, now) {
    await this.db.prepare("UPDATE webhook_events SET status = 'processed', processed_at = ? WHERE event_id = ?")
      .bind(now, eventId).run();
  }

  async releaseWebhook(eventId) {
    await this.db.prepare("DELETE FROM webhook_events WHERE event_id = ? AND status = 'processing'")
      .bind(eventId).run();
  }
}
