"""Verify that the real public-copy producers preserve the reopened sales flow."""
import json
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "scripts"))
import normalize_sponsorship_offer as source_guard
import guard_built_customer_copy as built_guard


class SponsorshipReopeningTests(unittest.TestCase):
    def test_source_and_built_finalizers_preserve_the_application_and_policy(self):
        with tempfile.TemporaryDirectory(prefix="coshuma-ad-reopen-") as temporary:
            root = Path(temporary)
            public = root / "public"
            public.mkdir()
            (root / "src").mkdir()
            (root / "data").mkdir()
            for name in ("advertise.html", "sponsorship.html", "terms.html", "privacy.html"):
                shutil.copy(PROJECT / "public" / name, public / name)
            shutil.copy(PROJECT / "data/sponsorship-inventory.json", root / "data/sponsorship-inventory.json")
            app = root / "src/App.jsx"
            app.write_text('export default function App(){ return <main>Existing buyer experience</main>; }\n')
            (public / "sitemap.xml").write_text('<?xml version="1.0"?><urlset><url><loc>https://coshuma.com/</loc></url></urlset>')
            with ExitStack() as stack:
                for name, value in (("ROOT", root), ("PUBLIC", public), ("APP", app)):
                    stack.enter_context(patch.object(source_guard, name, value))
                stack.enter_context(patch.object(source_guard.runpy, "run_path"))
                stack.enter_context(patch.object(source_guard, "run_fastlane_state_finalizers"))
                stack.enter_context(patch.object(source_guard, "prepare_sponsored_inventory"))
                source_guard.main()
                first = (public / "advertise.html").read_bytes()
                source_guard.main()
                self.assertEqual(first, (public / "advertise.html").read_bytes())
                self.assertEqual(app.read_text(), 'export default function App(){ return <main>Existing buyer experience</main>; }\n')
                self.assertEqual((public / "sitemap.xml").read_text().count("https://coshuma.com/advertise.html"), 1)

                # Run the actual post-build entry point on the prepared customer pages.
                stack.enter_context(patch.object(built_guard, "DIST", public))
                built_guard.main()
            html = (public / "advertise.html").read_text()
            for retained in ('id="sponsorship-application"', 'src="/sponsorship-sales.js"',
                             'id="application-receipt"', 'id="paypal-buttons"',
                             'href="/sponsorship.html"', 'data-cta="sponsorship-inquiry"',
                             'href="/downloads/coshuma-advertiser-guide-en.pdf"',
                             'href="/downloads/coshuma-advertiser-application-template-en.md"'):
                self.assertIn(retained, html)
            self.assertNotIn("Advertising inquiries are closed", html)
            self.assertNotIn("noindex", html)
            self.assertRegex(html, r'<button[^>]*id="submit-application"[^>]*disabled')
            self.assertRegex(html, r'<div[^>]*id="payment-area"[^>]*hidden')
            self.assertNotIn('src="https://www.paypal.com/sdk/js', html)
            policy = (public / "sponsorship.html").read_text()
            self.assertIn('id="refunds"', policy)
            self.assertIn("request cancellation and a full refund", policy)
            self.assertIn('href="/advertise.html"', policy)

    def test_catalog_regeneration_changes_both_display_and_form_rates_from_one_source(self):
        with tempfile.TemporaryDirectory(prefix="coshuma-ad-catalog-") as temporary:
            root = Path(temporary)
            (root / "public").mkdir()
            (root / "data").mkdir()
            shutil.copy(PROJECT / "public/advertise.html", root / "public/advertise.html")
            catalog = json.loads((PROJECT / "data/sponsorship-inventory.json").read_text())
            catalog["placements"]["tool-primary"]["pricing"]["7_days"] = 21
            (root / "data/sponsorship-inventory.json").write_text(json.dumps(catalog))
            with patch.object(source_guard, "ROOT", root), patch.object(source_guard, "PUBLIC", root / "public"):
                source_guard.sync_advertise_catalog()
            html = (root / "public/advertise.html").read_text()
            payload = json.loads(re.search(r'<script id="sponsorship-public-catalog" type="application/json">(.*?)</script>', html, re.S)[1])
            item = next(entry for entry in payload["catalog"] if entry["slot"] == "tool-primary")
            self.assertEqual(item["prices"]["7"], "21.00")
            self.assertIn("<td>$21</td>", html)
            self.assertNotIn("<td>$19</td>", html)

    def test_old_inline_sales_blocks_are_not_reintroduced_outside_the_dedicated_pages(self):
        legacy = '<main><section data-sponsorship-inquiry="tool"><h2>Request a COSHUMA sponsored placement</h2><a href="mailto:support@coshuma.com?subject=sponsorship">Email</a></section><p>Independent buyer guide.</p><script src="/sponsorship-sales.js"></script></main>'
        cleaned = source_guard.strip_page(legacy)
        self.assertNotIn("data-sponsorship-inquiry", cleaned)
        self.assertNotIn("sponsorship-sales.js", cleaned)
        self.assertIn("Independent buyer guide.", cleaned)


if __name__ == "__main__":
    unittest.main()
