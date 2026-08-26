import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TRACKING_URL = "https://get.descript.com/ole5fu20j5sq"


class DescriptAffiliateTests(unittest.TestCase):
    def test_directory_cta_override_uses_verified_tracking_url(self):
        url_js = (PROJECT / "src" / "utils" / "url.js").read_text(encoding="utf-8")
        self.assertIn('descript: "https://get.descript.com/ole5fu20j5sq"', url_js)
        self.assertIn("VERIFIED_AFFILIATE_OVERRIDES", url_js)


if __name__ == "__main__":
    unittest.main()
