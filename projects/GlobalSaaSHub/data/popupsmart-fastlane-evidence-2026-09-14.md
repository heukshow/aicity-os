# Popupsmart fast-lane evidence — 2026-09-14

## Revenue objective
Add one new conversion-optimization buyer surface without inventing affiliate attribution, then move the zero-cost affiliate activation to an authenticated browser queue.

## Duplicate-state check
- GitHub default-branch search for `Popupsmart` returned no prior COSHUMA record before this cycle.
- `support@coshuma.com` Gmail search `in:anywhere (popupsmart OR popupsmart.com)` returned no received, sent, spam, trash, approval, rejection, tracking-link, commission or payout message.

## Official evidence
- Affiliate program: https://popupsmart.com/affiliate-program
- Pricing: https://popupsmart.com/pricing
- Product home: https://popupsmart.com/
- Official affiliate page says no approval is required and a unique referral link is available after registering a Popupsmart account.
- Current program copy advertises 30% recurring commission on eligible paid subscriptions, a 30-day referral cookie and 50% off for referred customers for their first 3 months.
- Popupsmart advertises a forever-free plan and says no credit card is required to get started.
- The official affiliate calculator currently shows monthly list prices Basic $39, Advanced $69, Pro $99 and Expert $159. Annual billing can show lower effective monthly pricing.

## COSHUMA state after this cycle
- `application_state`: `not_submitted`
- `affiliate_status`: `browser_required_account_registration`
- exact customer referral URL: `null / unknown`
- signup / paid subscription / commission / payout / revenue: `unknown`
- GitHub issue: #482

## Buyer surfaces
- `/tool/popupsmart.html`
- `/best/popupsmart-free-plan-pricing.html`

A comparison page is intentionally omitted because this cycle did not find a sufficiently direct existing COSHUMA comparison target that would improve the buyer decision rather than manufacture SEO inventory.

## CTA rule
Until Popupsmart itself issues and COSHUMA verifies an account-specific customer referral URL, all Popupsmart CTAs remain official non-affiliate links. `app.popupsmart.com`, dashboard/login/onboarding URLs, the generic homepage and guessed query parameters are never to be promoted as affiliate links.

## Next action
Use the official free Popupsmart account flow with `support@coshuma.com`, checking for an existing account before creating one. If absent, register once, recover the exact vendor-issued customer referral URL, and validate its customer destination/attribution. Stop for CAPTCHA, OTP, account-holder legal/program consent, forced identity verification or payment approval. No paid plan is permitted.
