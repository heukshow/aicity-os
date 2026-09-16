import assert from 'node:assert/strict';
import test from 'node:test';
import { runCampaignMaintenance } from '../src/campaign-automation.js';

class Statement {
  constructor(db, sql) {
    this.db = db;
    this.sql = sql;
    this.args = [];
  }
  bind(...args) {
    this.args = args;
    return this;
  }
  async all() {
    if (this.sql.includes("SELECT * FROM campaigns WHERE status='published'")) {
      return { results: [this.db.campaign] };
    }
    return { results: [] };
  }
  async first() {
    if (this.sql.includes('FROM campaign_events WHERE campaign_id = ?')) {
      return { impressions: 100, clicks: 5 };
    }
    return null;
  }
  async run() {
    this.db.executed.push({ sql: this.sql, args: this.args });
    if (this.sql.includes('INSERT INTO campaign_reports')) return { meta: { changes: 1 } };
    return { meta: { changes: 1 } };
  }
}

class FakeD1 {
  constructor(campaign) {
    this.campaign = campaign;
    this.executed = [];
  }
  prepare(sql) {
    return new Statement(this, sql);
  }
}

test('maintenance creates a final verified-metrics report and expires an ended campaign', async () => {
  const db = new FakeD1({
    id: 'campaign-1',
    product_id: 'tool_page_7',
    placement: 'tool_page',
    duration_days: 7,
    contact_email: 'ads@example.com',
    report_token: 'a'.repeat(64),
    starts_at: '2026-09-01T00:00:00.000Z',
    ends_at: '2026-09-08T00:00:00.000Z',
  });

  await runCampaignMaintenance(db, '2026-09-08T01:00:00.000Z');

  const reportInsert = db.executed.find((entry) => entry.sql.includes('INSERT INTO campaign_reports'));
  assert.ok(reportInsert, 'final report should be inserted');
  assert.equal(reportInsert.args[2], 'final');
  assert.equal(reportInsert.args[5], 100);
  assert.equal(reportInsert.args[6], 5);
  assert.equal(reportInsert.args[7], 5);

  const outboxInsert = db.executed.find((entry) => entry.sql.includes('INSERT INTO notification_outbox'));
  assert.ok(outboxInsert, 'final report notification should be queued');
  assert.equal(outboxInsert.args[1], 'ads@example.com');

  const expiryUpdate = db.executed.find((entry) => entry.sql.includes("SET status='ended'"));
  assert.ok(expiryUpdate, 'campaign should be marked ended');
});
