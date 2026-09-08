# ActiveCampaign affiliate route verification — corrected 2026-09-09

## Authoritative COSHUMA-specific evidence

- Tool: `activecampaign`
- COSHUMA page: `https://coshuma.com/tool/activecampaign.html`
- Company identity: `support@coshuma.com`
- `data/activecampaign-affiliate-rejection-evidence-2026-08-28.md` records that PartnerStack received the COSHUMA application on 2026-08-24 and ActiveCampaign sent a later decision on 2026-08-28 declining it.
- `data/browser_required_queue.d/activecampaign-affiliate-2026-09-08.json` records `blocked_existing_rejection_evidence` / `rejected`.
- `data/affiliate-batch-scan-2026-09-08-0633.json` explicitly treats the prior rejection as stronger COSHUMA-specific evidence than a later observation that the public application page is available.
- Current `data/tools.json` and `data/tools.next.json` also preserve `affiliate_status: rejected`.

## Public program availability

ActiveCampaign's official affiliate program is currently public and PartnerStack-powered. Current official documentation states eligible affiliates may earn 30% recurring commission for up to 12 months, with a 90-day purchase attribution window. This only proves the program exists publicly; it does **not** reverse COSHUMA's application decision.

Official references:
- `https://help.activecampaign.com/hc/en-us/articles/115000199190-Affiliate-Program-Overview`
- `https://www.activecampaign.com/affiliate-program`

## Correct decision

- `affiliate_url`: `null`
- `affiliate_status`: `rejected`
- `affiliate_verified`: `true`
- Do **not** reapply automatically.
- Do **not** create or keep a browser-required application task merely because the public PartnerStack application route is available.
- Do **not** publish the ActiveCampaign homepage, affiliate landing page, PartnerStack application/dashboard/login/onboarding URL as a customer affiliate or revenue URL.
- Do not claim clicks, sign-ups, commissions or revenue for ActiveCampaign without customer-specific partner evidence.

## Reopen condition

Only reconsider enrollment if ActiveCampaign sends newer COSHUMA-specific first-party evidence that explicitly changes the rejection, invites a new application, or provides a concrete eligibility correction that COSHUMA has actually completed. A generic public program page is not enough.

## Correction note

The earlier 2026-09-08 version of this file incorrectly stated that no prior application or rejection evidence was found and classified the tool as `browser_required_partnerstack_application`. Repository-wide evidence review showed that statement was incomplete. GitHub issue #322, briefly created from that incomplete route note, was closed `not_planned` immediately after the conflict was found, before any duplicate application was submitted.
