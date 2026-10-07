import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const migrations = fileURLToPath(new URL('../migrations/', import.meta.url));

// Python's standard-library SQLite also runs on the Node 20 site CI; node:sqlite
// is not available there. Every database and payment record below is synthetic.
const setup = String.raw`
import sqlite3
import sys
from pathlib import Path

migrations = Path(sys.argv[1])
def database(include_new=True):
    db = sqlite3.connect(':memory:')
    db.execute('PRAGMA foreign_keys = ON')
    for path in sorted(migrations.glob('*.sql')):
        if not include_new and path.name.startswith('0004_'):
            continue
        db.executescript(path.read_text())
    return db

def insert(db, table, values):
    columns = ','.join(values)
    placeholders = ','.join('?' for _ in values)
    db.execute(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', tuple(values.values()))

def application(db, app_id='APP-1', **changes):
    values = dict(
        id=app_id, reference='COSHUMA-' + app_id, access_token_hash='synthetic-token-hash',
        company_name='Example Company', tool_name='Example Tool', contact_email='advertiser@example.com',
        slot='tool-primary', duration_days=30, target_page='/tool/pipedrive.html',
        destination_url='https://example.com/product', headline='Example product for sales teams',
        description='Synthetic advertiser material for an offline database regression.', cta_text='View product',
        seller_attestation=1, amount='49.00', currency='USD',
        payment_status='verified', review_status='approved', publication_status='draft',
        approved_at='2027-01-01T00:00:00.000Z', approved_by='offline-test-reviewer',
        created_at='2027-01-01T00:00:00.000Z', updated_at='2027-01-01T00:00:00.000Z',
    )
    values.update(changes)
    insert(db, 'sponsorship_applications', values)

def payment(db, app_id='APP-1', **changes):
    values = dict(
        id='PAY-' + app_id, application_id=app_id, environment='live',
        provider_order_id='ORDER-' + app_id, merchant_id='MERCHANT-EXPECTED',
        capture_id='CAPTURE-' + app_id, amount='49.00', currency='USD', state='verified',
        verified_at='2027-01-01T00:00:00.000Z',
        created_at='2027-01-01T00:00:00.000Z', updated_at='2027-01-01T00:00:00.000Z',
    )
    values.update(changes)
    insert(db, 'sponsorship_payments', values)

def publish(db, app_id='APP-1', **changes):
    values = dict(publication_status='published', starts_at='2027-01-01T00:00:00.000Z', ends_at='2027-01-31T00:00:00.000Z')
    values.update(changes)
    assignments = ','.join(f'{column}=?' for column in values)
    db.execute(f'UPDATE sponsorship_applications SET {assignments} WHERE id=?', (*values.values(), app_id))

def rejected(action, label):
    try:
        action()
    except sqlite3.IntegrityError:
        return
    raise AssertionError('Database allowed ' + label)
`;

function runSqlite(checks) {
  const result = spawnSync(process.platform === 'win32' ? 'python' : 'python3', ['-c', `${setup}\n${checks}\nprint('ok')`, migrations], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(result.status, 0, result.stderr || result.error?.message || 'SQLite regression failed');
  assert.equal(result.stdout.trim(), 'ok');
}

test('additive migration and replay preserve populated legacy financial and operations tables', () => {
  runSqlite(String.raw`
db = database(include_new=False)
insert(db, 'orders', dict(id='legacy-order', provider_order_id='LEGACY-PAYPAL', provider='paypal', status='paid', amount='49.00', currency='USD', created_at='2026-01-01', updated_at='2026-01-02'))
insert(db, 'webhook_events', dict(event_id='LEGACY-EVENT', event_type='PAYMENT.CAPTURE.COMPLETED', status='processed', received_at='2026-01-01', processed_at='2026-01-02'))
insert(db, 'private_ops_documents', dict(name='legacy-document', content='preserve exactly', content_type='text/plain', updated_at='2026-01-01'))
insert(db, 'private_ops_login_limits', dict(client='legacy-client', bucket=1, attempts=2))
insert(db, 'campaigns', dict(id='legacy-campaign', order_id='legacy-order', provider_order_id='LEGACY-PAYPAL', product_id='legacy-product', placement='tool_page', duration_days=30, price_usd='49.00', status='published', advertiser_name='Legacy advertiser', contact_email='legacy@example.com', starts_at='2026-01-01', ends_at='2026-01-31', created_at='2026-01-01', updated_at='2026-01-02'))
insert(db, 'campaign_assets', dict(campaign_id='legacy-campaign', company_name='Legacy company', product_name='Legacy product', contact_email='legacy@example.com', destination_url='https://example.com/legacy', logo_url='https://example.com/logo.svg', headline='Legacy headline', description='Legacy description', cta_text='Visit', target_page='/tool/legacy.html', seller_attestation=1, validation_status='valid', submitted_at='2026-01-01', updated_at='2026-01-02'))
insert(db, 'campaign_events', dict(campaign_id='legacy-campaign', event_type='sponsored_click', page='/tool/legacy.html', occurred_at='2026-01-02'))
insert(db, 'campaign_reports', dict(id='legacy-report', campaign_id='legacy-campaign', report_type='final', period_start='2026-01-01', period_end='2026-01-31', impressions=12, clicks=2, ctr=2/12, generated_at='2026-02-01', delivery_status='sent', delivered_at='2026-02-01'))
insert(db, 'notification_outbox', dict(id='legacy-notification', campaign_id='legacy-campaign', recipient_email='legacy@example.com', template='final', subject='Legacy report', payload_json='{"legacy":true}', status='sent', created_at='2026-02-01', sent_at='2026-02-01'))
tables = ['orders', 'webhook_events', 'private_ops_documents', 'private_ops_login_limits', 'campaigns', 'campaign_assets', 'campaign_events', 'campaign_reports', 'notification_outbox']
before = {table: db.execute(f'SELECT * FROM {table} ORDER BY rowid').fetchall() for table in tables}
assert all(before.values()), 'Every legacy table must be populated before testing preservation'
new_migration = migrations / '0004_sponsorship_sales.sql'
for _ in range(2):
    db.executescript(new_migration.read_text())
    after = {table: db.execute(f'SELECT * FROM {table} ORDER BY rowid').fetchall() for table in tables}
    assert after == before, 'Existing financial/operations records changed'
assert db.execute('PRAGMA foreign_key_check').fetchall() == []
assert db.execute('SELECT COUNT(*) FROM sponsorship_applications').fetchone()[0] == 0
rejected(lambda: insert(db, 'orders', dict(id='invalid-legacy', provider_order_id='INVALID-LEGACY', provider='paypal', status='pending', amount='0.01', currency='USD', created_at='now', updated_at='now')), 'a change to the legacy fixed-price contract')
`);
});

test('publication requires saved live payment, approval evidence and the exact purchased duration', () => {
  runSqlite(String.raw`
db = database()
application(db)
payment(db)
publish(db)
assert db.execute('SELECT publication_status FROM sponsorship_applications').fetchone()[0] == 'published'

cases = [
    ('no saved payment', {}, None, {}),
    ('unverified application', {'payment_status': 'unpaid'}, {}, {}),
    ('unreviewed application', {'review_status': 'pending'}, {}, {}),
    ('rejected material', {'review_status': 'rejected'}, {}, {}),
    ('missing reviewer', {'approved_by': None}, {}, {}),
    ('empty reviewer', {'approved_by': ''}, {}, {}),
    ('whitespace reviewer', {'approved_by': '   '}, {}, {}),
    ('missing approval timestamp', {'approved_at': None}, {}, {}),
    ('empty approval timestamp', {'approved_at': ''}, {}, {}),
    ('unparseable approval timestamp', {'approved_at': 'not-a-date'}, {}, {}),
    ('pending payment', {}, {'state': 'pending'}, {}),
    ('payment awaiting review', {}, {'state': 'review'}, {}),
    ('refunded payment', {}, {'state': 'refunded'}, {}),
    ('sandbox payment', {}, {'environment': 'sandbox'}, {}),
    ('missing provider order', {}, {'provider_order_id': None}, {}),
    ('empty provider order', {}, {'provider_order_id': ''}, {}),
    ('whitespace provider order', {}, {'provider_order_id': '   '}, {}),
    ('missing capture', {}, {'capture_id': None}, {}),
    ('empty capture', {}, {'capture_id': ''}, {}),
    ('whitespace capture', {}, {'capture_id': '   '}, {}),
    ('empty merchant', {}, {'merchant_id': ''}, {}),
    ('whitespace merchant', {}, {'merchant_id': '   '}, {}),
    ('missing verification timestamp', {}, {'verified_at': None}, {}),
    ('empty verification timestamp', {}, {'verified_at': ''}, {}),
    ('unparseable verification timestamp', {}, {'verified_at': 'not-a-date'}, {}),
    ('payment amount mismatch', {}, {'amount': '0.01'}, {}),
    ('missing start', {}, {}, {'starts_at': None}),
    ('missing end', {}, {}, {'ends_at': None}),
    ('invalid start', {}, {}, {'starts_at': 'not-a-date'}),
    ('invalid end', {}, {}, {'ends_at': 'not-a-date'}),
    ('shorter purchased duration', {}, {}, {'ends_at': '2027-01-30T00:00:00.000Z'}),
    ('longer purchased duration', {}, {}, {'ends_at': '2027-02-01T00:00:00.000Z'}),
    ('end before start', {}, {}, {'ends_at': '2026-12-02T00:00:00.000Z'}),
]
for label, app_changes, payment_changes, period_changes in cases:
    db = database()
    application(db, **app_changes)
    if payment_changes is not None:
        payment(db, **payment_changes)
    rejected(lambda: publish(db, **period_changes), label)
    assert db.execute('SELECT publication_status FROM sponsorship_applications').fetchone()[0] == 'draft', label
    db.close()

db = database()
rejected(lambda: application(db, publication_status='published'), 'published-at-insert bypass')
`);
});

test('one page and slot cannot oversell an overlapping period, but boundary periods remain available', () => {
  runSqlite(String.raw`
db = database()
application(db, 'APP-1')
payment(db, 'APP-1')
publish(db, 'APP-1')
application(db, 'APP-2')
payment(db, 'APP-2')
rejected(lambda: publish(db, 'APP-2'), 'identical page/slot/period')
rejected(lambda: publish(db, 'APP-2', starts_at='2027-01-15T00:00:00.000Z', ends_at='2027-02-14T00:00:00.000Z'), 'partially overlapping period')
publish(db, 'APP-2', starts_at='2027-01-31T00:00:00.000Z', ends_at='2027-03-02T00:00:00.000Z')
assert db.execute("SELECT COUNT(*) FROM sponsorship_applications WHERE publication_status='published'").fetchone()[0] == 2
application(db, 'APP-3', slot='buyer-intent-top', target_page='/best/claap-sales-follow-up-ai.html', amount='99.00')
payment(db, 'APP-3', amount='99.00')
publish(db, 'APP-3')
assert db.execute("SELECT COUNT(*) FROM sponsorship_applications WHERE publication_status='published'").fetchone()[0] == 3
`);
});

test('refunds stop a published placement and cannot be undone by late payment completion', () => {
  runSqlite(String.raw`
db = database()
application(db)
payment(db)
publish(db)
db.execute("UPDATE sponsorship_payments SET state='refunded', updated_at='2027-01-02T00:00:00.000Z' WHERE application_id='APP-1'")
assert db.execute('SELECT payment_status,publication_status FROM sponsorship_applications').fetchone() == ('refunded','paused')
rejected(lambda: db.execute("UPDATE sponsorship_payments SET state='verified' WHERE application_id='APP-1'"), 'late completed payment after refund')
rejected(lambda: publish(db), 'republication after refund')
assert db.execute('SELECT state FROM sponsorship_payments').fetchone()[0] == 'refunded'
db.execute("UPDATE sponsorship_payments SET state='refunded' WHERE application_id='APP-1'")
assert db.execute('SELECT payment_status,publication_status FROM sponsorship_applications').fetchone() == ('refunded','paused')
`);
});

test('a payment that needs review pauses publication and never silently republishes', () => {
  runSqlite(String.raw`
db = database()
application(db)
payment(db)
publish(db)
db.execute("UPDATE sponsorship_payments SET state='review' WHERE application_id='APP-1'")
assert db.execute('SELECT payment_status,publication_status FROM sponsorship_applications').fetchone() == ('review','paused')
db.execute("UPDATE sponsorship_payments SET state='verified' WHERE application_id='APP-1'")
assert db.execute('SELECT publication_status FROM sponsorship_applications').fetchone()[0] == 'paused'
`);
});

test('approved quote and creative cannot be replaced under the same application', () => {
  runSqlite(String.raw`
db = database()
application(db)
changes = dict(reference='OTHER', company_name='Other company', tool_name='Other tool', slot='buyer-intent-top', duration_days=7, target_page='/tool/gamma.html', destination_url='https://example.com/replacement', headline='Replacement headline', description='Replacement material', cta_text='Buy now', amount='0.01', currency='EUR')
original = db.execute('SELECT * FROM sponsorship_applications').fetchone()
for column, value in changes.items():
    rejected(lambda: db.execute(f'UPDATE sponsorship_applications SET {column}=? WHERE id=?', (value,'APP-1')), 'changed ' + column)
    assert db.execute('SELECT * FROM sponsorship_applications').fetchone() == original
`);
});

test('provider evidence and webhook IDs cannot be reused for another paid application', () => {
  runSqlite(String.raw`
db = database()
application(db, 'APP-1')
payment(db, 'APP-1')
application(db, 'APP-2')
rejected(lambda: payment(db, 'APP-2', provider_order_id='ORDER-APP-1'), 'reused provider order')
rejected(lambda: payment(db, 'APP-2', capture_id='CAPTURE-APP-1'), 'reused provider capture')
rejected(lambda: payment(db, 'APP-1', id='OTHER-PAYMENT', provider_order_id='OTHER-ORDER', capture_id='OTHER-CAPTURE'), 'second payment for one application')
event = dict(environment='live', event_id='WEBHOOK-1', event_type='PAYMENT.CAPTURE.COMPLETED', processed_at='2027-01-01T00:00:00.000Z')
insert(db, 'sponsorship_webhook_events', event)
rejected(lambda: insert(db, 'sponsorship_webhook_events', event), 'duplicate provider webhook')
assert db.execute('PRAGMA foreign_key_check').fetchall() == []
`);
});
