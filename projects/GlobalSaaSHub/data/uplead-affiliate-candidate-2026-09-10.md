# UpLead approved tracking — 2026-09-10

## Current operational status

- `affiliate_status`: `approved_tracking`
- `affiliate_verified`: `true`
- Homepage tracking URL: `https://www.uplead.com?fp_ref=sangkwon-3af7dc`
- Pricing tracking URL: `https://www.uplead.com/pricing/?fp_ref=sangkwon-3af7dc`
- 7-day trial tracking URL: `https://app.uplead.com/trial-signup?fp_ref=sangkwon-3af7dc`
- Company mailbox used: `support@coshuma.com`
- Vendor welcome Gmail message: `1a08b7419d47b773`
- Vendor human deep-link confirmation Gmail message: `1a08d9736524831d`
- Browser/dashboard login URL is operational only and must not be published as a buyer CTA.
- Do not reapply or create another UpLead affiliate account.

## Vendor-issued evidence

On 2026-09-10 UpLead sent `support@coshuma.com` the subject `Welcome to UpLead referral program!`. The message explicitly says COSHUMA can get started by sharing `https://www.uplead.com?fp_ref=sangkwon-3af7dc` and that UpLead will reward the account each time a referred user subscribes to a paid account. The message separately identifies `https://affiliates.uplead.com/login` as the dashboard used to view stats.

On 2026-09-11, Will Cannon from UpLead replied directly to the existing thread and explicitly confirmed two additional customer-facing tracking URLs for the same affiliate account:

- Pricing: `https://www.uplead.com/pricing/?fp_ref=sangkwon-3af7dc`
- 7-day trial signup: `https://app.uplead.com/trial-signup?fp_ref=sangkwon-3af7dc`

Will also directed COSHUMA to the existing affiliate dashboard login for clicks, referred sign-ups/leads, paying customers, commission and payout statistics. This keeps the dashboard operational-only and proves the two new URLs are vendor-issued tracking routes rather than guessed parameterized links.

No click, signup, paid customer, commission, payout, or revenue is inferred from link issuance alone.

## Official product facts rechecked 2026-09-11

- UpLead's live pricing page currently lists a `$0 / 7 days` free trial with `5 credits`.
- One credit unlocks one contact for download or CRM export and provides the contact's email and mobile direct dial.
- UpLead's support guidance says payment details are required to activate full trial access; no charge occurs during the trial, but billing can begin after Day 7 unless the trial is cancelled before then.

These product facts describe the customer offer only. They do not prove any COSHUMA referral, sale or commission.

## Revenue action applied

Production build runs `scripts/apply_uplead_verified_tracking.py`. The script now:

- routes trial-intent CTAs to the exact vendor-issued trial URL;
- routes pricing-intent CTAs to the exact vendor-issued pricing URL;
- preserves the payment-details / post-trial billing warning near trial CTAs;
- ensures `/best/b2b-email-list-providers.html` loads COSHUMA's first-party affiliate attribution script so its existing `data-cta` events are collected;
- keeps the affiliate dashboard/login URL out of public pages;
- fails the build if the required vendor-issued URLs or attribution markers are missing.

## Do not

- Do not use the affiliate dashboard/login URL as a customer CTA.
- Do not invent any additional UpLead deep links by appending `fp_ref` to other paths.
- The three URLs documented above are allowed because UpLead explicitly issued/confirmed them.
- Do not self-refer.
- Do not claim clicks, signups, commissions, payouts, or revenue without actual dashboard/vendor evidence.
