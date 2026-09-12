# Text / LiveChat Partner performance evidence — 2026-09-11

## Verified source

- Gmail account: `support@coshuma.com`
- Vendor sender: Pawel from LiveChat / Text Partner Program `<partners@livechat.com>`
- Gmail thread/message id used for this evidence: `1a08c0544c56b5ac`
- Report period: 2026-08-13 through 2026-09-10

## Vendor-reported aggregate results

- 28 clicks
- $0 earnings
- 0 trials
- 0 paid accounts

## Best-performing campaigns

- `Text wins MarTech Awards`: 14 clicks, 0 trials
- `HelpDesk - default`: 11 clicks, 0 trials

These are vendor-reported partner-platform metrics. They prove clicks only; they do **not** prove a signup, trial, paid customer, commission, or revenue.

## Existing verified revenue routes

- Text exact tracked customer URL already in repository: `https://www.text.com/?a=8IetMhQvR&utm_campaign=pp_text-wins-martech-awards&utm_source=PP`
- HelpDesk exact tracked customer URL already in repository: `https://www.helpdesk.com/?a=8IetMhQvR&utm_campaign=pp_helpdesk-default&utm_source=PP&d=14`

Do not replace either route with a generic homepage/dashboard URL and do not construct a deep link by copying tracking parameters onto another path.

## Revenue action executed on 2026-09-11

COSHUMA replied from `support@coshuma.com` in the vendor report thread (sent Gmail message id `1a08c26b4026d018`) asking Text Partners for an **exact vendor-supported customer-facing deep tracking URL** that lands directly on Text's 14-day free-trial signup or pricing page while preserving COSHUMA attribution and the existing campaign. The message explicitly says COSHUMA will not construct or guess a deep link.

## Vendor routing answer received on 2026-09-12

Text.com support representative Przemek Kurowski replied in the existing `support@coshuma.com` thread on 2026-09-12 04:28:39 UTC:

> The Partner Program is based on campaigns. We do not have a deeper campaign than the ones you can see in the panel. If you wish to proceed with a campaign, in the panel, choose the one you’re interested in, and you’ll be forwarded to the correct campaign.

Evidence interpretation:

- Text's program is campaign-based.
- The vendor says there is **no deeper campaign** beyond the campaigns exposed in the partner panel.
- COSHUMA must not invent a trial/signup/pricing deep link by transplanting affiliate parameters onto another Text path.
- The existing verified `Text wins MarTech Awards` campaign remains the authoritative Text customer-facing tracked route unless the authenticated panel exposes another campaign and it is separately verified.
- Text's current official pricing page still offers a 14-day free trial with no card required, but that fact does **not** turn the affiliate campaign URL into a direct trial deep link.

## Conversion copy correction executed on 2026-09-12

The build guard `scripts/normalize_text_verified_tracking.py` was updated so that:

1. every Text affiliate CTA is still forced to the exact vendor-issued campaign URL;
2. misleading direct-deeplink labels such as `Start Text Free for 14 Days — No Card` and `Test Text Free for 14 Days` are normalized to `Open Text.com → Start 14-day trial`;
3. the main Text buyer page receives a visible routing note explaining that the tracked campaign opens Text.com first and the visitor then chooses `Start free trial` on Text.com;
4. the build fails closed if the exact tracked URL is altered or if the main Text page loses the routing note / regains the old misleading labels.

This change preserves the already verified attribution route while reducing a conversion/trust mismatch that could cause visitors to expect a dedicated trial landing page that the vendor explicitly says it does not provide.

## Current decision

- Text status remains `approved_tracking`.
- HelpDesk status remains `approved_tracking`.
- No reapplication.
- No guessed deep link.
- No revenue claim.
- Vendor-reported historical funnel remains 28 clicks -> 0 trials -> 0 paid accounts -> $0 earnings for the stated report period.
- Future campaign changes must come from the authenticated partner panel or another direct vendor confirmation; a generic homepage, dashboard, onboarding URL, or hand-built parameterized URL is not sufficient evidence.
