# Airia partner-program evidence — 2026-09-08

## Current first-party program

- Airia's current official partner page is `https://airia.com/partners/`.
- The page explicitly offers a **Referral partner** path and routes all partner applications to its Airia-specific PartnerStack application.
- Exact application route observed from the official Airia page: `https://dash.partnerstack.com/application?company=airia&group=default`.
- PartnerStack's public program directory currently describes Airia's referral program as link-based attribution with lead/deal registration and 10% on new software sales for the first year. A directory note about an extra 20% ended in March 2026 and is therefore not treated as a current offer.
- Gmail duplicate check on the COSHUMA company mailbox (`support@coshuma.com`) found no prior Airia affiliate/partner application or partner email before this check.

## Decision

- `affiliate_url`: `null`
- `affiliate_status`: `browser_required_partnerstack_application`
- `cost`: `0`
- Do **not** publish the PartnerStack application/dashboard URL as a customer affiliate or revenue URL.
- Do **not** infer approval, clicks, customer signups, commission, or revenue.
- Application requires the authenticated PartnerStack JavaScript UI, so it is intentionally left for the browser-required path rather than guessed or duplicated by email.
- If the existing PartnerStack account shows Airia already pending/approved/rejected/cooldown, stop without submitting another application.
- If a legal agreement, CAPTCHA, OTP, payment, or forced identity verification appears, user intervention is required and only this candidate should pause.

## Sources checked

- Official Airia partner page: `https://airia.com/partners/`
- Airia-specific PartnerStack application route: `https://dash.partnerstack.com/application?company=airia&group=default`
- PartnerStack public Airia program directory: `https://market.partnerstack.com/program/airia`
- Company-mailbox duplicate search: no matching Airia messages as of 2026-09-08 04:25 KST.
