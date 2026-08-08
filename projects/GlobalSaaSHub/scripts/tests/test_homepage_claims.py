import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
APP = ROOT / "src" / "App.jsx"
DIST = ROOT / "dist"

FORBIDDEN_CLAIMS = (
    "Verified Tools",
    "4.8 / 5.0",
    "Avg Rating",
)


class HomepageClaimsTest(unittest.TestCase):
    def test_homepage_source_uses_accurate_claims(self):
        source = APP.read_text(encoding="utf-8")
        for claim in FORBIDDEN_CLAIMS:
            self.assertNotIn(claim, source)
        self.assertIn("Curated SaaS Profiles", source)
        self.assertIn("Source-led", source)
        self.assertIn("Pricing Details", source)

    def test_built_homepage_has_no_forbidden_claims_when_dist_exists(self):
        if not DIST.exists():
            self.skipTest("dist is created by the production build")

        built_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in DIST.rglob("*")
            if path.is_file() and path.suffix.lower() in {".html", ".js", ".json"}
        )
        for claim in FORBIDDEN_CLAIMS:
            self.assertNotIn(claim, built_text)


if __name__ == "__main__":
    unittest.main()
