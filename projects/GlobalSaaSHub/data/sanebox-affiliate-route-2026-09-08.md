# SaneBox affiliate route re-verification — 2026-09-08

## Fresh first-party evidence

- Official program page: https://www.sanebox.com/partners
- The live page currently identifies the program as **SaneBox Affiliate**, shows an **Apply now** button to `sanebox.partnerstack.com`, and states the program is run through PartnerStack.
- The page states affiliates can earn **up to 30% lifetime commission** on subscription revenue.
- It states referred customers receive a **$25 subscription credit** when they become customers.
- It states commissions are paid on **paid conversions**, not sign-ups or free trials.
- It states the customer/referral link is created in the authenticated PartnerStack dashboard after signup/approval.
- It lists `partners@sanebox.com` as the partner contact.

## Repository conflict found

The current COSHUMA tool data still contains an older `application_page_unavailable` observation for SaneBox. That observation is now superseded by the live first-party application route above.

## Decision

- `affiliate_url`: `null`
- `affiliate_status`: `browser_required_partnerstack_application`
- `cost`: `0`
- Do not publish the PartnerStack application/dashboard URL as a customer affiliate or revenue URL.
- Do not mark `approved_tracking` until the authenticated SaneBox PartnerStack account exposes an exact account-specific customer referral link and that link is verified.
- Do not infer clicks, signups, commissions, or revenue from program availability alone.

## Next action

Use the live SaneBox PartnerStack application route in the browser-required queue. Stop for CAPTCHA, OTP, payment, legal/program-term acceptance, or forced identity verification if encountered. After approval, copy only the exact customer-facing referral link from PartnerStack and verify its destination before changing COSHUMA CTA data.
