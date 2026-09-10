# Jotform pricing tracking URL — resolved 2026-09-10

## Revenue reason
- Last known healthy Search Console snapshot (`public/ops/traffic-revenue-data.json`, generated 2026-09-08T22:38:47Z) shows query `jotform pricing` with 34 impressions and 0 clicks, and `/tool/jotform.html` with 69 impressions and 0 clicks.
- COSHUMA already had verified Jotform affiliate attribution, but the pricing buyer guide deliberately kept its pricing button non-affiliate until Jotform supplied an exact customer-facing tracked pricing route.

## Verified routes — preserve
- Generic Jotform account-specific partner route: `https://www.jotform.com/?partner=coshuma`
- Jotform AI Agents customer route: `https://www.jotform.com/ai/agents/?partner=coshuma`
- Vendor-confirmed pricing route: `https://www.jotform.com/pricing/?partner=coshuma`
- Do not use the legacy onboarding redirect `https://link.jotform.com/17STYVOunG?username=AnSangkwon` as a production revenue CTA.

## Vendor confirmation
- Company mailbox: `support@coshuma.com`
- Human contact: Ayşe Dinçer, Team Lead / Affiliate Manager, Jotform
- COSHUMA request message: `1a0876d840d8a0a8`
- Jotform reply message: `1a08a037dece876d`
- Reply received: 2026-09-10
- Jotform explicitly wrote that `https://www.jotform.com/pricing/?partner=coshuma` is the exact tracked URL COSHUMA can use in its pricing guide to send visitors to Jotform's pricing page with COSHUMA partner attribution, and said it can be published as provided.

## State / guardrails
- Status: `approved_tracking_pricing`
- No new application was submitted.
- The pricing deep link was not constructed or inferred by COSHUMA; it was supplied verbatim by Jotform's affiliate manager.
- Keep official pricing-source citations separate from revenue CTA attribution.
- Do not infer clicks, signups, commission, or revenue from approval or publication of this link.
