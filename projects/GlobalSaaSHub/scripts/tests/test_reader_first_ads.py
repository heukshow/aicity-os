"""Protect article-first presentation without weakening ad or payment validation."""
from pathlib import Path
import sys,json,unittest
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from reader_first_ads import reader_style,STYLE,SCRIPT
class ReaderFirstTests(unittest.TestCase):
 def test_style_install_is_idempotent(self):
  text='<html><head></head><body></body></html>'
  once=reader_style(text);self.assertEqual(once,reader_style(once))
  self.assertEqual(once.count(STYLE),1);self.assertEqual(once.count(SCRIPT),1)
 def test_all_placements_keep_shared_styles(self):
  for p in ['tool/pipedrive.html','best/claap-sales-follow-up-ai.html','compare/semrush-vs-frase.html','best/index.html','compare/index.html','advertise.html']:
   text=(R/'public'/p).read_text(encoding='utf-8')
   self.assertEqual(text.count(STYLE),1,p)
   self.assertIn('data-advertiser-logo',text,p)
 def test_no_clip_or_tiny_text_strategy(self):
  css=(R/'public/reader-first-ads.css').read_text(encoding='utf-8')
  for bad in ['line-clamp','scale(','text-overflow:ellipsis','position:fixed','font-size:8px']:
   self.assertNotIn(bad,css)
  self.assertIn('font-size:14px;line-height:1.5',css)
  self.assertIn('min-height:44px',css)
  self.assertIn('object-fit:contain',css)
 def test_dock_only_moves_on_ad_bearing_pages(self):
  js=(R/'public/affiliate-attribution.js').read_text(encoding='utf-8')
  self.assertIn("Boolean(document.querySelector('[data-coshuma-promotion],[data-house-slot]'))",js)
  self.assertIn("articleEnd.appendChild(dock)",js)
  self.assertIn("save_source: 'tool-decision-dock'",js)
  self.assertIn('cta.href = primary.href',js)
 def test_layout_helper_is_not_measurement_or_storage(self):
  js=(R/'public/reader-first-ads.js').read_text(encoding='utf-8')
  for bad in ['gtag','fetch(','localStorage','sessionStorage','innerHTML','setInterval']:
   self.assertNotIn(bad,js)
  self.assertIn('copy.remove()',js);self.assertIn('minHeight',js)
 def test_fixed_paid_inventory_and_source_dimensions_remain(self):
  d=json.loads((R/'data/sponsorship-inventory.json').read_text(encoding='utf-8'))
  self.assertTrue(d['enabled']);self.assertTrue(d['applications_open'])
  expansion=json.loads((R/'data/placement-expansion.json').read_text(encoding='utf-8'))
  self.assertFalse(expansion['paid_bookings_open'])
  p=json.loads((R/'data/coshuma-promotions.json').read_text(encoding='utf-8'))['promotions']
  self.assertEqual([(r['width'],r['height'],r['max_bytes']) for r in p],[(600,600,300000),(1200,675,500000),(1200,400,400000)])
if __name__=='__main__':unittest.main()
