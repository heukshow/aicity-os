import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TRACKING_URL = "https://vidiq.com/coshuma"


class VidiqAffiliateTests(unittest.TestCase):
    def test_static_detail_page_uses_verified_tracking_url(self):
        html = (PROJECT / "public" / "tool" / "vidiq.html").read_text(encoding="utf-8")
        self.assertIn(f'href="{TRACKING_URL}"', html)
        self.assertIn('data-cta="affiliate"', html)
        self.assertIn('rel="sponsored noopener noreferrer"', html)
        self.assertIn("Visit vidIQ via Verified Affiliate Link", html)

    def test_directory_cta_override_uses_verified_tracking_url(self):
        url_js = (PROJECT / "src" / "utils" / "url.js").read_text(encoding="utf-8")
        self.assertIn('vidiq: "https://vidiq.com/coshuma"', url_js)
        self.assertIn("VERIFIED_AFFILIATE_OVERRIDES", url_js)


if __name__ == "__main__":
    unittest.main()
