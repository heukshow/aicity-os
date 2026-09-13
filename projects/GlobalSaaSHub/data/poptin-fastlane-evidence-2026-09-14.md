# Poptin fast-lane evidence — 2026-09-14

## Revenue objective
Add Poptin as the next sequential COSHUMA popup/on-site conversion buyer surface after Popupsmart, while keeping attribution evidence-first and avoiding duplicate account creation.

## Duplicate-state check
- GitHub default-branch search for `Poptin` returned no prior COSHUMA Poptin record before this cycle.
- `support@coshuma.com` Gmail search `in:anywhere (poptin OR poptin.com)` returned no received, sent, spam, trash, application, approval, rejection, tracking-link, commission or payout record.

## Official current evidence
- Affiliate program: https://www.poptin.com/affiliate/
- Pricing: https://www.poptin.com/pricing/
- Product home: https://www.poptin.com/
- Poptin's official affiliate page says the program is open to all and registration is free.
- The official program says a unique affiliate link is provided inside the authenticated control panel.
- Current public affiliate terms advertise a 90-day cookie window and lifetime 25% monthly commission for each new paying member recruited.
- Poptin advertises a Free Forever account for up to 1,000 visitors per month and says no credit card is required.
- Paid Basic, Pro and Agency tiers are available with monthly/annual billing. COSHUMA intentionally does not hard-code a checkout total because the official pricing view can vary by billing mode.

## COSHUMA state after this cycle
- `application_state`: `not_submitted`
- `affiliate_status`: `browser_required_account_registration`
- exact customer referral URL: `null / unknown`
- clicks / signups / paying customers / commission / payout / revenue: `unknown`
- GitHub issue: #485

## Buyer surfaces
- `/tool/poptin.html`
- `/best/poptin-free-plan-pricing.html`
- `/compare/poptin-vs-popupsmart.html`

The Poptin vs Popupsmart comparison is intentional rather than synthetic: both products target popup/on-site conversion workflows and both currently advertise free entry tiers. Comparison claims are limited to current public vendor evidence.

## CTA rule
Until Poptin itself issues and COSHUMA verifies the account-specific unique referral URL shown in the authenticated control panel, every Poptin CTA remains an official non-affiliate link. `app.popt.in`, dashboard/login/onboarding destinations, generic home links and guessed parameters must never be labeled as customer affiliate links.

## Next action
Use the official free Poptin account flow with `support@coshuma.com`, checking for an existing account before creating one. If absent, register once at zero cost, recover the exact vendor-issued referral URL, and validate its customer destination and attribution. Stop for CAPTCHA, OTP, account-holder legal/program consent, forced identity verification or payment approval. Do not start a paid plan.
