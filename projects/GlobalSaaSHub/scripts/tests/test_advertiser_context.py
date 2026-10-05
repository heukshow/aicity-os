"""Keep advertiser previews distinct from editorial and affiliate content."""
from pathlib import Path
from html.parser import HTMLParser
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import prepare_placement_expansion as producer

class Tags(HTMLParser):
    def __init__(self):super().__init__();self.tags=[]
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))

class ContextTests(unittest.TestCase):
    def setUp(self):
        self.config=producer.load_config();self.html=producer.inventory_section(self.config)
        self.tags=Tags();self.tags.feed(self.html)
    def test_eight_previews_and_all_thirteen_creatives(self):
        self.assertEqual(self.html.count('data-position-preview='),8)
        self.assertEqual(sum('data-preview-slide' in a for t,a in self.tags.tags),13)
        self.assertEqual(self.html.count('data-advertiser-logo'),13)
        self.assertEqual(self.html.count('Example advertiser: COSHUMA.'),8)
        self.assertNotIn('HighLevel',self.html)
    def test_default_links_stay_here_and_article_links_are_explicit(self):
        starts=[a for t,a in self.tags.tags if 'data-ad-position' in a]
        contexts=[a for t,a in self.tags.tags if 'data-context-link' in a]
        self.assertEqual(len(starts),8);self.assertEqual(len(contexts),8)
        for a in starts:self.assertEqual(a['href'],'#ad-preview-'+a['data-ad-position'])
        for a in contexts:
            self.assertEqual(a['target'],'_blank')
            self.assertIn('noopener',a['rel']);self.assertIn('data-live-example',a)
        self.assertIn('recommendations and affiliate links',self.html)
    def test_previews_have_no_vendor_link_or_paid_impression_path(self):
        for t,a in self.tags.tags:
            if t=='a':self.assertTrue(a['href'].startswith(('#','/')))
            if t=='img':self.assertTrue(a['src'].startswith(('/brand/','/promotions/')))
        for marker in ['data-house-slot=','data-coshuma-promotion=','data-cta="affiliate"','paypal.com','sponsored_impression']:
            self.assertNotIn(marker,self.html)
    def test_producer_repeatability_and_paid_hold(self):
        self.assertEqual(self.html,producer.inventory_section(self.config))
        self.assertFalse(self.config['paid_bookings_open'])
        self.assertFalse(json.loads((ROOT/'data/sponsorship-inventory.json').read_text(encoding='utf-8'))['enabled'])

if __name__=='__main__':unittest.main()
