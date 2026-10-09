"""Owner-requested clarity, no sales consultation, truthful readiness and logo consistency."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,unittest
R=Path(__file__).resolve().parents[2]
class Active(HTMLParser):
 def __init__(self):super().__init__();self.depth=0;self.tags=[];self.text=[]
 def handle_starttag(self,t,a):
  if t=='template':self.depth+=1
  elif not self.depth:self.tags.append((t,dict(a)))
 def handle_endtag(self,t):
  if t=='template':self.depth-=1
 def handle_data(self,s):
  if not self.depth:self.text.append(s)
class ClarityTests(unittest.TestCase):
 def setUp(self):
  self.html=(R/'public/advertise.html').read_text(encoding='utf-8');self.p=Active();self.p.feed(self.html);self.text=' '.join(self.p.text)
 def test_identity_and_editorial_independence(self):
  self.assertIn('COSHUMA is a software discovery and comparison site',self.text)
  self.assertIn('not the developer',self.text);self.assertIn('do not buy a better rating',self.text)
  hrefs=[a.get('href') for t,a in self.p.tags if t=='a']
  for href in ['/best/index.html','/compare/','/methodology.html','/affiliate-disclosure.html']:self.assertIn(href,hrefs)
 def test_review_gated_booking_has_no_inline_sales_consultation(self):
  # Customer fields stay in the inert template until the dedicated booking runtime
  # activates them; the static showcase itself remains free of inline collection.
  self.assertFalse(any(t in ['form','input','textarea'] for t,a in self.p.tags))
  for phrase in ['Discuss this placement','Help me choose','Prepare my inquiry','separate quote','start a conversation']:self.assertNotIn(phrase,self.text)
  self.assertIn('F1–F3 fixed image bookings are open',self.text)
  self.assertIn('Payment is offered only after COSHUMA approves the materials and reserves the position',self.text)
  self.assertIn('F4–F5 and R1–R3 remain preview-only',self.text)
  self.assertIn('No payment is collected with the application',self.text)
 def test_requirements_and_return_paths(self):
  for phrase in ['400 × 400','600 × 600','1200 × 675','1200 × 400','5–80','20–240','2–30','10–160']:self.assertIn(phrase,self.text)
  self.assertEqual(sum('data-position-preview' in a for t,a in self.p.tags),8)
  self.assertEqual(sum(a.get('class')=='ad-context-back' for t,a in self.p.tags),8)
  ids=[a['id'] for t,a in self.p.tags if 'id' in a];self.assertEqual(len(ids),len(set(ids)))
 def test_fresh_public_images_and_paid_stop(self):
  self.assertIn('Screenshots: 6 October 2026.',self.text)
  for t,a in self.p.tags:
   if t=='img' and a.get('src','').startswith('/'):self.assertTrue((R/'public'/a['src'].split('?')[0].lstrip('/')).is_file())
  inventory=json.loads((R/'data/sponsorship-inventory.json').read_text(encoding='utf-8'))
  self.assertFalse(inventory['enabled']);self.assertFalse(inventory['applications_open'])
  expansion=json.loads((R/'data/placement-expansion.json').read_text(encoding='utf-8'));self.assertFalse(expansion['paid_bookings_open'])
  self.assertTrue(all(s['rate_usd'] is None for s in expansion['slots']))
if __name__=='__main__':unittest.main()
