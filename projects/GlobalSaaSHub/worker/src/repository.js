import {
  canTransition,
  getProduct,
  ORDER_STATES,
  SPONSORSHIP_CURRENCY,
} from './domain.js';

export class D1OrderRepository {
  constructor(db) { this.db = db; }

  async create(order) {
    const product = getProduct(order.productId);
    await this.db.prepare(`
      INSERT INTO sponsorship_orders (
        id, provider_order_id, provider, status, product_id, amount, currency, created_at, updated_at
      ) VALUES (?, ?, 'paypal', 'created', ?, ?, ?, ?, ?)
    `).bind(
      order.id,
      order.providerOrderId,
      product.id,
      product.amount,
      SPONSORSHIP_CURRENCY,
      order.now,
      order.now,
    ).run();
    return this.getByProviderOrderId(order.providerOrderId);
  }

  async getByProviderOrderId(providerOrderId) {
    return this.db.prepare('SELECT * FROM sponsorship_orders WHERE provider_order_id = ?')
      .bind(providerOrderId).first();
  }

  async getLegacyByProviderOrderId(providerOrderId) {
    return this.db.prepare('SELECT * FROM orders WHERE provider_order_id = ?')
      .bind(providerOrderId).first();
  }

  async transition(providerOrderId, nextStatus, now) {
    if (!ORDER_STATES.includes(nextStatus)) throw new Error('Invalid order state');
    const current = await this.getByProviderOrderId(providerOrderId);
    if (!current) throw new Error('Order not found');
    if (!canTransition(current.status, nextStatus)) throw new Error('Invalid order state transition');
    if (current.status !== nextStatus) {
      await this.db.prepare(`
        UPDATE sponsorship_orders SET status = ?, updated_at = ?
        WHERE provider_order_id = ? AND status = ?
      `).bind(nextStatus, now, providerOrderId, current.status).run();
    }
    return this.getByProviderOrderId(providerOrderId);
  }

  async transitionLegacy(providerOrderId, nextStatus, now) {
    if (!ORDER_STATES.includes(nextStatus)) throw new Error('Invalid order state');
    const current = await this.getLegacyByProviderOrderId(providerOrderId);
    if (!current) throw new Error('Legacy order not found');
    if (!canTransition(current.status, nextStatus)) throw new Error('Invalid order state transition');
    if (current.status !== nextStatus) {
      await this.db.prepare(`
        UPDATE orders SET status = ?, updated_at = ?
        WHERE provider_order_id = ? AND status = ?
      `).bind(nextStatus, now, providerOrderId, current.status).run();
    }
    return this.getLegacyByProviderOrderId(providerOrderId);
  }

  async recordPayer(providerOrderId, payerName, payerEmail, paidAt) {
    await this.db.prepare(`
      UPDATE sponsorship_orders
      SET payer_name = ?, payer_email = ?, paid_at = COALESCE(paid_at, ?), updated_at = ?
      WHERE provider_order_id = ?
    `).bind(payerName || null, payerEmail || null, paidAt, paidAt, providerOrderId).run();
    return this.getByProviderOrderId(providerOrderId);
  }

  async ensureCampaign(order, now) {
    if (!order?.provider_order_id || !order?.product_id) {
      throw new Error('Order is missing campaign metadata');
    }
    const product = getProduct(order.product_id);
    const existing = await this.db.prepare('SELECT * FROM campaigns WHERE provider_order_id = ?')
      .bind(order.provider_order_id).first();
    if (existing) return existing;

    const campaignId = crypto.randomUUID();
    const intakeToken = crypto.randomUUID().replaceAll('-', '') + crypto.randomUUID().replaceAll('-', '');
    const reportToken = crypto.randomUUID().replaceAll('-', '') + crypto.randomUUID().replaceAll('-', '');

    // `campaigns.order_id` references the legacy fixed-$49 orders table.
    // Checkout v2 deliberately leaves it NULL and uses provider_order_id as the
    // stable unique relationship to sponsorship_orders.
    await this.db.prepare(`
      INSERT INTO campaigns (
        id, order_id, provider_order_id, product_id, placement, duration_days, price_usd,
        status, advertiser_name, contact_email, intake_token, report_token,
        starts_at, ends_at, created_at, updated_at
      ) VALUES (?, NULL, ?, ?, ?, ?, ?, 'awaiting_assets', ?, ?, ?, ?, NULL, NULL, ?, ?)
    `).bind(
      campaignId,
      order.provider_order_id,
      product.id,
      product.placement,
      product.durationDays,
      product.amount,
      order.payer_name || null,
      order.payer_email || null,
      intakeToken,
      reportToken,
      now,
      now,
    ).run();

    const campaign = await this.getCampaignById(campaignId);
    if (campaign?.contact_email) {
      await this.queueNotification(
        campaign.id,
        campaign.contact_email,
        'assets_request',
        'COSHUMA sponsorship — submit your campaign assets',
        {
          campaignId: campaign.id,
          productId: campaign.product_id,
          placement: campaign.placement,
          durationDays: campaign.duration_days,
          priceUsd: campaign.price_usd,
          intakeToken: campaign.intake_token,
          reportToken: campaign.report_token,
        },
        now,
      );
    }
    return campaign;
  }

  async getCampaignById(id) {
    return this.db.prepare('SELECT * FROM campaigns WHERE id = ?').bind(id).first();
  }

  async getCampaignByIntakeToken(token) {
    return this.db.prepare('SELECT * FROM campaigns WHERE intake_token = ?').bind(token).first();
  }

  async getCampaignByReportToken(token) {
    return this.db.prepare('SELECT * FROM campaigns WHERE report_token = ?').bind(token).first();
  }

  async saveAssets(campaignId, asset, validationStatus, validationNotes, now) {
    await this.db.prepare(`
      INSERT INTO campaign_assets (
        campaign_id, company_name, product_name, contact_email, destination_url, logo_url,
        headline, description, cta_text, desired_start_date, target_page, comparison_target,
        seller_attestation, validation_status, validation_notes, submitted_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(campaign_id) DO UPDATE SET
        company_name=excluded.company_name,
        product_name=excluded.product_name,
        contact_email=excluded.contact_email,
        destination_url=excluded.destination_url,
        logo_url=excluded.logo_url,
        headline=excluded.headline,
        description=excluded.description,
        cta_text=excluded.cta_text,
        desired_start_date=excluded.desired_start_date,
        target_page=excluded.target_page,
        comparison_target=excluded.comparison_target,
        seller_attestation=excluded.seller_attestation,
        validation_status=excluded.validation_status,
        validation_notes=excluded.validation_notes,
        updated_at=excluded.updated_at
    `).bind(
      campaignId,
      asset.companyName,
      asset.productName,
      asset.contactEmail,
      asset.destinationUrl,
      asset.logoUrl,
      asset.headline,
      asset.description,
      asset.ctaText,
      asset.desiredStartDate || null,
      asset.targetPage || null,
      asset.comparisonTarget || null,
      asset.sellerAttestation ? 1 : 0,
      validationStatus,
      validationNotes || null,
      now,
      now,
    ).run();

    const campaignStatus = validationStatus === 'valid'
      ? 'ready_to_publish'
      : validationStatus === 'invalid'
        ? 'rejected'
        : 'pending_review';

    await this.db.prepare(`
      UPDATE campaigns
      SET advertiser_name = ?, contact_email = ?, status = ?, updated_at = ?
      WHERE id = ?
    `).bind(asset.companyName, asset.contactEmail, campaignStatus, now, campaignId).run();
    return this.getCampaignById(campaignId);
  }

  async getAssets(campaignId) {
    return this.db.prepare('SELECT * FROM campaign_assets WHERE campaign_id = ?')
      .bind(campaignId).first();
  }

  async recordEvent(campaignId, eventType, page, placement, destinationUrl, now) {
    await this.db.prepare(`
      INSERT INTO campaign_events (campaign_id, event_type, page, placement, destination_url, occurred_at)
      VALUES (?, ?, ?, ?, ?, ?)
    `).bind(campaignId, eventType, page || null, placement || null, destinationUrl || null, now).run();
  }

  async metrics(campaignId) {
    const row = await this.db.prepare(`
      SELECT
        SUM(CASE WHEN event_type='sponsored_impression' THEN 1 ELSE 0 END) AS impressions,
        SUM(CASE WHEN event_type='sponsored_click' THEN 1 ELSE 0 END) AS clicks
      FROM campaign_events WHERE campaign_id = ?
    `).bind(campaignId).first();
    const impressions = Number(row?.impressions || 0);
    const clicks = Number(row?.clicks || 0);
    return {
      impressions,
      clicks,
      ctr: impressions > 0 ? Number(((clicks / impressions) * 100).toFixed(2)) : 0,
    };
  }

  async queueNotification(campaignId, recipientEmail, template, subject, payload, now) {
    await this.db.prepare(`
      INSERT INTO notification_outbox (
        id, campaign_id, recipient_email, template, subject, payload_json, status, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, 'queued', ?)
    `).bind(
      crypto.randomUUID(), campaignId || null, recipientEmail,
      template, subject, JSON.stringify(payload), now,
    ).run();
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
