import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def test_admin_and_checkout_code_are_not_in_public_source():
    app = (SRC / "App.jsx").read_text(encoding="utf-8")
    public_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in SRC.rglob("*")
        if path.is_file()
    )

    assert not (SRC / "components" / "AdminDashboard.jsx").exists()
    assert not (SRC / "components" / "PaymentModal.jsx").exists()
    assert "AdminDashboard" not in public_source
    assert "PaymentModal" not in public_source
    assert "master-console" not in public_source
    assert "sponsorship_order" not in public_source
    assert "trackSponsorshipOrder" not in public_source
    assert "paypal.com/cgi-bin/webscr" not in public_source
    assert "cardCvc" not in public_source
    assert "contactEmail" not in public_source
    assert "paymentConfig.checkoutEnabled &&" in app
    assert "<SponsorshipCheckout />" in app
    assert "if (!paymentConfig.checkoutEnabled) return null" in (
        SRC / "components" / "SponsorshipCheckout.jsx"
    ).read_text(encoding="utf-8")


def test_unused_payment_sdk_is_removed():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "cdn.portone.io" not in index


def test_affiliate_url_policy_is_fail_closed():
    script = """
      import { getValidExternalUrl } from './src/utils/url.js';
      const official = 'https://official.example/';
      const affiliate = 'https://affiliate.example/';
      const cases = [
        [{ official_url: official, affiliate_url: affiliate }, official],
        [{ official_url: official, affiliate_url: affiliate, affiliate_verified: null }, official],
        [{ official_url: official, affiliate_url: affiliate, affiliate_verified: false }, official],
        [{ official_url: official, affiliate_url: affiliate, affiliate_verified: true }, affiliate],
        [{ official_url: official, affiliate_url: 'javascript:alert(1)', affiliate_verified: true }, official],
      ];
      for (const [tool, expected] of cases) {
        const actual = getValidExternalUrl(tool);
        if (actual !== expected) throw new Error(`${actual} !== ${expected}`);
      }
    """
    subprocess.run(
        ["node", "--input-type=module", "--eval", script],
        cwd=ROOT,
        check=True,
    )
