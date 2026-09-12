# Catalister buyer-hub evidence — 2026-09-13

## Revenue route

- Existing authenticated COSHUMA affiliate evidence records the exact customer-facing Catalister referral URL as `https://app.catalister.com/signup?via=coshuma`.
- The authenticated Catalister dashboard issued that URL after onboarding and the customer signup destination retained `via=coshuma`.
- Pre-validation dashboard evidence recorded 0 clicks, 0 paying referrals, 0 trialing referrals, EUR 0 total/unpaid commission and EUR 0 revenue. Link issuance and a validation visit are not customer conversions.
- Source of the exact route: `data/approved-tracking-2026-09-08.json` and the existing `catalister` tool record.

## Current buyer facts rechecked against Catalister first-party pages

Rechecked on 2026-09-13:

- Official site: `https://catalister.com/`
- AI Shopify listing page: `https://catalister.com/ai-shopify-product-listing`

The current first-party site states:

- free 7-day trial,
- no credit card required to start,
- Starter €14.99/month,
- Stacker €24.99/month,
- Scaler €34.99/month,
- Slayer €59.99/month,
- Shopify-focused AI product listing/relisting and Google Ads analysis workflows.

Final checkout pricing, taxes and offer terms remain vendor-controlled.

## Safe production action

Surface Catalister on COSHUMA's verified software free-trial/partner-offer hub using only the exact issued customer referral URL. Keep the official Catalister homepage available separately for independent pricing verification. Do not invent a pricing or checkout affiliate deep link.

## Revenue truth guard

This change proves only that an already-issued customer-facing referral route is being surfaced on another buyer-intent page. It does not prove a new click, trial, paid customer, commission, payout or revenue. Downstream stages remain evidence-dependent.