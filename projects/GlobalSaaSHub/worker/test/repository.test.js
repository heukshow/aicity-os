import assert from 'node:assert/strict';
import test from 'node:test';
import { D1OrderRepository } from '../src/repository.js';

class Statement {
  constructor(db, sql) { this.db = db; this.sql = sql; this.args = []; }
  bind(...args) { this.args = args; return this; }
  async run() {
    if (this.sql.includes('INSERT INTO webhook_events')) {
      if (this.db.events.has(this.args[0])) return { meta: { changes: 0 } };
      this.db.events.add(this.args[0]);
      return { meta: { changes: 1 } };
    }
    return { meta: { changes: 1 } };
  }
  async first() { return null; }
}
class FakeD1 {
  constructor() { this.events = new Set(); }
  prepare(sql) { return new Statement(this, sql); }
}

test('duplicate webhook event is claimed exactly once', async () => {
  const repo = new D1OrderRepository(new FakeD1());
  assert.equal(await repo.claimWebhook('WH-1', 'PAYMENT.CAPTURE.COMPLETED', 'now'), true);
  assert.equal(await repo.claimWebhook('WH-1', 'PAYMENT.CAPTURE.COMPLETED', 'later'), false);
});
