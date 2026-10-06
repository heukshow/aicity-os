# Reader-first house advertisements — 6 October 2026

Owner instruction: reduce all advertisements so they do not hide or displace the content that defines COSHUMA. This is a bounded presentation repair to the eight existing house positions and advertiser previews, not new inventory, sales enablement or an editorial redesign.

## Observed defect and implementation
Earlier live measurements found mobile cards 571–774px high and desktop rotating units 774–814px high. The Pipedrive floating decision dock also covered visible content. A shared, cache-versioned stylesheet now uses smaller images next to headings on narrow screens and horizontal creative/copy layouts on desktop. The official advertiser logo, complete headline/description, destination and advertising label remain. No line-clamp, scale transform, fixed maximum card height or hidden required copy is used. Main actions and rotation controls retain 44px targets. File dimensions and byte limits remain unchanged.

Supplemental sales copy below house units is shortened, not substituted for the primary content. The same shared presentation is used by the advertiser-only previews. The house carousel reserves the tallest responsive creative in its track, rather than giving all paragraphs large arbitrary minimum heights. Existing rotation timing, visibility/pause logic, impression/click definitions and QA exclusion are unchanged.

On tool pages that contain the existing house units, the decision dock is inserted after the article in normal flow instead of floating over it. Its save action and exact vendor destination are retained. Other tool pages, protected experiments, affiliate destinations and the homepage are not redesigned. Annotate this dated presentation/dock correction within the existing measurement periods; do not reset them or claim improved conversion.

## Verification and release boundary
Six new source tests cover stylesheet installation/idempotence, all eight positions, complete readable content, inline dock scope, no analytics/storage in the layout helper, and unchanged paid hold/dimensions. Existing house, logo, expansion, navigation, context and showcase tests remain enabled. Local visual QA checks current official logo and main image loading, exact QA destinations, bounded default-height layouts, page overflow and every carousel creative at four viewport widths. Mobile is emulated. Actual public verification after CI/deployment is a separate completion gate.

No prices, payment/Worker settings, paid-booking flags, external advertiser files, accounts, credentials, subscriptions or spend are changed. Proposals and screenshot updates must use the final verified layout; they must not label local preview captures as actual live captures. Keep price/availability and paid intake as unresolved sales-readiness work.

Canonical maintenance owner: Product Experience Team; Audience Growth maintains the house producers; Editorial Quality maintains the matching advertiser documents. Final CI, source/deployment ancestry, measured public heights and visual QA evidence are recorded in issue #292.
