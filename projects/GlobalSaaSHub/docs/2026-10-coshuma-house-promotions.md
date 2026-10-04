# COSHUMA house promotions — 2026-10-05

The owner requested actual COSHUMA image advertisements in the three proposal locations and explicitly clarified that self-promotion does not require payment. These first-party cards are not external paid placements, orders, captures or revenue. This release does not publish the proposal PDFs or reopen paid advertising.

## Scope and authority

`data/coshuma-promotions.json` controls exactly three owned cards: Pipedrive before the current-plan section, Claap sales follow-up before the detailed follow-up advice, and Semrush/Frase after the product links and before sources. The manifest's `enabled` flag and the source producer are the only house-content controls. Set it to false and rebuild to remove these cards; do not manipulate paid transaction fields.

The images are the existing COSHUMA proposal samples, encoded as static WebP at 600×600, 1200×675 and 1200×400 pixels. Descriptions, buttons and alt text are separately readable. The actual card uses a single gold border and the label **Advertisement · COSHUMA**. No claim of an independent third-party sponsor or editor endorsement is made.

## Payment and display separation

The paid renderer, paid catalogue, Worker configuration, payment validation and financial records are unchanged. A house card is generated next to the existing hidden paid container and is hidden if that paid container becomes visible. It must not cover an independently authorized paid placement. The house runtime makes no provider or payment requests.

Public links go only to the three approved COSHUMA destinations. Existing product claims, prices, affiliate URLs and disclosures stay intact. Homepage, Gamma, Chatbase and the Privy/Omnisend experiment receive no house card.

## Measurement and QA

`coshuma_promo_view` and `coshuma_promo_click` are separate first-party promotion events, never `sponsored_*` or paid revenue. A view requires the card and image to be visible, at least 50% of the card in the viewport for one continuous second, and a visible tab. Unsupported measurement remains unmeasured. QA starts with `coshuma_qa=1`; internal links retain that flag and these events are not emitted during QA.

Source tests protect exact scope, dimensions, copy limits, safe text output, idempotent regeneration, removal and unchanged surrounding content. The production build reruns the generator and checks its final output. Desktop/mobile rendering, images, links, non-overlap and actual live deployment need separate evidence in #292 and the operations registry. A passed build alone does not establish publication, customer activity or revenue.
