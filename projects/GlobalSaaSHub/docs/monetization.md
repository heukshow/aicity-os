# GlobalSaaSHub monetization operations

## Separate revenue tracks

Affiliate revenue and paid sponsorship are independent products. An affiliate link is used only when its program URL has been verified; otherwise visitors receive the official product URL. Affiliate participation never changes editorial ratings, badges, comparison text, or ranking.

## Payout account handling

The COSHUMA Wise Business Basic account has been created for `support@coshuma.com`, but no USD, EUR, GBP, or other receiving account details have been issued. Never invent or submit Wise bank details to an affiliate platform. Allow commissions to accrue on each platform and defer payout setup until the balance approaches its payment threshold. Immediately before a real payout, re-check the current Wise terms and fee, complete any required Advanced activation and identity verification, and register only the receiving details actually issued by Wise. Passwords and authentication secrets must never be stored in this repository.

Paid sponsorship is a separate product. Payment alone does not guarantee acceptance or change an editorial rating. The placement begins at its approved publication time after payment verification, material review and an inventory check.

## Advertising catalogue

The server reads the existing USD prices from `data/sponsorship-inventory.json`:

| Placement | 7 days | 30 days | 90 days |
| --- | ---: | ---: | ---: |
| Tool Page Sponsored | $19 | $49 | $129 |
| Buyer-Intent Featured | $39 | $99 | $269 |
| Comparison Premium | $59 | $149 | $399 |

The initial explicit page list is `/tool/pipedrive.html`, `/best/claap-sales-follow-up-ai.html`, and `/compare/semrush-vs-frase.html`, each paired only with its corresponding placement. Home, Gamma, Chatbase, the Privy/Omnisend measurement page, wildcard pages and cross-placement requests are excluded. Adding a page requires a deliberate inventory and editorial review.

The format is a text card with a fixed **Sponsored** label, headline, description, button and HTTPS destination. No logo or image is required. Traffic, clicks, signups and revenue are not guaranteed.

## Payment architecture

GitHub Pages remains the static public site. The existing Cloudflare Worker owns PayPal credentials and the D1 records. The browser submits the requested product and creative; the server determines the price, USD currency, permitted page and duration. The browser never receives a PayPal client secret, merchant credential or webhook identifier.

Migration `0004_sponsorship_sales.sql` adds independent `sponsorship_*` tables. It does not rewrite the legacy `orders`, `webhook_events`, `campaigns` or analytics tables, and does not depend on a historical campaigns migration having succeeded. Legacy fixed-$49 payment records stay historical records; they do not become advertisements automatically.

An application stores company name, tool name, contact email, placement, duration, exact target page, destination URL, headline, description, button text, requested start date, seller attestation and an immutable server quote. The server issues a unique application ID and readable advertising reference. Company and tool names accompany the reference in the payment description; PayPal `custom_id` identifies the application and `invoice_id` is the unique reference. The payer's display name is not a sufficient payment match.

The application access token is returned once and only its SHA-256 hash is stored. Application status and checkout calls require this token in an Authorization header. Tokens must not appear in query strings, analytics, public issues or screenshots. Public status is a read of saved verification results; it does not create or capture a payment.

The checkout flow creates one persisted payment attempt per application and reuses its PayPal request IDs on retries. Verification re-reads the PayPal order and capture, requiring a live environment, the saved order ID, matching application and invoice references, the expected receiving merchant, exactly one completed capture, and the exact quoted gross amount and currency. Fees and net proceeds are not substituted for the gross price. Missing, pending, mismatched or inaccessible provider data never counts as verified payment.

The implemented provider is PayPal Orders. There is no bank-transfer reconciliation, PayPal.me reconciliation, Stripe checkout or Invoice payment inference in this flow.

## Intake, payment and publication are separate

The public configuration response separates `intakeReady` and `paymentReady`. The site can save an application when D1 and the allowed public origin are ready even while payment remains unavailable. A missing table or publication guard produces an explicit unavailable response; it is not treated as a successful application. A PayPal public client ID is returned only while the configured checkout is available.

Financial review uses existing owner authentication. The audience-growth workflow identity gains no payment, financial-read or approval rights. Owner write requests also require a same-origin JSON request. Credentials and private access routes are not published in operational issues or customer documentation.

The owner can independently recheck a payment, review the materials, publish an approved application, or pause a campaign. Material approval requires verified payment plus recorded destination and claim checks. Publication rechecks the provider again and requires verified live payment, approved materials, a permitted page/slot, a valid exact-length period and no overlapping paid placement. The D1 publication trigger enforces these conditions and detects inventory conflicts within the write transaction.

Public placement responses join the payment evidence with the approved application and require the current time to fall inside the stored flight. They expose only the public creative, dates, campaign ID and boolean publication gates. Invalid or duplicate active inventory is hidden. There is no automatic approval or immediate publication from a browser payment callback.

Signed refund and reversal events stop publication. Partial refunds also stop publication when detected by capture verification. A partial refund is terminal for this application: there is no automatic prorated restart or reactivation. Dispute events place all linked campaigns on hold for owner review; a late completed event cannot restore a refunded or held payment. Webhook verification remains active while creation of new checkouts is paused. This implementation does not execute refunds or withdraw money. A paused campaign cannot silently resume or extend its purchased end date; a new reviewed application is required for an extension.

The verified webhook handler also continues updating historical fixed-price orders and their existing event history. New legacy fixed-$49 checkouts are retired. A signed legacy refund cannot be undone by a late completed event; a new historical completion must independently match the saved order, expected merchant, capture and gross amount.

## Activation gate

`CHECKOUT_ENABLED` remains `false` in the committed Worker configuration. Enabling it is a separate production decision after the existing merchant/app, expected merchant ID, webhook registration, secrets, additive migration, owner authentication and operational refund/contact process are checked. Secrets must never use a `VITE_` variable.

The protected readiness probe authenticates with the existing PayPal app and reads the registered webhook URL and required event subscriptions. It does not create an app, order, capture, charge or refund. A successful OAuth/webhook read does not independently prove merchant identity or a completed customer payment. Local mock tests, migration rehearsals and a bundle dry run likewise do not establish live readiness. Record live configuration verification separately from the first real advertiser payment and its verified publication.

The public health endpoint remains a liveness response only. An `ok: true` value is not evidence that checkout is configured, that advertising tables are present, or that a customer has paid.
