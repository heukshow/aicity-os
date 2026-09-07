# ClickUp affiliate rejection evidence — 2026-08-25

## Decision

- `affiliate_url`: `null`
- `affiliate_status`: `rejected`
- Do not reapply automatically unless newer first-party or PartnerStack evidence materially changes this state.

## Official program evidence

- Current official ClickUp affiliate page: https://clickup.com/partners/affiliates
- Current official ClickUp Help article: https://help.clickup.com/hc/en-us/articles/6311978850967-Sign-up-for-the-affiliate-program
- ClickUp still operates an affiliate program through PartnerStack and only provides the unique affiliate link after approval.

## Account evidence

- PartnerStack application-received email: 2026-08-24, Gmail message id `1a0335635b16ee8a`.
- Newer PartnerStack decision email: 2026-08-25, Gmail message id `1a03902e9683c1b0`.
- The newer decision explicitly says ClickUp declined COSHUMA's application.

## Current status

- Rejected is the controlling state despite `tools.json` lacking a current affiliate status for ClickUp.
- Exact customer-facing affiliate/tracking URL is **not** issued or verified.
- No new application was submitted in this run, preventing duplicate/rejected-program churn.
