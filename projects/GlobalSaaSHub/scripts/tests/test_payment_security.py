import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKER = ROOT / "worker"


def test_worker_security_contract():
    domain = (WORKER / "src" / "domain.js").read_text(encoding="utf-8")
    worker = (WORKER / "src" / "index.js").read_text(encoding="utf-8")
    paypal = (WORKER / "src" / "paypal.js").read_text(encoding="utf-8")
    wrangler = (WORKER / "wrangler.toml").read_text(encoding="utf-8")
    legacy_migration = (WORKER / "migrations" / "0001_orders.sql").read_text(encoding="utf-8")
    v2_migration = (WORKER / "migrations" / "0004_sponsorship_order_metadata.sql").read_text(encoding="utf-8")

    assert "SPONSORSHIP_PRODUCTS = Object.freeze" in domain
    for product_id, price in (
        ("tool_page_7", "19.00"),
        ("tool_page_30", "49.00"),
        ("tool_page_90", "129.00"),
        ("buyer_intent_7", "39.00"),
        ("buyer_intent_30", "99.00"),
        ("buyer_intent_90", "269.00"),
        ("comparison_7", "59.00"),
        ("comparison_30", "149.00"),
        ("comparison_90", "399.00"),
    ):
        assert product_id in domain
        assert f"amount: '{price}'" in domain
    assert "SPONSORSHIP_CURRENCY = 'USD'" in domain
    assert "assertProductAmount" in domain
    assert "verification_status !== 'SUCCESS'" in worker
    assert "captureIsVerifiedPaid(verified, local.product_id)" in worker
    assert "PayPal-Request-Id" in paypal
    assert "CHECK (amount = '49.00')" in legacy_migration
    assert "CREATE TABLE IF NOT EXISTS sponsorship_orders" in v2_migration
    assert "ALTER TABLE orders" not in v2_migration
    assert "client-provided amount" not in worker.lower()

    # Security posture: checkout must fail closed server-side and admin access must
    # depend on the secret ADMIN_PATH rather than a fixed public login route.
    assert "env.CHECKOUT_ENABLED === 'true'" in worker
    assert 'CHECKOUT_ENABLED = "false"' in wrangler
    assert "PUBLIC_ADMIN_PATH" not in worker
    assert "'/ops-login'" not in worker
    assert "isAllowedBrowserRequest(request, env)" in worker
    assert "contentLength <= 4096" in worker
    assert "x-content-type-options" in worker
    assert "content-security-policy" in worker
    assert "checkoutConfigured(env)" in worker


def test_frontend_has_no_secret_and_stays_in_maintenance():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "src").rglob("*") if path.is_file()
    )
    app = (ROOT / "src" / "App.jsx").read_text(encoding="utf-8")
    config = (ROOT / "src" / "config" / "payment.js").read_text(encoding="utf-8")
    checkout = (ROOT / "src" / "components" / "SponsorshipCheckout.jsx").read_text(encoding="utf-8")
    payment_api = (ROOT / "src" / "services" / "paymentApi.js").read_text(encoding="utf-8")
    sdk = (ROOT / "src" / "services" / "paypalSdk.js").read_text(encoding="utf-8")

    assert "PAYPAL_CLIENT_SECRET" not in source
    assert "PAYPAL_WEBHOOK_ID" not in source
    assert "VITE_SPONSORSHIP_CHECKOUT_ENABLED === 'true'" in config
    assert "paymentConfig.checkoutEnabled &&" in app
    assert "if (!paymentConfig.checkoutEnabled) return null" in checkout
    assert "const CHECKOUT_MAINTENANCE = true" in checkout
    assert "if (CHECKOUT_MAINTENANCE) return <MaintenanceNotice />" in checkout
    assert "createSponsorshipOrder(product.id)" in checkout
    assert "captureVerifiedSponsorshipOrder(orderID)" in checkout
    assert "return post('/v1/orders', { productId });" in payment_api
    assert "client-id" in sdk
    assert "PAYPAL_CLIENT_SECRET" not in sdk


def test_node_payment_regressions():
    subprocess.run(
        [
            "node", "--test",
            "test/domain.test.js",
            "test/repository.test.js",
            "test/campaign-automation.test.js",
        ],
        cwd=WORKER,
        check=True,
    )
