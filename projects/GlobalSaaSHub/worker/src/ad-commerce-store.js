// Canonical sandbox repository. No production entrypoint imports this module.
// Integrates reviewed local transition semantics with the remote migration-readiness guards.
import { IMAGE_SLOTS } from './ad-commerce-catalog.js';
import { AdError, orderInput, digest, newToken, plain } from './ad-commerce-domain.js';
const TABLES = ['ad_sale_orders','ad_sale_files','ad_sale_holds','ad_sale_events','ad_sale_audit','ad_sale_metric_events','ad_sale_metrics'];
const GUARDS = ['ad_sale_new_draft','ad_sale_quote_immutable','ad_sale_material_lock','ad_sale_file_insert_guard',
  'ad_sale_file_update_guard','ad_sale_file_delete_guard','ad_sale_terminal','ad_sale_approval_guard',
  'ad_sale_active_guard','ad_sale_stop_guard','ad_sale_lane_guard','ad_sale_transition_guard','ad_sale_capture_guard'];
export class AdStore {
  constructor(db, { environment, clock = () => new Date() } = {}) {
    if (environment !== 'sandbox') throw new AdError('This repository requires an isolated sandbox.', 503);
    if (!db?.prepare || !db?.batch) throw new AdError('The sandbox database is unavailable.', 503);
    this.db = db; this.clock = clock;
  }
  q(sql, ...values) { return this.db.prepare(sql).bind(...values); }
  now() { return this.clock().toISOString(); }
  async ready() {
    for (const table of TABLES) {
      const found = await this.q("SELECT name FROM sqlite_master WHERE type='table' AND name=?", table).first();
      if (!found) throw new AdError('The sandbox schema is incomplete.', 503);
    }
    const result = await this.q("SELECT name FROM sqlite_master WHERE type='trigger' AND name IN (" + GUARDS.map(() => '?').join(',') + ')', ...GUARDS).all();
    const names = new Set((result.results || []).map(row => row.name));
    if (GUARDS.some(name => !names.has(name))) throw new AdError('The sandbox protection rules are incomplete.', 503);
  }
  get(id) { return this.q('SELECT * FROM ad_sale_orders WHERE id=?', id).first(); }
  async files(id) {
    return (await this.q('SELECT id,role,mime,width,height,byte_size,sha256 FROM ad_sale_files WHERE order_id=? ORDER BY role', id).all()).results || [];
  }
  audit(id, action, actor, detail, at) {
    return this.q('INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at) VALUES(?,?,?,?,?,?)', crypto.randomUUID(), id, action, actor, detail, at);
  }
  async createDraft(rawInput) {
    const input = orderInput(rawInput), id = crypto.randomUUID(), accessToken = newToken(), at = this.now();
    const reference = 'TEST-AD-' + id;
    await this.db.batch([
      this.q(`INSERT INTO ad_sale_orders
        (id,reference,access_hash,product,catalog_version,days,amount,currency,quote_json,
         company,product_name,email,materials_json,rights_confirmed,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,1,?,?)`,
        id, reference, await digest(accessToken), input.quote.product, input.quote.version,
        input.quote.days, input.quote.amount, input.quote.currency, JSON.stringify(input.quote),
        input.company, input.productName, input.email, JSON.stringify({items:input.items,claims:input.claims}), at, at),
      this.audit(id, 'draft_created', 'sandbox_applicant', 'Server-validated sandbox draft', at),
    ]);
    return {order:await this.get(id), accessToken};
  }
  async requireState(id, allowed) {
    const order = await this.get(id);
    if (!order) throw new AdError('Order not found.',404);
    if (!allowed.includes(order.state)) throw new AdError('This operation is not available in the current order state.',409);
    return order;
  }
  async submitDraft(id) {
    const order = await this.requireState(id,['draft']);
    const expected = ['logo',...JSON.parse(order.quote_json).slots], files = await this.files(id);
    if (files.length !== expected.length || expected.some(role => !files.some(file => file.role === role))) throw new AdError('Upload every required, validated asset before submitting.',409);
    const at = this.now();
    const results = await this.db.batch([
      this.q("UPDATE ad_sale_orders SET state='submitted',updated_at=? WHERE id=? AND state='draft'",at,id),
      this.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
        SELECT ?,?,'submission_requested','sandbox_applicant',?,? WHERE changes()=1`,crypto.randomUUID(),id,'Complete asset set submitted for review',at),
    ]);
    if (results[0].meta.changes !== 1) throw new AdError('The order changed; reload it before continuing.',409);
    return this.get(id);
  }
  async review(id,{reviewer,decision,notes,destinationChecked,claimsChecked}) {
    const actor = plain(reviewer,'Reviewer',1,120), detail = plain(notes,'Review notes',1,1800);
    if (!['approve','revise','reject'].includes(decision)) throw new AdError('Choose a valid review decision.');
    if (decision === 'approve' && (destinationChecked !== true || claimsChecked !== true)) throw new AdError('Confirm the destination and supporting claims before approving.');
    await this.requireState(id,['submitted']);
    const at = this.now(), state = {approve:'approved',revise:'draft',reject:'rejected'}[decision];
    const results = await this.db.batch([
      this.q(`UPDATE ad_sale_orders SET state=?,approved_by=?,approved_at=?,review_notes=?,updated_at=?
        WHERE id=? AND state='submitted'`,state,decision === 'approve' ? actor : null,decision === 'approve' ? at : null,detail,at,id),
      this.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
        SELECT ?,?,?,?,?,? WHERE changes()=1`,crypto.randomUUID(),id,'review_'+decision,actor,detail,at),
    ]);
    if (results[0].meta.changes !== 1) throw new AdError('The review state changed; reload the order.',409);
    return this.get(id);
  }
  async availability() {
    const at = this.now(), result = [];
    for (const slot of IMAGE_SLOTS) {
      const used = await this.q(`SELECT count(*) AS n FROM ad_sale_holds h JOIN ad_sale_orders o ON o.id=h.order_id
        WHERE h.slot=? AND (h.expires_at>? OR o.state IN('capturing','active'))`,slot.id,at).first();
      const legacy = await this.q(`SELECT count(*) AS n FROM sponsorship_applications WHERE slot=? AND publication_status='published' AND ends_at>?`,slot.id,at).first();
      result.push({...slot,available:legacy.n ? 0 : Math.max(0,slot.capacity-used.n)});
    }
    return result;
  }
  async reserveReviewedOrder(id,ttlMinutes=30) {
    if (!Number.isInteger(ttlMinutes) || ttlMinutes < 1 || ttlMinutes > 60) throw new AdError('Invalid reservation period.');
    const order = await this.requireState(id,['approved']);
    const at = this.now(), until = new Date(Date.parse(at)+ttlMinutes*60000).toISOString(), slots = JSON.parse(order.quote_json).slots;
    const reusable = async candidate => {
      if (!candidate || candidate.state !== 'approved' || !(candidate.hold_until > this.now())) return false;
      const existing = (await this.q('SELECT slot,expires_at FROM ad_sale_holds WHERE order_id=?',id).all()).results;
      return existing.length === slots.length && slots.every(slot => existing.some(hold => hold.slot === slot && hold.expires_at === candidate.hold_until));
    };
    if (await reusable(order)) return order;
    const statements = [this.q(`DELETE FROM ad_sale_holds WHERE expires_at<=?
      AND order_id IN(SELECT id FROM ad_sale_orders WHERE state NOT IN('capturing','active'))`,at)];
    for (const slotId of slots) {
      const slot = IMAGE_SLOTS.find(item => item.id === slotId);
      if (!slot) throw new AdError('Unknown reserved position.',409);
      const occupied = (await this.q(`SELECT h.lane FROM ad_sale_holds h JOIN ad_sale_orders o ON o.id=h.order_id
        WHERE h.slot=? AND (h.expires_at>? OR o.state IN('capturing','active'))`,slotId,at).all()).results;
      const lane = Array.from({length:slot.capacity},(_,i)=>i+1).find(candidate => !occupied.some(item=>item.lane===candidate));
      if (!lane) throw new AdError('A selected position is unavailable; nothing has been charged.',409);
      statements.push(this.q(`INSERT INTO ad_sale_holds(slot,lane,order_id,expires_at)
        SELECT ?,?,?,? WHERE EXISTS(SELECT 1 FROM ad_sale_orders WHERE id=? AND state='approved')`,slotId,lane,id,until,id));
    }
    statements.push(this.q("UPDATE ad_sale_orders SET hold_until=?,updated_at=? WHERE id=? AND state='approved'",until,at,id));
    statements.push(this.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
      SELECT ?,?,'positions_reserved','sandbox_service',?,? WHERE changes()=1`,crypto.randomUUID(),id,JSON.stringify({slots,expiresAt:until}),at));
    try {
      const results=await this.db.batch(statements);
      if (results[results.length-2].meta.changes !== 1) throw new AdError('The order changed before reservation.',409);
    } catch (error) {
      const current=await this.get(id);
      if (await reusable(current)) return current;
      throw error;
    }
    return this.get(id);
  }

  async renewCheckoutReservation(id,ttlMinutes=30) {
    if (!Number.isInteger(ttlMinutes) || ttlMinutes < 1 || ttlMinutes > 60) throw new AdError('Invalid reservation period.');
    const order = await this.requireState(id,['checkout']);
    const at = this.now(), until = new Date(Date.parse(at)+ttlMinutes*60000).toISOString(), slots = JSON.parse(order.quote_json).slots;
    const statements = [this.q(`DELETE FROM ad_sale_holds WHERE expires_at<=?
      AND order_id IN(SELECT id FROM ad_sale_orders WHERE state NOT IN('capturing','active'))`,at)];
    for (const slotId of slots) {
      const slot = IMAGE_SLOTS.find(item => item.id === slotId);
      if (!slot) throw new AdError('Unknown reserved position.',409);
      const occupied = (await this.q(`SELECT h.lane FROM ad_sale_holds h JOIN ad_sale_orders o ON o.id=h.order_id
        WHERE h.slot=? AND h.order_id<>? AND (h.expires_at>? OR o.state IN('capturing','active'))`,slotId,id,at).all()).results;
      const lane = Array.from({length:slot.capacity},(_,i)=>i+1).find(candidate => !occupied.some(item=>item.lane===candidate));
      if (!lane) throw new AdError('A selected position is unavailable; the approved payment was not captured.',409);
      statements.push(this.q(`INSERT INTO ad_sale_holds(slot,lane,order_id,expires_at) VALUES(?,?,?,?)`,
        slotId,lane,id,until));
    }
    statements.push(this.q("UPDATE ad_sale_orders SET hold_until=?,updated_at=? WHERE id=? AND state='checkout'",until,at,id));
    statements.push(this.q(`INSERT INTO ad_sale_audit(id,order_id,action,actor,detail,created_at)
      SELECT ?,?,'checkout_reservation_renewed','sandbox_service',?,? WHERE changes()=1`,
      crypto.randomUUID(),id,JSON.stringify({slots,expiresAt:until}),at));
    try {
      const results=await this.db.batch(statements);
      if (results[results.length-2].meta.changes !== 1) throw new AdError('The checkout changed before reservation recovery.',409);
    } catch (error) {
      throw error;
    }
    return this.get(id);
  }
}
