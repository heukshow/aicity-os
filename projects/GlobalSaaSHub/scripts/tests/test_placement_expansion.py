from pathlib import Path
from unittest.mock import patch
from html.parser import HTMLParser
import copy,json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_placement_expansion as p

class PlacementExpansionTests(unittest.TestCase):
 def setUp(self):
  self.data=p.load_config();self.by_id={c['id']:c for c in self.data['creatives']}
 def reject(self,changed):
  with patch.object(p.json,'loads',return_value=changed):
   with self.assertRaises(ValueError):p.load_config()
 def test_two_new_fixed_three_rotating_and_closed_paid_bookings(self):
  self.assertEqual(sum(r['mode']=='fixed' for r in self.data['slots']),2)
  self.assertEqual(sum(r['mode']=='rotating' for r in self.data['slots']),3)
  self.assertFalse(self.data['paid_bookings_open'])
  for row in self.data['slots']:
   self.assertEqual(row['capacity'],3 if row['mode']=='rotating' else 1)
   self.assertIsNone(row['rate_usd'])
 def test_fixed_cannot_become_shared_or_oversold(self):
  for mode in ['fixed','rotating']:
   data=copy.deepcopy(self.data);row=next(r for r in data['slots'] if r['mode']==mode)
   row['creative_ids']*=4;self.reject(data)
  data=copy.deepcopy(self.data);data['slots'][-1]['mode']='rotating';self.reject(data)
 def test_unsafe_external_creative_or_unapproved_pricing_is_rejected(self):
  for url in ['https://other.example/product','javascript:alert(1)','//other.example','/unknown']:
   data=copy.deepcopy(self.data);data['creatives'][0]['destination']=url;self.reject(data)
  data=copy.deepcopy(self.data);data['slots'][0]['rate_usd']=19;self.reject(data)
  data=copy.deepcopy(self.data);data['paid_bookings_open']=True;self.reject(data)
 def test_wrong_page_capacity_and_speed_are_rejected(self):
  for key,value in [('file','index.html'),('capacity',4),('interval_ms',500)]:
   data=copy.deepcopy(self.data);data['slots'][0][key]=value;self.reject(data)
 def test_all_real_anchors_and_producer_repeatability(self):
  for row in self.data['slots']:
   source=(ROOT/'public'/row['file']).read_text(encoding='utf-8')
   clean=p.BLOCK.sub('',source).replace(p.CSS,'').replace(p.JS,'')
   first=p.prepare(clean,row,self.by_id);second=p.prepare(first,row,self.by_id)
   self.assertEqual(first,second,row['id'])
   self.assertEqual(first.count('data-house-slot="'+row['id']+'"'),1)
   self.assertEqual(p.BLOCK.sub('',first).replace(p.CSS,'').replace(p.JS,''),clean)
   self.assertEqual(first.count('data-house-slide='),len(row['creative_ids']))
   self.assertLessEqual(first.count('data-house-slot=')+first.count('data-coshuma-promotion='),2)
 def test_disable_and_missing_anchor(self):
  row=self.data['slots'][0]
  source=(ROOT/'public'/row['file']).read_text(encoding='utf-8')
  self.assertNotIn('data-house-slot=',p.prepare(source,row,self.by_id,False))
  with self.assertRaises(ValueError):p.prepare('<html><head></head><body><section><h2>Unrelated</h2></section></body></html>',row,self.by_id)
 def test_ssr_has_only_one_visible_slide_and_controls_hidden_until_ready(self):
  class Parser(HTMLParser):
   def __init__(self):super().__init__();self.slides=[];self.controls=[]
   def handle_starttag(self,tag,attrs):
    a=dict(attrs)
    if 'data-house-slide' in a:self.slides.append(a)
    if 'data-house-controls' in a:self.controls.append(a)
  for row in self.data['slots']:
   parser=Parser();parser.feed(p.render_slot(row,self.by_id))
   self.assertEqual(sum('hidden' not in s for s in parser.slides),1)
   if row['mode']=='rotating':self.assertIn('hidden',parser.controls[0])
 def test_catalog_has_eight_positions_and_no_fixed_rate_for_rotation(self):
  text=p.inventory_section(self.data)
  self.assertEqual(text.count('<tr>'),9)
  self.assertIn('fixed-price catalogue',text)
  self.assertIn('not a guarantee of equal impressions',text)
  self.assertIn('not silently converted',text)
 def test_runtime_protects_privacy_and_measurement_contract(self):
  src=(ROOT/'public/house-placements.js').read_text(encoding='utf-8')
  for forbidden in ['fetch(', 'XMLHttpRequest','localStorage','sessionStorage','innerHTML','sponsored_impression','affiliate_click','paymentVerified']:
   self.assertNotIn(forbidden,src)
  for required in ['prefers-reduced-motion','visibilitychange','focusin','mouseenter','mouseleave','seen.has','intersectionRatio >= 0.5','8000','1000','coshuma_qa','house_placement_impression']:
   self.assertIn(required,src)
 def test_fixed_f1_f3_sales_open_without_opening_expansion_slots(self):
  self.assertIn('enabled: true',(ROOT/'public/sponsored-inventory.js').read_text(encoding='utf-8'))
  data=json.loads((ROOT/'data/sponsorship-inventory.json').read_text(encoding='utf-8'))
  self.assertIs(data['enabled'],True);self.assertIs(data['applications_open'],True)
  self.assertIs(self.data['paid_bookings_open'],False)
if __name__=='__main__':unittest.main()
