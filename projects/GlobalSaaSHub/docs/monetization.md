# GlobalSaaSHub monetization operations

## Separate revenue tracks

Affiliate revenue and paid sponsorship are independent products. An affiliate link is used only when its program URL has been verified; otherwise visitors receive the official product URL. Affiliate participation never changes editorial ratings, badges, comparison text, or ranking.

The one-time sponsorship is a separate USD 49 promotional placement. Payment alone does not guarantee acceptance, a particular position, or an editorial rating. The placement begins only after the payment is verified by the server and the submission is reviewed against the sponsorship policy.

## Payment architecture

GitHub Pages remains the static public site. A Cloudflare Worker owns PayPal credentials, creates and captures PayPal orders, verifies the final provider state, verifies webhook signatures, and persists orders in D1. The browser never chooses the amount and never receives a PayPal client secret or webhook identifier.

Order states are `created`, `pending`, `paid`, `failed`, `cancelled`, and `refunded`. Only a server-verified PayPal `COMPLETED` capture for exactly `49.00 USD` can move an order to `paid`. D1 uniqueness constraints and PayPal request IDs prevent duplicate processing.

## Activation gate

Checkout stays unavailable until all of the following are complete: policy review, PayPal Business/KYC and bank setup, a live PayPal app, webhook registration, Worker secrets, D1 migration, sandbox end-to-end tests, an operational refund/contact process, and an explicit production build with the public checkout flag, HTTPS API URL, and public PayPal client ID. Secrets must never use a `VITE_` variable.
