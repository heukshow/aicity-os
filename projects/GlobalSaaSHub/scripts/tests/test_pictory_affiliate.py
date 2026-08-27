import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TRACKING_URL = "https://pictory.ai?fpr=sangkwon-an23"


class PictoryAffiliateTests(unittest.TestCase):
    def test_directory_cta_override_uses_verified_tracking_url(self):
        url_js = (PROJECT / "src" / "utils" / "url.js").read_text(encoding="utf-8")
        self.assertIn('pictory: "https://pictory.ai?fpr=sangkwon-an23"', url_js)
        self.assertIn("VERIFIED_AFFILIATE_OVERRIDES", url_js)

    def test_static_page_publishes_verified_tracking_cta(self):
        page = (PROJECT / "public" / "tool" / "pictory.html").read_text(encoding="utf-8")
        self.assertIn(TRACKING_URL, page)
        self.assertIn('data-cta="affiliate"', page)
        self.assertIn('rel="sponsored noopener noreferrer"', page)


if __name__ == "__main__":
    unittest.main()
