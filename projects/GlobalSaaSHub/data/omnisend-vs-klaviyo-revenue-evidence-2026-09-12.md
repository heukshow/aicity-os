# Omnisend vs Klaviyo revenue comparison evidence — 2026-09-12

## Revenue objective
Create a new high-intent ecommerce email comparison that can route qualified buyers through COSHUMA's already verified Omnisend pricing tracker, while keeping Klaviyo official-only because no COSHUMA-specific Klaviyo customer revenue URL is verified.

## COSHUMA revenue route used
- Omnisend status: `approved_tracking`.
- Exact vendor-issued general tracker: `https://your.omnisend.com/4aA5k9`.
- Exact vendor-issued pricing tracker: `https://your.omnisend.com/VOKyAj`.
- The pricing tracker was sent directly by Omnisend Senior Affiliate Marketing Manager Deimantė Vaitkevičiūtė in Gmail message `1a085d0074ddb3a0` after COSHUMA specifically asked for a customer-facing link landing on Omnisend pricing.
- This comparison uses only `https://your.omnisend.com/VOKyAj` for the pricing-intent Omnisend CTA.
- Klaviyo remains official-only at `https://www.klaviyo.com/pricing/`; no affiliate parameter, dashboard, onboarding or guessed revenue URL is used.

## Official product facts rechecked 2026-09-12
### Omnisend
Sources:
- `https://support.omnisend.com/en/articles/3533018-omnisend-pricing-plans-2026`
- `https://www.omnisend.com/pricing/`

Current first-party facts used:
- Free plan: $0/month, up to 250 contacts for sending, up to 500 emails/month.
- Official help says no credit card is required for the Free plan.
- Standard starts at $16/month.
- Pro starts at $59/month.
- Paid pricing can scale based on billable contacts.
- Current docs say new paid subscriptions from May 4, 2026 onward use Pro for SMS, with volume-priced SMS add-on rules.
- Official pricing page advertises 24/7 support on all plans including Free.

### Klaviyo
Sources:
- `https://www.klaviyo.com/pricing/`
- `https://help.klaviyo.com/hc/en-us/articles/360050759151`

Current first-party facts used:
- Free plan: $0/month.
- Up to 250 active profiles.
- Up to 500 emails/month.
- Current pricing page lists $5 of mobile messages/month on Free, subject to region/carrier conditions.
- Official help says Free users get email support for the first 60 days, then community/self-service resources.
- Paid pricing is profile/usage dependent, so the comparison avoids inventing a fixed paid entry price.

## Publication
New page:
- `https://coshuma.com/compare/omnisend-vs-klaviyo-free-plan.html`

The page includes:
- canonical and social metadata
- FAQ structured data
- official-source links
- exact Omnisend pricing tracker with `rel="sponsored"`
- Klaviyo official pricing link only
- explicit affiliate disclosure
- no signup, sale, commission, payout or revenue claim

## Guardrails
- No new affiliate application or account.
- No paid subscription or purchase.
- No generic dashboard/login/onboarding URL used as a customer revenue link.
- No Klaviyo affiliate URL guessed or synthesized.
- Omnisend click/link publication is not treated as a signup, paid customer, commission or payout.
