# HelpDesk trial conversion evidence — 2026-09-11

## Why this revenue action was selected

Text/LiveChat Partner Program sent COSHUMA a campaign report for 2026-08-13 through 2026-09-10 to `support@coshuma.com`.

Vendor-reported totals:
- all campaigns: 28 clicks, 0 trials, 0 paid accounts, $0 earnings
- `HelpDesk - default`: 11 clicks, 0 trials
- `Text wins MarTech Awards`: 14 clicks, 0 trials

The HelpDesk campaign therefore has verified click activity but no vendor-reported trial conversion in the report window. This is evidence of a conversion gap, not evidence of revenue.

Gmail source:
- incoming message id: `1a08c0544c56b5ac`
- subject: `Check your last 4 week’s results: affiliate campaigns report`
- sender: `partners@livechat.com`

## Exact existing HelpDesk customer route

COSHUMA already has the exact HelpDesk customer-facing campaign URL verified from the authenticated Text Partner App:

`https://www.helpdesk.com/?a=8IetMhQvR&utm_campaign=pp_helpdesk-default&utm_source=PP&d=14`

This change reuses that exact route. It does not construct a new HelpDesk deep link, dashboard URL, signup URL, or referral parameter.

## Current official product evidence checked 2026-09-11

Official HelpDesk pricing page:
- https://www.helpdesk.com/pricing/
- 14-day free trial
- no credit card required
- Essential: $19/user/month billed yearly; $25/user/month billed monthly
- Growth: $79/user/month billed yearly; $99/user/month billed monthly
- Enterprise: custom pricing
- Essential includes 10 AI resolutions/month
- Growth includes 200 AI resolutions/month
- additional 50 AI resolutions auto-refill package listed at $49.50

Official free-trial page:
- https://www.helpdesk.com/free-help-desk/
- 14-day free trial, no credit card
- full help desk product during the trial
- shared inbox, workflows, AI Agent and reporting are included in the trial description

Official subscription guide:
- https://www.helpdesk.com/help/how-to-subscribe/
- paid subscription flow asks for plan, billing cycle, agent count and billing details
- first billing cycle is charged when the trial ends after subscription

## Revenue action

Added `/best/helpdesk-free-trial-pricing.html` as a high-intent pre-trial buyer guide.

The page:
- uses only the exact verified HelpDesk partner campaign URL for affiliate CTAs
- uses official non-affiliate HelpDesk pages only as evidence/price-check destinations
- gives visitors a concrete four-question trial plan to reduce low-intent clicks
- exposes distinct CTA source values for hero and bottom trial clicks so COSHUMA can separate this page's outbound behavior from other HelpDesk placements
- does not claim trial signups, paid accounts, commissions, or revenue

## Guardrails

- Do not treat the partner dashboard or report links as customer affiliate links.
- Do not infer a direct trial deep link by moving the existing attribution parameters to `/free-help-desk/` or `/pricing/` unless Text explicitly confirms that exact customer URL.
- Do not claim that the new page has improved conversion until partner or analytics evidence proves it.
