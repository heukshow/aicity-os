# Advertising commerce candidate: repository contract and restart checks

Draft only. This branch is not a deployable advertising sales service. The production Worker entrypoint, checkout configuration, public site and production database are unchanged.

## Repository contract

`AdStore` is the canonical sandbox repository interface: `createDraft`, `get`, `files`, `submitDraft`, `review`, `availability`, and `reserveReviewedOrder`.

The candidate combines explicit destination/claims approval checks, conditional audit writes and reservation reuse with checks for all seven required tables and all thirteen protection triggers. Reservations remain `approved` until a payment service binds a provider order. The previous `AdCommerceStore` interface is intentionally retired, not aliased.

The previous header-only `validateAdFile` implementation and its incorrect 24-byte PNG acceptance test have been removed. This is NOT a completed replacement image validator. A separately verified full decoder and upload route must be integrated before uploads or sales are enabled. Do not interpret the absence of the weak parser as finished PNG/JPEG/WebP support.

## Persistent fixture checks

A test-only SQLite adapter creates a fresh, marked temporary database. It refuses initialization over nonempty databases and refuses unrelated database files. Two independently started Node processes verify that the reviewed order, synthetic file records and all reserved positions survive process replacement without an extra reservation or audit.

The files in these persistence checks are one-byte synthetic metadata fixtures, not valid images. The checks establish local SQLite persistence and repository behavior, not production D1 recovery or real payment recovery after restart.

## Checkout return validation

`ad-commerce-checkout-return.js` builds purpose-bound, authenticated return/cancel URLs from the stored order. Browser-supplied status cannot mark an order paid. Approval requires the matching provider-order token. Cancellation may omit that token but still requires the signed, order-bound state. Return GETs perform no charge, refund, order cancellation or inventory release.

These are offline library checks. The URLs are not wired into a customer-facing checkout page or verified through a real PayPal return navigation in this change.

## Current test run

- 37 foundation/interface/report checks.
- 9 persistent SQLite checks, including independent process replacement.
- 14 checkout-return checks.
- 12 SQLite migration protection checks.

The focused candidate run passed 60 Node tests plus 12 Python migration tests. The subsequent full Worker regression run finished at 2026-10-06T23:00:05Z with 202 Node tests passed, zero failed and zero skipped across 17 test files. The focused 60 tests are included in 202, not additional tests. These numbers are not added to older prototype totals. The original end-to-end Sandbox prototype's separate test results are not evidence for unported modules in this candidate.

A dedicated pull-request workflow is configured to run all Worker regression tests and migration checks on Linux and Windows. Its first remote execution must be checked independently; local success does not establish remote success. It has read-only repository permission, no payment credentials and no production deployment step. Its entrypoint check prevents treating this draft as a production integration without a deliberate release review.

## Windows test-runner correction

Two existing offline SQLite test helpers invoked the Windows Store `python3` alias. They now use the installed `python` executable on Windows and `python3` elsewhere. No Python installation, filesystem permission or production behavior was changed. The full Worker test run passed after these portability fixes.

## Remaining release work

- Integrate the complete validated upload, payment, webhook and customer-screen modules with this canonical contract; rerun their full tests on the resulting single revision.
- Verify actual public Sandbox webhook delivery and provider signature verification.
- Wire and verify browser approval/cancellation return handling.
- Verify persistent payment reconciliation, unmatched-event recovery and cumulative partial refunds.
- Complete supported image formats and continuous rotating-ad/expiry behavior on the actual publication renderer.
- Verify the final frontend/Worker/database combination and synchronize prices, availability and documentation before enabling paid orders.

Passing this subset does not establish received money, deployed sales, a new advertiser, or increased revenue.
