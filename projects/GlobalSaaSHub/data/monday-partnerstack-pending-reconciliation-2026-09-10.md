# monday.com PartnerStack status reconciliation — 2026-09-10

## Decision

The September 9 reply from Digna Rivas does **not** change monday.com's affiliate state from pending.

- Authenticated PartnerStack previously displayed `monday.com / Application pending`.
- Digna supplied the official PartnerStack application route: `https://dash.partnerstack.com/application?company=mondaycom&gref=page`.
- Her reply did not state that COSHUMA was approved, declined, or invited, and it did not contain a customer-facing referral/tracking URL.
- Because an authenticated pending state already exists, opening or submitting the supplied application form risks a duplicate submission.

## Evidence

- Gmail thread: `1a07c4872cf1ca3b`
- Human reply message: `1a08722bc882d6bf`
- PartnerStack support ticket: `122275`
- Reply date: 2026-09-09 13:06 EDT / 2026-09-10 02:06 KST
- Prior authenticated state evidence: `data/affiliate-browser-results-2026-09-08.json`
- Current state: `pending`
- Exact customer tracking URL: `null`

The application URL is an operational enrollment route, not a customer-facing affiliate URL and must never be published as a COSHUMA CTA.

## Next action

Wait for the existing monday.com application decision. Do not reapply, open a new PartnerStack account, or send another support request. Recheck only when PartnerStack or monday.com provides a new decision or when the authenticated dashboard changes. If approved, recover and verify the exact issued customer-facing tracking URL before changing the monday.com affiliate status or CTA. Do not infer clicks, leads, trials, customers, commissions, or revenue.
