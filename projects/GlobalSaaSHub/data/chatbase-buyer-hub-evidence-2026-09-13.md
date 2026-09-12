# Chatbase buyer-hub evidence — 2026-09-13

## Verified customer route

- Existing COSHUMA partner evidence records the exact customer-facing Chatbase referral URL as `https://link.chatbase.co/sang-kwon-an`.
- Chatbase support directly provided this URL to `support@coshuma.com` after reviewing the partner account on 2026-09-05.
- Existing production sync logic already treats this route as `approved_tracking` and explicitly warns not to replace it with a dashboard or guessed destination.

## Current first-party buyer facts

Rechecked on 2026-09-13 against Chatbase's official pricing page (`https://www.chatbase.co/pricing`):

- Free: $0/month.
- Free includes 50 message credits/month and 1 member.
- Free-plan AI agents are deleted after 14 days of inactivity.
- Hobby: $40/month and currently offers a 7-day trial.
- Standard: $150/month and currently offers a 7-day trial.
- Pro: $500/month and currently offers a 7-day trial.
- Vendor checkout and current pricing remain authoritative.

Chatbase's current affiliate terms state that qualified referrals are customers who sign up for a paid subscription using the affiliate's unique referral link or code. The terms do not publish one fixed commission rate; applicable rates are shown in the partner dashboard. Therefore COSHUMA must not invent or publish an account-specific commission percentage from public terms alone.

## Safe production action

Surface Chatbase on COSHUMA's verified software free-trial/partner-offer hub using only `https://link.chatbase.co/sang-kwon-an`. Keep the official pricing page separate for independent verification. Do not construct a `/pricing` affiliate deep link from the referral route.

## Revenue truth guard

Publishing or validating the link proves only that an already-issued customer-facing referral route is exposed on another buyer-intent page. It does not prove a new click, signup, trial, paid customer, commission, payout or revenue. Downstream metrics remain unknown until partner-side evidence proves them.
