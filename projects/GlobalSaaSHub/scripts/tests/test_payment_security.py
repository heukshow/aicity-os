import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / "worker"


def test_worker_security_contract():
    domain = (WORKER / "src" / "domain.js").read_text(encoding="utf-8")
    worker = (WORKER / "src" / "index.js").read_text(encoding="utf-8")
    paypal = (WORKER / "src" / "paypal.js").read_text(encoding="utf-8")
    wrangler = (WORKER / "wrangler.toml").read_text(encoding="utf-8")
    migration = (WORKER / "migrations" / "0001_orders.sql").read_text(encoding="utf-8")
    sponsorship = (WORKER / "src" / "sponsorship.js").read_text(encoding="utf-8")

    assert "SPONSORSHIP_AMOUNT = '49.00'" in domain
    assert "SPONSORSHIP_CURRENCY = 'USD'" in domain
    assert "verification_status !== 'SUCCESS'" in worker + sponsorship
    assert "PayPal-Request-Id" in paypal
    assert "PRIMARY KEY" in migration
    assert "UNIQUE" in migration

    # Security posture: checkout must fail closed server-side and admin access must
    # depend on the secret ADMIN_PATH rather than a fixed public login route.
    assert "env.CHECKOUT_ENABLED === 'true'" in sponsorship
    assert 'CHECKOUT_ENABLED = "false"' in wrangler
    assert "PUBLIC_ADMIN_PATH" not in worker
    assert "'/ops-login'" not in worker
    assert "isAllowedBrowserRequest(request, env)" in worker
    assert "await handleSponsorshipRequest(request, env)" in worker
    assert "x-content-type-options" in worker
    assert "content-security-policy" in worker
    # Health/readiness may now report configuration safely; it must never expose
    # credentials. Behavioral payment gates are exercised by the Node tests below.
    assert "verifyPayPalPayment" in sponsorship
    assert "/v1/sponsorship/" in sponsorship


def test_frontend_has_no_secret_and_requires_public_configuration():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "src").rglob("*") if path.is_file()
    )
    app = (ROOT / "src" / "App.jsx").read_text(encoding="utf-8")
    config = (ROOT / "src" / "config" / "payment.js").read_text(encoding="utf-8")
    assert "PAYPAL_CLIENT_SECRET" not in source
    assert "PAYPAL_WEBHOOK_ID" not in source
    assert "VITE_SPONSORSHIP_CHECKOUT_ENABLED === 'true'" in config
    sdk = (ROOT / "src" / "services" / "paypalSdk.js").read_text(encoding="utf-8")
    payment_api = (ROOT / "src" / "services" / "paymentApi.js").read_text(encoding="utf-8")
    assert "paymentConfig.checkoutEnabled &&" in app
    # The paused legacy React component intentionally renders null. Do not require
    # obsolete calls inside that component or forbid public price display.
    assert "if (!paymentConfig.checkoutEnabled)" in payment_api
    assert "client-id" in sdk
    assert "PAYPAL_CLIENT_SECRET" not in sdk
    for relative in ("public/sponsorship-sales.js", "public/sponsored-inventory.js"):
        public_source = (ROOT / relative).read_text(encoding="utf-8")
        assert "PAYPAL_CLIENT_SECRET" not in public_source
        assert "PAYPAL_WEBHOOK_ID" not in public_source


def test_node_payment_regressions():
    subprocess.run(
        [
            "node", "--test", "test/domain.test.js", "test/repository.test.js",
            "test/sponsorship-domain.test.js", "test/sponsorship-migration.test.js",
            "test/sponsorship-routes.test.js",
        ],
        cwd=WORKER,
        check=True,
    )


if __name__ == "__main__":
    # Also support the offline workspace without requiring a pytest installation.
    test_worker_security_contract()
    test_frontend_has_no_secret_and_requires_public_configuration()
    test_node_payment_regressions()
    print("Payment security checks passed")
