# Launch gates

All gates are fail-closed. A green code build alone is not permission to open payments.

1. Worker tests pass on a staging head that is 0 commits behind current `main`.
2. `wrangler deploy --dry-run` passes with `CHECKOUT_ENABLED=false`.
3. The nine server-owned product IDs and USD prices pass fail-closed tests.
4. Migration `0004_sponsorship_order_metadata.sql` is applied to the existing `globalsaashub-orders` D1 only; the legacy fixed-$49 `orders` table remains untouched.
5. The compatible Worker is deployed to the existing Worker with `CHECKOUT_ENABLED=false` and existing secrets unchanged.
6. Live no-payment readiness passes: `/health` reports `checkoutConfigured=false`; placements/CORS/fail-closed advertiser/report/event checks pass; `POST /v1/orders` still returns checkout unavailable.
7. Verified capture/webhook product checks create at most one campaign and refund/reversal stops associated inventory.
8. Asset intake, reserved-slot verification, placement conflict handling, scheduled flight dates, impression/click recording, report metrics, renewal/final report generation, expiry, and the hourly maintenance trigger are verified.
9. Production frontend build is verified while `CHECKOUT_MAINTENANCE=true` and sponsored inventory runtime is still disabled.
10. Before accepting the first payment, enable the sponsored-inventory runtime first while checkout remains closed and verify that empty inventory renders nothing. This prevents a paid campaign clock from starting while the public renderer is unavailable.
11. Only after inventory is ready, perform a separate final checkout review. Then enable the Worker checkout gate and remove frontend maintenance as the final deliberate release changes.
12. After release, immediately verify health, product selector amounts, placement fetch, and fail-closed invalid requests without making a COSHUMA self-purchase.

Never during staging: real payment, PayPal secret changes, new Worker/D1/paid service, stale PR #397 merge, stale migration reuse, or production advertiser publication.
