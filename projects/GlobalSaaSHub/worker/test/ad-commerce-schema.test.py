"""SQLite in-memory guards only; never connects to Cloudflare or PayPal."""
import sqlite3,json,unittest
from pathlib import Path
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parents[1]
class SchemaTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:');self.db.execute('PRAGMA foreign_keys=ON')
  self.db.executescript((ROOT/'migrations/0004_sponsorship_sales.sql').read_text(encoding='utf-8'))
  self.db.executescript((ROOT/'migrations/0005_image_ad_fulfilment.sql').read_text(encoding='utf-8'))
  self.now=datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
  self.later=(datetime.now(timezone.utc)+timedelta(days=30)).isoformat(timespec='milliseconds').replace('+00:00','Z')
 def tearDown(self):self.db.close()
 def order(self,id='test',slots=None):
  slots=slots or ['tool-primary'];quote=json.dumps({'slots':slots})
  self.db.execute('''INSERT INTO ad_sale_orders(id,reference,access_hash,product,catalog_version,days,amount,currency,quote_json,company,product_name,email,materials_json,rights_confirmed,created_at,updated_at)
   VALUES(?,?,?,?,?,30,'49.00','USD',?,?,?,?,?,1,?,?)''',(id,'LOCAL-'+id,'a'*64,slots[0],'local-test',quote,'LOCAL TEST ONLY','TEST','test@example.com','{}',self.now,self.now))
  return id
 def files(self,id,slots=None):
  for role in ['logo',*(slots or ['tool-primary'])]:
   self.db.execute('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)',(id+'-'+role,id,role,'image/png',400,400,1,'b'*64,b'x'))
 def approved(self,id='test',slots=None):
  self.order(id,slots);self.files(id,slots)
  self.db.execute("UPDATE ad_sale_orders SET state='submitted' WHERE id=?",(id,))
  self.db.execute("UPDATE ad_sale_orders SET state='approved',approved_by='local-test',approved_at=? WHERE id=?",(self.now,id))
  return id
 def capturing(self,id='test',slots=None):
  self.approved(id,slots)
  for slot in slots or ['tool-primary']:
   self.db.execute('INSERT INTO ad_sale_holds VALUES(?,1,?,?)',(slot,id,self.later))
  self.db.execute("UPDATE ad_sale_orders SET state='checkout',provider_order=?,merchant_id='LOCAL',payment_environment='sandbox' WHERE id=?",('LOCAL-ORDER-'+id,id))
  self.db.execute("UPDATE ad_sale_orders SET state='capturing' WHERE id=?",(id,))
  return id
 def test_new_order_cannot_start_active(self):
  self.order()
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE ad_sale_orders SET state='active' WHERE id='test'")
 def test_quote_cannot_be_changed(self):
  self.order()
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE ad_sale_orders SET amount='0.01' WHERE id='test'")
 def test_approval_needs_complete_files(self):
  self.order();self.db.execute("UPDATE ad_sale_orders SET state='submitted' WHERE id='test'")
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE ad_sale_orders SET state='approved',approved_by='local',approved_at=? WHERE id='test'",(self.now,))
 def test_submitted_files_are_locked(self):
  self.approved()
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE ad_sale_files SET sha256='changed' WHERE order_id='test'")
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("DELETE FROM ad_sale_files WHERE order_id='test'")
 def test_unselected_file_role_is_rejected(self):
  self.order()
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute('INSERT INTO ad_sale_files VALUES(?,?,?,?,?,?,?,?,?)',('wrong','test','unknown','image/png',1,1,1,'b'*64,b'x'))
 def test_fixed_capacity_is_one(self):
  self.approved()
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("INSERT INTO ad_sale_holds VALUES('tool-primary',2,'test',?)",(self.later,))
 def test_rotation_capacity_cannot_exceed_three(self):
  self.approved(slots=['tool-rotation'])
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("INSERT INTO ad_sale_holds VALUES('tool-rotation',4,'test',?)",(self.later,))
 def test_missing_environment_or_hold_prevents_capture(self):
  self.approved();self.db.execute("UPDATE ad_sale_orders SET state='checkout',provider_order='LOCAL',merchant_id='LOCAL' WHERE id='test'")
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE ad_sale_orders SET state='capturing' WHERE id='test'")
 def test_activation_needs_verified_evidence(self):
  self.capturing()
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE ad_sale_orders SET state='active',starts_at=?,ends_at=? WHERE id='test'",(self.now,self.later))
 def test_quote_two_slots_must_both_be_reserved(self):
  slots=['tool-primary','buyer-intent-top'];self.approved(slots=slots)
  self.db.execute("INSERT INTO ad_sale_holds VALUES('tool-primary',1,'test',?)",(self.later,))
  self.db.execute("UPDATE ad_sale_orders SET state='checkout',provider_order='LOCAL',merchant_id='LOCAL',payment_environment='sandbox' WHERE id='test'")
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE ad_sale_orders SET state='capturing' WHERE id='test'")
 def test_competing_bundle_transaction_rolls_back(self):
  self.approved('first');self.approved('bundle',['buyer-intent-top','tool-primary'])
  self.db.execute("INSERT INTO ad_sale_holds VALUES('tool-primary',1,'first',?)",(self.later,));self.db.commit()
  with self.assertRaises(sqlite3.IntegrityError):
   with self.db:
    self.db.execute("INSERT INTO ad_sale_holds VALUES('buyer-intent-top',1,'bundle',?)",(self.later,))
    self.db.execute("INSERT INTO ad_sale_holds VALUES('tool-primary',1,'bundle',?)",(self.later,))
  self.assertEqual(self.db.execute("SELECT count(*) FROM ad_sale_holds WHERE order_id='bundle'").fetchone()[0],0)
 def test_refunded_state_is_terminal(self):
  self.capturing();self.db.execute("UPDATE ad_sale_orders SET state='refunded' WHERE id='test'")
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("UPDATE ad_sale_orders SET state='active' WHERE id='test'")
if __name__=='__main__':unittest.main(verbosity=2)
