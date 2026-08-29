import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TRACKING_URL = "https://link.jotform.com/yS9uTiLnz1?username=AnSangkwon"


class JotformAffiliateTests(unittest.TestCase):
    def test_directory_cta_override_uses_verified_tracking_url(self):
        url_js = (PROJECT / "src" / "utils" / "url.js").read_text(encoding="utf-8")
        self.assertIn(
            'jotform: "https://link.jotform.com/yS9uTiLnz1?username=AnSangkwon"',
            url_js,
        )
        self.assertIn("VERIFIED_AFFILIATE_OVERRIDES", url_js)

    def test_static_page_publishes_verified_tracking_cta(self):
        page = (PROJECT / "public" / "tool" / "jotform.html").read_text(encoding="utf-8")
        self.assertIn(TRACKING_URL, page)
        self.assertIn('data-cta="affiliate"', page)
        self.assertIn('rel="sponsored noopener noreferrer"', page)


if __name__ == "__main__":
    unittest.main()
