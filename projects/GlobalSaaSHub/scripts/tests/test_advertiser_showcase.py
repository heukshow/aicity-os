"""Regressions for the F1-F3 image-ad booking rollout and truthful sales UI."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,unittest,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import normalize_sponsorship_offer as normalizer

class ActiveElements(HTMLParser):
    def __init__(self):
        super().__init__();self.depth=0;self.tags=[];self.text=[]
    def handle_starttag(self,tag,attrs):
        if tag=='template': self.depth+=1
        elif not self.depth:self.tags.append((tag,dict(attrs)))
    def handle_endtag(self,tag):
        if tag=='template':self.depth-=1
    def handle_data(self,text):
        if not self.depth:self.text.append(text)

class AdvertiserShowcaseTests(unittest.TestCase):
    def setUp(self):
        self.html=(ROOT/'public/advertise.html').read_text(encoding='utf-8')
        self.parser=ActiveElements();self.parser.feed(self.html)
        self.active=' '.join(self.parser.text)
        self.js=(ROOT/'public/advertiser-showcase.js').read_text(encoding='utf-8')
    def test_booking_page_activates_only_the_scripted_image_application(self):
        self.assertIn('data-advertising-mode="booking"',self.html)
        ids=[attrs.get('id') for _,attrs in self.parser.tags if attrs.get('id')]
        self.assertEqual(len(ids),len(set(ids)))
        for name in ['about-coshuma','materials','materials-title']:
            self.assertIn(name,ids)
        for name in ['sponsorship-application','paypal-buttons','payment-area','advertiser-brief']:
            self.assertNotIn(name,ids)
        sales=(ROOT/'public/sponsorship-sales.js').read_text(encoding='utf-8')
        self.assertIn("['booking','live'].includes(document.body?.dataset.advertisingMode || '')",sales)
        self.assertIn("document.getElementById('image-ad-application')",sales)
        self.assertIn("'/v1/ads/applications'",sales)
        self.assertIn("input.accept = 'image/png,.png'",sales)
        self.assertIn('F1–F3 fixed image bookings are open',self.active)

    def test_showcase_preview_script_does_not_collect_application_data(self):
        for token in ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML']:
            self.assertNotIn(token,self.js)
        self.assertNotIn('clipboard.writeText',self.js)
        self.assertIn("params.get('coshuma_qa') === '1'",self.js)

    def test_real_examples_are_local_and_labeled_as_house_ads(self):
        images=[a['src'] for t,a in self.parser.tags if t=='img' and a.get('src','').startswith('/promotions/showcase-')]
        self.assertEqual(len(images),6)
        for src in images:
            self.assertTrue(src.startswith('/promotions/showcase-'))
            self.assertTrue((ROOT/'public'/src.split('?',1)[0].lstrip('/')).is_file())
        self.assertIn('not a paid client campaign',self.active)
        self.assertIn('simulated viewport',self.active)
        self.assertNotIn('Copyedited_20261005.pdf',self.html)
    def test_price_regeneration_is_idempotent_and_preserves_phase_one_checkout_gate(self):
        first=(ROOT/'public/advertise.html').read_bytes()
        normalizer.sync_advertise_catalog()
        second=(ROOT/'public/advertise.html').read_bytes()
        normalizer.sync_advertise_catalog()
        self.assertEqual(second,(ROOT/'public/advertise.html').read_bytes())
        self.assertIn(b'Published F1\xe2\x80\x93F3 image advertising rates in USD',second)
        inventory=json.loads((ROOT/'data/sponsorship-inventory.json').read_text(encoding='utf-8'))
        self.assertIs(inventory['enabled'],True)
        self.assertIs(inventory['applications_open'],True)
        self.assertIn('enabled: true',(ROOT/'public/sponsored-inventory.js').read_text(encoding='utf-8'))
        self.assertIn('CHECKOUT_ENABLED = "false"',(ROOT/'worker/wrangler.toml').read_text(encoding='utf-8'))
    def test_house_invitation_and_existing_primary_destination_are_separate(self):
        producer=(ROOT/'scripts/prepare_coshuma_promotions.py').read_text(encoding='utf-8')
        self.assertIn('data-advertiser-interest',producer)
        self.assertIn('data-promotion-link',producer)
        runtime=(ROOT/'public/coshuma-promotions.js').read_text(encoding='utf-8')
        self.assertIn('advertiser_interest_click',runtime)
        self.assertIn("emit('coshuma_promo_click')",runtime)

if __name__=='__main__':unittest.main()
