# FlowGent affiliate programme conflict — 2026-09-07

## Decision

- `affiliate_url`: `null`
- `affiliate_status`: `program_signup_inactive_conflict`
- Do not submit or publish a FlowGent affiliate link until the vendor resolves the conflict.

## Conflicting first-party evidence

- FlowGent's current official affiliate page at https://flowgent.ai/affiliate advertises a 20% lifetime recurring commission, a 60-day cookie, and says applications are open.
- The affiliate CTA on that same official page points to FlowGent's Rewardful signup at `flowgent-ai.getrewardful.com`.
- Following that vendor-provided signup destination currently resolves to Rewardful's `Affiliate Program Inactive` page, which says the affiliate program is no longer active.

## Resolution rule

The operational signup destination is more directly relevant to whether an application can actually be submitted than marketing copy on the landing page. Treat the program as conflicted/inactive for enrollment until newer first-party evidence restores a working signup route.

## Current status

- No application was submitted.
- Exact customer-facing referral URL is not issued or verified.
- No click, signup, commission, or revenue is claimed.
