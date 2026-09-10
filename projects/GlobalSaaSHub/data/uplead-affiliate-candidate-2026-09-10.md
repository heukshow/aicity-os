# UpLead approved tracking — 2026-09-10

## Current operational status

- `affiliate_status`: `approved_tracking`
- `affiliate_verified`: `true`
- `exact_tracking_url`: `https://www.uplead.com?fp_ref=sangkwon-3af7dc`
- Company mailbox used: `support@coshuma.com`
- Vendor welcome Gmail message: `1a08b7419d47b773`
- Browser/dashboard login URL is operational only and must not be published as a buyer CTA.
- Do not reapply or create another UpLead affiliate account.

## Vendor-issued evidence

On 2026-09-10 UpLead sent `support@coshuma.com` the subject `Welcome to UpLead referral program!`. The message explicitly says COSHUMA can get started by sharing `https://www.uplead.com?fp_ref=sangkwon-3af7dc` and that UpLead will reward the account each time a referred user subscribes to a paid account. The message separately identifies `https://affiliates.uplead.com/login` as the dashboard used to view stats. This separation is sufficient evidence that the `fp_ref` URL is the customer-facing referral route while the dashboard URL is not.

No click, signup, paid customer, commission, or revenue is inferred from the welcome email or link issuance alone.

## Official program terms rechecked 2026-09-10

- Program page: `https://www.uplead.com/partners/affiliates/`
- Program terms: `https://www.uplead.com/affiliate-program-terms/`
- UpLead currently advertises 20% recurring commission on paid plans and a 60-day default affiliate cookie.
- Payments are described as monthly, subject to the program terms and payout threshold.
- Self-referrals are prohibited.

## Revenue action applied

COSHUMA's existing `/best/b2b-email-list-providers.html` already contains UpLead buyer intent. Production build now runs `scripts/apply_uplead_verified_tracking.py`, which inserts only the exact vendor-issued customer URL into the UpLead CTA positions, adds explicit affiliate attribution metadata, retains the separate official pricing link where useful, and guards against accidentally publishing the affiliate dashboard URL.

## Do not

- Do not substitute `https://www.uplead.com/`, `/pricing/`, `https://affiliates.uplead.com/`, or the dashboard login URL for the verified referral URL.
- Do not construct a new UpLead deep link by appending `fp_ref` to another path unless UpLead explicitly confirms that exact deep-link behavior.
- Do not self-refer.
- Do not claim clicks, signups, commissions, payouts, or revenue without actual dashboard/vendor evidence.
