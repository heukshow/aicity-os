# Sandbox readiness checks without configuration churn

This is a control-side development change, not a production release or proof of a successful public checkout.

## Change

`worker/src/ad-commerce-public-readiness.js` checks a caller-supplied read-only preflight response. It has no default network transport, deployment action, secret write or payment operation.

After a secret-upload step has completed, the caller may retry only the exact existing HTTP 503 configuration-pending response. The check has at most five attempts with waits of 1, 2, 4 and 8 seconds. It does not turn missing configuration into a success. If the response remains pending, the outcome remains not-ready.

HTTP 401/403, provider registration failures, malformed success responses, other HTTP errors and transport rejections stop immediately. This mechanism does not retry a browser access restriction or change any access policy. A successful response must match the expected webhook ID, one application registration, zero account registrations, the intended event and a valid check timestamp.

The private loopback controller now has a separate existing-configuration preflight action. It keeps its configured credentials in memory, does not recreate registrations or re-upload secrets for this action, and leaves readiness false until the server's verification succeeds. Its original file was backed up before a context-checked edit. Updating the file does not update an already running controller process.

## Verification

The new offline regression suite contains 14 top-level tests. It covers bounded configuration retries, manual recheck without configuration writes, persistent failure, denial handling, exact registration matching, transport failure, invalid inputs, cancelled waits and exclusion of unrelated response fields. These tests use synthetic responses and do not visit the public test origin.

The original HTTP server isolation guards and payment gates are unchanged. No code in the production entrypoint or production deployment configuration imports the new helper.

## What this does not establish

The timing of a prior HTTP 503 alone cannot establish which deployment served it or whether propagation caused it. A later metadata listing of configured secrets does not prove their values or a successful HTTP preflight. This change does not claim to resolve a browser restriction, verify actual public webhook delivery or demonstrate actual approval/cancellation return flows.

A newly started controller may use the revised read-only preflight after normal access is available. Do not replace that check with a payment, a simulator event, an alternate hostname or a disabled guard. The PR remains a development draft pending the separate public integration checks.

## Final local regression for this change

The final source completed all 29 Worker test files: **456 passed, 0 failed, 0 skipped**. The 14 readiness tests are included in 456, not additional tests. The separate SQLite protection suite passed 12 tests and the separate runner safety suite passed 11 tests. The private controller syntax check also passed without external requests. Sources were unchanged during the tests. These counts do not include or add prior historical runs or repeat counts across operating systems.

The latest main changes were integrated into the development branch without conflicts; main itself was not modified. The remote PR checks must be associated with the resulting commit separately. No public-origin HTTP call, secret update, server deployment, payment or browser-policy change was performed during these offline checks.
