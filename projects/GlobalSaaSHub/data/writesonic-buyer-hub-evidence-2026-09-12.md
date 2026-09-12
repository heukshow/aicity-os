# Writesonic verified buyer-hub route — 2026-09-12

## Revenue objective
Surface an already-approved Writesonic customer referral route on COSHUMA's verified buyer-offers hub without creating a new affiliate application, inventing a deep link, or claiming unverified revenue.

## Existing account-specific evidence
- Repository state in `data/tools.json`, `data/tools.next.json`, and `scripts/sync_verified_affiliates.mjs` records Writesonic as `approved_tracking`.
- Exact customer-facing referral URL: `https://writesonic.com?fp_ref=sang-kwon-f5452a`.
- Existing repository evidence says the Writesonic welcome/approval message issued that exact URL and that referrals are rewarded after a referred user subscribes to a paid account.
- The September 2026 approval evidence supersedes the older stale rejected state.

## Current first-party public facts rechecked 2026-09-12
- Official affiliate page: `https://writesonic.com/affiliate`.
- Official pricing page: `https://writesonic.com/pricing`.
- Writesonic's live affiliate page currently advertises 20% recurring commission for up to 12 months, a 60-day cookie, and monthly payouts via FirstPromoter.
- The same live first-party page describes a free trial that requires no card.
- The pricing page is kept as a separate official reference only. COSHUMA does not append `fp_ref=sang-kwon-f5452a` to `/pricing` because no account-specific pricing deep link has been verified.

## Production safety rules
- Public affiliate CTA may use only `https://writesonic.com?fp_ref=sang-kwon-f5452a` unless Writesonic itself supplies a replacement/additional exact customer URL.
- `affiliates.writesonic.com`, FirstPromoter dashboard/login/onboarding URLs, and generic admin routes are never customer CTAs.
- Link publication or testing does not prove a trial, signup, paid customer, commission, payout, or revenue.
- No self-referral, paid subscription, checkout, payout-setting change, or duplicate application.
