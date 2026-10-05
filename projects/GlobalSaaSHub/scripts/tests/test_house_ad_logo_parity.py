"""Source and final-output logo coverage for the eight owned ad positions."""
from pathlib import Path
import json
import hashlib
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import prepare_coshuma_promotions as primary
import prepare_placement_expansion as expanded
from house_ad_identity import identity_html, LOGO_PATH


def check_identity(fragment):
    assert fragment.count('data-advertiser-logo') == 1, 'Exactly one official identity per creative'
    assert 'src="' + LOGO_PATH + '"' in fragment, 'Wrong logo source'
    assert 'alt="COSHUMA"' in fragment, 'Missing accessible brand name'


def verify_output(folder):
    fixed = primary.load_manifest()['promotions']
    extra = expanded.load_config()
    count = 0
    for row in fixed:
        text = (folder / row['page'].lstrip('/')).read_text(encoding='utf-8')
        matches = re.findall(r'<aside\b[^>]*data-coshuma-promotion="' + re.escape(row['id']) + r'"[^>]*>(.*?)</aside>', text, re.S)
        assert len(matches) == 1, row['page']
        check_identity(matches[0]); count += 1
    for row in extra['slots']:
        text = (folder / row['file']).read_text(encoding='utf-8')
        matches = re.findall(r'<aside\b[^>]*data-house-slot="' + re.escape(row['id']) + r'"[^>]*>(.*?)</aside>', text, re.S)
        assert len(matches) == 1, row['id']
        slides = re.findall(r'<article\b[^>]*data-house-slide="[^"]+"[^>]*>(.*?)</article>', matches[0], re.S)
        assert len(slides) == len(row['creative_ids']), row['id']
        for slide in slides:
            check_identity(slide)
            assert slide.count('data-house-image') == 1, 'Logo and main image must stay distinct'
            count += 1
    assert (folder / LOGO_PATH.lstrip('/')).is_file(), 'Logo missing from output'
    print(f'House logo parity: 8 positions / {count} individual creatives verified')


class HouseLogoTests(unittest.TestCase):
    def test_all_six_raster_assets_are_the_reviewed_branded_versions(self):
        assets = json.loads((ROOT / 'data/house-ad-logo-assets.json').read_text(encoding='utf-8'))
        self.assertEqual(len(assets), 6)
        for item in assets:
            image = ROOT / 'public/promotions' / item['file']
            self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), item['sha256'])
            self.assertEqual(primary.image_size(image), (item['width'], item['height']))

    def test_primary_cards_have_official_identity(self):
        for row in primary.load_manifest()['promotions']:
            check_identity(primary.card(row))

    def test_every_rotating_and_hub_creative_has_own_identity(self):
        config = expanded.load_config()
        creatives = {c['id']: c for c in config['creatives']}
        for row in config['slots']:
            html = expanded.render_slot(row, creatives)
            slides = re.findall(r'<article\b[^>]*>(.*?)</article>', html, re.S)
            self.assertEqual(len(slides), len(row['creative_ids']))
            for slide in slides:
                check_identity(slide)
                self.assertEqual(slide.count('data-house-image'), 1)

    def test_runtime_does_not_measure_logo_as_main_creative(self):
        js = (ROOT / 'public/house-placements.js').read_text(encoding='utf-8')
        self.assertNotIn("querySelector('img')", js)
        self.assertEqual(js.count("querySelector('[data-house-image]')"), 4)
        self.assertIn('8000', js)
        self.assertIn("'house_placement_impression'", js)
        self.assertIn("'house_placement_click'", js)

    def test_identity_has_background_specific_logo_and_size(self):
        for filename in ('coshuma-promotions.css', 'house-placements.css'):
            css = (ROOT / 'public' / filename).read_text(encoding='utf-8')
            self.assertIn('img[data-advertiser-logo]', css)
            self.assertIn('object-fit:contain', css)
            self.assertIn('width:260px', css)
        self.assertIn('coshuma-lockup-light.svg', identity_html())


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--verify':
        verify_output(Path(sys.argv[2]))
    else:
        unittest.main()
