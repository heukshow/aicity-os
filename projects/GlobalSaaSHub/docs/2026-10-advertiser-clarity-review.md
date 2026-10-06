# COSHUMA advertiser and reader clarity review — 6 October 2026

Owner request: re-review the advertising proposal for brand identity and advertiser understanding; audit the actual advertising UI and general reader journey, fix awkward flow and usability, then report only verified outcomes.

## Confirmed findings and narrow fixes
The advertiser page still invited a sales discussion/custom quote and collected an initial email brief, contrary to the owner's self-selection model. The proposal called the logo a concept while it had reached production. Public screenshot assets still showed the older text-only creative. There was no concise description distinguishing COSHUMA, a software discovery/comparison publisher, from a software vendor or sales consultancy. The separate bundle proposal was not integrated into the media-kit decision flow.

This source change adds the publisher/reader/advertiser distinction and editorial independence; removes the active pre-sales email form and its JS rather than relabeling a draft as a submitted application; provides static position-specific logo/image/copy requirements; keeps price and booking limitations explicit; adds return-to-position links and reader navigation; collapses optional full-article context. Existing eight ad previews and thirteen creative instances remain from the existing manifests. Manual preview controls remain separate from actual eight-second rotations. Updated screenshot assets were captured from the actual public house units on 6 October, not composed or substituted with vendor campaigns.

No paid rate, Worker/configuration, payment flow, advertiser record, live ad creative, affiliate URL, existing house measurement definition, or protected homepage experiment changed. Final bundle proposals and prices remain private review items, not a public sales offer. Owner-review PDFs are not published by this PR. Source tests preserve the paid hold and unavailable prices.

## Observations before the correction
Public browser reads covered /, /advertise.html, /tool/pipedrive.html, /best/claap-sales-follow-up-ai.html, /compare/semrush-vs-frase.html, /best/index.html, /compare/, /methodology.html at 320/390/768/1440 pixels: 32 page checks, HTTP 200, no page-wide overflow or page-script errors. This is a sample of principal journeys, not a proofread of every tool profile. Sixteen fresh unit screenshots cover eight positions at 390/1440; main and official logo images loaded. Capture run ended at 2026-10-06T01:27:23Z. Mobile evidence is emulation, not a physical-phone test.

## Local verification
At 01:30 UTC, four widths passed eight advertiser preview links and thirteen creative views each, current logo/image load, back links, keyboard disclosure, historical-context tabs, no active form, no provider/payment request and no script errors/overflow. Source tests cover new identity/requirements/paused availability and existing navigation, preview, logo, original house and expansion invariants. Changed historical-gallery and removed-form expectations were updated explicitly; the paid hold tests remain.

## Remaining completion gates
Canonical PR checks, exact merge/deploy/Pages ancestry, actual live repeat of the new UI, document rendering/copy review and report. No traffic, inquiry or revenue improvement has been observed. Maintain existing fixed measurement windows; annotate the source/deployment correction instead of resetting any period.

found_by: owner-requested review
fixed_by: current task
canonical_owner: Product Experience Team / Editorial Quality Team
handoff: keep the self-selection model, distinguish reviewed proposals from paid availability, and maintain source-of-truth images/wording together.
