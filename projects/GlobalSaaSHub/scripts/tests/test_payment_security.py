import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / "worker"


def test_worker_security_contract():
    domain = (WORKER / "src" / "domain.js").read_text(encoding="utf-8")
    worker = (WORKER / "src" / "index.js").read_text(encoding="utf-8")
    paypal = (WORKER / "src" / "paypal.js").read_text(encoding="utf-8")
    migration = (WORKER / "migrations" / "0001_orders.sql").read_text(encoding="utf-8")

    assert "SPONSORSHIP_AMOUNT = '49.00'" in domain
    assert "SPONSORSHIP_CURRENCY = 'USD'" in domain
    assert "verification_status !== 'SUCCESS'" in worker
    assert "validatePaidWebhook(event)" in worker
    assert "captureIsVerifiedPaid(verified)" in worker
    assert "PayPal-Request-Id" in paypal
    assert "PRIMARY KEY" in migration
    assert "UNIQUE" in migration
    assert "client-provided amount" not in worker.lower()


def test_frontend_has_no_secret_and_is_disabled_by_default():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "src").rglob("*") if path.is_file()
    )
    app = (ROOT / "src" / "App.jsx").read_text(encoding="utf-8")
    config = (ROOT / "src" / "config" / "payment.js").read_text(encoding="utf-8")
    assert "PAYPAL_CLIENT_SECRET" not in source
    assert "PAYPAL_WEBHOOK_ID" not in source
    assert "VITE_SPONSORSHIP_CHECKOUT_ENABLED === 'true'" in config
    checkout = (ROOT / "src" / "components" / "SponsorshipCheckout.jsx").read_text(encoding="utf-8")
    sdk = (ROOT / "src" / "services" / "paypalSdk.js").read_text(encoding="utf-8")
    assert "paymentConfig.checkoutEnabled &&" in app
    assert "if (!paymentConfig.checkoutEnabled) return null" in checkout
    assert "createSponsorshipOrder()" in checkout
    assert "captureVerifiedSponsorshipOrder(orderID)" in checkout
    assert "amount" not in checkout.lower()
    assert "client-id" in sdk
    assert "PAYPAL_CLIENT_SECRET" not in sdk


def test_node_payment_regressions():
    subprocess.run(
        ["node", "--test", "test/domain.test.js", "test/repository.test.js"],
        cwd=WORKER,
        check=True,
    )
