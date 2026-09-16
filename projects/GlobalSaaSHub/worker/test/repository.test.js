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

    if (this.sql.includes('INSERT INTO sponsorship_orders')) {
      const [id, providerOrderId, productId, amount, currency, createdAt, updatedAt] = this.args;
      this.db.orders.set(providerOrderId, {
        id,
        provider_order_id: providerOrderId,
        provider: 'paypal',
        status: 'created',
        product_id: productId,
        amount,
        currency,
        payer_name: null,
        payer_email: null,
        paid_at: null,
        created_at: createdAt,
        updated_at: updatedAt,
      });
      return { meta: { changes: 1 } };
    }

    if (this.sql.includes('UPDATE sponsorship_orders SET status')) {
      const [nextStatus, updatedAt, providerOrderId, expectedStatus] = this.args;
      const order = this.db.orders.get(providerOrderId);
      if (!order || order.status !== expectedStatus) return { meta: { changes: 0 } };
      order.status = nextStatus;
      order.updated_at = updatedAt;
      return { meta: { changes: 1 } };
    }

    if (this.sql.includes('UPDATE sponsorship_orders') && this.sql.includes('SET payer_name')) {
      const [payerName, payerEmail, paidAt, updatedAt, providerOrderId] = this.args;
      const order = this.db.orders.get(providerOrderId);
      order.payer_name = payerName;
      order.payer_email = payerEmail;
      order.paid_at ||= paidAt;
      order.updated_at = updatedAt;
      return { meta: { changes: 1 } };
    }

    if (this.sql.includes('INSERT INTO campaigns')) {
      const [
        id, providerOrderId, productId, placement, durationDays, priceUsd,
        advertiserName, contactEmail, intakeToken, reportToken, createdAt, updatedAt,
      ] = this.args;
      this.db.campaigns.set(providerOrderId, {
        id,
        order_id: null,
        provider_order_id: providerOrderId,
        product_id: productId,
        placement,
        duration_days: durationDays,
        price_usd: priceUsd,
        status: 'awaiting_assets',
        advertiser_name: advertiserName,
        contact_email: contactEmail,
        intake_token: intakeToken,
        report_token: reportToken,
        starts_at: null,
        ends_at: null,
        created_at: createdAt,
        updated_at: updatedAt,
      });
      return { meta: { changes: 1 } };
    }

    if (this.sql.includes('INSERT INTO campaign_assets')) {
      const [
        campaignId, companyName, productName, contactEmail, destinationUrl, logoUrl,
        headline, description, ctaText, desiredStartDate, targetPage, comparisonTarget,
        sellerAttestation, validationStatus, validationNotes, submittedAt, updatedAt,
      ] = this.args;
      this.db.assets.set(campaignId, {
        campaign_id: campaignId,
        company_name: companyName,
        product_name: productName,
        contact_email: contactEmail,
        destination_url: destinationUrl,
        logo_url: logoUrl,
        headline,
        description,
        cta_text: ctaText,
        desired_start_date: desiredStartDate,
        target_page: targetPage,
        comparison_target: comparisonTarget,
        seller_attestation: sellerAttestation,
        validation_status: validationStatus,
        validation_notes: validationNotes,
        submitted_at: submittedAt,
        updated_at: updatedAt,
      });
      return { meta: { changes: 1 } };
    }

    if (this.sql.includes('UPDATE campaigns') && this.sql.includes('SET advertiser_name')) {
      const [advertiserName, contactEmail, status, updatedAt, campaignId] = this.args;
      const campaign = [...this.db.campaigns.values()].find((item) => item.id === campaignId);
      campaign.advertiser_name = advertiserName;
      campaign.contact_email = contactEmail;
      campaign.status = status;
      campaign.updated_at = updatedAt;
      return { meta: { changes: 1 } };
    }

    if (this.sql.includes('INSERT INTO notification_outbox')) {
      this.db.notifications.push(this.args);
      return { meta: { changes: 1 } };
    }

    return { meta: { changes: 1 } };
  }

  async first() {
    if (this.sql.includes('FROM sponsorship_orders')) {
      return this.db.orders.get(this.args[0]) || null;
    }
    if (this.sql.includes('FROM campaigns WHERE provider_order_id')) {
      return this.db.campaigns.get(this.args[0]) || null;
    }
    if (this.sql.includes('FROM campaigns WHERE id')) {
      return [...this.db.campaigns.values()].find((campaign) => campaign.id === this.args[0]) || null;
    }
    if (this.sql.includes('FROM campaign_assets WHERE campaign_id')) {
      return this.db.assets.get(this.args[0]) || null;
    }
    return null;
  }
}

class FakeD1 {
  constructor() {
    this.events = new Set();
    this.orders = new Map();
    this.campaigns = new Map();
    this.assets = new Map();
    this.notifications = [];
  }

  prepare(sql) { return new Statement(this, sql); }
}

function exampleAsset() {
  return {
    companyName: 'Example Co',
    productName: 'Example Product',
    contactEmail: 'ads@example.com',
    destinationUrl: 'https://example.com',
    logoUrl: 'https://example.com/logo.png',
    headline: 'Useful product',
    description: 'A factual description.',
    ctaText: 'Learn more',
    desiredStartDate: '',
    targetPage: '/tool/example.html',
    comparisonTarget: '',
    sellerAttestation: true,
  };
}

test('duplicate webhook event is claimed exactly once', async () => {
  const repo = new D1OrderRepository(new FakeD1());
  assert.equal(await repo.claimWebhook('WH-1', 'PAYMENT.CAPTURE.COMPLETED', 'now'), true);
  assert.equal(await repo.claimWebhook('WH-1', 'PAYMENT.CAPTURE.COMPLETED', 'later'), false);
});

test('selected product persists through paid order and creates one campaign', async () => {
  const db = new FakeD1();
  const repo = new D1OrderRepository(db);

  const created = await repo.create({
    id: 'local-1',
    providerOrderId: 'PAYPAL-1',
    productId: 'buyer_intent_7',
    now: '2026-09-17T00:00:00.000Z',
  });
  assert.equal(created.product_id, 'buyer_intent_7');
  assert.equal(created.amount, '39.00');
  assert.equal(created.currency, 'USD');

  await repo.transition('PAYPAL-1', 'pending', '2026-09-17T00:01:00.000Z');
  await repo.transition('PAYPAL-1', 'paid', '2026-09-17T00:02:00.000Z');
  const paid = await repo.recordPayer(
    'PAYPAL-1',
    'Verified Buyer',
    'buyer@example.com',
    '2026-09-17T00:02:00.000Z',
  );

  const campaign = await repo.ensureCampaign(paid, '2026-09-17T00:02:00.000Z');
  assert.equal(campaign.order_id, null);
  assert.equal(campaign.product_id, 'buyer_intent_7');
  assert.equal(campaign.placement, 'buyer_intent');
  assert.equal(campaign.duration_days, 7);
  assert.equal(campaign.price_usd, '39.00');
  assert.equal(campaign.status, 'awaiting_assets');
  assert.equal(db.notifications.length, 1);

  const duplicate = await repo.ensureCampaign(paid, '2026-09-17T00:03:00.000Z');
  assert.equal(duplicate.id, campaign.id);
  assert.equal(db.campaigns.size, 1);
  assert.equal(db.notifications.length, 1);
});

test('invalid campaign materials stay retryable instead of rejecting a paid campaign', async () => {
  const db = new FakeD1();
  const repo = new D1OrderRepository(db);
  const created = await repo.create({
    id: 'local-2', providerOrderId: 'PAYPAL-2', productId: 'tool_page_7', now: 'now',
  });
  await repo.transition('PAYPAL-2', 'pending', 'later');
  await repo.transition('PAYPAL-2', 'paid', 'paid');
  const campaign = await repo.ensureCampaign(created, 'paid');

  const afterInvalid = await repo.saveAssets(
    campaign.id, exampleAsset(), 'invalid', 'Target page is invalid.', 'submitted-1',
  );
  assert.equal(afterInvalid.status, 'awaiting_assets');
  assert.equal((await repo.getAssets(campaign.id)).validation_status, 'invalid');

  const afterCorrection = await repo.saveAssets(
    campaign.id, exampleAsset(), 'valid', null, 'submitted-2',
  );
  assert.equal(afterCorrection.status, 'ready_to_publish');
  assert.equal((await repo.getAssets(campaign.id)).validation_status, 'valid');
});
