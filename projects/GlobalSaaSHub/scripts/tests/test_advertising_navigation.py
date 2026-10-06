"""Protect navigability without reopening advertising sales."""
from pathlib import Path
from html.parser import HTMLParser
from unittest.mock import patch
import json,re,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import normalize_sponsorship_offer as clean
import prepare_placement_expansion as expanded

class Links(HTMLParser):
 def __init__(self):super().__init__();self.items=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'data-ad-position' in a:self.items.append(a)

class NavigationTests(unittest.TestCase):
 def test_header_mobile_and_footer_entries(self):
  text=(ROOT/'src/App.jsx').read_text(encoding='utf-8')
  for place in ['home-header','home-mobile','home-footer']:
   self.assertEqual(text.count('data-advertising-entry="'+place+'"'),1)
  self.assertIn('data-site-menu',text)
  self.assertLess(text.index('data-advertising-entry="home-header"'),text.index('{paymentConfig.checkoutEnabled'))
  self.assertIn("new URLSearchParams(window.location.search).get('coshuma_qa') === '1'",text)
 def test_cleanup_preserves_navigation_and_removes_inline_purchase(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'App.jsx';p.write_text('<nav><a href="/advertise.html">Advertise</a></nav><section id="submit" class="old">Old purchase</section>',encoding='utf-8')
   with patch.object(clean,'APP',p):
    clean.remove_home_solicitation();once=p.read_text(encoding='utf-8');clean.remove_home_solicitation()
   self.assertEqual(once,p.read_text(encoding='utf-8'))
   self.assertIn('href="/advertise.html"',once)
   self.assertNotIn('Old purchase',once)
 def test_actual_app_survives_cleanup(self):
  original=(ROOT/'src/App.jsx').read_text(encoding='utf-8')
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'App.jsx';p.write_text(original,encoding='utf-8')
   with patch.object(clean,'APP',p):clean.remove_home_solicitation()
   self.assertEqual(original,p.read_text(encoding='utf-8'))
 def test_eight_direct_links_match_existing_configs(self):
  config=expanded.load_config();html=expanded.inventory_section(config)
  parser=Links();parser.feed(html)
  self.assertEqual(len(parser.items),8)
  actual={a['data-ad-position']:a['href'] for a in parser.items}
  base=json.loads((ROOT/'data/coshuma-promotions.json').read_text(encoding='utf-8'))
  expected={r['slot']:r['page']+'#coshuma-promotion' for r in base['promotions']}
  expected.update({r['id']:r['page']+'#'+r['id'] for r in config['slots']})
  self.assertEqual(actual,{key:'#ad-preview-'+key for key in expected})
  self.assertTrue(all('data-live-example' not in a for a in parser.items))
  for key,url in expected.items():
   self.assertIn('data-context-link="'+key+'" href="'+url+'"',html)
  self.assertFalse(config['paid_bookings_open'])
 def test_directory_is_near_the_top(self):
  text=(ROOT/'public/advertise.html').read_text(encoding='utf-8')
  self.assertLess(text.index('id="placement-formats"'),text.index('<section id="materials"'))
  self.assertEqual(text.count('data-ad-position='),8)
  self.assertIn('data-position-directory href="#placement-formats"',text)
  self.assertIn('data-advertising-mode="inquiry"',text)
 def test_no_new_payment_activation(self):
  self.assertIn('enabled: false',(ROOT/'public/sponsored-inventory.js').read_text(encoding='utf-8'))
  data=json.loads((ROOT/'data/sponsorship-inventory.json').read_text(encoding='utf-8'))
  self.assertFalse(data['enabled']);self.assertFalse(data['applications_open'])

if __name__=='__main__':unittest.main()
