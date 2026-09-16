const SLOT_BY_PLACEMENT = Object.freeze({
  tool_page: 'tool-primary',
  buyer_intent: 'buyer-intent-top',
  comparison: 'compare-decision-premium',
});

export function validateCampaignAssets(asset) {
  const required = [
    'companyName', 'productName', 'contactEmail', 'destinationUrl',
    'logoUrl', 'headline', 'description', 'ctaText', 'targetPage',
  ];
  const missing = required.filter((key) => typeof asset?.[key] !== 'string' || !asset[key].trim());
  if (missing.length) return { status: 'invalid', notes: `Missing required fields: ${missing.join(', ')}` };
  if (!asset.sellerAttestation) return { status: 'invalid', notes: 'Seller attestation is required.' };
  if (!asset.targetPage.startsWith('/') || asset.targetPage.startsWith('//') || asset.targetPage.length > 300) {
    return { status: 'invalid', notes: 'Target page must be an exact COSHUMA path beginning with /.' };
  }
  if (asset.contactEmail.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(asset.contactEmail)) {
    return { status: 'invalid', notes: 'Contact email is invalid.' };
  }
  try {
    const destination = new URL(asset.destinationUrl);
    const logo = new URL(asset.logoUrl);
    if (destination.protocol !== 'https:' || logo.protocol !== 'https:') {
      return { status: 'needs_review', notes: 'Destination and logo must use HTTPS.' };
    }
  } catch {
    return { status: 'invalid', notes: 'Destination URL or logo URL is invalid.' };
  }
  const risky = /(guaranteed income|guaranteed return|no risk|miracle|100% guaranteed|#1\b|number one\b)/i;
  if (risky.test(`${asset.headline} ${asset.description}`)) {
    return { status: 'needs_review', notes: 'Claims require manual review.' };
  }
  if (asset.headline.length > 100 || asset.description.length > 500 || asset.ctaText.length > 50) {
    return { status: 'needs_review', notes: 'Creative exceeds recommended length and requires review.' };
  }
  return { status: 'valid', notes: null };
}

function isoAddDays(iso, days) {
  return new Date(new Date(iso).getTime() + Number(days) * 86400000).toISOString();
}

async function queue(db, campaignId, recipientEmail, template, subject, payload, now) {
  if (!recipientEmail) return;
  await db.prepare(`
    INSERT INTO notification_outbox (
      id, campaign_id, recipient_email, template, subject, payload_json, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, 'queued', ?)
  `).bind(
    crypto.randomUUID(), campaignId, recipientEmail,
    template, subject, JSON.stringify(payload), now,
  ).run();
}

async function metrics(db, campaignId) {
  const row = await db.prepare(`
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

export async function publishCampaignIfEligible(db, campaignId, now = new Date().toISOString()) {
  const row = await db.prepare(`
    SELECT c.*, a.contact_email AS asset_contact_email,
      a.target_page, a.desired_start_date, a.validation_status
    FROM campaigns c JOIN campaign_assets a ON a.campaign_id = c.id
    WHERE c.id = ?
  `).bind(campaignId).first();
  if (!row || row.status !== 'ready_to_publish' || row.validation_status !== 'valid') return row;

  let startsAt = now;
  if (row.desired_start_date) {
    const candidate = new Date(`${row.desired_start_date}T00:00:00.000Z`);
    if (!Number.isNaN(candidate.getTime()) && candidate.getTime() > Date.parse(now)) startsAt = candidate.toISOString();
  }
  const endsAt = isoAddDays(startsAt, row.duration_days);
  const conflict = await db.prepare(`
    SELECT c.id FROM campaigns c JOIN campaign_assets a ON a.campaign_id=c.id
    WHERE c.id <> ? AND c.status='published' AND c.placement=? AND a.target_page=?
      AND c.starts_at < ? AND c.ends_at > ? LIMIT 1
  `).bind(campaignId, row.placement, row.target_page, endsAt, startsAt).first();
  if (conflict) {
    await db.prepare("UPDATE campaigns SET status='pending_review', updated_at=? WHERE id=?")
      .bind(now, campaignId).run();
    await db.prepare(`
      UPDATE campaign_assets
      SET validation_status='needs_review',
        validation_notes='Requested placement conflicts with an existing campaign flight.', updated_at=?
      WHERE campaign_id=?
    `).bind(now, campaignId).run();
    return db.prepare('SELECT * FROM campaigns WHERE id=?').bind(campaignId).first();
  }

  await db.prepare(`
    UPDATE campaigns SET status='published', starts_at=?, ends_at=?, updated_at=?
    WHERE id=? AND status='ready_to_publish'
  `).bind(startsAt, endsAt, now, campaignId).run();
  await queue(
    db,
    campaignId,
    row.asset_contact_email || row.contact_email,
    'campaign_live',
    'Your COSHUMA campaign is scheduled',
    {
      campaignId,
      productId: row.product_id,
      placement: row.placement,
      targetPage: row.target_page,
      startsAt,
      endsAt,
      reportToken: row.report_token,
    },
    now,
  );
  return db.prepare('SELECT * FROM campaigns WHERE id=?').bind(campaignId).first();
}

export async function activePlacementsForPath(db, path, now = new Date().toISOString()) {
  if (typeof path !== 'string' || !path.startsWith('/') || path.startsWith('//') || path.length > 300) return [];
  const result = await db.prepare(`
    SELECT c.id AS campaign_id, c.placement, c.starts_at, c.ends_at,
      a.product_name, a.destination_url, a.logo_url, a.headline, a.description, a.cta_text
    FROM campaigns c JOIN campaign_assets a ON a.campaign_id=c.id
    WHERE c.status='published' AND a.target_page=? AND c.starts_at <= ? AND c.ends_at > ?
  `).bind(path, now, now).all();
  return (result.results || []).map((row) => ({
    campaignId: row.campaign_id,
    slot: SLOT_BY_PLACEMENT[row.placement],
    placement: row.placement,
    label: 'Sponsored',
    title: row.headline,
    body: row.description,
    button: row.cta_text,
    url: row.destination_url,
    logoUrl: row.logo_url,
    productName: row.product_name,
    startAt: row.starts_at,
    endAt: row.ends_at,
  })).filter((item) => item.slot);
}

async function createReport(db, campaign, reportType, reportKey, periodStart, periodEnd, now) {
  const m = await metrics(db, campaign.id);
  const result = await db.prepare(`
    INSERT INTO campaign_reports (
      id, campaign_id, report_type, period_start, period_end,
      impressions, clicks, ctr, generated_at, delivery_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued')
    ON CONFLICT(id) DO NOTHING
  `).bind(
    reportKey, campaign.id, reportType, periodStart, periodEnd,
    m.impressions, m.clicks, m.ctr, now,
  ).run();
  if (result.meta?.changes !== 1) return false;
  const subject = reportType === 'final'
    ? 'COSHUMA final campaign report'
    : reportType === 'renewal'
      ? 'Your COSHUMA campaign ends in 3 days'
      : 'COSHUMA campaign performance update';
  await queue(
    db,
    campaign.id,
    campaign.contact_email,
    reportType === 'renewal' ? 'renewal' : 'campaign_report',
    subject,
    {
      campaignId: campaign.id,
      productId: campaign.product_id,
      placement: campaign.placement,
      startsAt: campaign.starts_at,
      endsAt: campaign.ends_at,
      verifiedMetrics: m,
      reportToken: campaign.report_token,
      signups: 'not_tracked_by_coshuma',
      purchases: 'not_tracked_by_coshuma',
      advertiserRevenue: 'not_tracked_by_coshuma',
    },
    now,
  );
  return true;
}

export async function runCampaignMaintenance(db, now = new Date().toISOString()) {
  const rows = await db.prepare("SELECT * FROM campaigns WHERE status='published'").all();
  for (const campaign of rows.results || []) {
    const startMs = Date.parse(campaign.starts_at);
    const endMs = Date.parse(campaign.ends_at);
    const nowMs = Date.parse(now);
    if (!Number.isFinite(startMs) || !Number.isFinite(endMs)) continue;
    const elapsedDays = Math.floor((nowMs - startMs) / 86400000);
    const remainingDays = Math.ceil((endMs - nowMs) / 86400000);
    const interimDays = campaign.duration_days <= 7 ? [3] : campaign.duration_days <= 30 ? [7, 14, 21] : [30, 60];
    for (const day of interimDays) {
      if (elapsedDays >= day && nowMs < endMs) {
        await createReport(
          db, campaign, 'interim', `${campaign.id}:interim:${day}`,
          campaign.starts_at, isoAddDays(campaign.starts_at, day), now,
        );
      }
    }
    if (remainingDays <= 3 && remainingDays > 0) {
      await createReport(
        db, campaign, 'renewal', `${campaign.id}:renewal`,
        campaign.starts_at, now, now,
      );
    }
    if (nowMs >= endMs) {
      await createReport(
        db, campaign, 'final', `${campaign.id}:final`,
        campaign.starts_at, campaign.ends_at, now,
      );
      await db.prepare("UPDATE campaigns SET status='ended', updated_at=? WHERE id=? AND status='published'")
        .bind(now, campaign.id).run();
    }
  }
}
