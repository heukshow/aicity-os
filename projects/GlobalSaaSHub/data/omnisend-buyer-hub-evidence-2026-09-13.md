# Omnisend buyer-hub evidence — 2026-09-13

## Revenue objective

Surface an already-approved Omnisend customer revenue route on COSHUMA's central verified-offers hub. This is a conversion-surface change only; it is not a new affiliate application and does not infer any downstream revenue event.

## Exact customer-facing tracking route

Existing repository evidence in `data/omnisend-affiliate-approved-2026-09-09.md` records two human/vendor-issued Omnisend tracking URLs:

- General customer route: `https://your.omnisend.com/4aA5k9`
- Direct pricing-intent route: `https://your.omnisend.com/VOKyAj`

The direct pricing route was supplied by Omnisend Senior Affiliate Marketing Manager Deimantė Vaitkevičiūtė after COSHUMA explicitly requested a customer-facing link landing on the Omnisend pricing page. Use that exact pricing route for the buyer hub. Do not append Impact parameters, do not construct another deep link, and never expose Impact login/dashboard/onboarding URLs as customer CTAs.

## Current first-party product facts checked 2026-09-13

Official pricing/help sources:

- `https://www.omnisend.com/pricing/`
- `https://support.omnisend.com/en/articles/3533018-omnisend-pricing-plans-2026`

Current vendor facts used on the buyer hub:

- Free plan: `$0/month`.
- Free plan limit: up to `500 emails/month` to a maximum of `250 contacts`.
- No credit card required for the Free plan.
- Standard regular entry price: `$16/month` before any current starter promotion.
- Pro regular entry price: `$59/month` before any current starter promotion.
- Omnisend currently advertises a 30% starter discount for the first three months when a new subscriber prepays three months, but checkout controls final eligibility and pricing.

## Current first-party affiliate terms checked 2026-09-13

Official source: `https://www.omnisend.com/affiliates/`

- 20% recurring commission on qualifying referred paying customers.
- Commission duration: up to 24 months while the referred customer remains paying.
- 60-day attribution window.
- Tracking/reporting/payments are handled through Impact.
- Omnisend instructs affiliates to use links exactly as provided.

These are program terms, not COSHUMA earnings.

## Revenue-truth boundary

No new authenticated Impact totals were read in this change. Therefore the following remain unproven for the current period unless separate dashboard/email evidence exists:

- clicks: unknown current total,
- referred signups: unknown current total,
- paid customers: unknown current total,
- commission earned/pending/paid: unknown current total,
- payout: unknown current total,
- actual revenue: unknown current total.

Publishing, opening, or validating the Omnisend CTA does not prove any downstream conversion or commission.
