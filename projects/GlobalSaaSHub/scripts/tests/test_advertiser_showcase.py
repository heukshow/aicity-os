"""Regressions for inquiry-only advertiser discovery, not paid-ad enablement."""
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
    def test_active_page_is_inquiry_only_and_payment_form_is_inert(self):
        self.assertIn('data-advertising-mode="inquiry"',self.html)
        ids=[attrs.get('id') for _,attrs in self.parser.tags if attrs.get('id')]
        self.assertEqual(len(ids),len(set(ids)))
        for name in ['advertiser-brief','brief-product','brief-url','prepare-brief','brief-draft','brief-result']:
            self.assertIn(name,ids)
        for name in ['sponsorship-application','paypal-buttons','payment-area']:
            self.assertNotIn(name,ids)
        old=(ROOT/'public/sponsorship-sales.js').read_text(encoding='utf-8')
        self.assertIn("if (document.body?.dataset.advertisingMode === 'inquiry') return;",old)
        self.assertIn('not open for booking',self.active)
    def test_inquiry_has_no_server_send_or_storage(self):
        for token in ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML']:
            self.assertNotIn(token,self.js)
        self.assertIn('Nothing is sent until you send the email yourself',self.active)
        self.assertIn('nothing has been submitted',self.js)
        self.assertIn("params.get('coshuma_qa') === '1'",self.js)
        for tag,attrs in self.parser.tags:
            if tag=='a' and attrs.get('href','').startswith('mailto:'):
                self.assertEqual(attrs['href'],'mailto:support@coshuma.com?subject=COSHUMA%20advertising%20inquiry')
    def test_real_examples_are_local_and_labeled_as_house_ads(self):
        images=[a['src'] for t,a in self.parser.tags if t=='img']
        self.assertEqual(len(images),7)
        for src in images:
            self.assertTrue(src.startswith('/promotions/showcase-'))
            self.assertTrue((ROOT/'public'/src.lstrip('/')).is_file())
        self.assertIn('not a paid client campaign',self.active)
        self.assertIn('simulated viewport',self.active)
        self.assertNotIn('Copyedited_20261005.pdf',self.html)
    def test_price_regeneration_is_idempotent_and_preserves_pause(self):
        first=(ROOT/'public/advertise.html').read_bytes()
        normalizer.sync_advertise_catalog()
        second=(ROOT/'public/advertise.html').read_bytes()
        normalizer.sync_advertise_catalog()
        self.assertEqual(second,(ROOT/'public/advertise.html').read_bytes())
        self.assertIn(b'Planning reference in USD',second)
        inventory=json.loads((ROOT/'data/sponsorship-inventory.json').read_text(encoding='utf-8'))
        self.assertIs(inventory['enabled'],False)
        self.assertIs(inventory['applications_open'],False)
        self.assertIn('enabled: false',(ROOT/'public/sponsored-inventory.js').read_text(encoding='utf-8'))
        self.assertIn('CHECKOUT_ENABLED = "false"',(ROOT/'worker/wrangler.toml').read_text(encoding='utf-8'))
    def test_house_invitation_and_existing_primary_destination_are_separate(self):
        producer=(ROOT/'scripts/prepare_coshuma_promotions.py').read_text(encoding='utf-8')
        self.assertIn('data-advertiser-interest',producer)
        self.assertIn('data-promotion-link',producer)
        runtime=(ROOT/'public/coshuma-promotions.js').read_text(encoding='utf-8')
        self.assertIn('advertiser_interest_click',runtime)
        self.assertIn("emit('coshuma_promo_click')",runtime)

if __name__=='__main__':unittest.main()
