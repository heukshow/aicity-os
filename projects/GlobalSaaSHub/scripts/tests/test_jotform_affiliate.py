import unittest
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
MISDIRECTING_URL = "https://link.jotform.com/yS9uTiLnz1?username=AnSangkwon"
CUSTOMER_URL = "https://www.jotform.com/ai/agents/?partner=coshuma"
LEGACY_ONBOARDING_URL = "https://link.jotform.com/17STYVOunG?username=AnSangkwon"


class CTAParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.anchors.append(dict(attrs))


class JotformAffiliateTests(unittest.TestCase):
    def test_directory_override_does_not_use_dashboard_redirect(self):
        url_js = (PROJECT / "src" / "utils" / "url.js").read_text(encoding="utf-8")
        self.assertNotIn(MISDIRECTING_URL, url_js)
        self.assertNotIn('jotform: "https://link.jotform.com/yS9uTiLnz1?username=AnSangkwon"', url_js)

    def test_static_page_uses_confirmed_customer_affiliate_cta(self):
        # The deploy workflow normalizes the checked-in onboarding URL first.
        # Exercise that existing step on a temporary copy, without changing source.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page_path = root / "public" / "tool" / "jotform.html"
            page_path.parent.mkdir(parents=True)
            script_path = root / "scripts" / "inject_jotform_partner_offer.py"
            script_path.parent.mkdir()
            shutil.copyfile(PROJECT / "public" / "tool" / "jotform.html", page_path)
            shutil.copyfile(PROJECT / "scripts" / script_path.name, script_path)
            subprocess.run([sys.executable, str(script_path)], check=True, capture_output=True)
            page = page_path.read_text(encoding="utf-8")
        self.assertNotIn(MISDIRECTING_URL, page)
        self.assertNotIn(LEGACY_ONBOARDING_URL, page)
        parser = CTAParser()
        parser.feed(page)
        affiliate_ctas = [a for a in parser.anchors if a.get("data-cta") == "affiliate"]
        self.assertTrue(affiliate_ctas)
        for anchor in affiliate_ctas:
            self.assertEqual(anchor.get("href"), CUSTOMER_URL)
            self.assertIn("sponsored", anchor.get("rel", "").split())
        self.assertTrue(any(a.get("data-cta") == "official" and a.get("href") == "https://www.jotform.com/pricing/" for a in parser.anchors))
        self.assertIn("Affiliate disclosure:", page)


if __name__ == "__main__":
    unittest.main()
