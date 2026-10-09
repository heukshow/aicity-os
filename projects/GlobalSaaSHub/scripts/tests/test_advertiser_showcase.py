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
    def test_active_page_opens_only_review_gated_image_booking(self):
        self.assertIn('data-advertising-mode="booking"',self.html)
        self.assertIn('data-advertising-status="f1-f3-open"',self.html)
        ids=[attrs.get('id') for _,attrs in self.parser.tags if attrs.get('id')]
        self.assertEqual(len(ids),len(set(ids)))
        for name in ['about-coshuma','materials','materials-title']:
            self.assertIn(name,ids)
        # Customer fields and PayPal controls remain inside the inert template until
        # the dedicated sales runtime activates them on the booking page.
        for name in ['sponsorship-application','paypal-buttons','payment-area','advertiser-brief']:
            self.assertNotIn(name,ids)
        sales=(ROOT/'public/sponsorship-sales.js').read_text(encoding='utf-8')
        self.assertIn("if (!['booking','live'].includes(document.body?.dataset.advertisingMode || '')) return;",sales)
        self.assertIn("application?.status === 'awaiting_payment'",sales)
        self.assertIn("application?.paymentReady === true",sales)
        self.assertIn('F1–F3 fixed image bookings are open',self.active)
        self.assertIn('Payment is offered only after COSHUMA approves the materials and reserves the position',self.active)
    def test_preview_runtime_stays_nontransactional_and_sales_access_is_ephemeral(self):
        # The showcase/preview runtime itself must remain unable to send or persist
        # advertiser data; transactional behavior lives only in sponsorship-sales.js.
        for token in ['fetch(', 'XMLHttpRequest', 'sendBeacon', 'localStorage', 'sessionStorage', 'innerHTML']:
            self.assertNotIn(token,self.js)
        self.assertNotIn('clipboard.writeText',self.js)
        self.assertIn("params.get('coshuma_qa') === '1'",self.js)
        sales=(ROOT/'public/sponsorship-sales.js').read_text(encoding='utf-8')
        self.assertIn("const SESSION_KEY = 'coshuma-ad-application'",sales)
        self.assertIn('sessionStorage.setItem(SESSION_KEY',sales)
        self.assertNotIn('localStorage',sales)
        self.assertIn("credentials: 'omit'",sales)
        self.assertIn("authorization: 'Bearer ' + access.accessToken",sales)
        self.assertIn('No COSHUMA account is required',self.html)
        self.assertIn('No payment is collected with the application',self.active)
        for tag,attrs in self.parser.tags:
            if tag=='a' and attrs.get('href','').startswith('mailto:'):
                self.assertEqual(attrs['href'],'mailto:support@coshuma.com?subject=COSHUMA%20technical%20support')
    def test_real_examples_are_local_and_labeled_as_house_ads(self):
        images=[a['src'] for t,a in self.parser.tags if t=='img' and a.get('src','').startswith('/promotions/showcase-')]
        self.assertEqual(len(images),6)
        for src in images:
            self.assertTrue(src.startswith('/promotions/showcase-'))
            self.assertTrue((ROOT/'public'/src.split('?',1)[0].lstrip('/')).is_file())
        self.assertIn('not a paid client campaign',self.active)
        self.assertIn('simulated viewport',self.active)
        self.assertNotIn('Copyedited_20261005.pdf',self.html)
    def test_price_regeneration_is_idempotent_and_preserves_pause(self):
        first=(ROOT/'public/advertise.html').read_bytes()
        normalizer.sync_advertise_catalog()
        second=(ROOT/'public/advertise.html').read_bytes()
        normalizer.sync_advertise_catalog()
        self.assertEqual(second,(ROOT/'public/advertise.html').read_bytes())
        self.assertIn(b'USD per placement. The agreed period starts when your card goes live, not when you submit or pay.',second)
        inventory=json.loads((ROOT/'data/sponsorship-inventory.json').read_text(encoding='utf-8'))
        # Legacy paid-inventory switches stay paused; F1-F3 image intake is a
        # separate server-gated flow and checkout remains independently disabled.
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
