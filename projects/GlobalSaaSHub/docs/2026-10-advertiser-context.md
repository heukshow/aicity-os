# Advertiser preview versus editorial context — 6 October 2026

Owner reported that HighLevel appeared while trying to view advertising placements. Public HTTP reads at 08:30 KST found one HighLevel mention in advertise.html's placement description, several existing comparison/affiliate references on the Pipedrive article, no HighLevel text on the Claap article, and COSHUMA-only house creatives on both articles. This identifies confusing navigation and copy, not evidence of a HighLevel paid-ad booking. The exact viewport the owner saw was not captured.

## Bounded correction
- Eight primary position links now open an ad-only preview within advertise.html rather than immediately navigating to a product article.
- Preview identity, images, copy and the thirteen creative instances come from the existing house manifests and official logo. No second campaign source, fabricated advertiser or screenshot is introduced.
- The rotating previews use manual previous/next controls. They are clearly distinguished from the timed on-article rotation.
- Viewing a complete article remains possible through an explicitly labeled separate-tab context link, with the QA flag preserved and a notice that comparisons and affiliate links belong to the surrounding editorial page.
- Replace the incidental named-vendor locator in the advertising directory with a neutral product-comparison section description. Do not remove or rewrite the actual Pipedrive comparison or its approved affiliate links.
- Existing screenshot captions state that surrounding product recommendations are article content, not paid advertisers.

## Safety and verification
No paid order, Worker configuration, price, external API request, application receipt, email, paid-activation flag, house-event definition or PDF is changed. Preview blocks carry no house/paid/affiliate measurement attributes. All preview product buttons are display-only, not navigation or checkout controls. The paid-booking hold remains.

Four new advertiser-context tests and revised navigation expectations preserve the actual editorial links as secondary context. Existing house-expansion, showcase and sales-cleanup tests remain release gates. Local 390/1440px checks covered eight preview links and thirteen creative views per width; images and official logos loaded, preview navigation remained on advertise.html, no vendor/payment request or page error was observed. Production completion requires canonical CI, merge, deployment ancestry and separate live checks.

Canonical maintenance owner: Product Experience Team. Preserve existing fixed measurement windows. No lead, traffic, advertiser or revenue improvement is asserted.
