# COSHUMA house-ad logo parity — 6 October 2026

Owner-approved scope: apply visible official COSHUMA branding to the actual five fixed and three rotating house-ad positions, instead of leaving it in proposal mockups only.

## Implementation
- A shared identity renderer places the unchanged official light lockup inside each owned advertisement. The page header is not counted as advertiser identity.
- Five fixed creatives plus eight entries across three rotations have their own identity: 8 positions, 13 creative views. No third advertiser is invented for the existing two-entry comparison rotation.
- All six reused raster creatives now contain the same official symbol and wordmark. Dimensions and file-size ceilings are preserved; hashes of the inspected branded versions are recorded in data/house-ad-logo-assets.json.
- Wide fixed cards use a side-by-side desktop layout; rotation cards stack the image and copy, with controls below. Mobile retains readable text and the original logo proportions.
- Runtime main-image selectors use data-house-image so a logo cannot be mistaken for the creative during validation or view measurement.
- Source and final-output checks verify per-creative identity; the existing house tests remain intact.

## Unchanged boundaries
No paid checkout, Worker settings, paid inventory, prices, external advertiser records, accounts, credentials, purchases, affiliate destinations or event definitions were changed. Existing 8-second eligible rotation, user pause, reduced-motion behavior and QA exclusion are retained. The older self-service application work and PDF publication are not included in this change. No traffic, conversion or revenue uplift is asserted.

## Completion evidence
Source tests, current-main CI, merge, site build, exact gh-pages/Pages ancestry and actual live desktop/mobile results must all be recorded in the existing #292 work log. A local screenshot is not production evidence. Interpret this dated visual revision within the existing measurement windows rather than resetting them.

Found/fixed by: owner-requested continuation. Canonical owner: Audience Growth Team for house display; Revenue Optimization Team for paid-ad boundaries. No user action is needed for this logo-only release.
