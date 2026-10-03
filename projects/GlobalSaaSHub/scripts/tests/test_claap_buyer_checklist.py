"""Exercise the real SEO replacement and content-enrichment order for Claap."""
import csv
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PAGES = ("tool/claap.html", "best/claap-sales-follow-up-ai.html")
CSV_PATH = "resources/claap-3-call-coaching-checklist.csv"


def buyer_links(html):
    return re.findall(r'<a\b(?=[^>]*data-cta="(?:affiliate|official)")[^>]*>', html)


class ClaapBuyerChecklistTests(unittest.TestCase):
    def assert_checklist(self, root):
        fields = ["call_label", "evidence_quote_or_timestamp", "objection", "next_step",
                  "owner_and_deadline", "crm_field_and_saved_value"]
        with (root / "public" / CSV_PATH).open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.assertEqual(reader.fieldnames, fields)
            rows = list(reader)
        self.assertEqual([row["call_label"] for row in rows], ["Call 1", "Call 2", "Call 3"])
        self.assertTrue(all(row[field] == "" for row in rows for field in fields[1:]))
        for relative in PAGES:
            html = (root / "public" / relative).read_text(encoding="utf-8")
            self.assertEqual(html.count('id="claap-3-call-checklist"'), 1)
            section = re.search(r'<section id="claap-3-call-checklist".*?</section>', html, re.S).group()
            self.assertEqual(len(re.findall(r'<th scope="row"', section)), 5)
            self.assertIn(f'href="/{CSV_PATH}" download=', section)
            self.assertNotIn('data-cta="affiliate"', section)
            self.assertNotIn("<form", section)
            self.assertNotRegex(html, r"(?i)14[- ]days?|no[- ]card|no[- ]credit[- ]card|full[- ]access|US-localized|\$(?:40|32|75|60)\b")
            self.assertNotIn("https://www.claap.io/pricing-v2", html)
            self.assertIn('href="https://www.claap.io/pricing"', html)
            self.assertIn("trial of Pro or Business", html)
            self.assertIn("pricing FAQ", html)
            self.assertIn("does not specify the trial duration or payment-card requirements", html)
        detail = (root / "public/tool/claap.html").read_text(encoding="utf-8")
        self.assertIn("The page viewed displayed prices in EUR", detail)
        for price in ("€0 per license/month", "€30 per license/month on monthly billing",
                      "€24 per license/month billed yearly", "€60 per license/month on monthly billing",
                      "€48 per license/month billed yearly"):
            self.assertIn(price, detail)

    def test_committed_csv_is_blank_and_linked_from_both_pages(self):
        self.assert_checklist(PROJECT)

    def test_both_seo_sources_preserve_review_checklist_and_late_enrichment(self):
        original_links = {relative: buyer_links((PROJECT / "public" / relative).read_text(encoding="utf-8"))
                          for relative in PAGES}
        with tempfile.TemporaryDirectory(prefix="coshuma-claap-checklist-") as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "public/best").mkdir(parents=True)
            for directory in ("data", "config", "scripts/public-copy-templates"):
                shutil.copytree(PROJECT / directory, root / directory)
            for filename in ("generate_seo_pages.py", "guard_public_copy.py", "apply_claap_partner_feedback.py",
                             "ensure_best_pages_in_sitemap.py",
                             "inject_tool_value_playbooks.py", "guard_tool_trust_disclosures.py",
                             "self_heal_source_affiliate_disclosures.py"):
                shutil.copy(PROJECT / "scripts" / filename, root / "scripts" / filename)
            shutil.copy(PROJECT / "index.html", root / "index.html")
            shutil.copy(PROJECT / "src/App.jsx", root / "src/App.jsx")
            shutil.copy(PROJECT / "public/methodology.html", root / "public/methodology.html")
            shutil.copytree(PROJECT / "public/best", root / "public/best", dirs_exist_ok=True)

            def run(script, *args):
                result = subprocess.run([sys.executable, str(root / "scripts" / script), *args],
                                        cwd=root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, f"{script}: {result.stdout}\n{result.stderr}")

            for dataset in ("tools.next.json", "tools.json"):
                run("generate_seo_pages.py", "--source", dataset)
                generated = (root / "public/tool/claap.html").read_text(encoding="utf-8")
                self.assertNotIn('id="claap-3-call-checklist"', generated)
                run("guard_public_copy.py", "--restore-descript-guides")
                run("apply_claap_partner_feedback.py")
                run("ensure_best_pages_in_sitemap.py")
                run("inject_tool_value_playbooks.py")
                run("apply_claap_partner_feedback.py")
                run("guard_tool_trust_disclosures.py")
                run("guard_public_copy.py")
                run("self_heal_source_affiliate_disclosures.py")
                self.assert_checklist(root)
                for relative in PAGES:
                    html = (root / "public" / relative).read_text(encoding="utf-8")
                    self.assertEqual(buyer_links(html), original_links[relative])
                    self.assertEqual(html.count("Affiliate disclosure:"), 1)
                detail = (root / "public/tool/claap.html").read_text(encoding="utf-8")
                self.assertIn("COSHUMA_TRUST_BLOCK", detail)
                self.assertIn("COSHUMA_VALUE_PLAYBOOK_START", detail)
                self.assertIn("Current pricing guidance: what buyers should compare", detail)
                before = [(root / "public" / page).read_bytes() for page in PAGES]
                (root / "public" / CSV_PATH).unlink()
                run("apply_claap_partner_feedback.py")
                self.assertEqual(before, [(root / "public" / page).read_bytes() for page in PAGES])
                self.assert_checklist(root)


if __name__ == "__main__":
    unittest.main()
