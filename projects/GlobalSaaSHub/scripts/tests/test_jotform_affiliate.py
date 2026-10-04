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
HOMEPAGE_AFFILIATE_URL = "https://www.jotform.com/?partner=coshuma"
PRICING_AFFILIATE_URL = "https://www.jotform.com/pricing/?partner=coshuma"
ALLOWED_AFFILIATE_URLS = {CUSTOMER_URL, HOMEPAGE_AFFILIATE_URL, PRICING_AFFILIATE_URL}
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
            compare_path = root / "public" / "compare" / "unbounce-vs-jotform.html"
            compare_path.parent.mkdir(parents=True)
            shutil.copyfile(PROJECT / "public" / "compare" / "unbounce-vs-jotform.html", compare_path)
            pricing_path = root / "public" / "best" / "jotform-pricing-free-plan.html"
            pricing_path.parent.mkdir(parents=True)
            shutil.copyfile(PROJECT / "public" / "best" / "jotform-pricing-free-plan.html", pricing_path)
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
            self.assertIn(anchor.get("href"), ALLOWED_AFFILIATE_URLS)
            self.assertIn("sponsored", anchor.get("rel", "").split())
        self.assertIn("Affiliate disclosure:", page)
        self.assertEqual(page.count('data-campaign-asset="coshuma-one-month-growth-c04"'), 1)
        self.assertIn('data-cta-source="jotform-c04-plan-checklist"', page)
        self.assertIn(f'href="{PRICING_AFFILIATE_URL}"', page)
        self.assertIn(
            'href="https://www.jotform.com/help/408-understanding-your-account-usage-and-limits/"',
            page,
        )
        section = page.split('data-campaign-asset="coshuma-one-month-growth-c04"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn("<form", section)
        self.assertNotIn("<input", section)
        self.assertIn("COSHUMA does not collect or store your answers.", section)


if __name__ == "__main__":
    unittest.main()
