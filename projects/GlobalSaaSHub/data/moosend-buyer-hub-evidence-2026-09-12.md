# Moosend verified buyer-hub route — 2026-09-12

## Revenue objective
Surface an already-approved Moosend customer referral route on COSHUMA's verified buyer-offers hub without creating a new affiliate application, guessing a deep link, or claiming unverified revenue.

## Existing account-specific evidence
- `data/approved-tracking-2026-09-08.json` records Moosend as `approved_tracking`.
- Exact customer-facing PartnerStack URL: `https://trymoo.moosend.com/6eappdpw04pw`.
- The prior authenticated PartnerStack check observed this exact link in the Links section and verified that it resolved to the official Moosend customer destination with attribution parameters.
- The same prior dashboard evidence recorded 2 clicks, 0 signups, and $0 revenue at that measurement time. Those historic values are not treated as current totals without a fresh partner-side read.

## Current first-party public facts rechecked 2026-09-12
- Official affiliate page: `https://moosend.com/affiliate-program/`.
- Official registration page: `https://identity.moosend.com/register/`.
- Current Moosend terms state a 30-day free trial.
- Current registration page says no credit card is required to get started.
- Current affiliate page advertises tiered recurring commission starting at 30% for 0–5 paid accounts and increasing to 40% for 36+ paid accounts, continuing while the referred customer remains paying. It also says the affiliate program is free to join and pays monthly via PayPal or Stripe.
- These affiliate terms describe COSHUMA's potential partner compensation; they are not a guaranteed customer discount.

## Production safety rules
- Public affiliate CTA may use only `https://trymoo.moosend.com/6eappdpw04pw` unless Moosend itself supplies another exact customer URL.
- PartnerStack dashboard/login/onboarding URLs and generic administrative routes are never customer CTAs.
- Do not manufacture a pricing deep link by copying attribution parameters onto `/pricing/`.
- Link publication or testing does not prove a signup, trial, paid customer, commission, payout, or revenue.
- No self-referral, paid subscription, checkout, payout-setting change, or duplicate application.