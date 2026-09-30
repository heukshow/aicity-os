#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "prepare_indexnow_urls.py"
BOOTSTRAP_MARKER = "indexnow-bootstrap-v1.txt"

SITEMAP = """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://coshuma.com/</loc></url>
  <url><loc>https://coshuma.com/tool/example.html</loc></url>
</urlset>
"""

HOME = """<!doctype html><html><head><link rel="canonical" href="https://coshuma.com/" /></head><body>home</body></html>"""
TOOL = """<!doctype html><html><head><link rel="canonical" href="https://coshuma.com/tool/example.html" /></head><body>tool</body></html>"""

class IndexNowPreparationTests(unittest.TestCase):
    def run_prepare(self, current: Path, previous: Path, output: Path):
        subprocess.run([
            "python", str(SCRIPT),
            "--current", str(current),
            "--previous", str(previous),
            "--output", str(output),
            "--bootstrap-marker", BOOTSTRAP_MARKER,
        ], check=True)
        return json.loads(output.read_text(encoding="utf-8"))

    def test_first_install_bootstraps_sitemap_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current"
            previous = root / "previous"
            current.mkdir(); previous.mkdir()
            (current / "tool").mkdir()
            (current / "sitemap.xml").write_text(SITEMAP, encoding="utf-8")
            (current / "index.html").write_text(HOME, encoding="utf-8")
            (current / "tool" / "example.html").write_text(TOOL, encoding="utf-8")
            out = root / "urls.json"
            doc = self.run_prepare(current, previous, out)
            self.assertTrue(doc["bootstrap"])
            self.assertEqual(doc["urlList"], [
                "https://coshuma.com/",
                "https://coshuma.com/tool/example.html",
            ])

    def test_existing_install_submits_only_changed_and_deleted_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = root / "current"
            previous = root / "previous"
            current.mkdir(); previous.mkdir()
            (current / "tool").mkdir(); (previous / "tool").mkdir()
            (current / "sitemap.xml").write_text(SITEMAP, encoding="utf-8")
            (previous / BOOTSTRAP_MARKER).write_text("done\n", encoding="utf-8")
            (previous / "index.html").write_text(HOME, encoding="utf-8")
            (current / "index.html").write_text(HOME, encoding="utf-8")
            (previous / "tool" / "example.html").write_text(TOOL, encoding="utf-8")
            (current / "tool" / "example.html").write_text(TOOL.replace("tool</body>", "tool updated</body>"), encoding="utf-8")
            old = previous / "tool" / "removed.html"
            old.write_text('<link rel="canonical" href="https://coshuma.com/tool/removed.html">', encoding="utf-8")
            out = root / "urls.json"
            doc = self.run_prepare(current, previous, out)
            self.assertFalse(doc["bootstrap"])
            self.assertEqual(doc["urlList"], [
                "https://coshuma.com/tool/example.html",
                "https://coshuma.com/tool/removed.html",
            ])

if __name__ == "__main__":
    unittest.main()
