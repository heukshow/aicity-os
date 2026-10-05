"""House-ad source/asset checks. No payment or network operations."""
import importlib.util
from pathlib import Path
import re
import unittest
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('house', ROOT / 'scripts/prepare_coshuma_promotions.py')
house = importlib.util.module_from_spec(spec)
spec.loader.exec_module(house)

class HousePromotionTests(unittest.TestCase):
    def setUp(self):
        self.config = house.load_manifest()
        self.rows = self.config['promotions']

    def test_exact_three_route_dimensions_and_small_images(self):
        self.assertEqual(len(self.rows), 3)
        for row in self.rows:
            f = ROOT / 'public' / row['image'].lstrip('/')
            self.assertEqual(house.image_size(f), (row['width'], row['height']))
            self.assertLessEqual(f.stat().st_size, row['max_bytes'])

    def test_copy_matches_guide_limits(self):
        for row in self.rows:
            for field, low, high in [('title',5,80),('description',20,240),('button',2,30),('alt',10,160)]:
                self.assertTrue(low <= len(row[field]) <= high)
                self.assertNotRegex(row[field], r'[<>\r\n]')

    def test_correct_position_and_idempotent(self):
        for row in self.rows:
            text = (ROOT / 'public' / row['page'].lstrip('/')).read_text(encoding='utf-8')
            first = house.prepare(text, row)
            self.assertEqual(house.prepare(first, row), first)
            self.assertEqual(first.count('data-coshuma-promotion='), 1)
            self.assertEqual(first.count('id="coshuma-promotion"'), 1)
            self.assertLess(first.index('data-sponsored-slot='), first.index('data-coshuma-promotion='))
            self.assertLess(first.index('data-coshuma-promotion='), first.index(row['next_heading']))

    def test_original_content_preserved_outside_our_exact_block(self):
        for row in self.rows:
            original = (ROOT / 'public' / row['page'].lstrip('/')).read_text(encoding='utf-8')
            clean = house.prepare(original, row, False)
            changed = house.prepare(clean, row)
            def normalize(text):
                text = house.BLOCK.sub('', text)
                for tag in (house.CSS, house.JS): text = text.replace(tag, '')
                return re.sub(r'\s+', ' ', text).strip()
            self.assertEqual(normalize(clean), normalize(changed))

    def test_disable_removes_only_house_block(self):
        for row in self.rows:
            original = (ROOT / 'public' / row['page'].lstrip('/')).read_text(encoding='utf-8')
            off = house.prepare(house.prepare(original,row),row,False)
            self.assertNotIn('data-coshuma-promotion=',off)
            self.assertIn('data-sponsored-slot=',off)
            self.assertNotIn(house.CSS,off)
            self.assertNotIn(house.JS,off)

    def test_missing_duplicate_or_changed_slot_fails_closed(self):
        row = self.rows[0]
        with self.assertRaises(ValueError): house.prepare('<html><head></head><body></body></html>',row)
        fixture = '<html><head></head><body><section data-sponsored-slot="tool-primary"></section>'
        with self.assertRaises(ValueError): house.prepare(fixture + '<section data-sponsored-slot="tool-primary"></section>Current Pipedrive plan snapshot</body></html>',row)
        with self.assertRaises(ValueError): house.prepare(fixture + '<h2>Different layout</h2></body></html>',row)

    def test_escaped_copy_and_no_paid_claim(self):
        row = dict(self.rows[0], title='A & B "guide"')
        html = house.card(row)
        self.assertIn('A &amp; B &quot;guide&quot;',html)
        self.assertIn('Advertisement',html)
        self.assertIn('COSHUMA self-promotion',html)
        self.assertNotRegex(html,r'paymentVerified|sponsored_impression|sponsored_click|data-cta="affiliate"')

    def test_runtime_has_no_payment_network_or_false_revenue_events(self):
        s = (ROOT/'public/coshuma-promotions.js').read_text(encoding='utf-8')
        self.assertNotRegex(s,r'\bfetch\s*\(|paypal|paymentVerified|sponsored_impression|sponsored_click')
        self.assertIn('coshuma_promo_view',s)
        self.assertIn('coshuma_promo_click',s)
        self.assertIn('coshuma_qa',s)

    def test_source_has_no_protected_route_house_card(self):
        for relative in ['index.html','public/tool/gamma.html','public/tool/chatbase.html','public/compare/privy-vs-omnisend.html']:
            path=ROOT/relative
            if path.is_file(): self.assertNotIn('data-coshuma-promotion=',path.read_text(encoding='utf-8'))

if __name__ == '__main__': unittest.main()
