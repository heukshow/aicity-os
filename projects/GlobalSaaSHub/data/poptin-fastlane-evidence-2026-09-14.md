# Poptin fast-lane evidence — 2026-09-14

## Revenue objective
Add Poptin as the next sequential COSHUMA popup/on-site conversion buyer surface after Popupsmart, while keeping attribution evidence-first and avoiding duplicate account creation.

## Duplicate-state check
- GitHub default-branch search for `Poptin` returned no prior COSHUMA Poptin record before this cycle.
- `support@coshuma.com` Gmail search `in:anywhere (poptin OR poptin.com)` returned no received, sent, spam, trash, application, approval, rejection, tracking-link, commission or payout record.

## Official current evidence
- Affiliate program: https://www.poptin.com/affiliate/
- Affiliate terms: https://help.poptin.com/en/article/affiliate-program-terms-and-conditions-1gvl7k4/
- Terms of Service: https://www.poptin.com/terms-of-service/
- Pricing: https://www.poptin.com/pricing/
- Product home: https://www.poptin.com/
- Poptin's official affiliate page says the program is open to all and registration is free.
- Official terms require signup and acceptance of the Terms of Service before access to the affiliate control panel.
- The official program says a unique affiliate link is provided inside the authenticated control panel.
- Current public affiliate terms advertise a 90-day cookie window and lifetime 25% monthly commission for each new paying member recruited.
- Poptin advertises a Free Forever account for up to 1,000 visitors per month and says no credit card is required.
- Paid Basic, Pro and Agency tiers are available with monthly/annual billing. COSHUMA intentionally does not hard-code a checkout total because the official pricing view can vary by billing mode.

## COSHUMA state after this cycle
- `application_state`: `not_submitted`
- `affiliate_status`: `browser_required_legal_program_consent`
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
Hold at legal consent. After the account holder accepts the official Terms of Service through a supported normal flow, check for an existing COSHUMA account before any registration, recover the exact vendor-issued referral URL, and validate its customer destination and attribution. Stop for CAPTCHA, OTP, forced identity verification or payment approval. Do not start a paid plan.

## Fix-First correction — 2026-10-07
- `found_by`: Security & Cost Control Team
- `fixed_by`: Security & Cost Control Team
- `canonical_owner`: Affiliate Partnerships Team
- `changed_scope`: Poptin lifecycle state, queue upsert behavior, and generated evidence only
- `verification`: official program terms require signup and Terms of Service acceptance; `affiliate_url` and exact tracking URL remain `null`
- `handoff`: Affiliate Partnerships Team must keep the legal-consent gate until direct account-holder consent and vendor-issued URL evidence exist
