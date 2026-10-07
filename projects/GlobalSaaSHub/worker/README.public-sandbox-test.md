# Isolated public PayPal Sandbox test entry

This development entry connects signed buyer returns and durable, verified PayPal Sandbox webhooks to the advertisement state machine. It is separate from the production worker and does not open live advertising sales.

**Current evidence boundary:** the public integration, actual buyer approval/cancellation navigation, and deployed scheduled execution have not been verified in this change. Local Node and browser-script VM tests are not evidence of those external results. A formally authorized local workerd run passed all 15 PNG/zlib smoke checks using workerd `1.20260911.1`, compatibility date `2026-08-09`, and `nodejs_compat`. It also initialized the separate public-entry bundle and confirmed rejection of missing configuration. This local runtime evidence does not establish a deployed HTTPS, PayPal, or scheduled-execution result; no external fetch or deployment occurred during that run.

## Test configuration

Use `testconfig.example.toml` only as a template for a private, dedicated test configuration. All account, worker, database, URL, and build placeholders must be replaced deliberately. Production `wrangler.toml`, the production worker, and the `ORDERS` binding are outside this configuration.

- Entry: `src/ad-commerce-public-sandbox-worker.js`.
- Runtime target: compatibility date `2026-08-09` with `nodejs_compat`. Actual local workerd execution verified `inflateSync` with `info`, `maxOutputLength`, and `engine.bytesWritten`, all nine maximum-byte role PNGs, oversized-file rejection, and rejection of trailing compressed junk or a second stream. Deployed runtime behavior still needs its own confirmation.
- Database: a separate `AD_SANDBOX_DB` binding and an isolated `coshuma-ads-sandbox-*` database label. Install base schemas `migrations/0004_sponsorship_sales.sql` and `migrations/0005_image_ad_fulfilment.sql` in the empty test database, then the migrations in `sandbox-migrations/`. Do not apply these steps to an existing production database.
- Origin: use only the dedicated HTTPS test origin stored in the private deployment configuration. Do not publish or reuse its exact hostname.
- Secrets: configure the Sandbox app credentials, merchant ID, expected webhook ID, and separate operator/reviewer keys only in the test worker's secret store. Keep them out of source, URLs, public logs, and PR descriptions.
- The once-per-minute scheduled trigger is commented out by default. Enabling it is not proof that it ran; preserve actual scheduled execution records when external verification is performed.

## Authentication and payment flow

| Surface | Required authorization and behavior |
| --- | --- |
| `/sandbox/purchase` | Public test start page. The buyer enters an existing test order ID and that order's access key. |
| Protected order creation | A dedicated test operator key is required; customer mutations also require the configured origin. Administrative endpoint details are intentionally omitted from this public document. |
| Order data, upload, checkout, capture, reconcile | The matching order access key in `Authorization`, never a URL parameter. |
| Protected review actions | A separate reviewer key is required. Administrative endpoint details are intentionally omitted from this public document. |
| `/sandbox/checkout-return` | Purpose-bound signed return URL and matching provider order token. GET renders without payment or inventory mutation. |
| `/sandbox/webhooks/paypal` | Original request body and provider signature headers; successful Sandbox verification is required before durable event processing. |

The start and return pages share `sessionStorage` keys under `coshuma-sandbox-order:<order-id>` and navigate to the provider in the same tab. The start page verifies storage before leaving. Authentication fields are locked while a request is pending. The access key is not placed in a return URL, referrer, or rendered status text.

An approval return reads the authenticated server order first. Only an eligible first capture attempt is posted. A session marker is written before that request; refreshes and ambiguous responses reconcile the existing transaction instead of issuing another capture. Cancellation reads status without capture. Missing access, invalid tokens, expired reservations, and stopped states do not authorize a new charge. The UI displays server order state and stored advertising start/end timestamps.

Before checkout or capture, registration preflight checks the configured Sandbox app's expected webhook ID, isolated destination, supported event, and absence of account-level registrations. A different or additional destination prevents the payment action. The public entry rejects noncanonical paths so alternate encoding cannot skip this check.

Verified webhook receipts retain bounded retry/lease state in the test DB. Capture-completed recovery reconciles an existing provider capture; it does not create a new charge. The test scheduler drains due receipts and processes period expiry. Any controlled clock acceleration is restricted to the selected test order.

## Validation and remaining proof

Focused coverage is in `ad-commerce-purchase-page.test.js`, `ad-commerce-checkout-return.test.js`, `ad-commerce-return-http.test.js`, `ad-commerce-public-worker.test.js`, and the webhook/preflight tests. These use synthetic credentials and transports. Do not treat an old test count, a configured webhook, or an accepted deployment as proof of the current external flow.

Still required for the public integration: deployed Worker PNG confirmation; a real Sandbox transaction event received by the HTTPS endpoint with provider verification and matching durable state; automatic success and cancellation returns observed in the browser; persisted processing across instance replacement; and actual scheduled retry/expiry records. Keep event-level evidence private and publish only sanitized results.

The `work/` compatibility probes and local diagnostics are scratch files and must be excluded from the commit. Existing source backups, handoff archives, proposals, and logos are unchanged by this entry. No production merge, deployment, migration, live charge, or refund is implied by this test configuration.
