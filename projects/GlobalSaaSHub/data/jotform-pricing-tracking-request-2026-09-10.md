# Jotform pricing tracking URL request — 2026-09-10

## Revenue reason
- Last known healthy Search Console snapshot (`public/ops/traffic-revenue-data.json`, generated 2026-09-08T22:38:47Z) shows query `jotform pricing` with 34 impressions and 0 clicks, and `/tool/jotform.html` with 69 impressions and 0 clicks.
- COSHUMA already has verified Jotform affiliate attribution, but the current buyer guide keeps the pricing button on the official non-affiliate pricing URL until a vendor-confirmed customer-facing pricing tracking route is available.

## Existing verified routes — preserve
- Generic Jotform account-specific partner route: `https://www.jotform.com/?partner=coshuma`
- Jotform AI Agents customer route used by the production build: `https://www.jotform.com/ai/agents/?partner=coshuma`
- Do not use the legacy onboarding redirect `https://link.jotform.com/17STYVOunG?username=AnSangkwon` as a production revenue CTA.

## Direct action taken
- Company mailbox: `support@coshuma.com`
- Human contact: Ayşe Dinçer, Affiliate Manager, Jotform
- Original Gmail message: `1a08624649fff94f`
- COSHUMA reply sent: `1a0876d840d8a0a8`
- Request: provide the exact customer-facing tracked URL that should be used for visitors going directly to Jotform's official pricing page.

## State / guardrails
- Status: `pricing_tracking_url_requested`
- No new application was submitted.
- Do not construct `pricing/?partner=coshuma`, append parameters, or infer a deep link from the generic affiliate URL.
- Keep the current official non-affiliate pricing CTA until Jotform explicitly confirms the exact customer-facing tracked pricing URL.
- A vendor reply that contains a dashboard/login/onboarding URL is not sufficient evidence for a revenue link.
- Do not infer clicks, signups, commission, or revenue from this request.
