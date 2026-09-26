# Supademo formal affiliate application route — 2026-09-24

- task_key: `affiliate-supademo-formal-application-20260924`
- vendor: Supademo
- vendor_reply_gmail_id: `1a0d02cddb650402`
- original_outreach_gmail_id: `1a09b43356bc3947`
- prior_acknowledgement_gmail_id: `1a09b43b5ba55b97`
- submission_evidence_comment_id: `5847971116`
- observed_submission_at: `2026-09-26T16:38:43Z`

## Official route and submission evidence
Supademo support agent Mohit replied to the existing COSHUMA affiliate thread and instructed COSHUMA to use the formal request form. The current official Supademo affiliate page independently links its `Affiliate form` to `https://eu.makeforms.io/k1ibmll/`.

COSHUMA submitted that official form exactly once using the existing company identity. The resulting page displayed `Thanks for your submission!` and stated that Supademo would respond in 1-2 business days. GitHub issue #292 comment 5847971116 records the browser evidence.

The separate `https://eu.makeforms.co/xtyzhps/` route renders a Link Exchange / Guest Post form. It is not the Supademo affiliate application and must not replace the official `.io/k1ibmll/` route.

## Canonical lifecycle interpretation
- Application state: `application_submitted`.
- Review state: `pending_review`.
- Duplicate guard: `do_not_reapply=true`.
- Approval state: `null` / not yet verified.
- Exact customer-facing referral/tracking URL: `null` / not issued.
- No referral signup, trial, paid customer, commission, payout, or revenue is inferred.
- Generic Supademo, dashboard, demo, support, and form URLs are not customer tracking URLs.

## Next action
Await a new vendor decision on the existing application. Do not reapply or send duplicate outreach. If approved, record `approved` with a null URL until an exact vendor-issued customer-facing tracking URL is independently recovered and validated; only then advance to `approved_tracking`.

## Governance handoff
- found_by: Operations Governance Team
- fixed_by: Operations Governance Team
- canonical_owner: Affiliate Partnerships Team
- changed_scope: Supademo lifecycle producer and state artifacts only
- verification: Official affiliate page route, one-time browser submission confirmation, and #292 comment 5847971116
- handoff: Affiliate Partnerships Team monitors Gmail/vendor review and records only the next direct decision or exact issued tracking URL.
