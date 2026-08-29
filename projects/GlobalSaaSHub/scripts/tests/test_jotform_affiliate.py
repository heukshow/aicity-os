import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
MISDIRECTING_URL = "https://link.jotform.com/yS9uTiLnz1?username=AnSangkwon"


class JotformAffiliateTests(unittest.TestCase):
    def test_directory_override_does_not_use_dashboard_redirect(self):
        url_js = (PROJECT / "src" / "utils" / "url.js").read_text(encoding="utf-8")
        self.assertNotIn(MISDIRECTING_URL, url_js)
        self.assertNotIn('jotform: "https://link.jotform.com/yS9uTiLnz1?username=AnSangkwon"', url_js)

    def test_static_page_does_not_publish_dashboard_redirect_as_affiliate_cta(self):
        page = (PROJECT / "public" / "tool" / "jotform.html").read_text(encoding="utf-8")
        self.assertNotIn(MISDIRECTING_URL, page)
        self.assertNotIn('data-cta="affiliate"', page)
        self.assertIn('data-cta="official"', page)
        self.assertIn('href="https://www.jotform.com/"', page)


if __name__ == "__main__":
    unittest.main()
