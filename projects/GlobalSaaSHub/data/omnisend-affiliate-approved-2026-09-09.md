# Omnisend affiliate approval — 2026-09-09

- COSHUMA account: `support@coshuma.com`
- Tool id: `omnisend`
- Current verified state: `approved_tracking`
- Approval evidence: Gmail message `1a084b27a331668b`, subject `Welcome to the Omnisend Affiliate Program!`
- Approval sender: `Omnisend Affiliate Team <notifications@app.impact.com>`
- Approval received: `2026-09-09 14:44:42 KST`
- Exact general tracking-link evidence: Gmail message `1a0855caf8f6dee2` from Omnisend Senior Affiliate Marketing Manager Deimantė Vaitkevičiūtė to `support@coshuma.com`.
- Vendor instruction: `Please use this link for tracking: https://your.omnisend.com/4aA5k9` and `the tracking link is in the assets.`
- Verified general customer tracking URL: `https://your.omnisend.com/4aA5k9`
- Direct pricing tracking-link evidence: Gmail message `1a085d0074ddb3a0` from Deimantė, received after COSHUMA explicitly requested a vendor-issued link landing on Omnisend's pricing page.
- Vendor instruction: `Absolutely, here's your direct tracking link to our pricing page: https://your.omnisend.com/VOKyAj`.
- Verified pricing-intent customer tracking URL: `https://your.omnisend.com/VOKyAj`
- Link classification: both URLs are vendor-issued customer-facing affiliate tracking URLs on the official `your.omnisend.com` tracking host. The pricing URL was supplied specifically in response to COSHUMA's request for a direct `https://www.omnisend.com/pricing/` destination. Neither is an Impact login/dashboard/onboarding URL or an email redirect.
- Official Omnisend affiliate documentation checked on 2026-09-09 says approved affiliates obtain links in Impact under **Content → Assets** and should use the link exactly as provided to ensure referrals are tracked.
- Official program documentation states tracking/reporting/payments are handled through Impact and uses a 60-day attribution window.
- Safety rule: preserve the exact issued URLs. Keep `https://your.omnisend.com/4aA5k9` as the canonical/general affiliate URL and use `https://your.omnisend.com/VOKyAj` only for Omnisend pricing-intent CTAs. Do not synthesize further deep links or append tracking parameters manually.

## Revenue evidence update — 2026-09-19 KST

- Vendor-human evidence: Gmail message `1a0b4ec7c76011ec` from Deimantė Vaitkevičiūtė.
- She confirmed that performance details including clicks, referrals, paying customers, commissions and payout status are visible in Impact.
- She explicitly stated that the **only activity currently visible is one click recorded on 2026-09-09**.
- Revenue-truth decision: record `outbound_clicks = 1` for this vendor-reported state. Keep referrals/signups, trials, paying customers, commission and payout fields `unknown` because the reply did not separately state zero totals for those fields.
- No customer tracking URL, pricing/trial claim or public CTA changed from this KPI update.
- COSHUMA replied in the same thread (`gmail:1a0b51b1c2d73cdd`) that Omnisend is already featured in relevant buyer-facing content using the verified tracking links and that promotion is currently organic, with no paid traffic.

## Revenue-optimization follow-up

- On 2026-09-09, COSHUMA sent a reply from `support@coshuma.com` to Deimantė requesting a vendor-issued tracking URL that lands directly on `https://www.omnisend.com/pricing/` for the pricing-focused buyer guide.
- Sent Gmail message id: `1a0857f4e0784af8` in the existing affiliate thread.
- Deimantė fulfilled that request in Gmail message `1a085d0074ddb3a0` with `https://your.omnisend.com/VOKyAj` and offered additional custom landing-page links if needed.

Next action: keep the verified general tracker live for generic Omnisend recommendations and use the vendor-issued direct pricing tracker for pricing-intent buyer CTAs. Track real clicks/signups/commissions separately; no downstream metric is inferred from the single click or from approval/link issuance.
