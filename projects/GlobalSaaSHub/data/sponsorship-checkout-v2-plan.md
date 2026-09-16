# COSHUMA Sponsorship Checkout v2 — Safe Integration Plan

This branch is intentionally based on current `main`, not stale PR #397.

## Non-negotiable launch gates

- `CHECKOUT_ENABLED=false` until final launch verification.
- Frontend maintenance mode remains enabled until the compatible Worker is deployed and verified.
- No real purchase is required for staging.
- No PayPal secret changes.
- No new Worker, D1 database, or paid service.

## Product catalog

| Product ID | Placement | Duration | Price |
| --- | --- | ---: | ---: |
| `tool_page_7` | Tool Page Sponsored | 7 days | $19 |
| `tool_page_30` | Tool Page Sponsored | 30 days | $49 |
| `tool_page_90` | Tool Page Sponsored | 90 days | $129 |
| `buyer_intent_7` | Buyer-Intent Featured | 7 days | $39 |
| `buyer_intent_30` | Buyer-Intent Featured | 30 days | $99 |
| `buyer_intent_90` | Buyer-Intent Featured | 90 days | $269 |
| `comparison_7` | Comparison Premium | 7 days | $59 |
| `comparison_30` | Comparison Premium | 30 days | $149 |
| `comparison_90` | Comparison Premium | 90 days | $399 |

## Migration strategy

Current `main` already contains:

- `0001_orders.sql`
- `0002_private_ops.sql`
- `0003_sponsored_campaigns.sql`

Therefore the stale branch migration `0002_advertiser_automation.sql` must not be applied. This branch adds only the missing order metadata through `0004_sponsorship_order_metadata.sql`.

## Safe rollout order

1. Implement and test server-owned product selection.
2. Store `product_id` on each order and verify provider amount against that product.
3. Create campaign only after verified capture.
4. Connect asset intake, placement publication, events, and reporting to the existing sponsored schema.
5. Run tests and `wrangler deploy --dry-run`.
6. Apply migration 0004 to the existing D1 database.
7. Deploy compatible Worker while checkout remains disabled.
8. Verify `/health` and `/v1/sponsored/placements` without payment.
9. Verify create-order behavior without real capture.
10. Only then wire and enable the matching frontend checkout.
11. Remove maintenance mode and set `CHECKOUT_ENABLED=true` only for final launch.
