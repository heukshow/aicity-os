# eProfessor buyer-hub evidence — 2026-09-13

## Existing COSHUMA customer route

- Existing authenticated eProfessor referral evidence records the account as `approved_tracking`.
- Exact customer-facing referral URL issued to COSHUMA: `https://eprofessor.com/invite/coshuma173`.
- The authenticated referral dashboard identified this as **Your Referral Link** and stated that signups through the account-specific URL are tracked.
- This is not an admin/dashboard URL and no referral parameter is being guessed or copied onto another destination.
- Existing source evidence: `data/approved-tracking-2026-09-08.json` and `data/eprofessor-payout-review-2026-09-09.md`.

## Current first-party buyer facts rechecked 2026-09-13

Official pricing page: `https://eprofessor.com/page/pricing`

- The current pricing page lists monthly plans at Basic **$24**, Pro **$49**, Business **$99**, and Ultimate **$149**.
- The same page advertises a free trial and explicitly states **No credit card required** in the pricing header.
- The page is internally inconsistent about trial duration: the top pricing header says **14 days**, while the FAQ on the same page says **seven days**. COSHUMA must therefore **not promise a trial duration** on the central buyer hub until eProfessor resolves the conflict. The vendor's live page controls the final term.

Official referral terms: `https://eprofessor.com/page/referral-program`

- eProfessor says referrals are counted when a customer signs up using the unique referral link.
- Current program terms state a participant can earn **20% of eProfessor net profit** from referred customers while the stated eligibility/active-account conditions remain satisfied.
- Commission terms are partner-side terms only. They are **not** evidence that COSHUMA has a signup, paid customer, commission, payout, or revenue.

Official referral help: `https://eprofessor.com/page/help/settings-1/referral-program-1`

- The help center describes the unique referral-link format and says it tracks who signs up through that link.
- It distinguishes Total signups from Active Subscribers and separately exposes Net Earnings and Unpaid Balance in the authenticated referral dashboard.

## Revenue-truth boundary

- Publication of a CTA is not a click.
- A validation visit is not an organic customer click.
- A click is not a signup.
- A signup/free trial is not a paid customer.
- A paid customer is not a commission until the partner system records an eligible commission.
- A commission is not a payout until payout evidence exists.
- This buyer-hub change must leave all currently unmeasured downstream values as **unknown** rather than infer revenue.

## Safe production decision

Surface the exact issued referral URL on the verified-offers hub with current monthly pricing context and a transparent note that the vendor's current pricing page conflicts on trial duration. Do not construct a pricing/trial affiliate deep link, do not expose the referral dashboard, and do not claim a conversion or commission.