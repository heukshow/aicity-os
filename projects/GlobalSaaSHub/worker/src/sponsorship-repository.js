import { SponsorshipError } from './sponsorship-domain.js';
import { approvalEmailMarkerId } from './sponsorship-email.js';

export class SponsorshipRepository {
  constructor(db) {
    if (!db) throw new SponsorshipError('Application storage is unavailable', 503);
    this.db = db;
  }

  async ready() {
    // Read every required table: a binding alone does not prove the migration ran.
    await this.db.batch(['sponsorship_applications', 'sponsorship_payments', 'sponsorship_webhook_events', 'sponsorship_audit_log', 'sponsorship_intake_limits']
      .map((name) => this.db.prepare(`SELECT 1 FROM ${name} LIMIT 1`)));
    const guards = await this.db.prepare("SELECT name FROM sqlite_master WHERE type='trigger' AND name IN ('sponsorship_publish_guard','sponsorship_no_published_insert','sponsorship_refund_is_terminal','sponsorship_payment_stop','sponsorship_application_terms_immutable')").all();
    if (guards.results?.length !== 5) throw new SponsorshipError('Application storage migration is incomplete', 503);
  }

  async imageReady() {
    await this.db.batch(['sponsorship_assets','sponsorship_holds'].map((name) =>
      this.db.prepare(`SELECT 1 FROM ${name} LIMIT 1`)));
    const guards = await this.db.prepare("SELECT name FROM sqlite_master WHERE type='trigger' AND name IN ('sponsorship_asset_insert_guard','sponsorship_asset_update_guard','sponsorship_asset_delete_guard','sponsorship_image_review_guard','sponsorship_image_publish_guard','sponsorship_hold_insert_guard')").all();
    if (guards.results?.length !== 6) throw new SponsorshipError('Image advertising storage migration is incomplete', 503);
  }

  async rateLimit(clientHash, now) {
    const bucket = Math.floor(Date.parse(now) / 3600000);
    const row = await this.db.prepare(`INSERT INTO sponsorship_intake_limits(client_hash,bucket,attempts) VALUES(?,?,1)
      ON CONFLICT(client_hash,bucket) DO UPDATE SET attempts=attempts+1 RETURNING attempts`).bind(clientHash, bucket).first();
    if (!row || row.attempts > 10) throw new SponsorshipError('Too many applications; try again later', 429);
    await this.db.prepare('DELETE FROM sponsorship_intake_limits WHERE bucket < ?').bind(bucket - 24).run();
  }

  async createApplication(id, reference, tokenHash, fields, now) {
    await this.db.prepare(`INSERT INTO sponsorship_applications
      (id,reference,access_token_hash,company_name,tool_name,contact_email,slot,duration_days,target_page,destination_url,headline,description,cta_text,desired_start_date,seller_attestation,amount,currency,created_at,updated_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?,?,?,?)`).bind(
      id, reference, tokenHash, fields.companyName, fields.toolName, fields.contactEmail,
      fields.slot, fields.durationDays, fields.targetPage, fields.destinationUrl,
      fields.headline, fields.description, fields.ctaText, fields.desiredStartDate,
      fields.amount, fields.currency, now, now,
    ).run();
    return this.getApplication(id);
  }

  async createImageApplication(id, reference, tokenHash, fields, now) {
    await this.db.prepare(`INSERT INTO sponsorship_applications
      (id,reference,access_token_hash,company_name,tool_name,contact_email,slot,duration_days,target_page,destination_url,headline,description,cta_text,desired_start_date,seller_attestation,amount,currency,created_at,updated_at,creative_mode,submission_status)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,?,?,?,?,'image','draft')`).bind(
      id, reference, tokenHash, fields.companyName, fields.toolName, fields.contactEmail,
      fields.slot, fields.durationDays, fields.targetPage, fields.destinationUrl,
      fields.headline, fields.description, fields.ctaText, fields.desiredStartDate,
      fields.amount, fields.currency, now, now,
    ).run();
    return this.getApplication(id);
  }

  async createImageRenewalApplication(parent, id, reference, tokenHash, quote, actor, now) {
    if (parent.creative_mode !== 'image' || parent.publication_status !== 'published'
      || parent.payment_status !== 'verified' || parent.review_status !== 'approved') {
      throw new SponsorshipError('Only a verified published image campaign can be renewed', 409);
    }
    const existing = await this.renewalFor(parent.id);
    if (existing) return existing;
    const result = await this.db.batch([
      this.db.prepare(`INSERT INTO sponsorship_applications
        (id,reference,access_token_hash,company_name,tool_name,contact_email,slot,duration_days,target_page,destination_url,headline,description,cta_text,desired_start_date,seller_attestation,amount,currency,created_at,updated_at,creative_mode,submission_status,renewal_of_application_id)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,NULL,1,?,?,?,?,'image','draft',?)`).bind(
        id, reference, tokenHash, parent.company_name, parent.tool_name, parent.contact_email,
        parent.slot, quote.durationDays, parent.target_page, parent.destination_url,
        parent.headline, parent.description, parent.cta_text,
        quote.amount, quote.currency, now, now, parent.id,
      ),
      this.db.prepare(`INSERT INTO sponsorship_assets(id,application_id,role,mime,width,height,byte_size,sha256,data)
        SELECT ?,?,role,mime,width,height,byte_size,sha256,data FROM sponsorship_assets
        WHERE application_id=? AND role='logo'`).bind(crypto.randomUUID(), id, parent.id),
      this.db.prepare(`INSERT INTO sponsorship_assets(id,application_id,role,mime,width,height,byte_size,sha256,data)
        SELECT ?,?,role,mime,width,height,byte_size,sha256,data FROM sponsorship_assets
        WHERE application_id=? AND role=?`).bind(crypto.randomUUID(), id, parent.id, parent.slot),
      this.db.prepare("UPDATE sponsorship_applications SET submission_status='submitted',updated_at=? WHERE id=? AND submission_status='draft'")
        .bind(now, id),
      this.db.prepare(`UPDATE sponsorship_applications SET review_status='approved',review_notes=?,approved_at=?,approved_by=?,updated_at=?
        WHERE id=? AND creative_mode='image' AND submission_status='submitted' AND review_status='pending'`)
        .bind('Priority renewal of unchanged previously approved creative', now, actor, now, id),
      this.audit(id, 'renewal_created', actor, JSON.stringify({ renewalOf: parent.id, startsAfter: parent.ends_at }), now),
      this.audit(id, 'materials_approved', actor, 'Previously approved creative copied unchanged for priority renewal', now),
    ]);
    if (result[0].meta.changes !== 1 || result[1].meta.changes !== 1 || result[2].meta.changes !== 1
      || result[3].meta.changes !== 1 || result[4].meta.changes !== 1) {
      throw new SponsorshipError('The priority renewal could not be prepared', 409);
    }
    const saved = await this.getApplication(id);
    if (!saved || saved.renewal_of_application_id !== parent.id || saved.review_status !== 'approved'
      || saved.submission_status !== 'submitted') throw new SponsorshipError('The priority renewal could not be confirmed', 409);
    return saved;
  }

  getApplication(id) { return this.db.prepare('SELECT * FROM sponsorship_applications WHERE id=?').bind(id).first(); }
  renewalFor(parentId) {
    return this.db.prepare(`SELECT * FROM sponsorship_applications
      WHERE renewal_of_application_id=? AND publication_status IN ('draft','published')
      ORDER BY created_at DESC LIMIT 1`).bind(parentId).first();
  }
  renewalParent(application) {
    if (!application?.renewal_of_application_id) return Promise.resolve(null);
    return this.getApplication(application.renewal_of_application_id);
  }
  getPayment(id) { return this.db.prepare('SELECT * FROM sponsorship_payments WHERE application_id=?').bind(id).first(); }
  getPaymentByOrder(id, environment) { return this.db.prepare('SELECT * FROM sponsorship_payments WHERE provider_order_id=? AND environment=?').bind(id, environment).first(); }

  async placementAvailability(slot, targetPage, now) {
    const published = await this.db.prepare(`SELECT a.id,a.ends_at FROM sponsorship_applications a
      JOIN sponsorship_payments p ON p.application_id=a.id
      WHERE a.slot=? AND a.target_page=? AND a.publication_status='published'
        AND a.payment_status='verified' AND a.review_status='approved'
        AND a.ends_at>? AND p.state='verified' AND p.environment='live'
      ORDER BY a.ends_at DESC LIMIT 1`).bind(slot, targetPage, now).first();
    if (published) return { available: false, reason: 'booked', availableAfter: published.ends_at };

    const hold = await this.db.prepare(`SELECT h.expires_at FROM sponsorship_holds h
      JOIN sponsorship_applications a ON a.id=h.application_id
      WHERE h.slot=? AND a.target_page=? AND h.expires_at>?
        AND a.review_status='approved' AND a.publication_status='draft'
        AND a.payment_status IN ('unpaid','pending')
      ORDER BY h.expires_at ASC LIMIT 1`).bind(slot, targetPage, now).first();
    if (hold) return { available: false, reason: 'reserved', availableAfter: hold.expires_at };

    return { available: true, reason: 'open', availableAfter: null };
  }
  getPaymentByCapture(id, environment) { return this.db.prepare('SELECT * FROM sponsorship_payments WHERE capture_id=? AND environment=?').bind(id, environment).first(); }

  async listApplications() {
    return (await this.db.prepare('SELECT * FROM sponsorship_applications ORDER BY created_at DESC LIMIT 100').all()).results || [];
  }

  audit(applicationId, action, actor, detail, now) {
    return this.db.prepare('INSERT INTO sponsorship_audit_log(id,application_id,action,actor,detail,created_at) VALUES(?,?,?,?,?,?)')
      .bind(crypto.randomUUID(), applicationId, action, actor, detail, now);
  }

  approvalEmailSent(application) {
    if (!application?.approved_at) return Promise.resolve(null);
    return this.db.prepare("SELECT id,detail,created_at FROM sponsorship_audit_log WHERE id=? AND action='approval_email_sent'")
      .bind(approvalEmailMarkerId(application)).first();
  }

  approvalEmailStatus(applicationId) {
    return this.db.prepare(`SELECT action,detail,created_at FROM sponsorship_audit_log
      WHERE application_id=? AND action IN ('approval_email_sent','approval_email_failed')
      ORDER BY created_at DESC LIMIT 1`).bind(applicationId).first();
  }

  async recordApprovalEmailSent(application, providerMessageId, actor, now) {
    const detail = JSON.stringify({ approvedAt: application.approved_at, providerMessageId });
    await this.db.prepare(`INSERT INTO sponsorship_audit_log(id,application_id,action,actor,detail,created_at)
      VALUES(?,?,'approval_email_sent',?,?,?) ON CONFLICT(id) DO NOTHING`)
      .bind(approvalEmailMarkerId(application), application.id, actor, detail, now).run();
    return this.approvalEmailSent(application);
  }

  recordApprovalEmailFailed(application, reason, actor, now) {
    const safe = String(reason || 'approval email delivery failed').replace(/[\r\n]+/g, ' ').slice(0, 240);
    const id = `approval-email-failed:${application.id}:${application.approved_at || 'unknown'}`;
    const detail = JSON.stringify({ approvedAt: application.approved_at, reason: safe });
    return this.db.prepare(`INSERT INTO sponsorship_audit_log(id,application_id,action,actor,detail,created_at)
      VALUES(?,?,'approval_email_failed',?,?,?)
      ON CONFLICT(id) DO UPDATE SET actor=excluded.actor,detail=excluded.detail,created_at=excluded.created_at`)
      .bind(id, application.id, actor, detail, now).run();
  }

  async pendingApprovalEmailApplications(now) {
    const result = await this.db.prepare(`SELECT a.* FROM sponsorship_applications a
      JOIN sponsorship_holds h ON h.application_id=a.id AND h.slot=a.slot
      WHERE a.creative_mode='image' AND a.submission_status='submitted'
        AND a.review_status='approved' AND a.publication_status='draft'
        AND a.payment_status IN ('unpaid','pending') AND h.expires_at>?
      ORDER BY a.approved_at ASC LIMIT 25`).bind(now).all();
    return result.results || [];
  }

  async imageAssets(applicationId) {
    return (await this.db.prepare('SELECT id,role,mime,width,height,byte_size,sha256 FROM sponsorship_assets WHERE application_id=? ORDER BY role')
      .bind(applicationId).all()).results || [];
  }

  async saveImageAsset(application, role, file, now) {
    if (application.creative_mode !== 'image' || application.submission_status !== 'draft'
      || application.review_status !== 'pending' || application.publication_status !== 'draft') {
      throw new SponsorshipError('Image assets are locked after submission', 409);
    }
    if (!['logo', application.slot].includes(role)) throw new SponsorshipError('This asset role is not part of the application', 422);
    await this.db.prepare(`INSERT INTO sponsorship_assets
      (id,application_id,role,mime,width,height,byte_size,sha256,data)
      VALUES(?,?,?,?,?,?,?,?,?)
      ON CONFLICT(application_id,role) DO UPDATE SET
        mime=excluded.mime,width=excluded.width,height=excluded.height,byte_size=excluded.byte_size,
        sha256=excluded.sha256,data=excluded.data`).bind(
      crypto.randomUUID(), application.id, role, file.mime, file.width, file.height,
      file.byte_size, file.sha256, file.data,
    ).run();
    await this.audit(application.id, 'image_asset_saved', 'advertiser', role, now).run();
    return this.imageAssets(application.id);
  }

  async submitImageApplication(application, now) {
    if (application.creative_mode !== 'image' || application.submission_status !== 'draft'
      || application.review_status !== 'pending' || application.publication_status !== 'draft') {
      throw new SponsorshipError('This image application cannot be submitted now', 409);
    }
    const assets = await this.imageAssets(application.id);
    if (assets.length !== 2 || !assets.some((item) => item.role === 'logo')
      || !assets.some((item) => item.role === application.slot)) {
      throw new SponsorshipError('Upload the required logo and placement image before submitting', 409);
    }
    const result = await this.db.batch([
      this.db.prepare("UPDATE sponsorship_applications SET submission_status='submitted',updated_at=? WHERE id=? AND creative_mode='image' AND submission_status='draft'")
        .bind(now, application.id),
      this.audit(application.id, 'image_application_submitted', 'advertiser', 'Complete image materials submitted for review', now),
    ]);
    if (result[0].meta.changes !== 1) throw new SponsorshipError('The application changed before submission', 409);
    return this.getApplication(application.id);
  }

  imageHold(applicationId) {
    return this.db.prepare('SELECT slot,application_id,expires_at FROM sponsorship_holds WHERE application_id=?')
      .bind(applicationId).first();
  }

  async reserveImagePlacement(application, now, ttlMinutes = 30) {
    if (application.creative_mode !== 'image' || application.submission_status !== 'submitted'
      || application.review_status !== 'approved' || application.publication_status !== 'draft'
      || !['unpaid','pending'].includes(application.payment_status)) {
      throw new SponsorshipError('Approved submitted image materials are required before reservation', 409);
    }
    const until = new Date(Date.parse(now) + ttlMinutes * 60000).toISOString();
    const existing = await this.imageHold(application.id);
    if (existing && existing.expires_at > now && existing.slot === application.slot) return existing;
    await this.db.prepare('DELETE FROM sponsorship_holds WHERE expires_at<=?').bind(now).run();
    try {
      await this.db.batch([
        this.db.prepare('INSERT INTO sponsorship_holds(slot,application_id,expires_at) VALUES(?,?,?)')
          .bind(application.slot, application.id, until),
        this.audit(application.id, 'image_position_reserved', 'owner-review', JSON.stringify({ slot: application.slot, expiresAt: until }), now),
      ]);
    } catch {
      throw new SponsorshipError('This placement is not currently available', 409);
    }
    const saved = await this.imageHold(application.id);
    if (!saved || saved.expires_at !== until) throw new SponsorshipError('The placement reservation could not be saved', 409);
    return saved;
  }

  async requireImageHold(application, now) {
    const hold = await this.imageHold(application.id);
    if (!hold || hold.slot !== application.slot || hold.expires_at <= now) {
      throw new SponsorshipError('The reviewed placement reservation has expired', 409);
    }
    return hold;
  }

  async releaseImageHold(applicationId) {
    await this.db.prepare('DELETE FROM sponsorship_holds WHERE application_id=?').bind(applicationId).run();
  }

  async reservePayment(application, env, now) {
    // The same payment ID is reused after network timeouts; never mint another charge blindly.
    await this.db.prepare(`INSERT INTO sponsorship_payments(id,application_id,environment,merchant_id,amount,currency,created_at,updated_at)
      VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(application_id) DO NOTHING`).bind(
      crypto.randomUUID(), application.id, env.PAYPAL_ENVIRONMENT, env.PAYPAL_MERCHANT_ID,
      application.amount, application.currency, now, now,
    ).run();
    const payment = await this.getPayment(application.id);
    if (payment.environment !== env.PAYPAL_ENVIRONMENT || payment.merchant_id !== env.PAYPAL_MERCHANT_ID) throw new SponsorshipError('This application requires payment configuration review', 409);
    return payment;
  }

  async attachProviderOrder(applicationId, providerId, now) {
    await this.db.batch([
      this.db.prepare("UPDATE sponsorship_payments SET provider_order_id=?,state='pending',updated_at=? WHERE application_id=? AND provider_order_id IS NULL AND state='created'").bind(providerId, now, applicationId),
      this.db.prepare("UPDATE sponsorship_applications SET payment_status='pending',updated_at=? WHERE id=? AND payment_status='unpaid'").bind(now, applicationId),
    ]);
    const payment = await this.getPayment(applicationId);
    if (payment.provider_order_id !== providerId) throw new SponsorshipError('The payment order could not be linked safely', 409);
    return payment;
  }

  async markVerified(application, evidence, actor, now) {
    await this.db.batch([
      this.db.prepare(`UPDATE sponsorship_payments SET capture_id=?,state='verified',verified_at=?,last_checked_at=?,verification_reason=NULL,updated_at=?
        WHERE application_id=? AND provider_order_id=? AND environment='live' AND merchant_id=? AND state!='refunded'
        AND coalesce(verification_reason,'') NOT LIKE 'hold:%'
        AND NOT EXISTS(SELECT 1 FROM sponsorship_webhook_events e WHERE e.environment='live'
          AND (e.related_order_id=? OR EXISTS(SELECT 1 FROM json_each(e.capture_ids_json) WHERE value=?))
          AND (e.event_type IN ('PAYMENT.CAPTURE.REFUNDED','PAYMENT.CAPTURE.REVERSED') OR e.event_type LIKE 'CUSTOMER.DISPUTE.%'))`)
        .bind(evidence.captureId, now, now, now, application.id, evidence.providerOrderId, evidence.merchantId, evidence.providerOrderId, evidence.captureId),
      this.db.prepare(`UPDATE sponsorship_applications SET payment_status='verified',updated_at=? WHERE id=? AND payment_status!='refunded'
        AND EXISTS(SELECT 1 FROM sponsorship_payments p WHERE p.application_id=? AND p.state='verified' AND p.capture_id=?)`)
        .bind(now, application.id, application.id, evidence.captureId),
      this.db.prepare(`INSERT INTO sponsorship_audit_log(id,application_id,action,actor,detail,created_at)
        SELECT ?,?,'payment_verified',?,?,? WHERE EXISTS(SELECT 1 FROM sponsorship_payments p JOIN sponsorship_applications a ON a.id=p.application_id
          WHERE p.application_id=? AND p.state='verified' AND a.payment_status='verified' AND p.capture_id=?)`)
        .bind(crypto.randomUUID(), application.id, actor, 'Live order and capture match the saved application, merchant, gross amount and currency', now, application.id, evidence.captureId),
    ]);
    const saved = await this.getApplication(application.id);
    if (saved.payment_status !== 'verified') throw new SponsorshipError('Payment verification was not saved', 409);
    return saved;
  }

  async stopPayment(applicationId, state, reason, actor, now, event = null) {
    const statements = [
      this.db.prepare(`UPDATE sponsorship_payments SET state=?,
        verification_reason=CASE WHEN verification_reason LIKE 'hold:%' AND ?='review' THEN verification_reason ELSE ? END,
        last_checked_at=?,updated_at=? WHERE application_id=? AND state!='refunded'`)
        .bind(state, state, reason, now, now, applicationId),
      this.db.prepare(`INSERT INTO sponsorship_audit_log(id,application_id,action,actor,detail,created_at)
        SELECT ?,?,?,?,?,? WHERE EXISTS(SELECT 1 FROM sponsorship_payments WHERE application_id=? AND state=?)`)
        .bind(crypto.randomUUID(), applicationId, state === 'refunded' ? 'payment_reversed' : 'payment_review', actor, reason, now, applicationId, state),
    ];
    if (event) statements.push(this.eventStatement(event, now));
    await this.db.batch(statements);
  }

  eventStatement(event, now) {
    return this.db.prepare('INSERT INTO sponsorship_webhook_events(environment,event_id,event_type,related_order_id,capture_ids_json,processed_at) VALUES(?,?,?,?,?,?) ON CONFLICT(environment,event_id) DO NOTHING')
      .bind(event.environment, event.id, event.event_type, event.relatedOrderId || null, JSON.stringify(event.captureIds || []), now);
  }
  hasEvent(environment, id) { return this.db.prepare('SELECT 1 AS found FROM sponsorship_webhook_events WHERE environment=? AND event_id=?').bind(environment, id).first(); }
  recordEvent(event, now) { return this.eventStatement(event, now).run(); }
  blockingPaymentEvent(environment, orderId, captureId) {
    return this.db.prepare(`SELECT event_type FROM sponsorship_webhook_events e WHERE environment=?
      AND (related_order_id=? OR EXISTS(SELECT 1 FROM json_each(e.capture_ids_json) WHERE value=?))
      AND (event_type IN ('PAYMENT.CAPTURE.REFUNDED','PAYMENT.CAPTURE.REVERSED') OR event_type LIKE 'CUSTOMER.DISPUTE.%')
      ORDER BY CASE WHEN event_type LIKE 'PAYMENT.CAPTURE.%' THEN 0 ELSE 1 END LIMIT 1`)
      .bind(environment, orderId, captureId).first();
  }

  async review(application, approved, notes, actor, now) {
    if (approved && application.creative_mode === 'image') {
      if (application.submission_status !== 'submitted') throw new SponsorshipError('Submit complete image materials before approval', 409);
      const assets = await this.imageAssets(application.id);
      if (assets.length !== 2 || !assets.some((item) => item.role === 'logo')
        || !assets.some((item) => item.role === application.slot)) {
        throw new SponsorshipError('Complete image assets are required before approval', 409);
      }
    } else if (approved && application.payment_status !== 'verified') {
      throw new SponsorshipError('Verify the payment before approving this application', 409);
    }
    if (application.publication_status === 'published') throw new SponsorshipError('Pause a published campaign before changing its review', 409);
    const condition = approved && application.creative_mode !== 'image' ? "AND payment_status='verified'" : '';
    await this.db.batch([
      this.db.prepare(`UPDATE sponsorship_applications SET review_status=?,review_notes=?,approved_at=?,approved_by=?,updated_at=?
        WHERE id=? AND publication_status!='published' ${condition}`)
        .bind(approved ? 'approved' : 'rejected', notes, approved ? now : null, approved ? actor : null, now, application.id),
      this.audit(application.id, approved ? 'materials_approved' : 'materials_rejected', actor, notes, now),
    ]);
    const saved = await this.getApplication(application.id);
    if (saved.review_status !== (approved ? 'approved' : 'rejected')) throw new SponsorshipError('Review could not be saved', 409);
    return saved;
  }

  getImageAsset(applicationId, role) {
    return this.db.prepare('SELECT mime,width,height,byte_size,sha256,data FROM sponsorship_assets WHERE application_id=? AND role=?')
      .bind(applicationId, role).first();
  }

  async publishImage(application, startsAt, endsAt, actor, now) {
    if (application.creative_mode !== 'image') throw new SponsorshipError('This is not an image application', 409);
    await this.requireImageHold(application, now);
    try {
      const results = await this.db.batch([
        this.db.prepare(`UPDATE sponsorship_applications
          SET publication_status='published',starts_at=?,ends_at=?,updated_at=?
          WHERE id=? AND creative_mode='image' AND submission_status='submitted'
            AND review_status='approved' AND payment_status='verified' AND publication_status='draft'
            AND EXISTS(SELECT 1 FROM sponsorship_holds h WHERE h.application_id=? AND h.slot=sponsorship_applications.slot AND h.expires_at>?)`)
          .bind(startsAt, endsAt, now, application.id, application.id, now),
        this.db.prepare(`INSERT INTO sponsorship_audit_log(id,application_id,action,actor,detail,created_at)
          SELECT ?,?,'published',?,?,? WHERE changes()=1`)
          .bind(crypto.randomUUID(), application.id, actor, `${startsAt} / ${endsAt}`, now),
        this.db.prepare(`DELETE FROM sponsorship_holds WHERE application_id=?
          AND EXISTS(SELECT 1 FROM sponsorship_applications WHERE id=? AND publication_status='published')`)
          .bind(application.id, application.id),
      ]);
      if (results[0].meta.changes !== 1) throw new SponsorshipError('Image publication conditions changed before commit', 409);
    } catch (error) {
      if (/inventory conflicts|Verified payment|approved materials|image assets|reservation/i.test(error?.message || '')) {
        throw new SponsorshipError('Payment, approval, image assets or placement inventory prevented publication', 409);
      }
      throw error;
    }
    const saved = await this.getApplication(application.id);
    if (saved.publication_status !== 'published' || saved.starts_at !== startsAt || saved.ends_at !== endsAt) {
      throw new SponsorshipError('Image publication could not be saved', 409);
    }
    return saved;
  }

  async publish(application, startsAt, endsAt, actor, now) {
    if (application.publication_status !== 'draft') throw new SponsorshipError('Only a new, approved campaign can be published; extensions require a new application', 409);
    try {
      await this.db.batch([
        this.db.prepare("UPDATE sponsorship_applications SET publication_status='published',starts_at=?,ends_at=?,updated_at=? WHERE id=? AND publication_status='draft'")
          .bind(startsAt, endsAt, now, application.id),
        this.audit(application.id, 'published', actor, `${startsAt} / ${endsAt}`, now),
      ]);
    } catch (error) {
      if (/inventory conflicts|Verified payment|approved materials/i.test(error?.message || '')) throw new SponsorshipError('Payment, approval, period or placement inventory prevented publication', 409);
      throw error;
    }
    const saved = await this.getApplication(application.id);
    if (saved.publication_status !== 'published' || saved.starts_at !== startsAt || saved.ends_at !== endsAt) throw new SponsorshipError('Publication could not be saved', 409);
    return saved;
  }

  async pause(applicationId, actor, now) {
    await this.db.batch([
      this.db.prepare("UPDATE sponsorship_applications SET publication_status='paused',updated_at=? WHERE id=? AND publication_status='published'").bind(now, applicationId),
      this.audit(applicationId, 'paused', actor, 'Owner paused publication', now),
    ]);
    return this.getApplication(applicationId);
  }

  async placements(path, now, merchantId) {
    return (await this.db.prepare(`SELECT a.* FROM sponsorship_applications a JOIN sponsorship_payments p ON p.application_id=a.id
      WHERE a.target_page=? AND a.publication_status='published' AND a.payment_status='verified' AND a.review_status='approved'
      AND a.approved_at IS NOT NULL AND a.approved_by IS NOT NULL AND a.starts_at<=? AND a.ends_at>?
      AND p.state='verified' AND p.environment='live' AND p.merchant_id=? AND p.capture_id IS NOT NULL
      AND p.provider_order_id IS NOT NULL AND p.verified_at IS NOT NULL AND p.amount=a.amount AND p.currency=a.currency`)
      .bind(path, now, now, merchantId).all()).results || [];
  }
}
